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

# Direct HTML page routes
@app.get("/")
@app.get("/index.html")
def serve_index():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"status": "online", "service": settings.PROJECT_NAME}

@app.get("/interview.html")
@app.get("/mock-interview")
def serve_interview():
    interview_file = os.path.join(frontend_dir, "interview.html")
    if os.path.exists(interview_file):
        return FileResponse(interview_file)
    return {"error": "interview.html not found"}

@app.get("/gd.html")
@app.get("/gd-room")
def serve_gd():
    gd_file = os.path.join(frontend_dir, "gd.html")
    if os.path.exists(gd_file):
        return FileResponse(gd_file)
    return {"error": "gd.html not found"}

@app.get("/debate.html")
@app.get("/debate-room")
def serve_debate():
    debate_file = os.path.join(frontend_dir, "debate.html")
    if os.path.exists(debate_file):
        return FileResponse(debate_file)
    return {"error": "debate.html not found"}

@app.get("/test_gd_websocket.html")
def serve_test_gd():
    test_file = os.path.join(frontend_dir, "test_gd_websocket.html")
    if os.path.exists(test_file):
        return FileResponse(test_file)
    return {"error": "test_gd_websocket.html not found"}

# Mount frontend directory as static fallback
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "llm_provider": settings.LLM_PROVIDER,
        "ollama_model": settings.OLLAMA_MODEL
    }