from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .api.gd_socket import gd

app = FastAPI(
    title="UnMute-Yourself AI Backend",
    description="Real-time WebSocket & AI Services for Virtual Group Discussion",
    version="1.0.0"
)

# Enable CORS for frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include WebSocket Routers
app.include_router(gd)

# Serve Frontend Static Assets & Web Page
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
        "service": "UnMute-Yourself AI Backend",
        "ws_endpoints": ["/gd/ws/{room_id}"]
    }

@app.get("/room")
def read_room():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"error": "Room template not found"}