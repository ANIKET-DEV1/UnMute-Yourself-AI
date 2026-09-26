"""REST and WebSocket API Handlers for 1-on-1 AI Mock Interview."""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File, Form
import json
import asyncio
from app.services.resume_service import parse_candidate_resume
from app.services.interview_service import get_or_create_interview_session

interview_router = APIRouter(prefix="/interview")

@interview_router.post("/upload-resume")
async def upload_and_parse_resume(
    resume_file: UploadFile = File(...),
    target_role: str = Form("Frontend Developer"),
    language: str = Form("English")
):
    """
    Endpoint to upload and extract candidate details from resume PDF/TXT.
    If parsing fails or file is empty, prompts the client to re-upload.
    """
    try:
        file_bytes = await resume_file.read()
        filename = resume_file.filename or "resume.pdf"
        
        result = await parse_candidate_resume(
            file_bytes=file_bytes,
            filename=filename,
            target_role=target_role
        )
        return result
    except Exception as e:
        print(f"[Resume Upload Error] {e}")
        return {
            "success": False,
            "error": f"Failed to parse resume: {str(e)}. Please upload a valid PDF or TXT file."
        }

@interview_router.websocket("/ws/{room_id}")
async def mock_interview_ws(websocket: WebSocket, room_id: str):
    """WebSocket connection handler for live 15-20 min 1-on-1 interview session."""
    await websocket.accept()

    role = websocket.query_params.get("role", "Frontend Developer")
    language = websocket.query_params.get("language", "English")

    session = get_or_create_interview_session(
        room_id=room_id,
        target_role=role,
        language=language
    )

    # 1. Connection acknowledgment
    await websocket.send_json({
        "event": "CONNECTED",
        "sender": "System",
        "message": f"Connected to 1-on-1 Mock Interview Room: {room_id}",
        "role": role,
        "language": language
    })

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                data = {"event": "USER_ANSWER", "text": raw_data}

            event_type = data.get("event", "USER_ANSWER")

            if event_type == "PING":
                await websocket.send_json({"event": "PONG"})
                continue

            # Stage: Configure Resume Context
            elif event_type == "INIT_INTERVIEW":
                resume_payload = data.get("resumeData", {})
                session.resume = session.resume.model_copy(update=resume_payload)
                
                # Send the opening greeting and first question
                opening_turn = await session.generate_opening_turn()
                await websocket.send_json({
                    "event": "INTERVIEWER_SPEAKING",
                    "sender": opening_turn["speaker"],
                    "text": opening_turn["text"],
                    "phase": opening_turn["phase"],
                    "audio": opening_turn["audio"],
                    "turnState": opening_turn["turnState"],
                    "questionNumber": opening_turn["questionNumber"]
                })

            # Stage: Candidate Answer
            elif event_type == "USER_ANSWER" or event_type == "USER_SPEECH":
                user_answer = data.get("text", "").strip()
                filler_count = data.get("filler_count", 0)
                if not user_answer:
                    continue

                await websocket.send_json({
                    "event": "USER_ANSWER_ACK",
                    "message": "Answer recorded. Interviewer is analyzing..."
                })

                interviewer_turn = await session.handle_candidate_answer(
                    user_answer=user_answer,
                    filler_count=filler_count
                )

                await websocket.send_json({
                    "event": "INTERVIEWER_SPEAKING",
                    "sender": interviewer_turn["speaker"],
                    "text": interviewer_turn["text"],
                    "phase": interviewer_turn["phase"],
                    "audio": interviewer_turn.get("audio", ""),
                    "turnState": interviewer_turn["turnState"],
                    "questionNumber": interviewer_turn["questionNumber"],
                    "feedbackTip": interviewer_turn.get("feedbackTip", "")
                })

            # Stage: End & Evaluate Interview
            elif event_type == "END_INTERVIEW" or event_type == "END_SESSION":
                await websocket.send_json({
                    "event": "INTERVIEWER_SPEAKING",
                    "sender": "System",
                    "text": "Evaluating your technical interview, STAR methodology, and hiring scorecard...",
                    "turnState": "EVALUATING"
                })
                scorecard = await session.evaluate_interview()
                await websocket.send_json({
                    "event": "INTERVIEW_COMPLETED",
                    "sender": "System",
                    "message": "Technical Mock Interview completed.",
                    "scorecard": scorecard
                })
                break

    except WebSocketDisconnect:
        print(f"[WebSocket] Candidate disconnected from interview room: {room_id}")
    except Exception as e:
        print(f"[WebSocket Error] Exception in interview room {room_id}: {e}")
