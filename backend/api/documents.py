"""
Document API Endpoints

Handles document upload and management.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import shutil
import uuid
import os
import logging
from datetime import datetime

from models.document import DocumentUploadResponse, DocumentListResponse, DocumentStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


def get_services():
    """Get required services"""
    from services.vector_service import create_vector_service
    from services.embedding_service import EmbeddingService
    from pdf.extractor import PDFExtractor
    from pdf.chunker import DocumentChunker
    from pdf.metadata_builder import MetadataBuilder
    from config import settings
    
    vector_service = create_vector_service(
        persist_directory=settings.chromadb_path,
        collection_name_prefix=settings.collection_name_prefix
    )
    
    embedding_service = EmbeddingService(
        api_key=settings.google_api_key,
        model=settings.embedding_model,
        dimensions=settings.embedding_dimensions
    )
    
    chunker = DocumentChunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap
    )
    
    return {
        "vector_service": vector_service,
        "embedding_service": embedding_service,
        "chunker": chunker
    }


# Document catalog (Phase 1 - in-memory)
document_catalog: dict = {}


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...)
):
    """
    Upload a PDF document for processing
    
    Args:
        file: PDF file to upload
        category: Document category
        
    Returns:
        Upload response with document ID and chunk count
    """
    import time
    start_time = time.time()
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Only PDF files are allowed"
        )
    
    # Create document ID
    document_id = str(uuid.uuid4())
    
    # Ensure directories exist
    os.makedirs(settings.manuals_dir, exist_ok=True)
    
    # Save uploaded file
    file_path = f"{settings.manuals_dir}/{document_id}_{file.filename}"
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(file_path)
        
        # Validate file size
        if file_size > settings.max_file_size_mb * 1024 * 1024:
            os.remove(file_path)
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
            )
        
        # Get services
        services = get_services()
        
        # Extract text from PDF
        extractor = PDFExtractor(file_path)
        extraction_result = extractor.extract_with_toc_context()
        extractor.close()
        
        # Build document info
        document_info = MetadataBuilder.build_document_metadata(
            document_id=document_id,
            filename=file.filename,
            category=category,
            page_count=extraction_result.metadata["page_count"],
            file_size_bytes=file_size
        )
        
        # Convert blocks for chunking
        blocks = []
        for page in extraction_result.pages:
            for block in page.blocks:
                blocks.append({
                    "text": block.text,
                    "page_number": block.page_number,
                    "type": block.block_type,
                    "bbox": {
                        "x": block.bbox[0],
                        "y": block.bbox[1],
                        "width": block.bbox[2] - block.bbox[0],
                        "height": block.bbox[3] - block.bbox[1]
                    },
                    "section": block.section
                })
        
        # Chunk document
        chunking_result = services["chunker"].chunk_document(
            extracted_blocks=blocks,
            document_metadata=document_info,
            document_id=document_id
        )
        
        # Generate embeddings
        texts = [chunk.text for chunk in chunking_result.chunks]
        embeddings = services["embedding_service"].embed_texts(texts)
        
        # Build metadata for each chunk
        metadatas = []
        for chunk in chunking_result.chunks:
            metadata = MetadataBuilder.build_chunk_metadata(
                chunk_id=chunk.id,
                document_info=document_info,
                page_number=chunk.page_number,
                section=chunk.section,
                bbox=None,  # Already in block metadata
                chunk_index=chunk.chunk_index,
                chunk_type="text"
            )
            metadatas.append(metadata)
        
        ids = [chunk.id for chunk in chunking_result.chunks]
        
        # Store in vector database
        services["vector_service"].add_documents(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
            category=category
        )
        
        # Update document catalog
        document_info["status"] = DocumentStatus.READY.value
        document_info["chunk_count"] = chunking_result.total_chunks
        document_catalog[document_id] = document_info
        
        processing_time = time.time() - start_time
        
        logger.info(f"Document {document_id} processed in {processing_time:.2f}s")
        
        return DocumentUploadResponse(
            success=True,
            document_id=document_id,
            filename=file.filename,
            chunk_count=chunking_result.total_chunks,
            message=f"Document processed successfully in {processing_time:.2f}s"
        )
    
    except Exception as e:
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        
        logger.error(f"Error processing document: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


@router.get("/list", response_model=DocumentListResponse)
async def list_documents():
    """
    List all uploaded documents
    
    Returns:
        List of documents with metadata
    """
    documents = list(document_catalog.values())
    
    # Count by category
    category_counts = {}
    for doc in documents:
        cat = doc.get("category", "unknown")
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return DocumentListResponse(
        documents=documents,
        total_count=len(documents),
        category_counts=category_counts
    )


@router.get("/{document_id}")
async def get_document(document_id: str):
    """
    Get document metadata
    
    Args:
        document_id: Document ID
        
    Returns:
        Document metadata
    """
    if document_id not in document_catalog:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document_catalog[document_id]


@router.delete("/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document
    
    Args:
        document_id: Document ID
        
    Returns:
        Deletion confirmation
    """
    if document_id not in document_catalog:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get document info
    doc_info = document_catalog[document_id]
    category = doc_info.get("category")
    
    # Delete from vector database
    try:
        services = get_services()
        # Note: In a full implementation, we'd delete specific chunks
        services["vector_service"].delete_collection(category)
    except Exception as e:
        logger.error(f"Error deleting from vector store: {e}")
    
    # Delete file
    filename = doc_info.get("filename", "")
    file_path = f"{settings.manuals_dir}/{document_id}_{filename}"
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove from catalog
    del document_catalog[document_id]
    
    return {
        "success": True,
        "document_id": document_id,
        "message": "Document deleted successfully"
    }


@router.get("/{document_id}/search")
async def search_in_document(
    document_id: str,
    query: str
):
    """
    Search within a specific document
    
    Args:
        document_id: Document ID
        query: Search query
        
    Returns:
        Search results within the document
    """
    if document_id not in document_catalog:
        raise HTTPException(status_code=404, detail="Document not found")
    
    doc_info = document_catalog[document_id]
    category = doc_info.get("category")
    
    services = get_services()
    
    # Generate query embedding
    query_embedding = services["embedding_service"].embed_query(query)
    
    # Search with category filter
    results = services["vector_service"].search(
        query_embedding=query_embedding,
        category=category,
        n_results=10,
        similarity_threshold=0.5
    )
    
    # Filter by document ID
    doc_results = [
        r for r in results 
        if r.get("metadata", {}).get("manual_id") == document_id
    ]
    
    return {
        "document_id": document_id,
        "query": query,
        "results": doc_results,
        "result_count": len(doc_results)
    }
