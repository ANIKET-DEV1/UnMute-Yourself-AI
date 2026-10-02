"""WebSocket Route Handler for 1v1 AI Debate Arena."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from app.services.debate_service import get_or_create_debate_session

debate_router = APIRouter(prefix="/debate")

@debate_router.websocket("/ws/{room_id}")
@debate_router.websocket("/{room_id}")
async def debate_1v1_ws(websocket: WebSocket, room_id: str):
    await websocket.accept()

    topic = websocket.query_params.get("topic", "Universal Basic Income vs Job Guarantees")
    session = get_or_create_debate_session(room_id=room_id, topic=topic)

    # 1. Connection Acknowledgment
    await websocket.send_json({
        "event": "CONNECTED",
        "sender": "System",
        "message": f"Successfully connected to 1v1 Debate Room: {room_id}",
        "topic": topic
    })

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                data = {"event": "USER_SPEECH", "text": raw_data}

            event_type = data.get("event", "USER_SPEECH")

            if event_type == "PING":
                await websocket.send_json({"event": "PONG"})
                continue

            elif event_type == "START_DEBATE":
                opening_turn = await session.generate_opening_turn()
                await websocket.send_json({
                    "event": "AGENT_SPEAKING",
                    "sender": opening_turn["speaker"],
                    "text": opening_turn["text"],
                    "phase": opening_turn["phase"],
                    "audio": opening_turn["audio"],
                    "turnState": opening_turn["turnState"]
                })

            elif event_type in ["USER_SPEECH", "USER_ANSWER", "USER_REBUTTAL"]:
                user_text = data.get("text", "").strip()
                filler_count = data.get("filler_count", 0)
                if not user_text:
                    continue

                await websocket.send_json({
                    "event": "USER_SPEECH_ACK",
                    "message": "User rebuttal recorded. Adversary is formulating counter-argument..."
                })

                rebuttal_turn = await session.handle_user_rebuttal(user_text, filler_count=filler_count)
                await websocket.send_json({
                    "event": "AGENT_SPEAKING",
                    "sender": rebuttal_turn["speaker"],
                    "text": rebuttal_turn["text"],
                    "phase": rebuttal_turn["phase"],
                    "audio": rebuttal_turn["audio"],
                    "turnState": rebuttal_turn["turnState"]
                })

            elif event_type in ["END_DEBATE", "END_SESSION"]:
                await websocket.send_json({
                    "event": "AGENT_SPEAKING",
                    "sender": "System",
                    "text": "Evaluating your debate logic, rebuttal effectiveness, and overall performance...",
                    "turnState": "EVALUATING"
                })
                scorecard = await session.evaluate_debate()
                await websocket.send_json({
                    "event": "SESSION_COMPLETED",
                    "sender": "System",
                    "message": "1v1 Debate session completed.",
                    "scorecard": scorecard
                })
                break

    except WebSocketDisconnect:
        print(f"[WebSocket] Debater disconnected from room: {room_id}")
    except Exception as e:
        print(f"[WebSocket Error] Debate room {room_id}: {e}")
