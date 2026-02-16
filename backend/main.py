import os
import shutil
import uuid
import json
from typing import List, Optional
from fastapi import FastAPI, Depends, UploadFile, File as FastAPIFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from .database import get_db, engine
from . import models
from .services.vector_service import vector_service
from .core.rag_pipeline import rag_pipeline
from .core.action_detector import action_detector
from .config import settings
from .api.files import router as files_router
from .api.pdf import router as pdf_router

# Initialize tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Biesse Chat Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/files", StaticFiles(directory=settings.UPLOAD_DIR), name="files")

# Serve PDF files
if not os.path.exists(settings.PDF_DIR):
    os.makedirs(settings.PDF_DIR, exist_ok=True)
app.mount("/pdf-files", StaticFiles(directory=settings.PDF_DIR), name="pdf-files")

app.include_router(files_router)
app.include_router(pdf_router)

@app.get("/pdf-viewer/{filename:path}")
async def serve_pdf(filename: str, db: Session = Depends(get_db)):
    """
    Unified PDF server that checks the database mapping first, 
    then fallbacks to physical directory scanning.
    """
    # 1. Check database for filename mapping (matches original filename or ID)
    # We check filename, rel_path or id
    file_id_attempt = os.path.splitext(filename)[0]
    db_file = db.query(models.File).filter(
        (models.File.filename == filename) | 
        (models.File.id == file_id_attempt) |
        (models.File.id == filename)
    ).first()
    
    if db_file and os.path.exists(db_file.filepath):
        return FileResponse(db_file.filepath)

    # 2. Try PDF_DIR first (direct physical match)
    pdf_path = os.path.join(settings.PDF_DIR, filename)
    if os.path.exists(pdf_path):
        return FileResponse(pdf_path)
    
    # 3. Try UPLOAD_DIR root
    upload_path = os.path.join(settings.UPLOAD_DIR, filename)
    if os.path.exists(upload_path):
        return FileResponse(upload_path)
        
    raise HTTPException(status_code=404, detail=f"File not found: {filename}")
    
    # 4. Recursive search in UPLOAD_DIR (last resort)
    base_filename = os.path.basename(filename)
    for root, dirs, files in os.walk(settings.UPLOAD_DIR):
        if base_filename in files:
            return FileResponse(os.path.join(root, base_filename))
            
    raise HTTPException(status_code=404, detail=f"PDF file {filename} not found")

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

class ConversationUpdate(BaseModel):
    memory_enabled: Optional[bool] = None
    title: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to Biesse Chat Assistant API"}

@app.get("/conversations")
def get_conversations(db: Session = Depends(get_db)):
    conversations = db.query(models.Conversation).order_by(models.Conversation.updated_at.desc()).all()
    return conversations

@app.post("/conversations/new")
def create_conversation(db: Session = Depends(get_db)):
    conv = models.Conversation(title="New Chat")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv

@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Load messages
    messages = db.query(models.Message).filter(models.Message.conversation_id == conversation_id).order_by(models.Message.timestamp.asc()).all()
    
    return {
        "id": conv.id,
        "title": conv.title,
        "memory_enabled": conv.memory_enabled,
        "created_at": conv.created_at,
        "updated_at": conv.updated_at,
        "messages": messages
    }

@app.patch("/conversations/{conversation_id}")
def update_conversation(conversation_id: str, request: ConversationUpdate, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if request.memory_enabled is not None:
        conv.memory_enabled = request.memory_enabled
    if request.title is not None:
        conv.title = request.title
        
    db.commit()
    db.refresh(conv)
    return conv

@app.delete("/conversations/{conversation_id}")
def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Files are handled by cascade delete in DB, but we should also delete physical files if any
    files = db.query(models.File).filter(models.File.conversation_id == conversation_id).all()
    for file in files:
        if os.path.exists(file.filepath):
            try:
                os.remove(file.filepath)
            except Exception as e:
                print(f"Error deleting file {file.filepath}: {e}")

    db.delete(conv)
    db.commit()
    return {"message": "Conversation deleted successfully"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Check Database
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check Vector DB
    vdb_status = "ok"
    count = 0
    try:
        count = vector_service.get_collection().count()
    except Exception as e:
        vdb_status = f"error: {str(e)}"
        
    return {
        "status": "online",
        "database": db_status,
        "vector_db": vdb_status,
        "vector_count": count
    }

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Get or create conversation
    if not request.conversation_id:
        conv = models.Conversation(title=request.query[:50])
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
    else:
        conversation_id = request.conversation_id
        conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
    # 2. Save user message
    user_msg = models.Message(
        conversation_id=conversation_id,
        role="user",
        content=request.query
    )
    db.add(user_msg)
    
    conv.updated_at = models.datetime.utcnow()
    if conv.title == "New Chat" or len(conv.title) < 5:
        conv.title = request.query[:50]
        
    db.commit()
    
    # 3. Fetch history
    history = []
    if conv.memory_enabled:
        past_messages = db.query(models.Message)\
            .filter(models.Message.conversation_id == conversation_id)\
            .filter(models.Message.id != user_msg.id)\
            .order_by(models.Message.timestamp.desc())\
            .limit(5)\
            .all()
        for msg in reversed(past_messages):
            history.append({"role": msg.role, "content": msg.content})
    
    # 4. Additional context
    additional_context = ""
    files = db.query(models.File).filter(
        models.File.conversation_id == conversation_id,
        models.File.processed == False
    ).all()
    
    for file in files:
        if file.filename.endswith(('.txt', '.csv', '.md')):
            try:
                if os.path.exists(file.filepath):
                    with open(file.filepath, 'r', encoding='utf-8') as f:
                        additional_context += f"\n---\nFile: {file.filename}\nContent:\n{f.read()}\n"
            except Exception as e:
                print(f"Error reading file {file.filename}: {e}")

    def stream_generator():
        full_answer = ""
        sources = []
        
        for chunk_str in rag_pipeline.query_stream(request.query, history=history, additional_context=additional_context):
            chunk_data = json.loads(chunk_str)
            if chunk_data["type"] == "metadata":
                sources = chunk_data["sources"]
                chunk_data["conversation_id"] = conversation_id
                yield json.dumps(chunk_data) + "\n"
            elif chunk_data["type"] == "content":
                full_answer += chunk_data["content"]
                yield chunk_str
        
        # After stream ends, detect actions and save message
        actions = action_detector.detect_actions(full_answer)
        assistant_msg = models.Message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_answer,
            sources=sources,
            actions=actions
        )
        try:
            db.add(assistant_msg)
            db.commit()
            yield json.dumps({
                "type": "final", 
                "message_id": assistant_msg.id,
                "actions": actions
            }) + "\n"
        except Exception as e:
            print(f"Error saving assistant message: {e}")
            db.rollback()

    return StreamingResponse(stream_generator(), media_type="application/x-ndjson")

@app.post("/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    # 1. Get or create conversation
    if not request.conversation_id:
        conv = models.Conversation(title=request.query[:50])
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
    else:
        conversation_id = request.conversation_id
        # Verify conversation exists
        conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
    # 2. Save user message
    user_msg = models.Message(
        conversation_id=conversation_id,
        role="user",
        content=request.query
    )
    db.add(user_msg)
    
    # Update conversation timestamp and title if it's the first message
    conv.updated_at = models.datetime.utcnow()
    if conv.title == "New Chat" or len(conv.title) < 5:
        conv.title = request.query[:50]
        
    db.commit()
    
    # 3. Fetch history if memory is enabled
    history = []
    if conv.memory_enabled:
        # Fetch last 5 messages (excluding the one we just added)
        past_messages = db.query(models.Message)\
            .filter(models.Message.conversation_id == conversation_id)\
            .filter(models.Message.id != user_msg.id)\
            .order_by(models.Message.timestamp.desc())\
            .limit(5)\
            .all()
        
        # Reverse to get chronological order
        for msg in reversed(past_messages):
            history.append({"role": msg.role, "content": msg.content})
    
    # 4. Query RAG pipeline
    # Fetch additional file context (text files uploaded to this conversation)
    additional_context = ""
    files = db.query(models.File).filter(
        models.File.conversation_id == conversation_id,
        models.File.processed == False
    ).all()
    
    for file in files:
        if file.filename.endswith(('.txt', '.csv', '.md')):
            try:
                if os.path.exists(file.filepath):
                    with open(file.filepath, 'r', encoding='utf-8') as f:
                        additional_context += f"\n---\nFile: {file.filename}\nContent:\n{f.read()}\n"
            except Exception as e:
                print(f"Error reading file {file.filename}: {e}")

    try:
        result = rag_pipeline.query(request.query, history=history, additional_context=additional_context)
    except Exception as e:
        print(f"Error in RAG pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"Error in RAG pipeline: {str(e)}")
        
    # 4.5 Detect actions
    actions = action_detector.detect_actions(result["answer"])

    # 5. Save assistant message
    assistant_msg = models.Message(
        conversation_id=conversation_id,
        role="assistant",
        content=result["answer"],
        sources=result["sources"],
        actions=actions
    )
    db.add(assistant_msg)
    db.commit()
    
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "actions": actions,
        "conversation_id": conversation_id,
        "message_id": assistant_msg.id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
