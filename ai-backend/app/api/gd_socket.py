from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio
from app.services.llm_service import get_or_create_room, generate_neural_audio_b64

gd = APIRouter(prefix="/gd")

@gd.websocket("/ws/{room_id}")
async def group_discussion_ws(websocket: WebSocket, room_id: str):
    await websocket.accept()

    topic = websocket.query_params.get("topic", "Will AI Replace Software Engineers?")
    session = get_or_create_room(room_id, topic=topic)

    await websocket.send_json({
        "event": "CONNECTED",
        "sender": "System",
        "message": f"Successfully joined Group Discussion room: {room_id}",
        "roomId": room_id
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

            elif event_type == "START_INTRODUCTIONS":
                # Stream the 4 persona member introductions
                intro_turns = await session.generate_introductions_list()
                for turn in intro_turns:
                    await websocket.send_json({
                        "event": "AGENT_SPEAKING",
                        "sender": turn["speaker"],
                        "text": turn["text"],
                        "audio": turn["audio"],
                        "turnState": turn["turnState"]
                    })
                    await asyncio.sleep(0.5)

            elif event_type == "END_SESSION":
                await websocket.send_json({
                    "event": "AGENT_SPEAKING",
                    "sender": "System",
                    "text": "Evaluating your GD performance, speech delivery, winner candidate, and weak points...",
                    "turnState": "EVALUATING"
                })
                scorecard = await session.evaluate_session()
                await websocket.send_json({
                    "event": "SESSION_COMPLETED",
                    "sender": "System",
                    "message": "Group Discussion session completed.",
                    "scorecard": scorecard
                })
                break

            elif event_type == "USER_SPEECH":
                user_text = data.get("text", "").strip()
                filler_count = data.get("filler_count", 0)
                if not user_text:
                    continue

                session.record_user_speech(user_text, filler_count=filler_count)

                await websocket.send_json({
                    "event": "USER_SPEECH_ACK",
                    "message": "User speech recorded. AI participants are debating..."
                })

                # Stream 2 AI agent turns with realistic neural speech audio:
                num_turns = 2
                for i in range(num_turns):
                    ai_response = await session.generate_next_agent_turn()
                    is_last = (i == num_turns - 1)

                    await websocket.send_json({
                        "event": "AGENT_SPEAKING",
                        "sender": ai_response["speaker"],
                        "text": ai_response["text"],
                        "audio": ai_response.get("audio", ""),
                        "turnState": "USER_TURN" if is_last else "AGENT_TURN"
                    })

                    if not is_last:
                        await asyncio.sleep(0.5)

            else:
                user_text = data.get("text") or str(data)
                filler_count = data.get("filler_count", 0) if isinstance(data, dict) else 0
                if user_text:
                    session.record_user_speech(user_text, filler_count=filler_count)
                    for i in range(2):
                        ai_response = await session.generate_next_agent_turn()
                        is_last = (i == 1)
                        await websocket.send_json({
                            "event": "AGENT_SPEAKING",
                            "sender": ai_response["speaker"],
                            "text": ai_response["text"],
                            "audio": ai_response.get("audio", ""),
                            "turnState": "USER_TURN" if is_last else "AGENT_TURN"
                        })
                        if not is_last:
                            await asyncio.sleep(0.5)

    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected from GD room: {room_id}")
    except Exception as e:
        print(f"[WebSocket Error] Exception in GD room {room_id}: {e}")