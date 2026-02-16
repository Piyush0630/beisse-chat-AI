import os
import shutil
import uuid
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from .. import models
from ..config import settings
from ..core.pdf_processor import extract_text_and_bbox, chunk_text
from .embedding_service import embedding_service
from .vector_service import vector_service

class PDFService:
    def upload_pdf(self, db: Session, file_content, filename: str) -> models.File:
        """
        Saves PDF to disk, creates embeddings, stores in vector DB, and saves metadata in SQLite.
        """
        # 1. Save file to UPLOAD_DIR
        file_id = str(uuid.uuid4())
        file_ext = os.path.splitext(filename)[1]
        saved_filename = f"{file_id}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_content, buffer)
        
        # 2. Create File record in DB
        db_file = models.File(
            id=file_id,
            filename=filename,
            filepath=file_path,
            file_type="pdf",
            processed=False
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # 3. Process and Embed
        try:
            self.process_and_embed(db_file)
            db_file.processed = True
            db.commit()
            db.refresh(db_file)
        except Exception as e:
            print(f"Error processing PDF {filename}: {e}")
            # Keep the record but processed=False
            
        return db_file

    def list_pdfs(self, db: Session) -> List[models.File]:
        """
        Lists all PDF files from metadata DB.
        """
        return db.query(models.File).filter(models.File.file_type == "pdf").all()

    def delete_pdf(self, db: Session, file_id: str) -> bool:
        """
        Deletes vectors, PDF file, and metadata.
        """
        db_file = db.query(models.File).filter(models.File.id == file_id).first()
        if not db_file:
            return False
        
        # 1. Delete vectors
        vector_service.delete_by_filename(db_file.filename)
        
        # 2. Delete file
        if os.path.exists(db_file.filepath):
            os.remove(db_file.filepath)
            
        # 3. Delete metadata
        db.delete(db_file)
        db.commit()
        return True

    def replace_pdf(self, db: Session, file_id: str, file_content, filename: str) -> Optional[models.File]:
        """
        Deletes old vectors, replaces file, creates new embeddings, and updates metadata.
        """
        db_file = db.query(models.File).filter(models.File.id == file_id).first()
        if not db_file:
            return None
            
        # 1. Delete old vectors
        vector_service.delete_by_filename(db_file.filename)
        
        # 2. Delete old file if name/path changed (or just overwrite)
        if os.path.exists(db_file.filepath):
            os.remove(db_file.filepath)
            
        # 3. Save new file
        file_ext = os.path.splitext(filename)[1]
        saved_filename = f"{file_id}{file_ext}" # Keep same ID for the file name if possible, or update it
        file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file_content, buffer)
            
        # 4. Update metadata
        db_file.filename = filename
        db_file.filepath = file_path
        db_file.processed = False
        db.commit()
        
        # 5. Process and Embed
        try:
            self.process_and_embed(db_file)
            db_file.processed = True
            db.commit()
        except Exception as e:
            print(f"Error processing replacement PDF {filename}: {e}")
            
        return db_file

    def reembed_pdf(self, db: Session, file_id: str) -> Optional[models.File]:
        """
        Deletes existing vectors, regenerates embeddings, and updates metadata.
        """
        db_file = db.query(models.File).filter(models.File.id == file_id).first()
        if not db_file:
            return None
            
        # 1. Delete existing vectors
        vector_service.delete_by_filename(db_file.filename)
        
        # 2. Process and Embed
        db_file.processed = False
        db.commit()
        
        try:
            self.process_and_embed(db_file)
            db_file.processed = True
            db.commit()
        except Exception as e:
            print(f"Error re-embedding PDF {db_file.filename}: {e}")
            
        return db_file

    def process_and_embed(self, db_file: models.File):
        """
        Helper to extract, chunk, embed and store in vector DB.
        """
        # Extract text and blocks
        blocks = extract_text_and_bbox(db_file.filepath)
        
        # Chunk text
        chunks = chunk_text(blocks)
        
        if not chunks:
            return
            
        texts = [c["text"] for c in chunks]
        metadatas = []
        ids = []
        
        # Generate embeddings
        embeddings = embedding_service.get_embeddings(texts)
        
        # Prepare for vector storage
        collection = vector_service.get_collection()
        
        # Determine base directory for rel_path
        base_dir = settings.UPLOAD_DIR if db_file.filepath.startswith(settings.UPLOAD_DIR) else settings.PDF_DIR
        rel_path = os.path.relpath(db_file.filepath, base_dir).replace('\\', '/')
        
        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            metadatas.append({
                "filename": db_file.filename,
                "rel_path": rel_path,
                "page": chunk["page"],
                "bbox": json.dumps(chunk["bbox"]),
                "text": chunk["text"]
            })
            
        # Add to collection
        collection.add(
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

pdf_service = PDFService()
