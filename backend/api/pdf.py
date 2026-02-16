from typing import List
from fastapi import APIRouter, Depends, UploadFile, File as FastAPIFile, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.pdf_service import pdf_service
from .. import models

router = APIRouter(prefix="/pdf", tags=["pdf"])

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    db_file = pdf_service.upload_pdf(db, file.file, file.filename)
    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "processed": db_file.processed
    }

@router.get("/list")
async def list_pdfs(db: Session = Depends(get_db)):
    pdfs = pdf_service.list_pdfs(db)
    return pdfs

@router.delete("/{file_id}")
async def delete_pdf(file_id: str, db: Session = Depends(get_db)):
    success = pdf_service.delete_pdf(db, file_id)
    if not success:
        raise HTTPException(status_code=404, detail="PDF not found")
    return {"message": "PDF deleted successfully"}

@router.put("/{file_id}/replace")
async def replace_pdf(
    file_id: str,
    file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    db_file = pdf_service.replace_pdf(db, file_id, file.file, file.filename)
    if not db_file:
        raise HTTPException(status_code=404, detail="PDF not found")
        
    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "processed": db_file.processed
    }

@router.post("/{file_id}/reembed")
async def reembed_pdf(file_id: str, db: Session = Depends(get_db)):
    db_file = pdf_service.reembed_pdf(db, file_id)
    if not db_file:
        raise HTTPException(status_code=404, detail="PDF not found")
        
    return {
        "id": db_file.id,
        "filename": db_file.filename,
        "processed": db_file.processed
    }
