# Biesse Chat Assistant - MVP Architecture (Enhanced V2)

**Version:** 2.3 (Local MVP + Detailed Flows + Enhanced UI Tree)  
**Date:** February 12, 2026  
**Focus:** Fast execution, local deployment, enhanced UI/UX features without complex infrastructure.

---

## 1. Executive Summary

This document defines the **Minimum Viable Product (MVP)** architecture for the Enhanced Biesse Chat Assistant (V2). It incorporates the six major UI/UX improvements from the V2 specification but streamlines the technical stack for a local, single-server environment.

**Key Simplifications:**
*   **No Docker/Cloud:** Runs directly on localhost (Node.js + Python).
*   **Database:** Uses **SQLite** for all relational data (Conversations, Messages).
*   **Storage:** Uses local filesystem for uploads.
*   **Vector DB:** Uses **ChromaDB** in persistent local mode.
*   **Action Detection:** Uses efficient rule-based logic or simplified class-based detection.

---

## 2. Technology Stack (MVP)

### Frontend
*   **Framework:** Next.js 14 (React 18)
*   **Language:** TypeScript 5.3
*   **Styling:** Tailwind CSS 3.4
*   **State Management:** Zustand 4.5
*   **PDF Viewer:** react-pdf 7.7
*   **Icons:** Lucide React

### Backend
*   **Framework:** FastAPI 0.109.0 (Python 3.11+)
*   **Database:** SQLite (via SQLAlchemy)
*   **Vector DB:** ChromaDB (Local Persistent Client)
*   **AI/ML:** Google Gemini Flash 2.0 (via `google-generativeai`)
*   **PDF Processing:** PyMuPDF (`pymupdf`)

---

## 3. System Architecture

### 3.1 High-Level Architecture Diagram

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
│  │ (Vectors)│  │   LLM API    │  │ Service  │  │ (SQLite)            │    │
│  └──────────┘  └──────────────┘  └──────────┘  └─────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Frontend Component Tree (Enhanced V2.0)

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

### 3.3 Backend Structure (`/backend`)
*Flattened for developer efficiency.*

```text
backend/
├── main.py                  # App Entry & API Routes
├── config.py                # Environment Config
├── database.py              # SQLite Connection & Session
├── models.py                # SQL Tables & Pydantic Models
├── requirements.txt         # Dependencies
├── data/                    # Local Data Storage
│   ├── uploads/             # PDF/CSV Storage
│   ├── chroma_db/           # Vector Index
│   └── app.db               # SQLite Database
└── core/
    ├── rag_pipeline.py      # Main Logic (Query -> Embed -> LLM)
    ├── action_detector.py   # [V2] Rule-based Action Logic
    ├── pdf_processor.py     # Extraction & Chunking
    └── memory_manager.py    # [V2] History Context Logic
```

---

## 4. Database & Data Models

### 4.1 Vector Database Schema (ChromaDB)

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

### 4.2 API Data Models (Pydantic)

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

### 4.3 SQLite Schema (Local DB)

**Table: `conversations`**
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID (PK) | Unique Session ID |
| `title` | TEXT | Auto-generated title |
| `created_at` | DATETIME | For timeline grouping |
| `updated_at` | DATETIME | For sorting |
| `memory_enabled` | BOOLEAN | [V2] Context toggle state |
| `status` | TEXT | 'active', 'archived', 'deleted' |

**Table: `messages`**
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID (PK) | Message ID |
| `conversation_id` | UUID (FK) | Link to Conversation |
| `role` | TEXT | 'user' or 'assistant' |
| `content` | TEXT | Message body (Markdown) |
| `sources` | JSON | Citation metadata (Page, BBox) |
| `actions` | JSON | [V2] Suggested actions |
| `timestamp` | DATETIME | Sending time |

**Table: `files`**
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | UUID (PK) | File ID |
| `conversation_id` | UUID (FK) | Context owner |
| `filename` | TEXT | Original name |
| `filepath` | TEXT | Local path in `/data/uploads` |
| `file_type` | TEXT | 'pdf', 'csv', 'xlsx' |
| `processed` | BOOLEAN | Indexing status |

---

## 5. Core Data Flows & Workflows

### 5.1 Document Upload Workflow

```
[User Uploads PDF]
       ↓
[1. File Validation]
   - Check file type (PDF)
   - Verify size (< 50MB)
   - Scan for corruption
       ↓
[2. Store Original]
   - Save to /data/uploads/
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

### 5.2 Query Processing Workflow

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

### 5.3 PDF Highlighting Workflow

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

## 6. Feature Specifications

### 6.1 Chat History Sidebar

**UI Placement & Layout**
*   **Location**: Left side of the application
*   **Width**: 20% of viewport (min 250px, max 350px)
*   **Background**: Light gray (#F9FAFB)
*   **Border**: 1px solid #E5E7EB on right edge

**Component Structure**
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

**ConversationItem Design**
*   **Height**: 72px
*   **Padding**: 12px
*   **States**:
    *   Default: White background, gray text
    *   Hover: Light gray background (#F3F4F6)
    *   Active: Blue left border (3px), light blue background (#EFF6FF)

**Interaction Flows**
1.  **Creating New Chat**: Check for unsaved content -> Confirm if needed -> `POST /api/conversations/new` -> Update sidebar -> Focus input.
2.  **Loading Past Conversation**: Click item -> Show skeleton -> `GET /api/conversations/{id}` -> Load messages -> Restore state.
3.  **Context Menu**: Rename, Delete, Pin.

**Time Grouping Logic**
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

## 7. Implementation Plan (MVP)

### Phase 1: Backend Core
1.  Setup FastAPI + SQLite (`database.py`, `models.py`).
2.  Implement `pdf_processor.py` (PyMuPDF).
3.  Implement `rag_pipeline.py` (Gemini + Chroma).
4.  Create API Endpoints (`/chat`, `/upload`, `/history`).

### Phase 2: Frontend Foundation
1.  Initialize Next.js + Tailwind.
2.  Build `ChatPanel` (MessageList, Input).
3.  Build `PDFViewer` (react-pdf).

### Phase 3: V2 Enhancements
1.  **Sidebar:** Build `HistorySidebar` with date grouping logic.
2.  **Actions:** Implement `ActionButtons` component and backend detector.
3.  **Memory:** Add Toggle UI and backend filter logic.
4.  **Uploads:** Add Drag & Drop zone and File API.
5.  **Resilience:** Add `ConnectionStatus` and Error Boundaries.

---

## 8. Running Locally

**Backend:**
```bash
cd backend
python -m venv venv
# Activate venv
pip install -r requirements.txt
python main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Access:**
*   Frontend: `http://localhost:3000`
*   API Docs: `http://localhost:8000/docs`
