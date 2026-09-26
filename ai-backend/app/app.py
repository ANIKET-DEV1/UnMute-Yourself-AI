"""FastAPI Application Entry Point for AI Backend."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.core.config import settings
from app.api.gd_socket import gd
from app.api.interview_socket import interview_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-time Multi-Agent AI & Speech Backend for GD, Debate & Interview",
    version=settings.VERSION
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(gd)
app.include_router(interview_router)

# Serve Static HTML & Avatars (Frontend)
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "html"))

if os.path.exists(os.path.join(frontend_dir, "avatars")):
    app.mount("/avatars", StaticFiles(directory=os.path.join(frontend_dir, "avatars")), name="avatars")

@app.get("/")
def read_root():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "ws_endpoints": ["/gd/ws/{room_id}", "/interview/ws/{room_id}"]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "ollama_model": settings.OLLAMA_MODEL
    }