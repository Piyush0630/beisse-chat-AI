import os
import shutil
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from ..config import settings
from ..core.rag_pipeline import rag_pipeline
from ..core.pdf_processor import extract_text_and_bbox, chunk_text
from ..services.embedding_service import embedding_service
from ..services.llm_service import llm_service

router = APIRouter(prefix="/api/files", tags=["files"])

@router.post("/upload-global")
async def upload_global(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a PDF for global knowledge. Stored in vector DB and local pdfs directory.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for global upload")

    # Ensure PDF_DIR exists
    if not os.path.exists(settings.PDF_DIR):
        os.makedirs(settings.PDF_DIR, exist_ok=True)

    # Save file locally in PDF_DIR
    file_path = os.path.join(settings.PDF_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Ingest into RAG pipeline (Vector DB)
    try:
        chunks_count = rag_pipeline.ingest_document(file_path, file.filename)
    except Exception as e:
        print(f"Error processing global document: {e}")
        # If ingestion fails, remove the file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
    
    return {
        "filename": file.filename,
        "chunks_ingested": chunks_count,
        "message": "File uploaded and indexed globally"
    }

@router.post("/upload-session")
async def upload_session(
    conversation_id: str,
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a file for session-specific context. Stored only in memory (llm_service).
    """
    # Verify conversation exists
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Save file in UPLOAD_DIR/{conversation_id} so it can be served but is isolated
    conv_dir = os.path.join(settings.UPLOAD_DIR, conversation_id)
    if not os.path.exists(conv_dir):
        os.makedirs(conv_dir, exist_ok=True)
    
    file_path = os.path.join(conv_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if file.filename.endswith(".pdf"):
            # Extract and chunk
            blocks = extract_text_and_bbox(file_path)
            chunks_data = chunk_text(blocks)
            
            texts = []
            metadata_list = []
            for c in chunks_data:
                texts.append(c["text"])
                metadata_list.append({
                    "filename": file.filename,
                    "page": c["page"],
                    "bbox": c["bbox"]
                })
            
            if texts:
                # Get embeddings
                embeddings = embedding_service.get_embeddings(texts)
                # Store in session memory with metadata
                llm_service.add_session_document(conversation_id, texts, embeddings, metadata_list)
            
            chunks_count = len(texts)
        elif file.filename.endswith(('.txt', '.csv', '.md')):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            chunks = [content]
            embeddings = embedding_service.get_embeddings(chunks)
            metadata_list = [{"filename": file.filename, "page": 1, "bbox": None}]
            llm_service.add_session_document(conversation_id, chunks, embeddings, metadata_list)
            chunks_count = 1
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type for session context")
            
    except Exception as e:
        print(f"Error processing session document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process session document: {str(e)}")
    
    return {
        "filename": file.filename,
        "conversation_id": conversation_id,
        "chunks_processed": chunks_count,
        "message": "File added to session context"
    }

@router.get("/{conversation_id}")
async def get_conversation_files(conversation_id: str, db: Session = Depends(get_db)):
    # Note: This still returns files from the DB. 
    # Since session files are in memory, they won't appear here unless we want them to.
    # The requirement says session upload -> stored only in memory.
    files = db.query(models.File).filter(models.File.conversation_id == conversation_id).all()
    return files

@router.delete("/{file_id}")
async def delete_file(file_id: str, db: Session = Depends(get_db)):
    db_file = db.query(models.File).filter(models.File.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Remove from filesystem
    if os.path.exists(db_file.filepath):
        os.remove(db_file.filepath)
        
    db.delete(db_file)
    db.commit()
    return {"message": "File deleted successfully"}
