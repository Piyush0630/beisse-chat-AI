from .services.vector_service import vector_service

def verify_vector_db():
    print("Verifying Vector DB...")
    collection = vector_service.get_collection()
    print(f"Collection '{collection.name}' is ready.")
    print(f"Current document count: {collection.count()}")

if __name__ == "__main__":
    verify_vector_db()
