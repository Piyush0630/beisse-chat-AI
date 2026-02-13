import os
import shutil
import uuid
from typing import List, Optional
from fastapi import FastAPI, Depends, UploadFile, File as FastAPIFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from .database import get_db, engine
from . import models
from .services.vector_service import vector_service
from .core.rag_pipeline import rag_pipeline
from .config import settings

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

class ChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to Biesse Chat Assistant API"}

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

@app.post("/upload")
async def upload_document(
    file: UploadFile = FastAPIFile(...),
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Create conversation if not provided
    if not conversation_id:
        conv = models.Conversation(title=f"Chat with {file.filename}")
        db.add(conv)
        db.commit()
        db.refresh(conv)
        conversation_id = conv.id
    
    # Save file locally
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save to database
    db_file = models.File(
        id=file_id,
        conversation_id=conversation_id,
        filename=file.filename,
        filepath=file_path,
        file_type="pdf"
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    # Ingest into RAG pipeline
    try:
        chunks_count = rag_pipeline.ingest_document(file_path, file.filename)
        db_file.processed = True
        db.commit()
    except Exception as e:
        # In case of error, we might want to keep the record but marked as not processed
        # For now, let's just log and raise
        print(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
        
    return {
        "filename": file.filename,
        "conversation_id": conversation_id,
        "chunks_ingested": chunks_count,
        "file_id": db_file.id
    }

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
    db.commit()
    
    # 3. Query RAG pipeline
    try:
        result = rag_pipeline.query(request.query)
    except Exception as e:
        print(f"Error in RAG pipeline: {e}")
        raise HTTPException(status_code=500, detail=f"Error in RAG pipeline: {str(e)}")
        
    # 4. Save assistant message
    assistant_msg = models.Message(
        conversation_id=conversation_id,
        role="assistant",
        content=result["answer"],
        sources=result["sources"]
    )
    db.add(assistant_msg)
    db.commit()
    
    return {
        "answer": result["answer"],
        "sources": result["sources"],
        "conversation_id": conversation_id,
        "message_id": assistant_msg.id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
