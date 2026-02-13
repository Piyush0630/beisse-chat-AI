import os
import sys

# Add the parent directory to sys.path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
from backend import models
from backend.core.rag_pipeline import rag_pipeline
from backend.config import settings

def ingest_manual_uploads():
    """
    Scans the upload directory and ingests any PDF files that are not already in the database.
    This is useful for files manually placed in the data/uploads folder.
    """
    # Ensure tables exist
    models.Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    upload_dir = settings.UPLOAD_DIR
    
    print(f"Scanning {upload_dir} for PDF files...")
    
    if not os.path.exists(upload_dir):
        print(f"Directory {upload_dir} does not exist.")
        return

    files_processed = 0
    files_skipped = 0
    
    for filename in os.listdir(upload_dir):
        if not filename.lower().endswith(".pdf"):
            continue
            
        filepath = os.path.join(upload_dir, filename)
        
        # Check if file is already in DB
        existing_file = db.query(models.File).filter(models.File.filename == filename).first()
        
        if existing_file and existing_file.processed:
            print(f"Skipping {filename} (already processed)")
            files_skipped += 1
            continue
            
        print(f"Processing {filename}...")
        
        # Create a conversation context for this file (optional, but good for organization)
        # We'll check if a conversation for this file already exists or create a general "Manual Uploads" one
        # For simplicity, let's create a new conversation for each file to match the upload endpoint logic
        conversation = models.Conversation(title=f"Chat with {filename}")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        
        # Create File record
        # If the file was already in DB but not processed, we update it. Otherwise create new.
        if existing_file:
            db_file = existing_file
            db_file.conversation_id = conversation.id
        else:
            db_file = models.File(
                conversation_id=conversation.id,
                filename=filename,
                filepath=filepath,
                file_type="pdf"
            )
            db.add(db_file)
        
        try:
            # Ingest content
            chunks = rag_pipeline.ingest_document(filepath, filename)
            
            db_file.processed = True
            db.commit()
            print(f"Successfully ingested {filename} ({chunks} chunks)")
            files_processed += 1
        except Exception as e:
            print(f"Error ingesting {filename}: {e}")
            db.rollback()
            
    print(f"\nSummary: {files_processed} files processed, {files_skipped} files skipped.")
    db.close()

if __name__ == "__main__":
    ingest_manual_uploads()
