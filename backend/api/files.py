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

router = APIRouter(prefix="/api/files", tags=["files"])

@router.post("/upload")
async def upload_document(
    conversation_id: str,
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    # Verify conversation exists
    conv = db.query(models.Conversation).filter(models.Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Create directory for conversation if it doesn't exist
    conv_dir = os.path.join(settings.UPLOAD_DIR, conversation_id)
    if not os.path.exists(conv_dir):
        os.makedirs(conv_dir, exist_ok=True)

    # Save file locally
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    saved_filename = f"{file_id}{file_ext}"
    file_path = os.path.join(conv_dir, saved_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save to database
    db_file = models.File(
        id=file_id,
        conversation_id=conversation_id,
        filename=file.filename,
        filepath=file_path,
        file_type=file_ext.replace(".", "").lower() or "unknown"
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    
    # Ingest into RAG pipeline if it's a PDF
    chunks_count = 0
    if file.filename.endswith(".pdf"):
        try:
            chunks_count = rag_pipeline.ingest_document(file_path, file.filename)
            db_file.processed = True
            db.commit()
        except Exception as e:
            print(f"Error processing document: {e}")
            # We keep the file but it's not marked as processed
    
    return {
        "filename": file.filename,
        "conversation_id": conversation_id,
        "chunks_ingested": chunks_count,
        "file_id": db_file.id,
        "path": f"/files/{conversation_id}/{saved_filename}"
    }

@router.get("/{conversation_id}")
async def get_conversation_files(conversation_id: str, db: Session = Depends(get_db)):
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
