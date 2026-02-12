# Biesse Technical Documentation Chat Assistant - Enhanced Architecture Document

**Version:** 2.0  
**Date:** February 12, 2026  
**Project Type:** Proof of Concept (POC) - Enhanced UI/UX  
**Duration:** 4 Weeks + 2 Weeks Enhancement Phase

---

## Executive Summary

This document provides the complete enhanced architecture for the Biesse Technical Documentation Chat Assistant, incorporating six major UI/UX improvements while maintaining enterprise-grade design principles.

### Version 2.0 Enhancements:
1. **Chat History Sidebar** - Persistent conversation management with temporal grouping
2. **New Chat / Reset Flow** - Safe conversation workflows preventing data loss
3. **Action Buttons System** - Context-driven action buttons under AI responses
4. **Memory Controls** - Transparent conversation persistence with user control
5. **File Upload (Chat Level)** - Seamless document upload with acknowledgment
6. **Backend Disconnect Handling** - Graceful degradation with smart retry logic

### Design Principles:
- **Enterprise-First**: Clean, professional, uncluttered interfaces
- **Trust Through Transparency**: Clear indicators for memory state, file uploads, connection status
- **User Safety**: Confirmation modals, preventing accidental data loss
- **Resilience**: Graceful handling of network failures with offline mode support

---

## Technology Stack

### Frontend Technologies

**Framework & Language**
- Next.js 14 (React 18)
- TypeScript 5.3
- Tailwind CSS 3.4

**Key Libraries**
```json
{
  "pdfViewer": "react-pdf 7.7 + PDF.js 3.11",
  "stateManagement": "Zustand 4.5",
  "httpClient": "Axios 1.6",
  "markdown": "react-markdown 9.0",
  "icons": "lucide-react 0.263",
  "notifications": "react-hot-toast 2.4",
  "modals": "radix-ui/dialog 1.0",
  "fileUpload": "react-dropzone 14.2"
}
```

### Backend Technologies

**Framework & Language**
- FastAPI 0.109.0
- Python 3.11+
- Uvicorn (ASGI server)

**Core Dependencies**
```python
# AI/ML Stack
google-generativeai==0.3.2  # Gemini LLM
chromadb==0.4.22            # Vector database
sentence-transformers==2.3.1 # Embeddings

# PDF Processing
pymupdf==1.23.8  # Text extraction with coordinates
pdfplumber==0.10.3

# Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3

# Database (New for V2.0)
sqlalchemy==2.0.25  # ORM for conversation management
alembic==1.13.1     # Database migrations

# Utilities
python-dotenv==1.0.0
loguru==0.7.2
redis==5.0.1  # Optional: for session management
```

### Database Selection

**For POC (4-6 week timeline):**
- SQLite for conversation storage (simple, zero-config)
- File system for uploaded documents
- ChromaDB for vectors (embedded mode)

**For Production:**
- PostgreSQL for conversation storage
- S3/MinIO for uploaded documents
- Qdrant Cloud for vectors (scalable)

### AI/ML Models

**Embedding Model**
- Google Text Embedding API
- Model: `text-embedding-004`
- Dimensions: 768
- Purpose: Convert text chunks and queries to vectors

**LLM for Response Generation**
- Google Gemini Flash 2.0
- Model: `gemini-2.0-flash-exp`
- Temperature: 0.3 (factual responses)
- Max tokens: 2048
- Purpose: Generate answers with citations

### Infrastructure Components

**Development Environment**
- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Git

**Production Infrastructure**
- Load Balancer (Nginx)
- Application Servers (Auto-scaling)
- Database (PostgreSQL with replication)
- Object Storage (S3-compatible)
- CDN (CloudFlare/CloudFront)
- Monitoring (Prometheus + Grafana)

---

## Component Architecture

### Frontend Component Structure

**Original V1.0 Component Tree:**
```
App
├── Layout
│   ├── Header
│   │   ├── Logo
│   │   ├── CategorySelector
│   │   └── SettingsMenu
│   └── MainContent (Split Panel)
│       ├── ChatPanel (40%)
│       │   ├── MessageList
│       │   │   ├── UserMessage
│       │   │   └── AIMessage (with Citations)
│       │   ├── InputBox
│       │   └── NewChatButton
│       └── PDFViewerPanel (60%)
│           ├── PDFToolbar
│           ├── PDFRenderer
│           ├── HighlightOverlay
│           └── MultiSourceTabs
└── Providers
    ├── StateProvider (Zustand)
    └── ThemeProvider
```

**Enhanced V2.0 Component Tree:**
```
App
├── Layout
│   ├── Header
│   │   ├── Logo
│   │   ├── CategorySelector
│   │   ├── ConnectionStatusIndicator [NEW]
│   │   └── SettingsMenu
│   └── MainContent (Three-Panel)
│       ├── HistorySidebar (20%) [NEW]
│       │   ├── NewChatButton
│       │   ├── SearchInput
│       │   └── ConversationList
│       │       ├── TimeGroup (Today)
│       │       ├── TimeGroup (Yesterday)
│       │       ├── TimeGroup (Last 7 Days)
│       │       └── TimeGroup (Older)
│       │           └── ConversationItem
│       │               ├── Title
│       │               ├── Preview
│       │               ├── Timestamp
│       │               └── ContextMenu
│       ├── ChatPanel (30%)
│       │   ├── MemoryControlBar [NEW]
│       │   │   ├── MemoryToggle
│       │   │   └── MemoryStatusIndicator
│       │   ├── MessageList
│       │   │   ├── UserMessage
│       │   │   └── AIMessage
│       │   │       ├── MessageContent (Markdown)
│       │   │       ├── Citations
│       │   │       └── ActionButtonGroup [NEW]
│       │   ├── FileUploadIndicator [NEW]
│       │   ├── InputBox
│       │   │   ├── TextArea
│       │   │   ├── FileAttachButton [NEW]
│       │   │   └── SendButton
│       │   └── DisconnectOverlay [NEW]
│       └── PDFViewerPanel (50%)
│           ├── PDFToolbar
│           ├── PDFRenderer
│           ├── HighlightOverlay
│           └── MultiSourceTabs
└── Providers
    ├── StateProvider (Zustand)
    ├── ThemeProvider
    └── ErrorBoundary
└── Modals [NEW]
    ├── NewChatConfirmationModal
    ├── DeleteConversationModal
    ├── FileUploadPreviewModal
    └── DisconnectWarningModal
```

### Backend Module Structure

**Original V1.0 Structure:**
```
backend/
├── main.py                 # FastAPI app entry
├── config.py               # Configuration
├── api/                    # API endpoints
│   ├── chat.py
│   ├── documents.py
│   └── health.py
├── core/                   # Business logic
│   ├── rag_pipeline.py
│   ├── query_processor.py
│   └── response_formatter.py
├── services/               # External services
│   ├── llm_service.py
│   ├── embedding_service.py
│   └── vector_service.py
├── pdf/                    # PDF processing
│   ├── extractor.py
│   ├── chunker.py
│   └── metadata_builder.py
├── models/                 # Pydantic models
├── utils/                  # Utilities
└── tests/                  # Test suite
```

**Enhanced V2.0 Structure:**
```
backend/
├── main.py                      # FastAPI app entry
├── config.py                    # Configuration
├── api/                         # API endpoints
│   ├── chat.py                  # Chat endpoints
│   ├── conversations.py         # [NEW] Conversation management
│   ├── documents.py             # Document management
│   ├── files.py                 # [NEW] File upload handling
│   └── health.py                # Health checks
├── core/                        # Business logic
│   ├── rag_pipeline.py          # RAG orchestration
│   ├── query_processor.py       # Query processing
│   ├── response_formatter.py    # Response formatting
│   ├── action_detector.py       # [NEW] Action button detection
│   └── memory_manager.py        # [NEW] Conversation memory
├── services/                    # External services
│   ├── llm_service.py           # LLM integration
│   ├── embedding_service.py     # Embedding generation
│   ├── vector_service.py        # Vector DB operations
│   └── storage_service.py       # [NEW] File storage
├── pdf/                         # PDF processing
│   ├── extractor.py             # Text extraction
│   ├── chunker.py               # Document chunking
│   └── metadata_builder.py      # Metadata generation
├── models/                      # Pydantic models
│   ├── chat.py                  # Chat models
│   ├── conversation.py          # [NEW] Conversation models
│   ├── document.py              # Document models
│   └── action.py                # [NEW] Action models
├── db/                          # [NEW] Database layer
│   ├── connection.py            # DB connection
│   ├── repositories/            # Data access layer
│   │   ├── conversation_repo.py
│   │   ├── message_repo.py
│   │   └── file_repo.py
│   └── migrations/              # Alembic migrations
├── utils/                       # Utilities
│   ├── logger.py
│   ├── validators.py
│   └── retry_handler.py         # [NEW] Retry logic
└── tests/                       # Test suite
    ├── test_api/
    ├── test_core/
    └── test_integration/
```

---

## Core Data Flows & Workflows

### Document Upload Workflow (Original - Unchanged)

```
[User Uploads PDF]
       ↓
[1. File Validation]
   - Check file type (PDF)
   - Verify size (< 50MB)
   - Scan for corruption
       ↓
[2. Store Original]
   - Save to /data/manuals/
   - Generate document ID
   - Create metadata entry
       ↓
[3. Text Extraction (PyMuPDF)]
   - Extract text blocks
   - Capture bounding box coordinates (x, y, width, height)
   - Extract page metadata
   - Classify block types (heading, text, list, table)
       ↓
[4. Intelligent Chunking]
   - Split into ~500 token chunks
   - Maintain 50 token overlap
   - Preserve section context
   - Assign unique chunk IDs
       ↓
[5. Generate Embeddings]
   - Call Google Embedding API
   - Model: text-embedding-004
   - Generate 768-dim vectors
   - Batch process (50 chunks/request)
       ↓
[6. Store in Vector DB]
   - Insert into ChromaDB
   - Index by category
   - Store metadata (page, bbox, manual info)
       ↓
[7. Update Catalog]
   - Mark document as "ready"
   - Update document count
       ↓
[Document Ready for Search]
```

### Query Processing Workflow (Original - Enhanced with Actions)

```
[User Sends Query: "How do I calibrate the blade?"]
       ↓
[1. Query Preprocessing]
   - Clean and normalize text
   - Extract intent (how-to question)
   - Add conversation context [ENHANCED: from memory]
   - Apply category filter
       ↓
[2. Generate Query Embedding]
   - Call embedding service
   - Create 768-dim vector
   - Time: ~200ms
       ↓
[3. Vector Similarity Search]
   - Query ChromaDB with embedding
   - Apply category filter
   - Retrieve top-10 chunks
   - Similarity threshold: 0.7
   - Time: ~100ms
       ↓
[Retrieved Chunks Example:]
  [1] Rover A Manual, p.47 (score: 0.94)
      "To calibrate blade height..."
  [2] Safety Guide, p.12 (score: 0.89)
      "Before calibration, disconnect power..."
  [3] Rover B Manual, p.23 (score: 0.76)
      "Blade adjustment procedure..."
       ↓
[4. Reranking]
   - Score by: similarity (70%) + keyword match (20%) + recency (10%)
   - Select top-3 for context
       ↓
[5. Context Assembly]
   - Format chunks for LLM prompt
   - Add conversation history (last 3 exchanges) [ENHANCED: memory-aware]
   - [NEW] Add uploaded file context if present
   - Build system instructions
   - Total context: ~2000 tokens
       ↓
[6. LLM Generation (Gemini)]
   - Model: gemini-2.0-flash-exp
   - Temperature: 0.3 (factual)
   - Max tokens: 2048
   - Include source citations
   - Time: ~1.5s
       ↓
[7. Response Formatting]
   - Extract answer text
   - Parse citations
   - Attach source metadata (page, bbox)
   - Calculate confidence score
   - [NEW] Detect action buttons
       ↓
[8. Save to Conversation] [NEW]
   - Store message in DB (if memory enabled)
   - Update conversation timestamp
       ↓
[Return to Frontend]
{
  "answer": "To calibrate the blade height...",
  "sources": [
    {
      "manual": "Rover A Manual",
      "page": 47,
      "bbox": {"x": 72, "y": 450, "width": 450, "height": 85},
      "text": "..."
    }
  ],
  "actions": [ [NEW]
    {"type": "view_dashboard", "label": "View Dashboard"},
    {"type": "download_report", "label": "Download Report"}
  ],
  "confidence": 0.92,
  "message_id": "msg_123" [NEW]
}
```

### PDF Highlighting Workflow (Original - Unchanged)

```
[User Clicks Citation]
       ↓
[Extract Metadata]
   - PDF filename
   - Page number
   - Bounding box coordinates {x, y, width, height}
       ↓
[Load PDF if Needed]
   - Check if already loaded
   - Fetch from /api/documents/{filename}
   - Initialize PDF.js renderer
       ↓
[Navigate to Page]
   - Jump to specified page number
   - Wait for page render complete
       ↓
[Transform Coordinates]
   PDF coords → Canvas coords
   - PDF origin: bottom-left, Y increases upward
   - Canvas origin: top-left, Y increases downward
   - Apply scale factor
   - Formula: canvasY = (pdfHeight - pdfY - height) * scale
       ↓
[Draw Highlight Overlay]
   - Create canvas layer above PDF
   - Draw yellow transparent rectangle (rgba(255,255,0,0.3))
   - Add orange border (rgba(255,200,0,0.8))
   - Add citation number badge (if multiple sources)
       ↓
[Smooth Scroll]
   - Calculate scroll offset to center highlight
   - Animate scroll (300ms)
       ↓
[Highlighted Text Visible]
```

---

## Vector Database Schema (ChromaDB)

### Collection Structure
```python
collection_name = "biesse_{category}"  # e.g., "biesse_machine_operation"

# Each chunk document
{
    "id": "md5_hash_of_content",
    "document": "actual chunk text content",
    "embedding": [0.023, -0.45, ...],  # 768-dim vector
    "metadata": {
        # Document Info
        "manual_name": "Biesse Rover A CNC User Manual",
        "manual_file": "rover_a_cnc.pdf",
        "manual_id": "doc_123abc",
        "category": "Machine Operation",
        
        # Location Info
        "page_number": 47,
        "section": "5.3 Blade Calibration",
        "chunk_index": 12,
        
        # Bounding Box (for highlighting)
        "bbox": {
            "x": 72.0,
            "y": 450.0,
            "width": 450.0,
            "height": 85.0
        },
        
        # Metadata
        "chunk_type": "text",  # or "heading", "list", "table"
        "confidence": 0.96,
        "language": "en",
        "created_at": "2026-02-10T10:00:00Z"
    }
}
```

### API Data Models (Pydantic)

```python
from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime

class BoundingBox(BaseModel):
    x: float
    y: float
    width: float
    height: float
    page: int

class Source(BaseModel):
    manual_name: str
    manual_file: str
    page: int
    section: str
    text: str
    bbox: BoundingBox
    confidence: float

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    category: Optional[str] = None
    history: List[dict] = []
    max_sources: int = 3
    file_context: List[str] = []  # [NEW] File IDs for context

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    conversation_id: str
    category: str
    confidence: float
    processing_time: float
    actions: List[dict] = []  # [NEW] Action buttons
    message_id: str  # [NEW] Message ID
    metadata: dict

class DocumentUpload(BaseModel):
    file_name: str
    file_size: int
    category: str
    language: str = "en"
    description: Optional[str] = None

class DocumentStatus(BaseModel):
    document_id: str
    status: Literal["uploading", "processing", "ready", "failed"]
    progress: float  # 0.0 to 1.0
    message: str
    chunks_processed: int
    total_chunks: int
```

---

## Enhanced System Architecture

### High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT BROWSER                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐ │
│  │                         REACT APPLICATION                                │ │
│  │  ┌──────────┐  ┌──────────────────────┐  ┌────────────────────────┐   │ │
│  │  │ History  │  │   Chat Panel         │  │   PDF Viewer Panel     │   │ │
│  │  │ Sidebar  │  │   (Left 30%)         │  │   (Right 50%)          │   │ │
│  │  │ (20%)    │  │                      │  │                        │   │ │
│  │  │          │  │ ┌──────────────────┐ │  │ - PDF.js Renderer      │   │ │
│  │  │ Today    │  │ │ Memory Indicator │ │  │ - Highlight Overlay    │   │ │
│  │  │ ├─Chat1  │  │ │ [●Remembering]   │ │  │ - Navigation Controls  │   │ │
│  │  │ └─Chat2  │  │ └──────────────────┘ │  │                        │   │ │
│  │  │          │  │                      │  │                        │   │ │
│  │  │ Yesterday│  │ - Message List       │  │                        │   │ │
│  │  │ └─Chat3  │  │ - Action Buttons     │  │                        │   │ │
│  │  │          │  │ - Input + File Zone  │  │                        │   │ │
│  │  │ Last 7   │  │                      │  │                        │   │ │
│  │  │ └─Chat4  │  │ [New Chat Button]    │  │                        │   │ │
│  │  └──────────┘  └──────────────────────┘  └────────────────────────┘   │ │
│  │                              │                      │                    │ │
│  │  ┌───────────────────────────────────────────────────────────────────┐ │ │
│  │  │              Enhanced State Management (Zustand)                   │ │ │
│  │  │  - Conversation List  - Memory State  - Connection State          │ │ │
│  │  │  - Upload Status      - Retry Queue   - Action Context            │ │ │
│  │  └───────────────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST API
                                    ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND SERVER                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                      FastAPI Application                                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐  │  │
│  │  │  Chat    │  │Conversation│ │   File   │  │   Health/Status      │  │  │
│  │  │Endpoints │  │ Management │ │ Upload   │  │   Monitoring         │  │  │
│  │  └────┬─────┘  └─────┬──────┘  └────┬─────┘  └──────────────────────┘  │  │
│  └───────┼──────────────┼──────────────┼─────────────────────────────────┘  │
│          │              │              │                                      │
│          ▼              ▼              ▼                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │       RAG Pipeline + Action Detector + Memory Manager                │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│          │              │              │              │                       │
│          ▼              ▼              ▼              ▼                       │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌─────────────────────┐    │
│  │ ChromaDB │  │   Gemini     │  │ Storage  │  │ Conversation DB     │    │
│  │ (Vectors)│  │   LLM API    │  │ Service  │  │ (SQLite/PostgreSQL) │    │
│  └──────────┘  └──────────────┘  └──────────┘  └─────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Feature 1: Chat History Sidebar

### UI Placement & Layout

**Location**: Left side of the application  
**Width**: 20% of viewport (min 250px, max 350px)  
**Background**: Light gray (#F9FAFB)  
**Border**: 1px solid #E5E7EB on right edge

### Component Structure

```
HistorySidebar
├── Header Section (Fixed at top, 64px)
│   └── NewChatButton (Full width, primary blue)
├── Search Section (48px)
│   └── SearchInput (Filter conversations)
└── Scrollable List (Remaining height)
    ├── TimeGroup: "Today"
    │   └── ConversationItem × N
    ├── TimeGroup: "Yesterday"
    │   └── ConversationItem × N
    ├── TimeGroup: "Last 7 Days"
    │   └── ConversationItem × N
    └── TimeGroup: "Older" (Collapsed by default)
        └── ConversationItem × N
```

### ConversationItem Design

**Height**: 72px  
**Padding**: 12px  
**States**:
- Default: White background, gray text
- Hover: Light gray background (#F3F4F6)
- Active: Blue left border (3px), light blue background (#EFF6FF)

**Content Layout**:
```
┌─────────────────────────────────┐
│ Title (1 line, truncated)       │  ← 14px font, semibold
│ Preview (2 lines, truncated)    │  ← 13px font, gray-600
│ 2 hours ago • 6 messages         │  ← 12px font, gray-500
└─────────────────────────────────┘
```

### Interaction Flows

**Creating New Chat**:
1. User clicks "New Chat" button
2. Check if current conversation has unsaved content
3. If yes → Show confirmation modal: "Start new chat? Current chat will be saved."
4. If no unsaved content → Create immediately
5. API: `POST /api/conversations/new`
6. Update sidebar with new conversation
7. Focus on input box

**Loading Past Conversation**:
1. User clicks conversation in sidebar
2. Show loading skeleton in chat panel
3. API: `GET /api/conversations/{id}`
4. Load messages sequentially
5. Restore PDF viewer state if applicable
6. Highlight selected conversation in sidebar

**Context Menu** (Right-click on conversation):
- Rename
- Delete (with confirmation)
- Export as PDF
- Pin to top

### Time Grouping Logic

```javascript
function groupConversationsByTime(conversations) {
  const now = new Date();
  const today = startOfDay(now);
  const yesterday = subDays(today, 1);
  const sevenDaysAgo = subDays(today, 7);
  
  return {
    today: conversations.filter(c => isAfter(c.updated_at, today)),
    yesterday: conversations.filter(c => 
      isAfter(c.updated_at, yesterday) && isBefore(c.updated_at, today)
    ),
    last_7_days: conversations.filter(c =>
      isAfter(c.updated_at, sevenDaysAgo) && isBefore(c.updated_at, yesterday)
    ),
    older: conversations.filter(c => isBefore(c.updated_at, sevenDaysAgo))
  };
}
```

---

## Feature 2: New Chat / Reset Conversation

### UI Components

**NewChatButton**:
- Location: Top of chat history sidebar + optional header
- Style: Primary blue (#2563EB), white text, rounded corners
- Icon: Plus icon (16px) + "New Chat" text
- Size: Full width in sidebar, compact in header

**ConfirmationModal**:
- Triggered when starting new chat with unsaved content
- Width: 400px
- Centered overlay with backdrop
- Contains:
  - Title: "Start New Chat?"
  - Message: "Your current conversation will be saved to history."
  - Checkbox: "Remember this conversation" (checked by default)
  - Buttons: "Cancel" (ghost) + "Start New Chat" (primary)

### Interaction Flow

```
User clicks "New Chat"
    ↓
Check current conversation state
    ↓
Has content? ──No──→ Create new chat immediately
    │
    Yes
    ↓
Show confirmation modal
    ↓
User confirms ──→ Save current conversation
    ↓             (if "Remember" checked)
Create new conversation
    ↓
Generate UUID for conversation_id
    ↓
API: POST /api/conversations/new
    {
      "memory_enabled": true/false,
      "category": "current_category"
    }
    ↓
Clear chat panel
    ↓
Add new conversation to sidebar
    ↓
Focus input box
    ↓
Show toast: "New conversation started"
```

### Backend API

```python
@router.post("/conversations/new")
async def create_new_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db)
) -> ConversationResponse:
    """
    Create a new conversation.
    
    Request:
    {
      "title": null,  # Auto-generated from first message
      "memory_enabled": true,
      "category": "technical_support"
    }
    
    Response:
    {
      "conversation_id": "uuid",
      "title": "New Conversation",
      "created_at": "2026-02-12T10:30:00Z",
      "memory_enabled": true,
      "status": "active"
    }
    """
    conversation = Conversation(
        id=str(uuid.uuid4()),
        title="New Conversation",
        memory_enabled=request.memory_enabled,
        category=request.category,
        status="active",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation
```

---

## Feature 3: Action Buttons Under AI Responses

### Button Types & Triggers

**1. View Dashboard**
- **Trigger**: Response mentions metrics, analytics, dashboard, performance data
- **Action**: Navigate to /dashboard with context parameters
- **Example Context**: Filter by mentioned machine, date range, or metric type

**2. Download Report**
- **Trigger**: Response contains comprehensive summary or analysis
- **Action**: Generate PDF report with conversation context and sources
- **Parameters**: Format (PDF/DOCX), include_citations, date_range

**3. Refine Analysis**
- **Trigger**: Response contains calculations, estimates, or approximations
- **Action**: Pre-fill input with "Can you provide more detail on..."
- **Behavior**: User can edit before sending

**4. Ask Follow-up**
- **Trigger**: Response poses questions or suggests next steps
- **Action**: Show dropdown with 3 auto-generated follow-up questions
- **Behavior**: User can click suggestion or type their own

### UI Design Specifications

**Button Group Layout**:
- Position: Below AI message, 12px top margin
- Display: Flex row, wrapped, 8px gap
- Alignment: Left-aligned with message content

**Individual Button**:
- Height: 32px
- Padding: 8px 12px
- Border: 1px solid #D1D5DB
- Border-radius: 6px
- Background: White
- Hover: Background #F9FAFB, border #9CA3AF
- Active: Border #2563EB
- Disabled: Opacity 50%, cursor not-allowed

**Button Content**:
```
┌────────────────────┐
│ [Icon] Label       │  ← Icon 16px, Text 13px medium
└────────────────────┘
```

### Action Detection Logic

```python
# Backend: services/action_detector.py

class ActionDetector:
    def detect_actions(
        self,
        response_content: str,
        sources: List[Dict],
        query_intent: str
    ) -> List[Action]:
        """
        Detect appropriate actions based on response content.
        
        Detection Rules:
        1. Scan response for keywords/patterns
        2. Analyze query intent
        3. Consider available data sources
        4. Return prioritized action list
        """
        actions = []
        content_lower = response_content.lower()
        
        # Check for dashboard action
        if any(keyword in content_lower for keyword in 
               ['metrics', 'analytics', 'performance', 'dashboard', 'statistics']):
            actions.append(Action(
                type='view_dashboard',
                label='View Dashboard',
                icon='chart-bar',
                url='/dashboard',
                params={'filter': self._extract_dashboard_context(response_content)}
            ))
        
        # Check for report action
        if any(keyword in content_lower for keyword in
               ['summary', 'report', 'comprehensive', 'detailed']):
            actions.append(Action(
                type='download_report',
                label='Download Report',
                icon='download',
                params={'format': 'pdf', 'include_sources': True}
            ))
        
        # Check for refinement action
        if any(keyword in content_lower for keyword in
               ['approximately', 'roughly', 'estimate', 'could', 'might']):
            actions.append(Action(
                type='refine_analysis',
                label='Refine Analysis',
                icon='zoom-in',
                params={'prompt_template': 'provide more detail on'}
            ))
        
        # Always include follow-up for non-terminal responses
        if not self._is_terminal_response(response_content):
            actions.append(Action(
                type='ask_followup',
                label='Ask Follow-up',
                icon='message-circle',
                params={
                    'suggestions': self._generate_followup_suggestions(
                        response_content, query_intent
                    )
                }
            ))
        
        return actions
```

### Frontend Implementation

```typescript
// components/ActionButtonGroup.tsx

interface ActionButtonGroupProps {
  actions: Action[];
  messageId: string;
}

export function ActionButtonGroup({ actions, messageId }: ActionButtonGroupProps) {
  const [loadingAction, setLoadingAction] = useState<string | null>(null);
  const [executedActions, setExecutedActions] = useState<Set<string>>(new Set());
  
  const handleAction = async (action: Action) => {
    setLoadingAction(action.type);
    
    try {
      switch (action.type) {
        case 'view_dashboard':
          // Navigate with context
          router.push(`${action.url}?${new URLSearchParams(action.params)}`);
          break;
          
        case 'download_report':
          // Generate and download report
          const blob = await api.post('/reports/generate', {
            message_id: messageId,
            ...action.params
          });
          downloadFile(blob, `report_${messageId}.pdf`);
          toast.success('Report downloaded');
          break;
          
        case 'refine_analysis':
          // Pre-fill input
          const input = document.querySelector('textarea[name="message"]');
          input.value = `Can you ${action.params.prompt_template}: `;
          input.focus();
          break;
          
        case 'ask_followup':
          // Show suggestions dropdown
          showFollowupSuggestions(action.params.suggestions);
          break;
      }
      
      // Mark as executed (except ask_followup which can be reused)
      if (action.type !== 'ask_followup') {
        setExecutedActions(prev => new Set(prev).add(action.type));
      }
      
    } catch (error) {
      toast.error('Action failed');
      console.error(error);
    } finally {
      setLoadingAction(null);
    }
  };
  
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      {actions.map(action => (
        <button
          key={action.type}
          onClick={() => handleAction(action)}
          disabled={executedActions.has(action.type) || loadingAction !== null}
          className="action-button"
        >
          {loadingAction === action.type ? (
            <Spinner size={16} />
          ) : (
            <Icon name={action.icon} size={16} />
          )}
          <span>{action.label}</span>
        </button>
      ))}
    </div>
  );
}
```

---

## Feature 4: Memory Controls

### UI Placement & Design

**Location**: Top of chat panel, below header  
**Height**: 48px  
**Background**: Light gray (#F3F4F6)  
**Border**: Bottom border 1px solid #E5E7EB

### Component Layout

```
┌─────────────────────────────────────────────────────────┐
│ [●] Remembering this conversation  [i]        [ Toggle ]│
└─────────────────────────────────────────────────────────┘
```

**Elements**:
1. Status Indicator (●): 
   - Green (#10B981) when enabled
   - Gray (#9CA3AF) when disabled
2. Status Text: 13px, medium weight
3. Info Icon: Hover to show explanation tooltip
4. Toggle Switch: Standard switch component

### States

**Memory Enabled (Default)**:
- Green indicator dot
- Text: "Remembering this conversation"
- Toggle: ON position
- No warning icons

**Memory Disabled**:
- Gray indicator dot
- Text: "This conversation won't be saved"
- Toggle: OFF position
- Warning icon (⚠) displayed after text
- Subtle yellow background (#FEF3C7)

### Interaction Flow

```
User clicks toggle switch
    ↓
Current state: Enabled
    ↓
Show confirmation dialog:
    "Stop remembering this conversation?"
    
    Message: "This conversation won't be saved in your
    history after this session ends. You won't be able
    to return to it later."
    
    [Cancel] [Forget This Conversation]
    ↓
User confirms
    ↓
API: PATCH /api/conversations/{id}/memory
    {
      "memory_enabled": false
    }
    ↓
Update UI:
    - Change indicator to gray
    - Update status text
    - Show warning icon
    - Apply yellow background
    - Remove from history sidebar
    ↓
Set auto-delete flag for session end
```

### Explanation Popover

**Triggered**: Click on info icon (i)  
**Width**: 320px  
**Content**:

```
┌────────────────────────────────────────┐
│   Conversation Memory                   │
├────────────────────────────────────────┤
│                                         │
│ ● Remembering                           │
│   • Conversation saved in history       │
│   • Return to it anytime                │
│   • Context preserved for future        │
│                                         │
│ ○ Forget After Session                  │
│   • Conversation ends when you          │
│     close the tab                       │
│   • Not saved in history                │
│   • Use for sensitive topics            │
│                                         │
│                     [Got it]            │
└────────────────────────────────────────┘
```

### Backend Implementation

```python
@router.patch("/conversations/{conversation_id}/memory")
async def update_memory_settings(
    conversation_id: str,
    request: MemoryUpdate,
    db: Session = Depends(get_db)
) -> ConversationResponse:
    """
    Update memory settings for a conversation.
    
    Request:
    {
      "memory_enabled": false
    }
    
    Response:
    {
      "conversation_id": "uuid",
      "memory_enabled": false,
      "updated_at": "2026-02-12T15:00:00Z",
      "auto_delete_at": "2026-02-12T23:59:59Z"  # End of session
    }
    """
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    conversation.memory_enabled = request.memory_enabled
    conversation.updated_at = datetime.utcnow()
    
    # Set auto-delete time if memory disabled
    if not request.memory_enabled:
        # Delete 24 hours from now (end of session)
        conversation.auto_delete_at = datetime.utcnow() + timedelta(hours=24)
    else:
        conversation.auto_delete_at = None
    
    db.commit()
    db.refresh(conversation)
    
    return conversation
```

### Auto-Cleanup Background Task

```python
# Background task runs every hour
@router.on_event("startup")
async def start_cleanup_scheduler():
    """Start background task for cleaning up ephemeral conversations"""
    
    async def cleanup_task():
        while True:
            try:
                # Find conversations marked for deletion
                conversations_to_delete = db.query(Conversation).filter(
                    Conversation.memory_enabled == False,
                    Conversation.auto_delete_at <= datetime.utcnow()
                ).all()
                
                for conv in conversations_to_delete:
                    # Delete messages
                    db.query(Message).filter(
                        Message.conversation_id == conv.id
                    ).delete()
                    
                    # Delete conversation
                    db.delete(conv)
                
                db.commit()
                logger.info(f"Cleaned up {len(conversations_to_delete)} ephemeral conversations")
                
            except Exception as e:
                logger.error(f"Cleanup task error: {e}")
            
            # Run every hour
            await asyncio.sleep(3600)
    
    asyncio.create_task(cleanup_task())
```

---

## Feature 5: File Upload at Chat Level

### UI Components

**File Attach Button**:
- Location: Next to send button in chat input
- Icon: Paperclip (20px)
- Color: Gray, hover to dark gray
- Tooltip: "Attach file (PDF, CSV, Excel)"

**Drag & Drop Zone**:
- Triggered: When user drags file over chat area
- Display: Full-screen overlay with dashed border
- Background: Blue-50 with 90% opacity
- Border: 4px dashed blue-400
- Center content: Upload icon + "Drop file to upload" text

**Upload Preview Modal**:
- Width: 480px
- Centered overlay
- Contains:
  - File preview (icon, name, size, type)
  - Optional instruction textarea
  - Cancel / Upload buttons

**Upload Progress Indicator**:
- Position: Above input box
- Design: Compact progress bar with file name
- Show: During upload
- Hide: When complete (with fade animation)

**File Chip** (After upload):
- Position: Inside input box, above text
- Design: Pill-shaped, light blue background
- Content: File icon + name + remove button (×)

### Supported File Types

| Type | Extensions | Purpose | Max Size |
|------|-----------|---------|----------|
| PDF | .pdf | Technical manuals, documents | 50MB |
| CSV | .csv | Data analysis, records | 10MB |
| Excel | .xlsx, .xls | Structured data, spreadsheets | 10MB |

### Interaction Flow

```
User drags file OR clicks attach button
    ↓
Validate file:
    - Check type (PDF, CSV, XLSX)
    - Check size (< max limit)
    - Reject if invalid
    ↓
Show Upload Preview Modal:
    ┌────────────────────────────────────┐
    │ Upload File                         │
    ├────────────────────────────────────┤
    │                                     │
    │ [📄] sales_data.csv                 │
    │      2.3 MB • CSV                   │
    │                                     │
    │ How should I use this file?         │
    │ ┌─────────────────────────────────┐│
    │ │ Analyze trends and summarize... ││
    │ └─────────────────────────────────┘│
    │                                     │
    │              [Cancel] [Upload]      │
    └────────────────────────────────────┘
    ↓
User confirms upload
    ↓
Show progress indicator:
    [████████░░] Uploading sales_data.csv... 80%
    ↓
API: POST /api/conversations/{id}/files
    FormData:
    - file: binary
    - instruction: "Analyze trends..."
    ↓
Backend processing:
    1. Save file to /data/uploads/{conversation_id}/
    2. Process based on type:
       - PDF: Extract text, create chunks, embed
       - CSV: Parse structure, generate preview
       - XLSX: Read sheets, preview data
    3. Store metadata in database
    4. Generate acknowledgment message
    ↓
Response:
    {
      "file_id": "file_abc123",
      "file_name": "sales_data.csv",
      "processed": true,
      "preview": {
        "rows": 1250,
        "columns": ["date", "product", "sales", "region"]
      },
      "acknowledgment": "I've received sales_data.csv
                        containing 1,250 sales records across
                        4 columns. What would you like to know?"
    }
    ↓
Frontend update:
    1. Hide progress indicator
    2. Add file chip to input area
    3. Display AI acknowledgment as new message:
       
       [AI Message]
       ✓ I've received sales_data.csv (1,250 rows, 4 columns).
       What would you like to know about it?
    4. Auto-focus input for user's question
    5. Show success toast: "File uploaded successfully"
```

### File Processing Pipeline

```python
# Backend: api/files.py

@router.post("/conversations/{conversation_id}/files")
async def upload_file(
    conversation_id: str,
    file: UploadFile = File(...),
    instruction: Optional[str] = Form(None),
    db: Session = Depends(get_db)
) -> FileUploadResponse:
    """
    Upload and process a file for conversation context.
    
    Returns:
    {
      "file_id": "uuid",
      "file_name": "data.csv",
      "file_type": "csv",
      "processed": true,
      "preview": {...},
      "acknowledgment": "I've received..."
    }
    """
    # 1. Validate file
    allowed_types = {
        'application/pdf': 50 * 1024 * 1024,  # 50MB
        'text/csv': 10 * 1024 * 1024,  # 10MB
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 10 * 1024 * 1024
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(400, "Unsupported file type")
    
    # Check file size
    file_size = await file.read()
    await file.seek(0)
    
    if len(file_size) > allowed_types[file.content_type]:
        raise HTTPException(400, "File too large")
    
    # 2. Save file
    file_id = str(uuid.uuid4())
    file_path = f"/data/uploads/{conversation_id}/{file_id}_{file.filename}"
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # 3. Process file based on type
    processor = FileProcessor()
    
    if file.content_type == 'application/pdf':
        result = await processor.process_pdf(file_path)
    elif file.content_type == 'text/csv':
        result = await processor.process_csv(file_path)
    else:  # Excel
        result = await processor.process_excel(file_path)
    
    # 4. Store metadata
    file_record = ConversationFile(
        id=file_id,
        conversation_id=conversation_id,
        file_name=file.filename,
        file_type=file.content_type,
        file_size=len(file_size),
        file_path=file_path,
        processed=True,
        preview_data=result['preview']
    )
    
    db.add(file_record)
    db.commit()
    
    # 5. Generate acknowledgment
    acknowledgment = generate_acknowledgment(file.filename, result['preview'])
    
    return {
        "file_id": file_id,
        "file_name": file.filename,
        "file_type": file.content_type,
        "processed": True,
        "preview": result['preview'],
        "acknowledgment": acknowledgment
    }

def generate_acknowledgment(filename: str, preview: Dict) -> str:
    """Generate contextual acknowledgment message"""
    
    if preview.get('type') == 'csv':
        return (
            f"✓ I've received {filename} containing {preview['rows']} rows "
            f"across {len(preview['columns'])} columns "
            f"({', '.join(preview['columns'][:3])}{'...' if len(preview['columns']) > 3 else ''}). "
            f"What would you like to know about this data?"
        )
    elif preview.get('type') == 'pdf':
        return (
            f"✓ I've received {filename} ({preview['pages']} pages). "
            f"I can help you find information from this document. "
            f"What are you looking for?"
        )
    elif preview.get('type') == 'xlsx':
        return (
            f"✓ I've received {filename} with {preview['sheets']} sheets. "
            f"What would you like to analyze?"
        )
    else:
        return f"✓ I've received {filename}. How can I help you with it?"
```

### File Context Integration

When a user sends a message after uploading files, include file context:

```python
# core/rag_pipeline.py

async def process_query(
    query: str,
    conversation_id: str,
    file_ids: List[str] = None
) -> Dict:
    """Process query with optional file context"""
    
    # Get file metadata
    files_context = []
    if file_ids:
        files = db.query(ConversationFile).filter(
            ConversationFile.id.in_(file_ids)
        ).all()
        
        for file in files:
            files_context.append({
                'name': file.file_name,
                'type': file.file_type,
                'preview': file.preview_data
            })
    
    # Include files in LLM context
    enhanced_query = f"""
    Query: {query}
    
    Available Files:
    {json.dumps(files_context, indent=2)}
    
    Consider the uploaded files when answering.
    """
    
    # Continue with RAG pipeline...
```

---

## Feature 6: Backend Disconnect Handling

### Connection Monitoring

**Health Check System**:
- Frontend pings `/api/health` every 30 seconds
- Timeout: 5 seconds
- Tracks connection state in Zustand store

**Connection States**:
1. `connected`: Normal operation
2. `disconnecting`: Detected loss, attempting reconnect
3. `disconnected`: Failed after retries
4. `reconnecting`: Active retry in progress

### UI Components

**Connection Status Indicator**:
- Location: Top-right corner of header
- Size: Small dot (8px) + optional text
- States:
  - Connected: Green dot, no text
  - Reconnecting: Yellow dot + "Reconnecting..."
  - Disconnected: Red dot + "Offline"

**Disconnect Overlay**:
- Trigger: Connection lost
- Display: Semi-transparent overlay over chat area
- Prevents input while disconnected
- Shows status and action buttons

### Disconnect Overlay Design

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│                   [Spinner/Icon]                     │
│                                                      │
│           Attempting to reconnect...                 │
│              Retry attempt 3 of 10                   │
│                                                      │
│                   [Try Again]                        │
│                                                      │
│    Unable to connect? Continue in offline mode      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Retry Logic - Exponential Backoff

```typescript
// stores/connectionStore.ts

interface ConnectionStore {
  isConnected: boolean;
  connectionStatus: ConnectionStatus;
  retryCount: number;
  offlineMode: boolean;
  queuedMessages: Message[];
  
  attemptReconnect: () => Promise<void>;
  toggleOfflineMode: () => void;
  syncQueuedMessages: () => Promise<void>;
}

export const useConnectionStore = create<ConnectionStore>((set, get) => ({
  isConnected: true,
  connectionStatus: 'connected',
  retryCount: 0,
  offlineMode: false,
  queuedMessages: [],
  
  attemptReconnect: async () => {
    const { retryCount } = get();
    
    // Max 10 attempts
    if (retryCount >= 10) {
      set({
        connectionStatus: 'disconnected',
        isConnected: false
      });
      return;
    }
    
    set({
      connectionStatus: 'reconnecting',
      retryCount: retryCount + 1
    });
    
    try {
      // Attempt health check
      const response = await axios.get('/api/health', {
        timeout: 5000
      });
      
      if (response.status === 200) {
        // Connection restored
        set({
          isConnected: true,
          connectionStatus: 'connected',
          retryCount: 0
        });
        
        toast.success('Connection restored');
        
        // Sync any queued messages
        const { queuedMessages } = get();
        if (queuedMessages.length > 0) {
          await get().syncQueuedMessages();
        }
        
        return;
      }
    } catch (error) {
      // Retry failed, schedule next attempt
      const delay = calculateBackoffDelay(retryCount);
      
      setTimeout(() => {
        get().attemptReconnect();
      }, delay);
    }
  },
  
  toggleOfflineMode: () => {
    set(state => ({
      offlineMode: !state.offlineMode
    }));
    
    if (get().offlineMode) {
      toast.info('Offline mode enabled. Your messages will be saved locally.');
    }
  },
  
  syncQueuedMessages: async () => {
    const { queuedMessages } = get();
    
    toast.info(`Syncing ${queuedMessages.length} messages...`);
    
    for (const message of queuedMessages) {
      try {
        await api.post('/api/chat', message);
      } catch (error) {
        console.error('Failed to sync message:', error);
        // Keep in queue
        return;
      }
    }
    
    // Clear queue after successful sync
    set({ queuedMessages: [] });
    toast.success('Messages synced');
  }
}));

function calculateBackoffDelay(retryCount: number): number {
  // Exponential backoff: 2^n seconds, max 15 seconds
  const delay = Math.min(1000 * Math.pow(2, retryCount), 15000);
  return delay;
}
```

### Axios Interceptor Setup

```typescript
// services/api.ts

import axios from 'axios';
import { useConnectionStore } from '@/stores/connectionStore';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000
});

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    const connectionStore = useConnectionStore.getState();
    
    if (error.code === 'ECONNABORTED' || error.code === 'ERR_NETWORK') {
      // Network error detected
      if (connectionStore.isConnected) {
        connectionStore.set({
          isConnected: false,
          connectionStatus: 'disconnecting'
        });
        
        // Start reconnection attempts
        connectionStore.attemptReconnect();
      }
    } else if (error.response?.status >= 500) {
      // Server error
      toast.error('Server error. Please try again.');
      
      if (error.response.status === 503) {
        // Service unavailable, trigger reconnect
        connectionStore.attemptReconnect();
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
```

### Offline Mode Features

**Local Storage Backup**:
```typescript
// utils/localStorageBackup.ts

export function saveMessageToLocal(message: Message) {
  const queue = getLocalQueue();
  queue.push(message);
  localStorage.setItem('message_queue', JSON.stringify(queue));
}

export function getLocalQueue(): Message[] {
  const queue = localStorage.getItem('message_queue');
  return queue ? JSON.parse(queue) : [];
}

export function clearLocalQueue() {
  localStorage.removeItem('message_queue');
}

export function saveConversationState(conversation: Conversation) {
  localStorage.setItem(
    `conversation_${conversation.id}`,
    JSON.stringify(conversation)
  );
}
```

**Offline Mode UI Indicators**:
1. Banner at top: "Offline Mode - Messages saved locally"
2. Input placeholder: "Type message (will send when online)..."
3. "Draft saved" indicator appears after typing
4. "Copy conversation" button to export data

### Error Response Handling

```python
# Backend: middleware/error_handler.py

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for graceful error responses.
    """
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "retry_after": 0
            }
        )
    
    # Database connection errors
    if isinstance(exc, OperationalError):
        return JSONResponse(
            status_code=503,
            content={
                "error": "database_unavailable",
                "message": "Database temporarily unavailable. Please try again.",
                "retry_after": 10,
                "support_action": "retry"
            }
        )
    
    # LLM API errors
    if isinstance(exc, LLMServiceError):
        return JSONResponse(
            status_code=503,
            content={
                "error": "llm_service_unavailable",
                "message": "AI service temporarily unavailable. Please try again.",
                "retry_after": 5,
                "support_action": "retry"
            }
        )
    
    # Generic server error
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again.",
            "retry_after": 5,
            "support_action": "retry"
        }
    )
```

---

## Database Schema

### Conversations Table

```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    title VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    memory_enabled BOOLEAN DEFAULT TRUE,
    status VARCHAR(50) DEFAULT 'active',
    category VARCHAR(100),
    auto_delete_at TIMESTAMP NULL,
    metadata JSONB,
    
    INDEX idx_created_at (created_at DESC),
    INDEX idx_status (status),
    INDEX idx_auto_delete (auto_delete_at)
);
```

### Messages Table

```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- Assistant message fields
    sources JSONB,
    actions JSONB,
    confidence_score FLOAT,
    
    -- User message fields
    attachments JSONB,
    
    INDEX idx_conversation_timestamp (conversation_id, timestamp)
);
```

### Files Table

```sql
CREATE TABLE conversation_files (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    preview_data JSONB,
    
    INDEX idx_conversation_id (conversation_id),
    INDEX idx_uploaded_at (uploaded_at DESC)
);
```

---

## API Reference

### Conversation Management

```
POST   /api/conversations/new          Create new conversation
GET    /api/conversations              List conversations (grouped)
GET    /api/conversations/{id}         Get conversation details
PATCH  /api/conversations/{id}         Update conversation
DELETE /api/conversations/{id}         Delete conversation
PATCH  /api/conversations/{id}/memory  Toggle memory settings
```

### File Management

```
POST   /api/conversations/{id}/files   Upload file
GET    /api/conversations/{id}/files   List conversation files
GET    /api/files/{id}/download        Download file
DELETE /api/files/{id}                 Delete file
```

### Chat

```
POST   /api/chat                       Send message, get AI response
```

### Health & Status

```
GET    /api/health                     Quick health check
GET    /api/status                     Detailed system status
```

---

## Testing Strategy

### Frontend Tests

**Component Tests**:
- HistorySidebar: Rendering, grouping, selection
- MemoryControlBar: Toggle, confirmation, state changes
- ActionButtonGroup: Action execution, loading states
- FileUploadZone: Drag-drop, validation, upload flow
- DisconnectOverlay: State changes, retry logic

**Integration Tests**:
- Complete new chat flow
- Load and switch conversations
- File upload and acknowledgment
- Connection loss and recovery

### Backend Tests

**Unit Tests**:
- ActionDetector: Pattern matching, action generation
- MemoryManager: Context retrieval, cleanup
- FileProcessor: PDF, CSV, Excel processing

**Integration Tests**:
- Complete conversation lifecycle
- File upload and processing pipeline
- Memory persistence and cleanup
- Error handling and recovery

---

## Deployment Checklist

### Frontend Deployment

- [ ] Build production bundle
- [ ] Set environment variables (API_URL)
- [ ] Configure CORS
- [ ] Enable compression
- [ ] Set up CDN for static assets
- [ ] Configure error tracking (Sentry)

### Backend Deployment

- [ ] Database migrations
- [ ] Set up file storage
- [ ] Configure LLM API keys
- [ ] Set up logging
- [ ] Configure rate limiting
- [ ] Set up health check monitoring
- [ ] Schedule cleanup tasks

### Infrastructure

- [ ] Load balancer configuration
- [ ] SSL certificates
- [ ] Database backups
- [ ] File storage backups
- [ ] Monitoring and alerting
- [ ] Auto-scaling rules

---

## Appendix: Component Reference

### Button Styles

```css
/* Primary Button */
.btn-primary {
  background: #2563EB;
  color: white;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  transition: background 150ms;
}

.btn-primary:hover {
  background: #1D4ED8;
}

/* Secondary Button */
.btn-secondary {
  background: white;
  color: #374151;
  border: 1px solid #D1D5DB;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 150ms;
}

.btn-secondary:hover {
  background: #F9FAFB;
  border-color: #9CA3AF;
}

/* Action Button */
.action-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: white;
  border: 1px solid #D1D5DB;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  transition: all 150ms;
}

.action-button:hover:not(:disabled) {
  background: #F9FAFB;
  border-color: #9CA3AF;
}

.action-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

### Color Palette

```
Primary Blue: #2563EB
Primary Blue Hover: #1D4ED8
Light Blue BG: #EFF6FF

Gray 50: #F9FAFB (Sidebar background)
Gray 100: #F3F4F6 (Hover states)
Gray 200: #E5E7EB (Borders)
Gray 300: #D1D5DB (Button borders)
Gray 400: #9CA3AF (Secondary text)
Gray 500: #6B7280 (Tertiary text)
Gray 600: #4B5563 (Primary text on light)
Gray 700: #374151 (Primary text)
Gray 800: #1F2937 (Headings)

Success Green: #10B981
Warning Yellow: #F59E0B
Warning Yellow BG: #FEF3C7
Error Red: #EF4444

Amber 50: #FEF3C7 (Warning backgrounds)
Amber 600: #D97706 (Warning text)
```

---

## Conclusion

This enhanced architecture maintains all core functionality from Version 1.0 while adding six critical UI/UX improvements that elevate the user experience to enterprise standards. The design prioritizes:

- **User Safety**: Confirmations prevent data loss
- **Transparency**: Clear indicators for all system states
- **Resilience**: Graceful handling of failures
- **Productivity**: Action buttons streamline workflows
- **Flexibility**: File uploads enable richer interactions
- **Control**: Memory settings empower users

All enhancements follow enterprise design principles: clean interfaces, professional aesthetics, minimal animations, and predictable interactions.

**Next Steps**:
1. Review and approve architecture
2. Set up enhanced database schema
3. Implement backend endpoints
4. Build frontend components
5. Integration testing
6. User acceptance testing
7. Production deployment

---

**Document Version:** 2.0  
**Last Updated:** February 12, 2026  
**Status:** Ready for Implementation
