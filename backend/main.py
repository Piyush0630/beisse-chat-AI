from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import get_db, engine
from . import models
from .services.vector_service import vector_service

# Initialize tables (redundant but safe)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Biesse Chat Assistant API")

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    # Check Database
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    # Check Vector DB
    vdb_status = "ok"
    try:
        count = vector_service.get_collection().count()
    except Exception as e:
        vdb_status = f"error: {str(e)}"
        
    return {
        "status": "online",
        "database": db_status,
        "vector_db": vdb_status,
        "vector_count": count if vdb_status == "ok" else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
