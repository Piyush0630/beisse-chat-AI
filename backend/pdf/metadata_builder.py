"""
Metadata Builder for PDF Processing

Builds comprehensive metadata for vector storage.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetadataBuilder:
    """Builds metadata for documents and chunks"""
    
    @staticmethod
    def build_chunk_metadata(
        chunk_id: str,
        document_info: Dict,
        page_number: int,
        section: Optional[str] = None,
        bbox: Optional[Dict] = None,
        chunk_index: int = 0,
        chunk_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Build metadata dictionary for a chunk
        
        Args:
            chunk_id: Unique chunk identifier
            document_info: Document metadata dict
            page_number: Page number in source PDF
            section: Section title if available
            bbox: Bounding box coordinates
            chunk_index: Index of chunk in document
            chunk_type: Type of content (text, heading, list, etc.)
            
        Returns:
            Metadata dictionary for ChromaDB
        """
        return {
            # Identifiers
            "id": chunk_id,
            "manual_id": document_info.get("id", ""),
            "chunk_index": chunk_index,
            
            # Document Info
            "manual_name": document_info.get("title", document_info.get("filename", "Unknown Manual")),
            "manual_file": document_info.get("filename", ""),
            "category": document_info.get("category", "general"),
            
            # Location Info
            "page_number": page_number,
            "section": section,
            
            # Bounding Box (for highlighting)
            "bbox": bbox,
            
            # Content Type
            "chunk_type": chunk_type,
            
            # Quality Metrics
            "confidence": 0.96,  # Default confidence for extracted content
            
            # Language
            "language": document_info.get("language", "en"),
            
            # Timestamps
            "created_at": datetime.utcnow().isoformat(),
            "document_created_at": document_info.get("created_at", "")
        }
    
    @staticmethod
    def build_document_metadata(
        document_id: str,
        filename: str,
        title: Optional[str] = None,
        category: str = "general",
        page_count: int = 0,
        chunk_count: int = 0,
        file_size_bytes: int = 0,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Build metadata for a complete document
        
        Args:
            document_id: Unique document identifier
            filename: Original filename
            title: Document title (defaults to filename without extension)
            category: Document category
            page_count: Number of pages
            chunk_count: Number of chunks created
            file_size_bytes: File size in bytes
            language: Document language
            
        Returns:
            Document metadata dictionary
        """
        return {
            # Identifiers
            "id": document_id,
            "filename": filename,
            "title": title or filename.replace('.pdf', '').replace('_', ' '),
            
            # Categorization
            "category": category,
            "status": "processing",  # Will be updated to "ready" after processing
            
            # Content Metrics
            "page_count": page_count,
            "chunk_count": chunk_count,
            "file_size_bytes": file_size_bytes,
            
            # Language
            "language": language,
            
            # Timestamps
            "created_at": datetime.utcnow().isoformat(),
            "processed_at": "",
            "updated_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def build_vector_metadata(
        chunk_id: str,
        text: str,
        source_metadata: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """
        Build complete metadata for vector storage
        
        Args:
            chunk_id: Unique chunk identifier
            text: Chunk text content
            source_metadata: Source document metadata
            category: Document category
            
        Returns:
            Complete metadata for ChromaDB document
        """
        return {
            # Identifiers
            "id": chunk_id,
            
            # Content
            "text_preview": text[:200] + "..." if len(text) > 200 else text,
            "text_length": len(text),
            
            # Source
            "manual_name": source_metadata.get("manual_name", "Unknown"),
            "manual_file": source_metadata.get("manual_file", ""),
            "manual_id": source_metadata.get("manual_id", ""),
            
            # Location
            "page_number": source_metadata.get("page_number", 0),
            "section": source_metadata.get("section"),
            "bbox": source_metadata.get("bbox"),
            
            # Categorization
            "category": category,
            
            # Quality
            "confidence": source_metadata.get("confidence", 0.95),
            
            # Metadata
            "language": source_metadata.get("language", "en"),
            "chunk_type": source_metadata.get("chunk_type", "text"),
            
            # Timestamps
            "created_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def update_document_status(
        metadata: Dict[str, Any],
        status: str,
        chunk_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update document status after processing
        
        Args:
            metadata: Existing document metadata
            status: New status (processing, ready, error)
            chunk_count: Optional chunk count update
            
        Returns:
            Updated metadata dictionary
        """
        updated = metadata.copy()
        updated["status"] = status
        updated["updated_at"] = datetime.utcnow().isoformat()
        
        if status == "ready":
            updated["processed_at"] = datetime.utcnow().isoformat()
        
        if chunk_count is not None:
            updated["chunk_count"] = chunk_count
        
        return updated
    
    @staticmethod
    def build_search_result_metadata(
        chunk: Dict,
        similarity_score: float
    ) -> Dict[str, Any]:
        """
        Build metadata for search results
        
        Args:
            chunk: Search result chunk
            similarity_score: Similarity score from vector search
            
        Returns:
            Formatted metadata for response
        """
        metadata = chunk.get("metadata", {})
        
        return {
            "manual_name": metadata.get("manual_name", "Unknown"),
            "manual_file": metadata.get("manual_file", ""),
            "page_number": metadata.get("page_number", 0),
            "section": metadata.get("section"),
            "bbox": metadata.get("bbox"),
            "similarity_score": similarity_score,
            "chunk_type": metadata.get("chunk_type", "text"),
            "category": metadata.get("category", "general")
        }
    
    @staticmethod
    def extract_sections_from_toc(
        toc: List[List],
        page_data: Dict[int, Dict]
    ) -> Dict[int, str]:
        """
        Extract section mappings from table of contents
        
        Args:
            toc: Table of contents from PyMuPDF
            page_data: Page data dictionary
            
        Returns:
            Dictionary mapping page numbers to section titles
        """
        section_mapping = {}
        
        for entry in toc:
            if len(entry) >= 3:
                level, title, page_dest = entry[:3]
                if isinstance(page_dest, int):
                    section_mapping[page_dest] = title
        
        return section_mapping
    
    @staticmethod
    def build_batch_metadata(
        chunks: List[Dict],
        document_info: Dict,
        category: str
    ) -> List[Dict]:
        """
        Build metadata for a batch of chunks
        
        Args:
            chunks: List of chunk data
            document_info: Document metadata
            category: Document category
            
        Returns:
            List of metadata dictionaries
        """
        metadata_list = []
        
        for idx, chunk in enumerate(chunks):
            metadata = MetadataBuilder.build_chunk_metadata(
                chunk_id=chunk.get("id", f"chunk_{idx}"),
                document_info=document_info,
                page_number=chunk.get("page_number", 1),
                section=chunk.get("section"),
                bbox=chunk.get("bbox"),
                chunk_index=idx,
                chunk_type=chunk.get("type", "text")
            )
            metadata_list.append(metadata)
        
        return metadata_list


def build_document_info(
    document_id: str,
    filename: str,
    category: str,
    page_count: int,
    file_size_bytes: int = 0
) -> Dict[str, Any]:
    """Convenience function to build document info"""
    return MetadataBuilder.build_document_metadata(
        document_id=document_id,
        filename=filename,
        category=category,
        page_count=page_count,
        file_size_bytes=file_size_bytes
    )
