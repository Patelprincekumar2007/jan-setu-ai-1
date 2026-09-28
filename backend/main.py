from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database import init_db, SessionLocal
from backend.routes.requests import router as requests_router
from backend.public_data.routes import router as public_data_router
from backend.public_data.service import PublicDataService
from backend.knowledge.routes import router as knowledge_router
from backend.knowledge.service import KnowledgeService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and tables on application startup
    init_db()
    
    # Auto-seed verified baseline public datasets & knowledge evidence
    db = SessionLocal()
    try:
        PublicDataService.seed_default_datasets(db)
        KnowledgeService.seed_default_knowledge(db)
    finally:
        db.close()
        
    yield

app = FastAPI(
    title="NagrikLens AI API",
    description="Multilingual Citizen Development Intelligence Platform API",
    version="0.2.0",
    lifespan=lifespan,
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(requests_router)
app.include_router(public_data_router)
app.include_router(knowledge_router)

@app.get("/health")
def get_health():
    """Basic health check endpoint for monitoring service readiness."""
    return {
        "status": "ok",
        "service": "nagriklens-ai-api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=True)
