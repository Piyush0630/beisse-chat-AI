import uuid
import json
from typing import List, Dict, Any
from backend.core.pdf_processor import extract_text_and_bbox, chunk_text
from backend.services.embedding_service import embedding_service
from backend.services.vector_service import vector_service
from backend.services.llm_service import llm_service

class RAGPipeline:
    def ingest_document(self, file_path: str, filename: str) -> int:
        """
        Processes a PDF document, chunks it, embeds chunks, and stores them in the vector database.
        Returns the number of chunks ingested.
        """
        # 1. Extract text and bounding boxes
        blocks = extract_text_and_bbox(file_path)
        
        # 2. Chunk text
        chunks = chunk_text(blocks)
        
        if not chunks:
            return 0
            
        texts = [c["text"] for c in chunks]
        metadatas = []
        ids = []
        
        # 3. Generate embeddings for all chunks
        embeddings = embedding_service.get_embeddings(texts)
        
        # 4. Prepare for vector storage
        collection = vector_service.get_collection()
        
        for i, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            metadatas.append({
                "filename": filename,
                "page": chunk["page"],
                "bbox": json.dumps(chunk["bbox"]),
                "text": chunk["text"]  # Store text in metadata for easy retrieval
            })
            
        # 5. Add to collection
        collection.add(
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(ids)

    def query(self, question: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Retrieves relevant document chunks and generates an answer.
        """
        # 1. Embed the query
        query_embedding = embedding_service.get_embedding(question)
        
        # 2. Search for similar chunks
        collection = vector_service.get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # 3. Format retrieved context and collect sources
        retrieved_texts = []
        sources = []
        
        # results['ids'][0] contains the ids of the top results
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                retrieved_texts.append(metadata['text'])
                sources.append({
                    "filename": metadata['filename'],
                    "page": metadata['page'],
                    "bbox": json.loads(metadata['bbox'])
                })
            
        context = "\n---\n".join(retrieved_texts)
        
        # 4. Generate answer using LLM
        answer = llm_service.generate_answer(question, context)
        
        return {
            "answer": answer,
            "sources": sources
        }

rag_pipeline = RAGPipeline()
