"""
PDF Text Extractor using PyMuPDF (fitz)

Extracts text blocks with bounding box coordinates from PDF documents.
"""

import fitz  # PyMuPDF
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


@dataclass
class TextBlock:
    """A single block of extracted text"""
    text: str
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    block_type: str  # heading, text, list, table, caption
    page_number: int
    font_size: Optional[float] = None
    font_name: Optional[str] = None
    font_flags: Optional[int] = None


@dataclass
class ExtractedPage:
    """Extracted content from a single page"""
    page_number: int
    blocks: List[TextBlock]
    width: float
    height: float
    rotation: int


@dataclass
class PDFExtractionResult:
    """Result of PDF extraction"""
    document_id: str
    filename: str
    pages: List[ExtractedPage]
    metadata: Dict
    extraction_time_seconds: float
    total_blocks: int


class PDFExtractor:
    """Extract text with coordinates from PDF documents"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc: Optional[fitz.Document] = None
        self._validate_pdf()
    
    def _validate_pdf(self):
        """Validate that the file exists and is a valid PDF"""
        import os
        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
        
        if not self.pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {self.pdf_path}")
        
        try:
            self.doc = fitz.open(self.pdf_path)
        except Exception as e:
            raise ValueError(f"Failed to open PDF: {e}")
    
    def extract_all(self) -> List[ExtractedPage]:
        """Extract all text blocks from the entire PDF"""
        if self.doc is None:
            raise RuntimeError("PDF document not loaded")
        
        pages = []
        for page_num, page in enumerate(self.doc, start=1):
            extracted_page = self._extract_page(page, page_num)
            pages.append(extracted_page)
        
        return pages
    
    def _extract_page(self, page: fitz.Page, page_number: int) -> ExtractedPage:
        """Extract text blocks from a single page"""
        blocks = []
        
        # Get page dimensions
        width = page.rect.width
        height = page.rect.height
        
        # Extract text in dict format
        text_dict = page.get_text("dict")
        
        for block in text_dict.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line.get("spans", []):
                        block_text = span.get("text", "").strip()
                        if block_text:
                            text_block = TextBlock(
                                text=block_text,
                                bbox=tuple(span["bbox"]),
                                block_type=self._classify_block(span),
                                page_number=page_number,
                                font_size=span.get("size"),
                                font_name=span.get("font"),
                                font_flags=span.get("flags")
                            )
                            blocks.append(text_block)
        
        return ExtractedPage(
            page_number=page_number,
            blocks=blocks,
            width=width,
            height=height,
            rotation=page.rotation if hasattr(page, 'rotation') else 0
        )
    
    def _classify_block(self, span: dict) -> str:
        """Classify text block based on formatting characteristics"""
        font_size = span.get("size", 0)
        font_name = span.get("font", "").lower()
        font_flags = span.get("flags", 0)
        
        # Check for bold text (flag 1 = serif, flag 16 = monospace, flag 2 = italic, flag 1 = superscript)
        is_bold = "bold" in font_name or "black" in font_name or font_flags & 8
        
        # Classify based on size and formatting
        if font_size >= 16 or (font_size >= 14 and is_bold):
            return "heading"
        elif font_size <= 8:
            return "caption"
        elif "-" in font_name or "italic" in font_name:
            return "emphasis"
        else:
            return "text"
    
    def get_metadata(self) -> Dict:
        """Get PDF metadata"""
        if self.doc is None:
            raise RuntimeError("PDF document not loaded")
        
        return {
            "page_count": len(self.doc),
            "metadata": dict(self.doc.metadata) if self.doc.metadata else {},
            "toc": self.doc.get_toc() if hasattr(self.doc, 'get_toc') else [],
            "filename": self.pdf_path.split("/")[-1],
            "extracted_at": datetime.utcnow().isoformat()
        }
    
    def extract_with_toc_context(self) -> Dict:
        """Extract text with table of contents context"""
        import time
        start_time = time.time()
        
        pages = self.extract_all()
        metadata = self.get_metadata()
        
        # Build section mapping from TOC
        toc = metadata.get("toc", [])
        section_mapping = self._build_section_mapping(toc, pages)
        
        # Associate sections with blocks
        for page in pages:
            for block in page.blocks:
                block.section = self._get_section_for_block(
                    page.page_number, block.bbox[1], section_mapping
                )
        
        extraction_time = time.time() - start_time
        
        return {
            "document_id": hashlib.md5(self.pdf_path.encode()).hexdigest()[:12],
            "filename": metadata["filename"],
            "pages": pages,
            "metadata": metadata,
            "extraction_time_seconds": extraction_time,
            "total_blocks": sum(len(p.blocks) for p in pages)
        }
    
    def _build_section_mapping(self, toc: List, pages: List[ExtractedPage]) -> Dict:
        """Build mapping of page/section relationships from TOC"""
        mapping = {}
        for entry in toc:
            if len(entry) >= 3:
                level, title, page_dest = entry[:3]
                if isinstance(page_dest, int):
                    mapping[page_dest] = title
        return mapping
    
    def _get_section_for_block(
        self, 
        page_num: int, 
        block_y: float,
        section_mapping: Dict
    ) -> Optional[str]:
        """Determine which section a block belongs to based on its position"""
        # Find the most recent section that appears before this block
        relevant_pages = [p for p in section_mapping.keys() if p <= page_num]
        if not relevant_pages:
            return None
        
        # Get the last section before this page
        last_section_page = max(relevant_pages)
        return section_mapping[last_section_page]
    
    def close(self):
        """Close the PDF document"""
        if self.doc:
            self.doc.close()
            self.doc = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def extract_text_blocks(pdf_path: str) -> PDFExtractionResult:
    """Convenience function to extract all text from a PDF"""
    with PDFExtractor(pdf_path) as extractor:
        start_time = datetime.utcnow()
        pages = extractor.extract_all()
        metadata = extractor.get_metadata()
        extraction_time = (datetime.utcnow() - start_time).total_seconds()
        
        total_blocks = sum(len(page.blocks) for page in pages)
        
        return PDFExtractionResult(
            document_id=hashlib.md5(pdf_path.encode()).hexdigest()[:12],
            filename=pdf_path.split("/")[-1],
            pages=pages,
            metadata=metadata,
            extraction_time_seconds=extraction_time,
            total_blocks=total_blocks
        )
