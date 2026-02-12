# Biesse Technical Documentation Chat Assistant - Phase 1 Implementation Plan

**Version:** 1.0  
**Date:** February 12, 2026  
**Phase:** Phase 1 - Foundation & Core RAG Pipeline  
**Duration:** 2 Weeks

---

## 1. Overview

Phase 1 focuses on building the foundational infrastructure and core RAG (Retrieval-Augmented Generation) pipeline for the Biesse Technical Documentation Chat Assistant. This phase establishes the backend architecture, database layer, document processing pipeline, and basic frontend setup.

### Goals
- Set up complete project structure (frontend + backend)
- Implement document upload and processing pipeline
- Build RAG query processing with citations
- Create basic chat interface with PDF viewer
- Establish development environment

### Deliverables
1. Fully functional backend with FastAPI
2. Document processing pipeline (PDF → chunks → vectors)
3. RAG query engine with Google Gemini
4. Basic frontend application
5. Docker Compose development environment
6. Unit tests for core functionality

---

## 2. Project Structure

```
beisse-chat-ai/
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── chat.py               # Chat endpoints
│   │   ├── documents.py          # Document management endpoints
│   │   └── health.py             # Health check endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── rag_pipeline.py       # RAG orchestration
│   │   ├── query_processor.py    # Query processing logic
│   │   └── response_formatter.py # Response formatting with citations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py       # Google Gemini integration
│   │   ├── embedding_service.py  # Text embedding generation
│   │   └── vector_service.py     # ChromaDB operations
│   ├── pdf/
│   │   ├── __init__.py
│   │   ├── extractor.py         # PDF text extraction
│   │   ├── chunker.py           # Document chunking
│   │   └── metadata_builder.py  # Metadata generation
│   ├── models/
│   │   ├── __init__.py
│   │   ├── chat.py             # Chat-related Pydantic models
│   │   └── document.py         # Document-related Pydantic models
│   ├── db/
│   │   ├── __init__.py
│   │   ├── connection.py       # Database connection management
│   │   └── repositories/       # Data access layer (placeholder for V2)
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logger.py          # Logging utilities
│   ├── data/
│   │   ├── manuals/           # Uploaded PDF documents
│   │   ├── chromadb/          # ChromaDB persistence
│   │   └── uploads/           # Temporary file uploads
│   ├── requirements.txt       # Python dependencies
│   └── tests/
│       ├── __init__.py
│       ├── test_api/
│       ├── test_core/
│       └── test_services/
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── Layout.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   └── MainContent.tsx
│   │   │   ├── ChatPanel/
│   │   │   │   ├── ChatPanel.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── UserMessage.tsx
│   │   │   │   ├── AIMessage.tsx
│   │   │   │   └── InputBox.tsx
│   │   │   └── PDFViewer/
│   │   │       ├── PDFViewerPanel.tsx
│   │   │       ├── PDFRenderer.tsx
│   │   │       └── HighlightOverlay.tsx
│   │   ├── lib/
│   │   │   ├── api.ts         # API client
│   │   │   ├── store.ts       # Zustand state management
│   │   │   └── types.ts       # TypeScript type definitions
│   │   └── hooks/
│   │       └── useChat.ts    # Chat-related React hooks
│   ├── public/
│   │   └── (static assets)
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   └── next.config.js
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 3. Backend Implementation Details

### 3.1 Configuration Management (config.py)

**Purpose:** Centralized configuration for the entire application

**Key Configuration Variables:**
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    app_name: str = "Biesse Technical Documentation Chat Assistant"
    debug: bool = True
    log_level: str = "INFO"
    
    # API Keys
    google_api_key: str  # Required for Gemini and Embeddings
    
    # Database
    database_url: str = "sqlite:///./data/conversations.db"
    
    # Vector Database
    chromadb_path: str = "./data/chromadb"
    collection_name_prefix: str = "biesse_"
    
    # PDF Processing
    max_file_size_mb: int = 50
    chunk_size: int = 500  # tokens
    chunk_overlap: int = 50  # tokens
    
    # LLM Settings
    embedding_model: str = "text-embedding-004"
    embedding_dimensions: int = 768
    llm_model: str = "gemini-2.0-flash-exp"
    llm_temperature: float = 0.3
    max_tokens: int = 2048
    
    # Categories
    document_categories: List[str] = [
        "machine_operation",
        "maintenance",
        "safety",
        "troubleshooting",
        "programming"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

**File:** [`backend/config.py`](backend/config.py)

---

### 3.2 Pydantic Models

#### 3.2.1 Chat Models (models/chat.py)

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class SourceMetadata(BaseModel):
    manual_name: str
    manual_file: str
    page_number: int
    section: Optional[str] = None
    bbox: Optional[dict] = None
    similarity_score: Optional[float] = None

class Citation(BaseModel):
    id: str
    source: SourceMetadata
    quoted_text: str

class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: f"msg_{datetime.now().timestamp()}")
    role: MessageRole
    content: str
    citations: List[Citation] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    category: Optional[str] = None
    memory_enabled: bool = True

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceMetadata]
    citations: List[Citation]
    confidence: float
    message_id: str
    conversation_id: Optional[str] = None

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None

class ConversationResponse(BaseModel):
    id: str
    title: str
    category: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
```

**File:** [`backend/models/chat.py`](backend/models/chat.py)

#### 3.2.2 Document Models (models/document.py)

```python
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

class DocumentUpload(BaseModel):
    filename: str
    category: DocumentCategory
    title: Optional[str] = None

class DocumentInfo(BaseModel):
    id: str
    filename: str
    title: Optional[str]
    category: DocumentCategory
    status: DocumentStatus
    page_count: int
    chunk_count: int
    created_at: datetime
    file_size_bytes: int

class DocumentProcessResult(BaseModel):
    document_id: str
    success: bool
    chunk_count: int
    processing_time_seconds: float
    error_message: Optional[str] = None

class DocumentListResponse(BaseModel):
    documents: List[DocumentInfo]
    total_count: int
    category_counts: dict
```

**File:** [`backend/models/document.py`](backend/models/document.py)

---

### 3.3 PDF Processing Pipeline

#### 3.3.1 Text Extractor (pdf/extractor.py)

**Purpose:** Extract text with bounding box coordinates from PDF documents

```python
import fitz  # PyMuPDF
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import hashlib

@dataclass
class TextBlock:
    text: str
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    block_type: str  # heading, text, list, table
    page_number: int
    font_size: Optional[float] = None
    font_name: Optional[str] = None

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
    
    def extract_all(self) -> List[TextBlock]:
        """Extract all text blocks from the PDF"""
        blocks = []
        for page_num, page in enumerate(self.doc, start=1):
            text_dict = page.get_text("dict")
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            block_text = span.get("text", "").strip()
                            if block_text:
                                text_block = TextBlock(
                                    text=block_text,
                                    bbox=(span["bbox"][0], span["bbox"][1],
                                          span["bbox"][2], span["bbox"][3]),
                                    block_type=self._classify_block(span),
                                    page_number=page_num,
                                    font_size=span.get("size"),
                                    font_name=span.get("font")
                                )
                                blocks.append(text_block)
        return blocks
    
    def _classify_block(self, span: dict) -> str:
        """Classify text block based on formatting"""
        font_size = span.get("size", 0)
        font_name = span.get("font", "").lower()
        
        if font_size > 14 or "bold" in font_name:
            return "heading"
        elif font_size < 9:
            return "caption"
        else:
            return "text"
    
    def get_metadata(self) -> Dict:
        """Get PDF metadata"""
        return {
            "page_count": len(self.doc),
            "metadata": self.doc.metadata,
            "toc": self.doc.get_toc()
        }
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()
```

**File:** [`backend/pdf/extractor.py`](backend/pdf/extractor.py)

#### 3.3.2 Document Chunker (pdf/chunker.py)

**Purpose:** Split documents into semantically coherent chunks

```python
from typing import List, Optional
import re
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    id: str
    text: str
    page_number: int
    section: Optional[str] = None
    chunk_index: int
    start_char: int
    end_char: int

class DocumentChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_document(
        self,
        text_blocks: List[dict],
        document_metadata: dict
    ) -> List[DocumentChunk]:
        """Split document into overlapping chunks"""
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for block in text_blocks:
            block_text = block["text"]
            block_tokens = len(block_text.split())
            
            # If adding this block exceeds chunk size, create new chunk
            if current_size + block_tokens > self.chunk_size and current_chunk:
                chunk = self._create_chunk(
                    chunks=current_chunk,
                    metadata=document_metadata,
                    chunk_index=chunk_index
                )
                chunks.append(chunk)
                chunk_index += 1
                
                # Keep overlap from previous chunk
                current_chunk = current_chunk[-self.chunk_overlap:] if self.chunk_overlap > 0 else []
                current_size = sum(len(b["text"].split()) for b in current_chunk)
            
            current_chunk.append(block)
            current_size += block_tokens
        
        # Don't forget the last chunk
        if current_chunk:
            chunk = self._create_chunk(
                chunks=current_chunk,
                metadata=document_metadata,
                chunk_index=chunk_index
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(
        self,
        chunks: List[dict],
        metadata: dict,
        chunk_index: int
    ) -> DocumentChunk:
        """Create a single document chunk"""
        combined_text = " ".join(b["text"] for b in chunks)
        chunk_id = self._generate_chunk_id(combined_text)
        
        # Find section from first heading in chunk
        section = None
        for block in chunks:
            if block.get("type") == "heading":
                section = block["text"]
                break
        
        # Calculate character positions
        start_char = chunks[0].get("start_char", 0)
        end_char = chunks[-1].get("end_char", len(combined_text))
        
        return DocumentChunk(
            id=chunk_id,
            text=combined_text,
            page_number=chunks[0].get("page_number", 1),
            section=section,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char
        )
    
    def _generate_chunk_id(self, text: str) -> str:
        """Generate unique chunk ID from content hash"""
        return hashlib.md5(text.encode()).hexdigest()[:12]
```

**File:** [`backend/pdf/chunker.py`](backend/pdf/chunker.py)

#### 3.3.3 Metadata Builder (pdf/metadata_builder.py)

**Purpose:** Build comprehensive metadata for vector storage

```python
from typing import Dict, Any, Optional
from datetime import datetime

class MetadataBuilder:
    @staticmethod
    def build_chunk_metadata(
        chunk_id: str,
        document_info: Dict,
        page_number: int,
        section: Optional[str] = None,
        bbox: Optional[Dict] = None,
        chunk_index: int = 0
    ) -> Dict[str, Any]:
        """Build metadata dictionary for a chunk"""
        return {
            "id": chunk_id,
            "manual_name": document_info.get("title", "Unknown Manual"),
            "manual_file": document_info.get("filename", ""),
            "manual_id": document_info.get("id", ""),
            "category": document_info.get("category", "general"),
            "page_number": page_number,
            "section": section,
            "chunk_index": chunk_index,
            "bbox": bbox,
            "chunk_type": "text",
            "confidence": 0.96,
            "language": document_info.get("language", "en"),
            "created_at": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def build_document_metadata(
        document_id: str,
        filename: str,
        title: Optional[str],
        category: str,
        page_count: int
    ) -> Dict[str, Any]:
        """Build metadata for a complete document"""
        return {
            "id": document_id,
            "filename": filename,
            "title": title or filename,
            "category": category,
            "page_count": page_count,
            "status": "processing",
            "created_at": datetime.utcnow().isoformat()
        }
```

**File:** [`backend/pdf/metadata_builder.py`](backend/pdf/metadata_builder.py)

---

### 3.4 Vector Database Service (services/vector_service.py)

**Purpose:** Manage ChromaDB operations for document retrieval

```python
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import os

class VectorService:
    def __init__(
        self,
        persist_directory: str = "./data/chromadb",
        collection_name_prefix: str = "biesse_"
    ):
        self.persist_directory = persist_directory
        self.collection_name_prefix = collection_name_prefix
        os.makedirs(persist_directory, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
    
    def get_collection(self, category: str):
        """Get or create a collection for a category"""
        collection_name = f"{self.collection_name_prefix}{category}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": f"Biesse {category} documentation"}
        )
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: List[str],
        category: str
    ):
        """Add document chunks to the vector database"""
        collection = self.get_collection(category)
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadads,
            ids=ids
        )
    
    def search(
        self,
        query_embedding: List[float],
        category: str,
        n_results: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict]:
        """Search for similar documents"""
        collection = self.get_collection(category)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where={"$and": []}  # For filtering if needed
        )
        
        # Filter by similarity threshold
        filtered_results = []
        for idx, (doc, metadata, distance) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )):
            similarity = 1 - distance  # Convert distance to similarity
            if similarity >= similarity_threshold:
                filtered_results.append({
                    "text": doc,
                    "metadata": metadata,
                    "similarity": similarity
                })
        
        return filtered_results
    
    def delete_collection(self, category: str):
        """Delete a category collection"""
        collection_name = f"{self.collection_name_prefix}{category}"
        self.client.delete_collection(collection_name)
    
    def list_categories(self) -> List[str]:
        """List all category collections"""
        collections = self.client.list_collections()
        return [
            c.name.replace(self.collection_name_prefix, "")
            for c in collections
            if c.name.startswith(self.collection_name_prefix)
        ]
```

**File:** [`backend/services/vector_service.py`](backend/services/vector_service.py)

---

### 3.5 AI Services

#### 3.5.1 Embedding Service (services/embedding_service.py)

```python
from typing import List
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from config import Settings

class EmbeddingService:
    def __init__(self, settings: Settings):
        self.settings = settings
        genai.configure(api_key=settings.google_api_key)
        
        # Use Google Embedding API
        self.model = settings.embedding_model
        self.dimensions = settings.embedding_dimensions
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type="retrieval_query"
        )
        return result["embedding"]
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (batch)"""
        embeddings = []
        # Process in batches to avoid rate limits
        batch_size = 50
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            for text in batch:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a search query"""
        return self.embed_text(query)
```

**File:** [`backend/services/embedding_service.py`](backend/services/embedding_service.py)

#### 3.5.2 LLM Service (services/llm_service.py)

```python
from typing import List, Optional, Dict
import google.generativeai as genai
from config import Settings

class LLMService:
    def __init__(self, settings: Settings):
        self.settings = settings
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(settings.llm_model)
    
    def generate_response(
        self,
        prompt: str,
        system_instruction: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """Generate a response using Gemini"""
        # Build the full prompt with conversation context
        full_prompt = self._build_prompt(
            system_instruction=system_instruction,
            conversation_history=conversation_history or [],
            current_query=prompt
        )
        
        response = self.model.generate_content(
            contents=full_prompt,
            generation_config={
                "temperature": self.settings.llm_temperature,
                "max_output_tokens": self.settings.max_tokens
            }
        )
        
        return response.text
    
    def generate_with_citations(
        self,
        query: str,
        context_chunks: List[Dict],
        system_instruction: str
    ) -> Dict:
        """Generate response with citation extraction"""
        # Build context from retrieved chunks
        context = self._build_context(context_chunks)
        
        # Create citation-included prompt
        prompt = f"""{system_instruction}

## User Question
{query}

## Relevant Documentation
{context}

## Instructions
Provide a clear, accurate answer based on the documentation above.
Include specific page numbers and citations in your response.
If the documentation doesn't contain the answer, clearly state this.
"""
        
        response = self.generate_response(
            prompt=prompt,
            system_instruction="You are a helpful technical documentation assistant for Biesse CNC machines."
        )
        
        return {
            "answer": response,
            "sources": context_chunks
        }
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        for idx, chunk in enumerate(chunks, 1):
            metadata = chunk["metadata"]
            context_parts.append(
                f"[{idx}] {metadata.get('manual_name', 'Unknown')}, "
                f"Page {metadata.get('page_number', 'N/A')}: "
                f"{chunk['text'][:500]}..."  # Truncate for token limit
            )
        return "\n\n".join(context_parts)
    
    def _build_prompt(
        self,
        system_instruction: str,
        conversation_history: List[Dict],
        current_query: str
    ) -> str:
        """Build full prompt with conversation history"""
        prompt_parts = [system_instruction, "\n\n## Conversation History\n"]
        
        for msg in conversation_history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prompt_parts.append(f"**{role.upper()}:** {content}")
        
        prompt_parts.append(f"\n**USER:** {current_query}")
        prompt_parts.append("\n**ASSISTANT:**")
        
        return "\n".join(prompt_parts)
```

**File:** [`backend/services/llm_service.py`](backend/services/llm_service.py)

---

### 3.6 RAG Pipeline Core

#### 3.6.1 Query Processor (core/query_processor.py)

```python
from typing import List, Dict, Optional
from services.vector_service import VectorService
from services.embedding_service import EmbeddingService
from config import Settings

class QueryProcessor:
    def __init__(
        self,
        vector_service: VectorService,
        embedding_service: EmbeddingService,
        settings: Settings
    ):
        self.vector_service = vector_service
        self.embedding_service = embedding_service
        self.settings = settings
    
    def process_query(
        self,
        query: str,
        category: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        memory_enabled: bool = True
    ) -> Dict:
        """Process a user query through the RAG pipeline"""
        # Step 1: Preprocess query
        clean_query = self._preprocess_query(query)
        enriched_query = self._enrich_with_context(clean_query, conversation_history)
        
        # Step 2: Generate query embedding
        query_embedding = self.embedding_service.embed_query(enriched_query)
        
        # Step 3: Search vector database
        categories = [category] if category else self._get_all_categories()
        all_results = []
        
        for cat in categories:
            results = self.vector_service.search(
                query_embedding=query_embedding,
                category=cat,
                n_results=self.settings.top_k_chunks
            )
            all_results.extend(results)
        
        # Step 4: Rerank results
        reranked_results = self._rerank_results(
            query=enriched_query,
            results=all_results
        )
        
        # Step 5: Prepare context for LLM
        context_chunks = self._prepare_context(reranked_results)
        
        return {
            "query": clean_query,
            "enriched_query": enriched_query,
            "context_chunks": context_chunks,
            "total_results": len(all_results)
        }
    
    def _preprocess_query(self, query: str) -> str:
        """Clean and normalize the query"""
        # Remove extra whitespace
        clean = " ".join(query.split())
        # Preserve technical terms
        return clean
    
    def _enrich_with_context(
        self,
        query: str,
        history: Optional[List[Dict]] = None
    ) -> str:
        """Enrich query with conversation context"""
        if not history or len(history) == 0:
            return query
        
        # Get last 3 exchanges for context
        recent_history = history[-6:]  # Last 3 user/assistant pairs
        
        context_parts = [query]
        for msg in recent_history:
            if msg.get("role") == "user":
                context_parts.append(f"Previous question: {msg['content']}")
            elif msg.get("role") == "assistant":
                context_parts.append(f"Previous answer summary: {msg['content'][:200]}")
        
        return " | ".join(context_parts)
    
    def _get_all_categories(self) -> List[str]:
        """Get all available categories"""
        return self.settings.document_categories
    
    def _rerank_results(
        self,
        query: str,
        results: List[Dict]
    ) -> List[Dict]:
        """Rerank results by multiple factors"""
        # Simple scoring: 70% similarity + 20% keyword + 10% position
        scored = []
        for idx, result in enumerate(results):
            score = (
                result.get("similarity", 0) * 0.7 +
                self._keyword_match_score(query, result.get("text", "")) * 0.2 +
                (1.0 - idx * 0.05) * 0.1  # Position bonus
            )
            result["rerank_score"] = score
            scored.append(result)
        
        # Sort by rerank score
        return sorted(scored, key=lambda x: x["rerank_score"], reverse=True)
    
    def _keyword_match_score(self, query: str, text: str) -> float:
        """Calculate keyword match score"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        if not query_words:
            return 0
        return len(query_words & text_words) / len(query_words)
    
    def _prepare_context(self, results: List[Dict]) -> List[Dict]:
        """Prepare top chunks for LLM context"""
        # Return top 3 chunks
        return results[:3]
```

**File:** [`backend/core/query_processor.py`](backend/core/query_processor.py)

#### 3.6.2 Response Formatter (core/response_formatter.py)

```python
from typing import List, Dict, Optional
from models.chat import Citation, SourceMetadata
import re

class ResponseFormatter:
    @staticmethod
    def format_response(
        answer: str,
        sources: List[Dict],
        confidence: float
    ) -> Dict:
        """Format the final response with citations"""
        # Extract citations from answer
        citations = ResponseFormatter._extract_citations(answer, sources)
        
        # Clean answer text
        clean_answer = ResponseFormatter._clean_answer(answer)
        
        return {
            "answer": clean_answer,
            "sources": sources,
            "citations": citations,
            "confidence": confidence
        }
    
    @staticmethod
    def _extract_citations(
        answer: str,
        sources: List[Dict]
    ) -> List[Citation]:
        """Extract citation references from the answer"""
        citations = []
        
        # Pattern to match citation markers like [1], (p.47), etc.
        citation_pattern = r'\[(\d+)\]|\(p\.?\s*(\d+)\)'
        
        for idx, source in enumerate(sources, 1):
            citation = Citation(
                id=f"cite_{idx}",
                source=SourceMetadata(
                    manual_name=source.get("metadata", {}).get("manual_name", "Unknown"),
                    manual_file=source.get("metadata", {}).get("manual_file", ""),
                    page_number=source.get("metadata", {}).get("page_number", 0),
                    section=source.get("metadata", {}).get("section"),
                    bbox=source.get("metadata", {}).get("bbox")
                ),
                quoted_text=source.get("text", "")[:200]
            )
            citations.append(citation)
        
        return citations
    
    @staticmethod
    def _clean_answer(answer: str) -> str:
        """Clean and format the answer text"""
        # Remove excessive newlines
        clean = re.sub(r'\n{3,}', '\n\n', answer)
        # Fix spacing around punctuation
        clean = re.sub(r'\s+([.,;:!?])', r'\1', clean)
        return clean.strip()
    
    @staticmethod
    def calculate_confidence(sources: List[Dict]) -> float:
        """Calculate confidence score based on source quality"""
        if not sources:
            return 0.0
        
        # Average similarity of top sources
        similarities = [s.get("similarity", 0) for s in sources[:3]]
        avg_similarity = sum(similarities) / len(similarities)
        
        # Boost if multiple sources agree
        agreement_bonus = 0.1 if len(sources) >= 3 else 0
        
        return min(0.95, avg_similarity + agreement_bonus)
```

**File:** [`backend/core/response_formatter.py`](backend/core/response_formatter.py)

#### 3.6.3 RAG Pipeline Orchestrator (core/rag_pipeline.py)

```python
from typing import Dict, Optional, List
from services.llm_service import LLMService
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService
from core.query_processor import QueryProcessor
from core.response_formatter import ResponseFormatter
from config import Settings
from models.chat import ChatResponse, SourceMetadata

class RAGPipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.vector_service = VectorService(
            persist_directory=settings.chromadb_path,
            collection_name_prefix=settings.collection_name_prefix
        )
        self.embedding_service = EmbeddingService(settings)
        self.llm_service = LLMService(settings)
        self.query_processor = QueryProcessor(
            vector_service=self.vector_service,
            embedding_service=self.embedding_service,
            settings=settings
        )
    
    def process_chat_message(
        self,
        message: str,
        category: Optional[str] = None,
        conversation_history: Optional[List[Dict]] = None,
        memory_enabled: bool = True
    ) -> ChatResponse:
        """Main entry point for chat message processing"""
        
        # Step 1: Process query through RAG pipeline
        query_result = self.query_processor.process_query(
            query=message,
            category=category,
            conversation_history=conversation_history,
            memory_enabled=memory_enabled
        )
        
        # Step 2: Generate response with LLM
        llm_result = self.llm_service.generate_with_citations(
            query=query_result["query"],
            context_chunks=query_result["context_chunks"],
            system_instruction=self._get_system_instruction(category)
        )
        
        # Step 3: Format response
        formatted = ResponseFormatter.format_response(
            answer=llm_result["answer"],
            sources=llm_result["sources"],
            confidence=ResponseFormatter.calculate_confidence(llm_result["sources"])
        )
        
        # Step 4: Build response
        sources_metadata = [
            SourceMetadata(
                manual_name=s["metadata"].get("manual_name", ""),
                manual_file=s["metadata"].get("manual_file", ""),
                page_number=s["metadata"].get("page_number", 0),
                section=s["metadata"].get("section"),
                bbox=s["metadata"].get("bbox")
            )
            for s in formatted["sources"]
        ]
        
        return ChatResponse(
            answer=formatted["answer"],
            sources=sources_metadata,
            citations=formatted["citations"],
            confidence=formatted["confidence"],
            message_id=f"msg_{hash(message) % 1000000}"
        )
    
    def _get_system_instruction(self, category: Optional[str] = None) -> str:
        """Get system instruction based on category"""
        base_instruction = """You are a helpful technical documentation assistant for Biesse CNC machines.
Your role is to:
1. Provide accurate, factual answers based on the documentation
2. Include specific page numbers and citations
3. Be clear and concise
4. If information is not available, clearly state this"""
        
        if category:
            category_instructions = {
                "machine_operation": " Focus on operational procedures, controls, and workflows.",
                "maintenance": " Focus on maintenance schedules, procedures, and troubleshooting.",
                "safety": " Emphasize safety precautions and warning labels.",
                "troubleshooting": " Focus on error codes, diagnostic procedures, and solutions.",
                "programming": " Focus on G-code, machine programming, and code examples."
            }
            base_instruction += category_instructions.get(category, "")
        
        return base_instruction
```

**File:** [`backend/core/rag_pipeline.py`](backend/core/rag_pipeline.py)

---

### 3.7 API Endpoints

#### 3.7.1 Chat Endpoints (api/chat.py)

```python
from fastapi import APIRouter, HTTPException
from typing import Optional, List
from models.chat import ChatRequest, ChatResponse
from core.rag_pipeline import RAGPipeline
from datetime import datetime

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])
pipeline: Optional[RAGPipeline] = None

def get_pipeline() -> RAGPipeline:
    global pipeline
    if pipeline is None:
        from config import Settings
        settings = Settings()
        pipeline = RAGPipeline(settings)
    return pipeline

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a chat message and get a response"""
    try:
        rag = get_pipeline()
        
        response = rag.process_chat_message(
            message=request.message,
            category=request.category,
            conversation_history=[],  # TODO: Load from database
            memory_enabled=request.memory_enabled
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    # TODO: Implement with database
    return {"conversation_id": conversation_id, "messages": []}
```

**File:** [`backend/api/chat.py`](backend/api/chat.py)

#### 3.7.2 Document Endpoints (api/documents.py)

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from models.document import DocumentInfo, DocumentStatus
from pdf.extractor import PDFExtractor
from pdf.chunker import DocumentChunker
from services.vector_service import VectorService
from services.embedding_service import EmbeddingService
from utils.logger import logger
import shutil
import uuid
import os

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])

# Initialize services
vector_service = VectorService()
embedding_service = None  # Will be initialized lazily
chunker = DocumentChunker()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...)
):
    """Upload a PDF document for processing"""
    
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save uploaded file
    file_id = str(uuid.uuid4())
    file_path = f"./data/manuals/{file_id}_{file.filename}"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text from PDF
        extractor = PDFExtractor(file_path)
        blocks = extractor.extract_all()
        metadata = extractor.get_metadata()
        extractor.close()
        
        # Build document info
        document_info = {
            "id": file_id,
            "filename": file.filename,
            "title": file.filename.replace('.pdf', ''),
            "category": category,
            "page_count": metadata["page_count"],
            "file_size_bytes": os.path.getsize(file_path)
        }
        
        # Chunk document
        chunks = chunker.chunk_document(
            text_blocks=[{
                "text": b.text,
                "page_number": b.page_number,
                "type": b.block_type,
                "start_char": 0,
                "end_char": len(b.text)
            } for b in blocks],
            document_metadata=document_info
        )
        
        # Generate embeddings
        global embedding_service
        if embedding_service is None:
            from config import Settings
            from services.embedding_service import EmbeddingService
            embedding_service = EmbeddingService(Settings())
        
        texts = [c.text for c in chunks]
        embeddings = embedding_service.embed_texts(texts)
        
        # Store in vector database
        metadatas = []
        for chunk in chunks:
            metadata = {
                "chunk_id": chunk.id,
                "page_number": chunk.page_number,
                "section": chunk.section,
                "manual_name": document_info["title"],
                "manual_file": file.filename,
                "category": category
            }
            metadatas.append(metadata)
        
        ids = [c.id for c in chunks]
        vector_service.add_documents(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
            category=category
        )
        
        return {
            "success": True,
            "document_id": file_id,
            "filename": file.filename,
            "chunk_count": len(chunks),
            "message": f"Document processed successfully. {len(chunks)} chunks created."
        }
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.get("/list")
async def list_documents():
    """List all uploaded documents"""
    # TODO: Implement document catalog
    return {"documents": [], "total_count": 0}
```

**File:** [`backend/api/documents.py`](backend/api/documents.py)

#### 3.7.3 Health Endpoints (api/health.py)

```python
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "biesse-chat-assistant"
    }

@router.get("/ready")
async def readiness_check():
    """Readiness check including dependencies"""
    checks = {
        "database": "unknown",
        "vector_store": "unknown",
        "llm": "unknown"
    }
    
    # Check database
    try:
        import sqlite3
        conn = sqlite3.connect("./data/conversations.db")
        conn.close()
        checks["database"] = "healthy"
    except:
        checks["database"] = "unhealthy"
    
    # Check vector store
    try:
        from services.vector_service import VectorService
        vs = VectorService()
        categories = vs.list_categories()
        checks["vector_store"] = f"healthy ({len(categories)} categories)"
    except Exception as e:
        checks["vector_store"] = f"unhealthy: {str(e)}"
    
    # Check LLM
    try:
        from config import Settings
        import google.generativeai as genai
        settings = Settings()
        genai.configure(api_key=settings.google_api_key)
        # Simple API test
        model = genai.GenerativeModel(settings.llm_model)
        model.generate_content("test")
        checks["llm"] = "healthy"
    except Exception as e:
        checks["llm"] = f"unhealthy: {str(e)}"
    
    all_healthy = all("unhealthy" not in v for v in checks.values())
    
    return {
        "status": "ready" if all_healthy else "degraded",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

**File:** [`backend/api/health.py`](backend/api/health.py)

---

### 3.8 Main Application Entry (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.chat import router as chat_router
from api.documents import router as documents_router
from api.health import router as health_router
from config import Settings

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"Starting {settings.app_name}")
    print(f"Debug mode: {settings.debug}")
    yield
    # Shutdown
    print("Shutting down...")

app = FastAPI(
    title=settings.app_name,
    description="Technical Documentation Chat Assistant for Biesse Machines",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(documents_router)

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**File:** [`backend/main.py`](backend/main.py)

---

## 4. Frontend Implementation Details

### 4.1 State Management (src/lib/store.ts)

```typescript
import { create } from 'zustand';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}

interface Citation {
  id: string;
  manualName: string;
  pageNumber: number;
  bbox?: { x: number; y: number; width: number; height: number };
  quotedText: string;
}

interface PDFState {
  currentFile: string | null;
  currentPage: number;
  scale: number;
  highlights: Citation[];
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentFile: string | null;
  selectedCitation: Citation | null;
}

interface AppState {
  chat: ChatState;
  pdf: PDFState;
  
  // Actions
  addMessage: (message: Message) => void;
  setLoading: (loading: boolean) => void;
  setCurrentFile: (file: string | null) => void;
  setCurrentPage: (page: number) => void;
  addHighlight: (citation: Citation) => void;
  selectCitation: (citation: Citation | null) => void;
  clearChat: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  chat: {
    messages: [],
    isLoading: false,
    currentFile: null,
    selectedCitation: null,
  },
  pdf: {
    currentFile: null,
    currentPage: 1,
    scale: 1.0,
    highlights: [],
  },
  
  addMessage: (message) =>
    set((state) => ({
      chat: {
        ...state.chat,
        messages: [...state.chat.messages, message],
      },
    })),
  
  setLoading: (loading) =>
    set((state) => ({
      chat: { ...state.chat, isLoading: loading },
    })),
  
  setCurrentFile: (file) =>
    set((state) => ({
      chat: { ...state.chat, currentFile: file },
      pdf: { ...state.pdf, currentFile: file, currentPage: 1, highlights: [] },
    })),
  
  setCurrentPage: (page) =>
    set((state) => ({
      pdf: { ...state.pdf, currentPage: page },
    })),
  
  addHighlight: (citation) =>
    set((state) => ({
      pdf: {
        ...state.pdf,
        highlights: [...state.pdf.highlights, citation],
      },
    })),
  
  selectCitation: (citation) =>
    set((state) => ({
      chat: { ...state.chat, selectedCitation: citation },
    })),
  
  clearChat: () =>
    set({
      chat: {
        messages: [],
        isLoading: false,
        currentFile: null,
        selectedCitation: null,
      },
      pdf: {
        currentFile: null,
        currentPage: 1,
        scale: 1.0,
        highlights: [],
      },
    }),
}));
```

**File:** [`frontend/src/lib/store.ts`](frontend/src/lib/store.ts)

### 4.2 API Client (src/lib/api.ts)

```typescript
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: string;
}

export interface Citation {
  id: string;
  source: {
    manualName: string;
    manualFile: string;
    pageNumber: number;
    section?: string;
    bbox?: {
      x: number;
      y: number;
      width: number;
      height: number;
    };
  };
  quotedText: string;
}

export interface ChatRequest {
  message: string;
  conversationId?: string;
  category?: string;
  memoryEnabled: boolean;
}

export interface ChatResponse {
  answer: string;
  sources: {
    manualName: string;
    manualFile: string;
    pageNumber: number;
    section?: string;
    bbox?: any;
  }[];
  citations: Citation[];
  confidence: number;
  messageId: string;
  conversationId?: string;
}

export const chatApi = {
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post<ChatResponse>('/chat/message', request);
    return response.data;
  },
  
  async getHistory(conversationId: string): Promise<ChatMessage[]> {
    const response = await api.get<ChatMessage[]>(`/chat/history/${conversationId}`);
    return response.data;
  },
};

export const documentApi = {
  async uploadDocument(
    file: File,
    category: string
  ): Promise<{ success: boolean; documentId: string; chunkCount: number }> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  async listDocuments(): Promise<{ documents: any[]; totalCount: number }> {
    const response = await api.get('/documents/list');
    return response.data;
  },
};

export const healthApi = {
  async check(): Promise<{ status: string; checks: Record<string, string> }> {
    const response = await api.get('/health/ready');
    return response.data;
  },
};
```

**File:** [`frontend/src/lib/api.ts`](frontend/src/lib/api.ts)

### 4.3 Chat Components

#### 4.3.1 ChatPanel (src/components/ChatPanel/ChatPanel.tsx)

```typescript
import React from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { useAppStore } from '@/lib/store';

export function ChatPanel() {
  const { chat, addMessage, setLoading, selectCitation } = useAppStore();

  const handleSendMessage = async (message: string) => {
    // Add user message
    addMessage({
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    });

    setLoading(true);

    try {
      // Call API
      const response = await chatApi.sendMessage({
        message,
        memoryEnabled: true,
      });

      // Add AI response
      addMessage({
        id: response.messageId,
        role: 'assistant',
        content: response.answer,
        citations: response.citations,
        timestamp: new Date(),
      });
    } catch (error) {
      console.error('Chat error:', error);
      addMessage({
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <MessageList 
        messages={chat.messages} 
        onCitationClick={selectCitation}
      />
      <InputBox onSend={handleSendMessage} disabled={chat.isLoading} />
    </div>
  );
}
```

**File:** [`frontend/src/components/ChatPanel/ChatPanel.tsx`](frontend/src/components/ChatPanel/ChatPanel.tsx)

#### 4.3.2 MessageList (src/components/ChatPanel/MessageList.tsx)

```typescript
import React from 'react';
import { UserMessage } from './UserMessage';
import { AIMessage } from './AIMessage';
import { useAppStore } from '@/lib/store';

interface MessageListProps {
  messages: any[];
  onCitationClick: (citation: any) => void;
}

export function MessageList({ messages, onCitationClick }: MessageListProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full text-gray-400">
          <div className="text-center">
            <p className="text-lg mb-2">👋 Welcome to Biesse Chat Assistant</p>
            <p className="text-sm">Ask questions about Biesse machine documentation</p>
          </div>
        </div>
      ) : (
        messages.map((message) => (
          message.role === 'user' ? (
            <UserMessage key={message.id} message={message} />
          ) : (
            <AIMessage 
              key={message.id} 
              message={message} 
              onCitationClick={onCitationClick}
            />
          )
        ))
      )}
    </div>
  );
}
```

**File:** [`frontend/src/components/ChatPanel/MessageList.tsx`](frontend/src/components/ChatPanel/MessageList.tsx)

#### 4.3.3 AIMessage with Citations (src/components/ChatPanel/AIMessage.tsx)

```typescript
import React from 'react';
import { Citation } from '@/lib/api';

interface AIMessageProps {
  message: {
    id: string;
    content: string;
    citations?: Citation[];
    timestamp: Date;
  };
  onCitationClick: (citation: Citation) => void;
}

export function AIMessage({ message, onCitationClick }: AIMessageProps) {
  return (
    <div className="flex gap-3 p-4 bg-white rounded-lg shadow-sm">
      <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
        <span className="text-white text-sm">AI</span>
      </div>
      
      <div className="flex-1">
        <div className="prose max-w-none">
          <p className="text-gray-800">{message.content}</p>
        </div>
        
        {message.citations && message.citations.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <p className="text-xs font-semibold text-gray-500 mb-2">Sources:</p>
            <div className="space-y-2">
              {message.citations.map((citation, idx) => (
                <button
                  key={citation.id}
                  onClick={() => onCitationClick(citation)}
                  className="block w-full text-left p-2 rounded bg-yellow-50 hover:bg-yellow-100 transition-colors"
                >
                  <span className="text-xs font-medium text-gray-700">
                    [{idx + 1}] {citation.source.manualName}
                  </span>
                  <span className="text-xs text-gray-500 ml-2">
                    Page {citation.source.pageNumber}
                  </span>
                </button>
              ))}
            </div>
          </div>
        )}
        
        <p className="text-xs text-gray-400 mt-2">
          {message.timestamp.toLocaleTimeString()}
        </p>
      </div>
    </div>
  );
}
```

**File:** [`frontend/src/components/ChatPanel/AIMessage.tsx`](frontend/src/components/ChatPanel/AIMessage.tsx)

#### 4.3.4 InputBox (src/components/ChatPanel/InputBox.tsx)

```typescript
import React, { useState } from 'react';

interface InputBoxProps {
  onSend: (message: string) => void;
  disabled: boolean;
}

export function InputBox({ onSend, disabled }: InputBoxProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 bg-white">
      <div className="flex gap-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask about Biesse machine documentation..."
          disabled={disabled}
          className="flex-1 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={2}
        />
        <button
          type="submit"
          disabled={disabled || !message.trim()}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {disabled ? (
            <span className="animate-pulse">...</span>
          ) : (
            'Send'
          )}
        </button>
      </div>
    </form>
  );
}
```

**File:** [`frontend/src/components/ChatPanel/InputBox.tsx`](frontend/src/components/ChatPanel/InputBox.tsx)

### 4.4 PDF Viewer Components

#### 4.4.1 PDFViewerPanel (src/components/PDFViewer/PDFViewerPanel.tsx)

```typescript
import React, { useEffect, useState } from 'react';
import { PDFRenderer } from './PDFRenderer';
import { HighlightOverlay } from './HighlightOverlay';
import { useAppStore } from '@/lib/store';

export function PDFViewerPanel() {
  const { pdf, setCurrentPage, addHighlight, selectCitation } = useAppStore();
  const [pdfDoc, setPdfDoc] = useState<any>(null);

  useEffect(() => {
    if (pdf.currentFile) {
      loadPDF(pdf.currentFile);
    }
  }, [pdf.currentFile]);

  const loadPDF = async (filename: string) => {
    // Load PDF using PDF.js
    // Implementation details...
  };

  const handleCitationClick = (citation: any) => {
    // Navigate to page and highlight
    setCurrentPage(citation.source.pageNumber);
    addHighlight(citation);
  };

  return (
    <div className="h-full bg-gray-100 flex flex-col">
      <div className="bg-white border-b border-gray-200 p-2 flex gap-2">
        {/* PDF Toolbar controls */}
        <button
          onClick={() => setCurrentPage(Math.max(1, pdf.currentPage - 1))}
          className="p-2 hover:bg-gray-100 rounded"
        >
          ←
        </button>
        <span className="p-2">
          Page {pdf.currentPage} {pdfDoc ? `/ ${pdfDoc.numPages}` : ''}
        </span>
        <button
          onClick={() => setCurrentPage(Math.min(pdfDoc.numPages, pdf.currentPage + 1))}
          className="p-2 hover:bg-gray-100 rounded"
        >
          →
        </button>
      </div>
      
      <div className="flex-1 overflow-auto p-4 flex justify-center">
        <div className="relative">
          {pdfDoc && (
            <>
              <PDFRenderer
                pdfDoc={pdfDoc}
                pageNumber={pdf.currentPage}
                scale={pdf.scale}
              />
              <HighlightOverlay
                highlights={pdf.highlights.filter(h => h.source.pageNumber === pdf.currentPage)}
                onHighlightClick={selectCitation}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
```

**File:** [`frontend/src/components/PDFViewer/PDFViewerPanel.tsx`](frontend/src/components/PDFViewer/PDFViewerPanel.tsx)

#### 4.4.2 HighlightOverlay (src/components/PDFViewer/HighlightOverlay.tsx)

```typescript
import React from 'react';

interface HighlightOverlayProps {
  highlights: any[];
  onHighlightClick: (citation: any) => void;
}

export function HighlightOverlay({ highlights, onHighlightClick }: HighlightOverlayProps) {
  return (
    <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
      {highlights.map((highlight, idx) => {
        const bbox = highlight.source.bbox;
        if (!bbox) return null;
        
        return (
          <div
            key={highlight.id || idx}
            className="absolute pointer-events-auto cursor-pointer"
            style={{
              left: bbox.x,
              top: bbox.y,
              width: bbox.width,
              height: bbox.height,
              backgroundColor: 'rgba(255, 200, 0, 0.3)',
              border: '2px solid rgba(255, 200, 0, 0.8)',
            }}
            onClick={() => onHighlightClick(highlight)}
            title={`${highlight.source.manualName} - Page ${highlight.source.pageNumber}`}
          >
            <span className="absolute -top-5 -left-5 bg-orange-500 text-white text-xs rounded px-1">
              {idx + 1}
            </span>
          </div>
        );
      })}
    </div>
  );
}
```

**File:** [`frontend/src/components/PDFViewer/HighlightOverlay.tsx`](frontend/src/components/PDFViewer/HighlightOverlay.tsx)

### 4.5 Main Layout (src/components/Layout/MainContent.tsx)

```typescript
import React from 'react';
import { ChatPanel } from '../ChatPanel/ChatPanel';
import { PDFViewerPanel } from '../PDFViewer/PDFViewerPanel';

export function MainContent() {
  return (
    <div className="flex h-full overflow-hidden">
      {/* Chat Panel - 40% */}
      <div className="w-5/12 min-w-[400px] border-r border-gray-200">
        <ChatPanel />
      </div>
      
      {/* PDF Viewer Panel - 60% */}
      <div className="flex-1">
        <PDFViewerPanel />
      </div>
    </div>
  );
}
```

**File:** [`frontend/src/components/Layout/MainContent.tsx`](frontend/src/components/Layout/MainContent.tsx)

### 4.6 Main App Page (src/app/page.tsx)

```typescript
import React from 'react';
import { Header } from '@/components/Layout/Header';
import { MainContent } from '@/components/Layout/MainContent';

export default function HomePage() {
  return (
    <div className="h-screen flex flex-col">
      <Header />
      <main className="flex-1 overflow-hidden">
        <MainContent />
      </main>
    </div>
  );
}
```

**File:** [`frontend/src/app/page.tsx`](frontend/src/app/page.tsx)

---

## 5. Dependencies

### 5.1 Backend Requirements (backend/requirements.txt)

```
# AI/ML Stack
google-generativeai==0.3.2
chromadb==0.4.22
sentence-transformers==2.3.1

# PDF Processing
pymupdf==1.23.8
pdfplumber==0.10.3

# Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.25
alembic==1.13.1

# Utilities
python-dotenv==1.0.0
loguru==0.7.2

# Development
pytest==7.4.0
pytest-asyncio==0.23.0
httpx==0.26.0
```

### 5.2 Frontend Dependencies (frontend/package.json)

```json
{
  "name": "biesse-chat-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.5",
    "zustand": "^4.5.0",
    "lucide-react": "^0.263.1",
    "react-markdown": "^9.0.1",
    "react-hot-toast": "^2.4.1",
    "@radix-ui/react-dialog": "^1.0.5",
    "react-dropzone": "^14.2.3"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "tailwindcss": "^3.4.1",
    "typescript": "^5.3.0"
  }
}
```

---

## 6. Development Environment

### 6.1 Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DEBUG=true
    volumes:
      - ./backend:/app
      - ./data:/app/data
    depends_on:
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    volumes:
      - ./frontend:/app
      - ./data:/app/data
    stdin_open: true
    tty: true

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

volumes:
  redis-data:
```

### 6.2 Environment Variables (.env.example)

```env
# Google API Key (required for Gemini and Embeddings)
GOOGLE_API_KEY=your_google_api_key_here

# Application Settings
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=sqlite:///./data/conversations.db

# Vector Database
CHROMADB_PATH=./data/chromadb
COLLECTION_NAME_PREFIX=biesse_

# PDF Processing
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=500
CHUNK_OVERLAP=50

# LLM Settings
EMBEDDING_MODEL=text-embedding-004
LLM_MODEL=gemini-2.0-flash-exp
LLM_TEMPERATURE=0.3
MAX_TOKENS=2048

# Categories
DOCUMENT_CATEGORIES=machine_operation,maintenance,safety,troubleshooting,programming
```

---

## 7. Testing Strategy

### 7.1 Unit Tests

#### Backend Tests
- `tests/test_core/test_query_processor.py` - Query processing logic
- `tests/test_services/test_vector_service.py` - Vector database operations
- `tests/test_services/test_llm_service.py` - LLM integration
- `tests/test_pdf/test_extractor.py` - PDF text extraction
- `tests/test_api/test_chat.py` - Chat API endpoints

#### Frontend Tests
- `tests/lib/store.test.ts` - Zustand state management
- `tests/components/ChatPanel.test.tsx` - Chat components

### 7.2 Integration Tests
- Document upload → processing → search workflow
- Chat query → RAG pipeline → response generation
- PDF viewer → citation highlighting flow

---

## 8. Implementation Order

### Week 1: Backend Foundation
1. Day 1-2: Project setup, configuration, models
2. Day 3-4: PDF processing pipeline (extractor, chunker)
3. Day 5: Vector database service, embedding service

### Week 2: RAG Pipeline & Frontend
1. Day 1-2: LLM service, query processor, response formatter
2. Day 3: FastAPI endpoints, main application
3. Day 4: Frontend setup, core components
4. Day 5: Integration testing, bug fixes

---

## 9. Success Criteria

- [ ] Backend compiles and runs without errors
- [ ] Document upload creates chunks in vector database
- [ ] Chat queries return responses with citations
- [ ] PDF viewer displays documents with highlighting
- [ ] Frontend loads and interacts with backend
- [ ] All unit tests pass (>80% coverage)
- [ ] End-to-end workflow tested

---

## 10. Notes & Constraints

1. **Phase 1 focuses on core functionality** - V2 enhancements (history sidebar, memory controls, etc.) will be implemented in subsequent phases
2. **SQLite for POC** - Full conversation storage will be enhanced in Phase 2
3. **File-based storage** - Object storage (S3) will be added in production
4. **Embedded ChromaDB** - Production will use Qdrant Cloud
5. **Single category** - Multi-category filtering will be enhanced in V2

---

*Document generated from ARCHITECTURE_V2_ENHANCED (1).md - Phase 1 Implementation Plan*

















