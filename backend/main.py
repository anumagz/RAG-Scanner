from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.database import Base, engine

# Import models so SQLAlchemy registers all tables
from models.repository import Repository
from models.file import File
from models.summary import (
    RepositorySummary,
    FileSummary,
)

# API routers
from api.repositories import router as repository_router
from api.files import router as file_router
from api.repository_files import router as repository_files_router
from api.summaries import router as summary_router
from api.chat import router as chat_router
from api.code import router as code_router


# Create database tables
Base.metadata.create_all(bind=engine)


# Create FastAPI application
app = FastAPI(
    title="AI Repository Scanner",
    version="1.0.0",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(repository_router)
app.include_router(file_router)
app.include_router(repository_files_router)
app.include_router(summary_router)
app.include_router(chat_router)
app.include_router(code_router)


# Root endpoint
@app.get("/")
def root():
    return {
        "message": "AI Repository Scanner API",
    }


# Health check endpoint
@app.get("/health")
def health():
    return {
        "status": "ok",
    }