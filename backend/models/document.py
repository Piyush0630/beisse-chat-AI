"""
Pydantic models for document-related data structures
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class DocumentCategory(str, Enum):
    MACHINE_OPERATION = "machine_operation"
    MAINTENANCE = "maintenance"
    SAFETY = "safety"
    TROUBLESHOOTING = "troubleshooting"
    PROGRAMMING = "programming"


class DocumentInfo(BaseModel):
    """Metadata for an uploaded document"""
    id: str = ""
    filename: str = ""
    title: Optional[str] = None
    category: DocumentCategory = DocumentCategory.MACHINE_OPERATION
    status: DocumentStatus = DocumentStatus.PENDING
    page_count: int = 0
    chunk_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    file_size_bytes: int = 0


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    success: bool
    document_id: str
    filename: str
    chunk_count: int
    message: str


class DocumentListResponse(BaseModel):
    """List of documents"""
    documents: List[DocumentInfo]
    total_count: int
    category_counts: dict


class DocumentProcessResult(BaseModel):
    """Result of document processing"""
    document_id: str
    success: bool
    chunk_count: int
    processing_time_seconds: float
    error_message: Optional[str] = None


class DocumentDeleteResponse(BaseModel):
    """Response after document deletion"""
    success: bool
    document_id: str
    message: str
