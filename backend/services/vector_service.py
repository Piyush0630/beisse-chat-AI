"""
Vector Database Service using ChromaDB

Manages document embeddings and similarity search.
"""

import chromadb
from chromadb.config import Settings
from chromadb.errors import InvalidCollectionException
from typing import List, Dict, Optional, Tuple
import os
import logging

logger = logging.getLogger(__name__)


class VectorService:
    """Manages ChromaDB operations for document retrieval"""
    
    def __init__(
        self,
        persist_directory: str = "./data/chromadb",
        collection_name_prefix: str = "biesse_"
    ):
        self.persist_directory = persist_directory
        self.collection_name_prefix = collection_name_prefix
        self._collections: Dict[str, chromadb.Collection] = {}
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        logger.info(f"VectorService initialized with persist_directory: {persist_directory}")
    
    def _get_collection_name(self, category: str) -> str:
        """Get full collection name with prefix"""
        return f"{self.collection_name_prefix}{category}"
    
    def get_collection(self, category: str) -> chromadb.Collection:
        """Get or create a collection for a category"""
        collection_name = self._get_collection_name(category)
        
        if collection_name in self._collections:
            return self._collections[collection_name]
        
        try:
            collection = self.client.get_collection(name=collection_name)
        except InvalidCollectionException:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={
                    "description": f"Biesse {category} documentation",
                    "category": category,
                    "created_at": str(__import__('datetime').datetime.utcnow().isoformat())
                }
            )
        
        self._collections[collection_name] = collection
        return collection
    
    def add_documents(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: List[str],
        category: str
    ) -> int:
        """
        Add document chunks to the vector database
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique chunk IDs
            category: Document category
            
        Returns:
            Number of documents added
        """
        if not documents:
            logger.warning(f"No documents to add for category: {category}")
            return 0
        
        collection = self.get_collection(category)
        
        # Add to ChromaDB
        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"Added {len(documents)} chunks to {category} collection")
        return len(documents)
    
    def add_batch(
        self,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
        ids: List[str],
        category: str,
        batch_size: int = 100
    ) -> int:
        """
        Add documents in batches to avoid memory issues
        
        Args:
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries
            ids: List of unique chunk IDs
            category: Document category
            batch_size: Size of each batch
            
        Returns:
            Total number of documents added
        """
        total_added = 0
        
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_embs = embeddings[i:i + batch_size]
            batch_metas = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            
            added = self.add_documents(
                documents=batch_docs,
                embeddings=batch_embs,
                metadatas=batch_metas,
                ids=batch_ids,
                category=category
            )
            total_added += added
        
        return total_added
    
    def search(
        self,
        query_embedding: List[float],
        category: str,
        n_results: int = 10,
        similarity_threshold: float = 0.7,
        where_clause: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query_embedding: Query embedding vector
            category: Document category to search
            n_results: Number of results to return
            similarity_threshold: Minimum similarity score
            where_clause: Optional metadata filter
            
        Returns:
            List of search results with text, metadata, and scores
        """
        collection = self.get_collection(category)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where_clause,
            include=["documents", "metadatas", "distances", "embeddings"]
        )
        
        # Process and filter results
        processed_results = []
        
        for idx, (doc, metadata, distance, embedding) in enumerate(zip(
            results.get("documents", [[]])[0],
            results.get("metadatas", [[]])[0],
            results.get("distances", [[]])[0],
            results.get("embeddings", [[]])[0]
        )):
            # Convert distance to similarity (ChromaDB uses cosine distance)
            similarity = self._distance_to_similarity(distance)
            
            if similarity >= similarity_threshold:
                processed_results.append({
                    "id": results["ids"][0][idx] if results.get("ids") else f"result_{idx}",
                    "text": doc,
                    "metadata": metadata or {},
                    "embedding": embedding,
                    "distance": distance,
                    "similarity": similarity
                })
        
        # Sort by similarity
        processed_results.sort(key=lambda x: x["similarity"], reverse=True)
        
        logger.info(f"Search in {category} returned {len(processed_results)} results above threshold")
        return processed_results
    
    def search_all_categories(
        self,
        query_embedding: List[float],
        n_results_per_category: int = 5,
        similarity_threshold: float = 0.7
    ) -> Dict[str, List[Dict]]:
        """
        Search across all available categories
        
        Args:
            query_embedding: Query embedding vector
            n_results_per_category: Results per category
            similarity_threshold: Minimum similarity score
            
        Returns:
            Dictionary of category -> list of results
        """
        categories = self.list_categories()
        all_results = {}
        
        for category in categories:
            results = self.search(
                query_embedding=query_embedding,
                category=category,
                n_results=n_results_per_category,
                similarity_threshold=similarity_threshold
            )
            if results:
                all_results[category] = results
        
        return all_results
    
    def get_document(self, document_id: str, category: str) -> Optional[Dict]:
        """Get a specific document by ID"""
        collection = self.get_collection(category)
        
        results = collection.get(
            ids=[document_id],
            include=["documents", "metadatas"]
        )
        
        if results["documents"]:
            return {
                "id": document_id,
                "document": results["documents"][0],
                "metadata": results["metadatas"][0] if results["metadatas"] else {}
            }
        return None
    
    def get_by_metadata(
        self,
        category: str,
        key: str,
        value: str
    ) -> List[Dict]:
        """Get documents by metadata"""
        collection = self.get_collection(category)
        
        results = collection.get(
            where={key: value},
            include=["documents", "metadatas"]
        )
        
        documents = []
        for idx, doc in enumerate(results.get("documents", [])):
            documents.append({
                "id": results["ids"][idx] if results.get("ids") else None,
                "document": doc,
                "metadata": results["metadatas"][idx] if results.get("metadatas") else {}
            })
        
        return documents
    
    def count_documents(self, category: str) -> int:
        """Count documents in a category"""
        try:
            collection = self.get_collection(category)
            return collection.count()
        except Exception as e:
            logger.error(f"Error counting documents in {category}: {e}")
            return 0
    
    def delete_document(self, document_id: str, category: str) -> bool:
        """Delete a document from a category"""
        try:
            collection = self.get_collection(category)
            collection.delete(ids=[document_id])
            logger.info(f"Deleted document {document_id} from {category}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    def delete_collection(self, category: str) -> bool:
        """Delete an entire category collection"""
        collection_name = self._get_collection_name(category)
        
        try:
            if collection_name in self._collections:
                del self._collections[collection_name]
            
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {category}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {category}: {e}")
            return False
    
    def list_categories(self) -> List[str]:
        """List all available category collections"""
        collections = self.client.list_collections()
        
        categories = []
        for collection in collections:
            name = collection.name
            if name.startswith(self.collection_name_prefix):
                category = name.replace(self.collection_name_prefix, "")
                categories.append(category)
        
        return categories
    
    def list_all_documents(self, category: str, limit: int = 100) -> List[Dict]:
        """List documents in a category"""
        collection = self.get_collection(category)
        
        results = collection.get(
            include=["documents", "metadatas"],
            limit=limit
        )
        
        documents = []
        for idx, doc in enumerate(results.get("documents", [])):
            documents.append({
                "id": results["ids"][idx] if results.get("ids") else None,
                "document": doc,
                "metadata": results["metadatas"][idx] if results.get("metadatas") else {}
            })
        
        return documents
    
    def reset(self):
        """Reset the vector database (deletes all data)"""
        self.client.reset()
        self._collections.clear()
        logger.warning("Vector database reset - all data deleted")
    
    def get_collection_info(self, category: str) -> Dict:
        """Get information about a collection"""
        collection = self.get_collection(category)
        
        return {
            "name": collection.name,
            "count": collection.count(),
            "metadata": collection.metadata
        }
    
    def _distance_to_similarity(self, distance: float) -> float:
        """Convert ChromaDB cosine distance to similarity score"""
        # Cosine distance ranges from 0 (identical) to 2 (opposite)
        # Convert to similarity: 1 - (distance / 2)
        # This gives range [0, 1] where 1 is identical
        return max(0.0, 1.0 - (distance / 2.0))


def create_vector_service(
    persist_directory: str = "./data/chromadb",
    collection_name_prefix: str = "biesse_"
) -> VectorService:
    """Factory function to create VectorService"""
    return VectorService(
        persist_directory=persist_directory,
        collection_name_prefix=collection_name_prefix
    )
