"""
Document Chunker

Splits documents into semantically coherent overlapping chunks for vector storage.
"""

import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """A single chunk of a document"""
    id: str
    text: str
    page_number: int
    section: Optional[str] = None
    chunk_index: int = 0
    start_char: int = 0
    end_char: int = 0
    token_count: int = 0


@dataclass
class ChunkingResult:
    """Result of document chunking"""
    document_id: str
    chunks: List[DocumentChunk]
    total_chunks: int
    total_tokens: int
    processing_time_seconds: float


class DocumentChunker:
    """Splits documents into semantically coherent chunks"""
    
    def __init__(
        self, 
        chunk_size: int = 500,  # tokens
        chunk_overlap: int = 50  # tokens
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(
        self,
        extracted_blocks: List[Dict],
        document_metadata: Dict,
        document_id: Optional[str] = None
    ) -> ChunkingResult:
        """Split document into overlapping chunks"""
        import time
        start_time = time.time()
        
        # Convert blocks to TextBlock-like objects
        blocks = self._normalize_blocks(extracted_blocks)
        
        # Build chunks
        chunks = self._build_chunks(blocks, document_metadata)
        
        # Calculate total tokens
        total_tokens = sum(c.token_count for c in chunks)
        
        # Generate document ID if not provided
        if document_id is None:
            doc_content = "".join(b["text"] for b in extracted_blocks)
            document_id = hashlib.md5(doc_content.encode()).hexdigest()[:12]
        
        processing_time = time.time() - start_time
        
        return ChunkingResult(
            document_id=document_id,
            chunks=chunks,
            total_chunks=len(chunks),
            total_tokens=total_tokens,
            processing_time_seconds=processing_time
        )
    
    def _normalize_blocks(self, blocks: List[Dict]) -> List[Dict]:
        """Normalize block data to consistent format"""
        normalized = []
        current_char_pos = 0
        
        for block in blocks:
            normalized_block = {
                "text": block.get("text", "").strip(),
                "page_number": block.get("page_number", 1),
                "type": block.get("type", "text"),
                "section": block.get("section"),
                "start_char": current_char_pos,
                "end_char": current_char_pos + len(block.get("text", "")),
                "font_size": block.get("font_size"),
                "bbox": block.get("bbox")
            }
            current_char_pos = normalized_block["end_char"]
            normalized.append(normalized_block)
        
        return normalized
    
    def _build_chunks(
        self, 
        blocks: List[Dict],
        metadata: Dict
    ) -> List[DocumentChunk]:
        """Build overlapping chunks from blocks"""
        chunks = []
        current_chunk_blocks = []
        current_token_count = 0
        chunk_index = 0
        
        for block in blocks:
            block_tokens = self._estimate_tokens(block["text"])
            
            # Check if adding this block exceeds chunk size
            if current_token_count + block_tokens > self.chunk_size and current_chunk_blocks:
                # Create chunk from current blocks
                chunk = self._create_chunk(
                    blocks=current_chunk_blocks,
                    metadata=metadata,
                    chunk_index=chunk_index
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Keep overlap from previous chunk
                current_chunk_blocks = self._get_overlap_blocks(
                    current_chunk_blocks, 
                    self.chunk_overlap
                )
                current_token_count = sum(
                    self._estimate_tokens(b["text"]) 
                    for b in current_chunk_blocks
                )
            
            current_chunk_blocks.append(block)
            current_token_count += block_tokens
        
        # Don't forget the last chunk
        if current_chunk_blocks:
            chunk = self._create_chunk(
                blocks=current_chunk_blocks,
                metadata=metadata,
                chunk_index=chunk_index
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(
        self,
        blocks: List[Dict],
        metadata: Dict,
        chunk_index: int
    ) -> DocumentChunk:
        """Create a single document chunk"""
        # Combine text from all blocks
        combined_text = " ".join(b["text"] for b in blocks)
        
        # Generate unique chunk ID
        chunk_id = self._generate_chunk_id(combined_text, chunk_index)
        
        # Find section from first heading in chunk
        section = None
        for block in blocks:
            if block.get("type") == "heading":
                section = block["text"]
                break
        
        # Calculate character positions
        start_char = blocks[0].get("start_char", 0)
        end_char = blocks[-1].get("end_char", len(combined_text))
        
        # Estimate tokens
        token_count = self._estimate_tokens(combined_text)
        
        # Get page number (use the most common page in chunk)
        page_numbers = [b.get("page_number", 1) for b in blocks]
        page_number = max(set(page_numbers), key=page_numbers.count)
        
        # Get bbox for first block (for highlighting)
        bbox = blocks[0].get("bbox")
        
        return DocumentChunk(
            id=chunk_id,
            text=combined_text,
            page_number=page_number,
            section=section,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            token_count=token_count
        )
    
    def _get_overlap_blocks(
        self, 
        blocks: List[Dict], 
        max_overlap_tokens: int
    ) -> List[Dict]:
        """Get blocks from the end of current chunk for overlap"""
        overlap_blocks = []
        current_tokens = 0
        
        # Work backwards from the end
        for block in reversed(blocks):
            block_tokens = self._estimate_tokens(block["text"])
            if current_tokens + block_tokens <= max_overlap_tokens:
                overlap_blocks.insert(0, block)
                current_tokens += block_tokens
            else:
                break
        
        return overlap_blocks
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 4 chars per token)"""
        return len(text) // 4
    
    def _generate_chunk_id(self, text: str, index: int) -> str:
        """Generate unique chunk ID"""
        content = f"{text[:100]}_{index}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def chunk_text(
        self,
        text: str,
        document_metadata: Dict,
        start_page: int = 1,
        start_section: Optional[str] = None
    ) -> List[DocumentChunk]:
        """Chunk plain text (fallback method)"""
        # Split by paragraphs/sections
        paragraphs = text.split("\n\n")
        
        chunks = []
        current_chunk = []
        current_text = ""
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if adding this paragraph exceeds chunk size
            if len(current_text) + len(para) > (self.chunk_size * 4):
                if current_text:
                    chunk = DocumentChunk(
                        id=self._generate_chunk_id(current_text, chunk_index),
                        text=current_text.strip(),
                        page_number=start_page,
                        section=start_section,
                        chunk_index=chunk_index,
                        token_count=self._estimate_tokens(current_text)
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_text = para
                else:
                    # Paragraph too large, split it
                    para_chunks = self._split_large_paragraph(
                        para, start_page, start_section, chunk_index
                    )
                    chunks.extend(para_chunks)
                    chunk_index += len(para_chunks)
            else:
                if current_text:
                    current_text += "\n\n"
                current_text += para
        
        # Add final chunk
        if current_text:
            chunk = DocumentChunk(
                id=self._generate_chunk_id(current_text, chunk_index),
                text=current_text.strip(),
                page_number=start_page,
                section=start_section,
                chunk_index=chunk_index,
                token_count=self._estimate_tokens(current_text)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_large_paragraph(
        self,
        text: str,
        page: int,
        section: Optional[str],
        start_index: int
    ) -> List[DocumentChunk]:
        """Split a paragraph that's too large for a single chunk"""
        chunks = []
        max_chunk_chars = self.chunk_size * 4
        words = text.split()
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) > max_chunk_chars:
                # Create chunk
                chunk_text = " ".join(current_chunk)
                chunk = DocumentChunk(
                    id=self._generate_chunk_id(chunk_text, start_index),
                    text=chunk_text,
                    page_number=page,
                    section=section,
                    chunk_index=start_index,
                    token_count=self._estimate_tokens(chunk_text)
                )
                chunks.append(chunk)
                start_index += 1
                current_chunk = [word]
                current_length = len(word)
            else:
                current_chunk.append(word)
                current_length += len(word) + 1
        
        # Final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk = DocumentChunk(
                id=self._generate_chunk_id(chunk_text, start_index),
                text=chunk_text,
                page_number=page,
                section=section,
                chunk_index=start_index,
                token_count=self._estimate_tokens(chunk_text)
            )
            chunks.append(chunk)
        
        return chunks


def chunk_document(
    blocks: List[Dict],
    metadata: Dict,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> ChunkingResult:
    """Convenience function for document chunking"""
    chunker = DocumentChunker(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return chunker.chunk_document(blocks, metadata)
