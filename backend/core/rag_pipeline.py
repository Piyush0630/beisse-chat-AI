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
        import os
        from backend.config import settings
        # 1. Determine base directory for rel_path
        if file_path.startswith(settings.UPLOAD_DIR):
            base_dir = settings.UPLOAD_DIR
        else:
            base_dir = settings.PDF_DIR
            
        rel_path = os.path.relpath(file_path, base_dir).replace('\\', '/')
        
        # 2. Extract text and bounding boxes
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
                "rel_path": rel_path,
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

    def query(self, question: str, n_results: int = 5, history: List[Dict[str, str]] = None, additional_context: str = "", conversation_id: str = None) -> Dict[str, Any]:
        """
        Retrieves relevant document chunks and generates an answer using context and history.
        """
        # Simple check for greetings to avoid unnecessary RAG search
        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "how are you"]
        clean_question = question.lower().strip().rstrip('?!.')
        is_greeting = any(clean_question == g or clean_question.startswith(g + " ") for g in greetings)
        
        if is_greeting:
            answer = llm_service.generate_answer(question, "", history)
            return {
                "answer": answer,
                "sources": []
            }

        context, sources = self._retrieve_context(question, n_results, additional_context, conversation_id)
        
        # 4. Generate answer using LLM (with history)
        answer = llm_service.generate_answer(question, context, history)
        
        return {
            "answer": answer,
            "sources": sources
        }

    def query_stream(self, question: str, n_results: int = 5, history: List[Dict[str, str]] = None, additional_context: str = "", conversation_id: str = None):
        """
        Retrieves relevant document chunks and generates a streaming answer.
        """
        # Simple check for greetings to avoid unnecessary RAG search
        greetings = ["hi", "hello", "hey", "greetings", "good morning", "good afternoon", "good evening", "how are you"]
        clean_question = question.lower().strip().rstrip('?!.')
        is_greeting = any(clean_question == g or clean_question.startswith(g + " ") for g in greetings)
        
        if is_greeting:
            yield json.dumps({"type": "metadata", "sources": []}) + "\n"
            for chunk in llm_service.generate_answer_stream(question, "", history):
                yield json.dumps({"type": "content", "content": chunk}) + "\n"
            return

        context, sources = self._retrieve_context(question, n_results, additional_context, conversation_id)
        
        # Yield metadata first (sources)
        yield json.dumps({"type": "metadata", "sources": sources}) + "\n"
        
        # Generate answer using LLM stream
        for chunk in llm_service.generate_answer_stream(question, context, history):
            yield json.dumps({"type": "content", "content": chunk}) + "\n"

    def _retrieve_context(self, question: str, n_results: int = 5, additional_context: str = "", conversation_id: str = None):
        # 1. Embed the query
        query_embedding = embedding_service.get_embedding(question)
        
        # 2. Search in session context store FIRST
        session_texts = []
        session_sources = []
        if conversation_id:
            import numpy as np
            session_docs = llm_service.get_session_context(conversation_id)
            session_matches = []
            
            for doc in session_docs:
                chunks = doc["chunks"]
                embeddings = doc["embeddings"]
                meta = doc.get("metadata", [])
                
                for i, emb in enumerate(embeddings):
                    # Cosine similarity
                    similarity = np.dot(emb, query_embedding) / (np.linalg.norm(emb) * np.linalg.norm(query_embedding))
                    session_matches.append({
                        "text": chunks[i],
                        "similarity": similarity,
                        "metadata": meta[i] if i < len(meta) else None
                    })
            
            session_matches.sort(key=lambda x: x["similarity"], reverse=True)
            # Take top relevant chunks from session
            for match in session_matches[:5]:
                if match["similarity"] > 0.4:
                    session_texts.append(f"[CURRENT SESSION FILE CONTEXT]\n{match['text']}")
                    if match["metadata"]:
                        session_sources.append({
                            "filename": match["metadata"]["filename"],
                            "rel_path": match["metadata"]["filename"],
                            "page": match["metadata"]["page"],
                            "bbox": match["metadata"]["bbox"]
                        })

        # 3. Search for similar chunks in Global Vector DB
        collection = vector_service.get_collection()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        global_texts = []
        global_sources = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i]
                global_texts.append(f"[GLOBAL KNOWLEDGE BASE]\n{metadata['text']}")
                global_sources.append({
                    "filename": metadata['filename'],
                    "rel_path": metadata.get('rel_path', metadata['filename']),
                    "page": metadata['page'],
                    "bbox": json.loads(metadata['bbox'])
                })
        
        # 4. Filter and Combine
        query_lower = question.lower()
        # If user is asking about "this file" or similar, we ONLY use session context and session sources
        if any(keyword in query_lower for keyword in ["this file", "attached", "uploaded", "profile", "resume", "candidate"]):
            if session_texts:
                retrieved_texts = session_texts
                sources = session_sources
            else:
                retrieved_texts = session_texts + global_texts
                sources = session_sources + global_sources
        else:
            retrieved_texts = session_texts + global_texts
            sources = session_sources + global_sources
            
        context = "\n---\n".join(retrieved_texts)
        if additional_context:
            context += f"\n\n[RAW FILE CONTEXT]:\n{additional_context}"
        
        return context, sources

rag_pipeline = RAGPipeline()
