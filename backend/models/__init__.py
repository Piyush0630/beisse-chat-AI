"""
Pydantic models for chat-related data structures
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class SourceMetadata(BaseModel):
    """Metadata for a source document"""
    manual_name: str = ""
    manual_file: str = ""
    page_number: int = 0
    section: Optional[str] = None
    bbox: Optional[dict] = None
    similarity_score: Optional[float] = None


class Citation(BaseModel):
    """Citation reference in a response"""
    id: str = ""
    source: SourceMetadata = Field(default_factory=SourceMetadata)
    quoted_text: str = ""


class ChatMessage(BaseModel):
    """A chat message"""
    id: str = Field(default_factory=lambda: f"msg_{int(datetime.now().timestamp() * 1000)}")
    role: MessageRole
    content: str
    citations: List[Citation] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request to send a chat message"""
    message: str
    conversation_id: Optional[str] = None
    category: Optional[str] = None
    memory_enabled: bool = True


class ChatResponse(BaseModel):
    """Response from chat API"""
    answer: str
    sources: List[SourceMetadata] = Field(default_factory=list)
    citations: List[Citation] = Field(default_factory=list)
    confidence: float = 0.0
    message_id: str = ""
    conversation_id: Optional[str] = None


class ConversationCreate(BaseModel):
    """Request to create a new conversation"""
    title: Optional[str] = None
    category: Optional[str] = None


class ConversationResponse(BaseModel):
    """Conversation metadata response"""
    id: str
    title: str
    category: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class ConversationListResponse(BaseModel):
    """List of conversations"""
    conversations: List[ConversationResponse]
    total_count: int
