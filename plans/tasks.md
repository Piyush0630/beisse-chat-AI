# Implementation Plan: Biesse Chat Assistant (MVP V2)

This plan breaks down the development of the Enhanced Biesse Chat Assistant into 7 logical phases, focusing on delivering the core MVP first and then layering the V2 enhancements.

---

## Phase 1: Infrastructure & Database Setup
**Goal:** Establish the foundational environment and data storage layers.

- [✓] **1.1 Environment Setup**
    - [✓] Initialize `backend/` directory with `venv`.
    - [✓] Install dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `chromadb`, `pymupdf`, `google-generativeai`.
    - [✓] Create `config.py` for environment variables (API Keys).

- [✓] **1.2 Database Implementation (SQLite)**
    - [✓] Create `database.py` (SQLAlchemy engine & session).
    - [✓] Define Models in `models.py`:
        - [✓] `Conversation` (id, title, created_at, memory_enabled).
        - [✓] `Message` (id, role, content, sources, actions).
        - [✓] `File` (id, filename, path).
    - [✓] Run initial migration (create tables).

- [✓] **1.3 Vector DB Setup (ChromaDB)**
    - [✓] Initialize Persistent Client in `services/vector_service.py`.
    - [✓] Create collection `biesse_manuals`.

---

## Phase 2: Core Logic & API Development
**Goal:** Implement the intelligence layer (PDF processing, RAG) and exposure endpoints.

- [✓] **2.1 PDF Processing Pipeline**
    - [✓] Implement `pdf_processor.py` using PyMuPDF.
    - [✓] Function: `extract_text_and_bbox(pdf_path)`.
    - [✓] Function: `chunk_text(text_blocks)`.

- [✓] **2.2 RAG Pipeline Implementation**
    - [✓] Implement `services/llm_service.py` (Gemini Client).
    - [✓] Implement `services/embedding_service.py` (Google Embeddings).
    - [✓] Implement `core/rag_pipeline.py`:
        - [✓] `ingest_document(file)` -> Chunk -> Embed -> Store.
        - [✓] `query(question)` -> Retrieve -> Generate Answer.

- [✓] **2.3 Core API Endpoints**
    - [✓] `GET /health` (Check DB & Vector DB connection).
    - [✓] `POST /chat` (Basic QA loop).
    - [✓] `POST /upload` (Document ingestion).

---

## Phase 3: Core Frontend & Chat Interface (Shell)
**Goal:** Build the user interface and connect it to the backend.

- [✓] **3.1 Frontend Setup**
    - [✓] Initialize `frontend/` (Next.js 14, TypeScript, Tailwind).
    - [✓] Install dependencies: `zustand`, `lucide-react`, `axios`, `react-markdown`, `react-pdf`.
    - [✓] Configure Tailwind & Global Styles.

- [✓] **3.2 Layout Implementation**
    - [✓] Create `components/Layout/MainContent.tsx` (Three-Panel Grid).
    - [✓] Create `components/Layout/Header.tsx`.
    - [✓] Create placeholder Sidebar & PDF Panel.

- [✓] **3.3 Chat Interface**
    - [✓] Create `components/ChatPanel/MessageList.tsx`.
    - [✓] Create `components/ChatPanel/InputBox.tsx`.
    - [✓] Create `lib/store.ts` (Zustand) for managing chat messages.
    - [✓] Implement `API.postMessage` integration with backend.

- [✓] **3.4 PDF Viewer Integration**
    - [✓] Create `components/PDFViewer/PDFRenderer.tsx` using `react-pdf`.
    - [✓] Implement basic PDF loading from URL/File.

---

## Phase 4: V2 Feature - History & Memory
**Goal:** Implement persistent conversations and the "Memory" toggle.

- [✓] **4.1 Backend History Logic**
    - [✓] Update `POST /chat` to save messages to SQLite.
    - [✓] Create `GET /conversations` endpoint (List all).
    - [✓] Create `GET /conversations/{id}` endpoint (Load history).
    - [✓] Implement `POST /conversations/new` endpoint.

- [✓] **4.2 Memory Control Logic**
    - [✓] Update `models.py` with `memory_enabled` flag.
    - [✓] Update RAG Pipeline to respect `memory_enabled`:
        - [✓] If `True`: Fetch last 5 messages from DB & append to context.
        - [✓] If `False`: Use only current query.

- [✓] **4.3 Frontend History Sidebar**
    - [✓] Create `components/Layout/HistorySidebar.tsx`.
    - [✓] Implement Time Grouping Logic (Today, Yesterday, Last 7 Days).
    - [✓] Connect to `GET /conversations`.
    - [✓] Implement "New Chat" button behavior.

- [✓] **4.4 Memory UI**
    - [✓] Create `components/ChatPanel/MemoryControl.tsx` (Toggle Switch).
    - [✓] Connect toggle to API (Update conversation state).

---

## Phase 5: V2 Feature - Actions & Interactive Citations
**Goal:** Make the chat actionable and the PDF viewer interactive.

- [✓] **5.1 Backend Action Detection**
    - [✓] Create `core/action_detector.py`.
    - [✓] Implement rule-based logic (Regex/Keywords) to detect:
        - [✓] "Dashboard" -> `view_dashboard`.
        - [✓] "Page X" -> `open_pdf`.
    - [✓] Update `POST /chat` response to include `actions` list.

- [✓] **5.2 Frontend Action Buttons**
    - [✓] Create `components/ChatPanel/ActionButtons.tsx`.
    - [✓] Render buttons below AI message.
    - [✓] Implement click handlers (e.g., console log or toast for now).

- [✓] **5.3 Interactive Citations**
    - [✓] Update `AIMessage` component to render citations as clickable links.
    - [✓] Implement `components/PDFViewer/HighlightOverlay.tsx`.
    - [✓] Handle citation click:
        - [✓] Load relevant PDF.
        - [✓] Scroll to Page.
        - [✓] Draw Bounding Box (Highlight).

---

## Phase 6: V2 Feature - File Uploads & Reliability
**Goal:** Add file context support and handle network issues gracefully.

- [✓] **6.1 Backend File Handling**
    - [✓] Create `api/files.py` endpoints.
    - [✓] Implement logic to store uploaded files in `data/uploads/{conv_id}`.
    - [✓] Update RAG Pipeline to read file content (if text/csv) and append to context.

- [✓] **6.2 Frontend Upload UI**
    - [✓] Create `components/ChatPanel/FileUpload.tsx` (Drag & Drop).
    - [✓] Create `components/Modals/FileUploadPreviewModal.tsx` (Integrated into FileUpload).
    - [✓] Connect to `POST /upload`.

- [✓] **6.3 Disconnect Handling**
    - [✓] Create `components/Modals/DisconnectModal.tsx`.
    - [✓] Implement Axios Interceptor in `lib/api.ts` to detect 503/Network Errors.
    - [✓] Implement "Reconnecting..." toast and retry logic.
    - [✓] Add `ConnectionStatus` indicator in Header.

---

## Phase 7: Final Polish & Testing
**Goal:** Ensure a smooth user experience.

- [✓] **7.1 UI Polish**
    - [✓] Add Loading Skeletons for chat history.
    - [✓] Add Streaming support for AI responses.
    - [✓] Ensure consistent styling (Tailwind).

- [✓] **7.2 Testing**
    - [✓] Test complete flow: New Chat -> Upload PDF -> Query -> Check History.
    - [✓] Test Memory Toggle (On/Off).
    - [✓] Test Disconnect (Stop backend -> Check UI).

