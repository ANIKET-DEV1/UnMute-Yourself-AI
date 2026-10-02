"""FastAPI Application Entry Point for AI Backend."""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.core.config import settings
from app.api.gd_socket import gd, group_discussion_ws
from app.api.interview_socket import interview_router, mock_interview_ws
from app.api.debate_socket import debate_router, debate_1v1_ws

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

# Register Routers
app.include_router(gd)
app.include_router(interview_router)
app.include_router(debate_router)

# Direct top-level WebSocket alias routes matching README specifications
@app.websocket("/ws/gd/{room_id}")
async def ws_gd_alias(websocket: WebSocket, room_id: str):
    await group_discussion_ws(websocket, room_id)

@app.websocket("/ws/debate/{room_id}")
async def ws_debate_alias(websocket: WebSocket, room_id: str):
    await debate_1v1_ws(websocket, room_id)

@app.websocket("/ws/interview/{room_id}")
async def ws_interview_alias(websocket: WebSocket, room_id: str):
    await mock_interview_ws(websocket, room_id)

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

@app.get("/login.html")
@app.get("/login")
def serve_login():
    login_file = os.path.join(frontend_dir, "login.html")
    if os.path.exists(login_file):
        return FileResponse(login_file)
    return {"error": "login.html not found"}

@app.get("/register.html")
@app.get("/register")
def serve_register():
    register_file = os.path.join(frontend_dir, "register.html")
    if os.path.exists(register_file):
        return FileResponse(register_file)
    return {"error": "register.html not found"}

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