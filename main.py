import sys
import os

# Ensure ai-backend is discoverable in Python's module path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "ai-backend"))


if __name__ == "__main__":
    import uvicorn
    print("[INFO] Starting UnMute-Yourself AI Backend on http://127.0.0.1:8000")
    print("[INFO] WebSocket GD Endpoint: ws://127.0.0.1:8000/gd/ws/{room_id}")
    uvicorn.run("app.app:app", host="127.0.0.1", port=8000, reload=True)