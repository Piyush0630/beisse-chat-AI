import os
import sys

# Add the parent directory to sys.path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.vector_service import vector_service

def reset_vector_db():
    print("Resetting vector database...")
    try:
        # Delete the collection
        vector_service.client.delete_collection(vector_service.collection_name)
        print(f"Collection '{vector_service.collection_name}' deleted.")
        
        # Re-initialize vector service to recreate the collection
        vector_service.__init__()
        print(f"Collection '{vector_service.collection_name}' recreated.")
        print("Vector database reset successfully.")
    except Exception as e:
        print(f"Error resetting vector database: {e}")

if __name__ == "__main__":
    reset_vector_db()
