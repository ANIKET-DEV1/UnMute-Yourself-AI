# 🎙️ UnMute-Yourself AI
> **An intelligent, real-time multi-agent communication training platform for Group Discussions (GD), Debates, and Mock Interviews.**

---

## 📌 1. Project Overview & Vision

**UnMute-Yourself AI** is built to help students and professionals conquer public speaking anxiety and master verbal communication. The platform simulates realistic 15–20 minute interactive voice-and-text sessions with AI personas:
- **Group Discussion (GD):** A live room featuring 1 User, 2–3 diverse AI peers (the Analyst, the Contrarian, the Peacemaker), and 1 AI Moderator steering the debate.
- **1-on-1 AI Debate:** A structured debate arena where the AI takes the opposing stance, challenges logical fallacies, and delivers rebuttals.
- **Adaptive Mock Interview:** Dynamic domain-specific or HR interviews that ask contextual follow-up questions and grade answers using the STAR framework.
- **Comprehensive Post-Session Analytics:** Instant feedback on filler words (*um, like, actually*), speaking pace (WPM), confidence, clarity, argument strength, and vocabulary.

---

## 🏗️ 2. High-Level Architecture (HLD)

The system operates on a decoupled **Two-Backend Architecture**:

```text
+-----------------------------------------------------------------------------------------------+
|                                    FRONTEND (React / Vite)                                    |
|   - User Dashboard & Rooms        - Audio Capture (MediaRecorder)      - Live WebSocket UI   |
+-----------------------------------------------+-----------------------------------------------+
                        |                       |                       ^
                        | 1. Auth, Profile,     | 2. Create Session     | 3. Live 15-20 Min WS
                        |    History (REST)     |    (Get Token)        |    Audio & Text Stream
                        v                       v                       v
+-----------------------------------------------+     +-----------------------------------------+
|          NODE.JS BACKEND (Port 5000)          |     |      PYTHON AI BACKEND (FastAPI : 8000) |
|                                               |     |                                         |
|  [ Auth & JWT Controller ]                    |     |  [ WebSocket Room Manager ]             |
|  [ User Profile & Streak Tracker ]            |     |  [ Multi-Agent GD Orchestrator ]        |
|  [ Session Lifecycle Manager ]                |     |  [ Debate & Rebuttal Engine ]           |
|                                               |     |  [ Adaptive Interviewer Engine ]        |
|  +-----------------------------------------+  |     |  [ STT Whisper & TTS Engine ]           |
|  | Database: MongoDB / PostgreSQL          |  |     |  [ Scoring & Analytics Engine ]         |
|  +-----------------------------------------+  |     +--------------------+--------------------+
|                       ^                       |                          |
|                       | 4. Push Final Report  |                          |
|                       +-----------------------+--------------------------+
+-----------------------------------------------+
                                                                           |
                                                                           v
                                                              +-------------------------+
                                                              |    LLM & Speech Cloud   |
                                                              | (Gemini 2.0 Flash/Groq) |
                                                              +-------------------------+
```

---

## 🔄 3. Detailed Session Lifecycle & Python Handoff Flow

Understanding how a practice room starts, runs, and wraps up between **Node.js** and **Python FastAPI**:

```text
[ FRONTEND (React) ]                      [ NODE.JS BACKEND ]                [ PYTHON FASTAPI (AI) ]
         |                                         |                                    |
         | -- 1. POST /api/sessions/create ------> |                                    |
         |    (Headers: JWT, Body: mode, topic)    |                                    |
         |                                         | -- 2. Auth Check & Insert Doc      |
         |                                         |    Status: "IN_PROGRESS"           |
         | <--- 3. Returns { sessionId: "sess_123"}|                                    |
         |                                                                              |
         | ========================= HANDOFF TO PYTHON ================================ |
         |                                                                              |
         | -- 4. Connect WebSocket: ws://localhost:8000/ws/gd/sess_123 ---------------> |
         |                                                                              |
         |                                                                   5. Accepts connection
         |                                                                      Spawns AI Personas
         |                                                                      Starts Session Timer
         |                                                                              |
         | <--- 6. Moderator AI: "Welcome! Today's topic is..." ----------------------- |
         |                                                                              |
         | ================= LIVE 15-20 MIN SPEECH/AUDIO LOOP ========================== |
         |                                                                              |
         | -- 7. User Speech Chunks / Transcripts ------------------------------------> |
         | <--- 8. AI Agent Audio & Text Responses ------------------------------------ |
         |                                                                              |
         | ================= SESSION COMPLETION & EVALUATION =========================== |
         |                                                                              |
         |                                                                   9. Runs Evaluator LLM
         |                                         | <--- 10. POST /api/internal/... ---|
         |                                         |     (Pushes final report)          |
         |                                         |     (Status: "COMPLETED")          |
         | <--- 11. WS returns Final Scorecard JSON ------------------------------------|
```

### ⚙️ Step-by-Step Breakdown

#### Phase 1: Session Initialization (Node.js)
1. **User clicks "Start Practice"**: Frontend sends `POST /api/sessions/create` to Node.js with the user's JWT.
2. **Node.js Verifies User**: Validates JWT, verifies user quotas/streaks.
3. **Generates `sessionId`**: Creates a unique ID (e.g. `sess_987654`).
4. **Inserts Initial DB Document**: Saves session record with status `"IN_PROGRESS"` in MongoDB/PostgreSQL:
   ```json
   {
     "_id": "sess_987654",
     "userId": "usr_101",
     "mode": "GROUP_DISCUSSION",
     "topic": "Will AI Replace Software Engineers?",
     "durationMinutes": 20,
     "status": "IN_PROGRESS",
     "startedAt": "2026-09-22T21:05:00Z",
     "transcript": [],
     "report": null
   }
   ```
5. **Returns Credentials**: Node.js sends back `{ sessionId, topic, wsUrl }`.

#### Phase 2: Python Connection Establishment (FastAPI WebSocket)
1. **Frontend opens WebSocket directly to Python**:
   ```javascript
   const ws = new WebSocket(`ws://localhost:8000/ws/gd/${sessionId}`);
   ```
2. **FastAPI accepts handshake**:
   ```python
   @app.websocket("/ws/gd/{session_id}")
   async def gd_room(websocket: WebSocket, session_id: str):
       await websocket.accept()
       # In-memory session state
       active_rooms[session_id] = { "transcript": [], "start_time": time.time() }
   ```
3. **Moderator Intro**: Python AI initiates the room by sending the Moderator's opening speech (audio + text).

#### Phase 3: Active Session (15–20 Min Speech Loop)
* User speaks $\rightarrow$ Speech-to-Text (STT) converts audio to text.
* Turn manager orchestrates which AI agent speaks next (Analyst vs Contrarian vs Moderator).
* Text-to-Speech (TTS) streams agent voice back to the frontend.
* Lightweight ping/pong packets every 15s ensure the WebSocket never drops.

#### Phase 4: Session Wrap-up & Scoring
* At timer expiry (or user ends session), Python's Evaluator Engine computes scores (Clarity, Confidence, Grammar, Fillers, Rebuttal quality).
* Python saves the report by calling Node.js: `POST /api/internal/sessions/{sessionId}/report`.
* Node.js updates the MongoDB document status to `"COMPLETED"` and saves the final analytics.
* Frontend receives the scorecard and redirects to the detailed Performance Report page.

---

## 👥 4. Team Division & Required Skillsets

### 🅰️ Python AI Backend (Lead: AI Engineer)
* **Core Responsibilities:**
  * Real-time WebSocket connection handling for 15–20 min active sessions.
  * Multi-agent conversation state machines (Turn-taking, interruptions, silence detection).
  * Prompt engineering for distinct AI personas (Moderator, Contrarian, Analyst).
  * Speech-to-Text (STT) & Text-to-Speech (TTS) integration.
  * Evaluation engine for communication analytics (WPM, fillers, clarity, sentiment).
* **Skills Required:**
  * Python 3.10+, FastAPI, `asyncio`, WebSockets.
  * LLM APIs (Google Gemini 2.0 Flash / OpenAI / Groq Llama-3).
  * Speech tooling (Faster-Whisper, Deepgram, Edge-TTS, or Web Speech API).
  * Prompt Engineering, Structured JSON parsing (Pydantic).

---

### 🅱️ Node.js Backend (Lead: Backend Engineer)
* **Core Responsibilities:**
  * Authentication (JWT, bcrypt, password hashing, session tokens).
  * Database schema design (Users, Sessions, Scorecards, Streaks).
  * CRUD APIs for dashboards, user history, and leaderboard/progress graphs.
  * Internal API endpoint to receive and verify final evaluation reports from the AI backend.
* **Skills Required:**
  * Node.js, Express.js (or NestJS).
  * Database (MongoDB with Mongoose OR PostgreSQL with Prisma/TypeORM).
  * JWT Auth middleware, Input Validation (Joi/Zod), CORS handling.
  * REST API best practices.

---

### 🅲 Frontend (Lead: Frontend Engineer)
* **Core Responsibilities:**
  * Modern, responsive UI with smooth animations, mic visualizers, and dark mode.
  * Audio recording and playback using the Web Audio API / `MediaRecorder`.
  * Persistent WebSocket client management with auto-reconnect and keep-alive pinging.
  * Post-session analytics dashboard with graphs (Radar charts, timeline breakdown).
* **Skills Required:**
  * React.js (Vite), JavaScript / TypeScript, TailwindCSS / CSS Modules.
  * WebSocket handling & audio streaming in the browser.
  * Charting libraries (Recharts / Chart.js) and Icon sets (Lucide-react).

---

## 🔌 5. Detailed API Specifications

### 🟢 Node.js REST APIs (`http://localhost:5000`)

#### 1. Authentication & Profile
| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/register` | Register a new user | `{ name, email, password }` | `{ user, token }` |
| `POST` | `/api/auth/login` | Login existing user | `{ email, password }` | `{ user, token }` |
| `GET` | `/api/auth/me` | Fetch active user profile | *Bearer Token Header* | `{ userProfile, stats }` |

#### 2. Session Management
| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/sessions/create` | Initialize a new session | `{ userId, mode, topic, durationMins }` | `{ sessionId, sessionToken, topic, expiresAt }` |
| `GET` | `/api/sessions/:id` | Get single session details | None | `{ session, transcript, report }` |
| `GET` | `/api/sessions/user/:userId` | Get past session history | None | `[{ sessionId, mode, score, date }]` |

#### 3. Internal AI Callback
| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/internal/sessions/:id/report` | AI Backend pushes final evaluation report | Detailed Metrics JSON (see below) | `{ status: "SAVED" }` |

---

### 🟣 Python FastAPI Endpoints & WebSockets (`http://localhost:8000`)

#### 1. Health & Utility
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Check if AI services and LLM keys are operational |

#### 2. Real-Time WebSockets (15–20 Min Active Rooms)

##### A. Group Discussion Room (15–20 Min Live Execution)
* **URI:** `ws://localhost:8000/ws/gd/{sessionId}`
* **Step-by-Step Flow:**

```text
[ USER / MIC ]                   [ FRONTEND (WS CLIENT) ]              [ FASTAPI AI BACKEND ]
      |                                     |                                     |
      | --- 1. Connects to Room ----------> | --- WebSocket Handshake ----------> |
      |                                     | <--- Moderator Intro Audio/Text --- |
      |                                     |                                     |
      | === PHASE: OPEN DISCUSSION (Minutes 1:00 - 18:00) ====================== |
      | --- Speaks into Microphone -------> |                                     |
      |                                     | --- Audio / Text Chunk -----------> | (VAD / STT)
      |                                     |                                     | (Decides Next Speaker)
      |                                     | <--- AI Agent Audio/Text Chunk ---- | (TTS Generation)
      | <--- Plays Agent Audio in Ear ----- |                                     |
      |                                     |                                     |
      | === PHASE: CLOSING ROUND (Minutes 18:00 - 20:00) ======================= |
      |                                     | <--- Moderator: "2 mins left..." -- |
      | --- Speaks Final Summary ---------> | --- Final Speech Chunk -----------> |
      |                                     |                                     |
      | === PHASE: EVALUATION & CLOSURE ======================================== |
      |                                     |                                     | (Runs Evaluator Engine)
      |                                     |                                     | ---> Pushes Report to Node.js
      |                                     | <--- Returns Final Scorecard JSON - |
      | <--- Views Performance Dashboard -- |                                     |
```

##### B. Debate Arena
* **URI:** `ws://localhost:8000/ws/debate/{sessionId}`
* **Workflow:** Round 1 (Opening Statements) -> Round 2 & 3 (Rebuttals & Cross-examination) -> Round 4 (Closing Statements) -> Verdict & Scorecard.

##### C. Mock Interview
* **URI:** `ws://localhost:8000/ws/interview/{sessionId}`
* **Workflow:** Greeting & Resume context -> Dynamic technical/behavioral questions -> Follow-up probes based on weak answers -> Structured interview scorecard.

---

## 📡 6. WebSocket Message Protocol (JSON Schemas)

### Client $\rightarrow$ Server Messages

```json
// 1. Sending Speech Transcript or Audio Chunk
{
  "event": "USER_SPEECH",
  "text": "I believe artificial intelligence creates more jobs than it displaces because...",
  "durationSeconds": 12.4
}

// 2. Keep-Alive Heartbeat (Sent every 15s)
{
  "event": "PING"
}

// 3. User voluntarily ends session early
{
  "event": "END_SESSION_REQUEST"
}
```

### Server $\rightarrow$ Client Messages

```json
// 1. AI Agent Speaking (Text + Audio)
{
  "event": "AGENT_SPEAKING",
  "agentName": "Aarav (The Contrarian)",
  "text": "While that sounds promising, historical data shows sudden disruptions leave blue-collar workers displaced without safety nets.",
  "audioBase64": "UklGRi...",
  "turnState": "AGENT_TURN"
}

// 2. Room Notification / Time Alert
{
  "event": "MODERATOR_ALERT",
  "message": "2 minutes remaining. Please present your concluding arguments.",
  "timeRemainingSeconds": 120
}

// 3. Final Session Report (End of Session)
{
  "event": "SESSION_COMPLETED",
  "report": {
    "overallScore": 84,
    "metrics": {
      "clarity": 82,
      "confidence": 88,
      "relevance": 85,
      "vocabularyGrammar": 79,
      "speakingTimeRatio": 0.28,
      "fillerWordsCount": 6,
      "fillerWordsList": ["um", "like", "basically"],
      "wordsPerMinute": 138
    },
    "feedback": {
      "strengths": ["Clear voice modulation", "Strong opening rebuttal"],
      "areasToImprove": ["Reduce filler words when transitioning", "Support economic arguments with specific statistics"]
    }
  }
}
```

---

## 📁 7. Recommended Repository Structure

```
UnMute-Yourself-AI/
├── ai-backend/                      # Python FastAPI (AI Services)
│   ├── app/
│   │   ├── api/                     # WebSocket & REST routes
│   │   │   ├── gd_socket.py         # Group Discussion WS Handler
│   │   │   ├── debate_socket.py     # Debate WS Handler
│   │   │   └── interview_socket.py  # Interview WS Handler
│   │   ├── core/                    # Config, Prompts, Personas
│   │   │   ├── config.py            # API Keys, Environment variables
│   │   │   └── prompts/             # Prompt engineering templates
│   │   ├── services/                # Business logic
│   │   │   ├── llm_service.py       # Gemini / OpenAI / Groq client
│   │   │   ├── stt_service.py       # Speech-to-Text handler
│   │   │   ├── tts_service.py       # Text-to-Speech handler
│   │   │   ├── turn_manager.py      # Turn-taking & GD moderation logic
│   │   │   └── evaluator.py         # Evaluation & grading engine
│   │   └── app.py                   # FastAPI Application Entry
│   ├── requirements.txt
│   └── .env
│
├── node_backend/                    # Node.js Express (User, Auth, DB)
│   ├── src/
│   │   ├── config/                  # DB connection (MongoDB/PostgreSQL)
│   │   ├── controllers/             # Auth, User, Session, Report controllers
│   │   ├── middleware/              # JWT auth, Error handling
│   │   ├── models/                  # User.js, Session.js, Report.js
│   │   ├── routes/                  # /api/auth, /api/sessions, /api/internal
│   │   └── index.js                 # Express Server Entry
│   ├── package.json
│   └── .env
│
├── frontend/                        # React / Vite (Client UI)
│   ├── src/
│   │   ├── components/              # AudioVisualizer, MicButton, Timer, TranscriptView
│   │   ├── hooks/                   # useWebSocket.js, useAudioRecorder.js
│   │   ├── pages/                   # Login, Register, Dashboard, GDRoom, ReportPage
│   │   ├── services/                # API client (Axios/Fetch)
│   │   └── App.jsx
│   ├── package.json
│   └── .env
│
├── main.py                          # Root convenience launcher
└── README.md
```

---

## 🚀 8. Step-by-Step Prototype Roadmap

1. **Milestone 1 (AI Backend Standalone Test):**
   * Build the FastAPI WebSocket endpoint for **Group Discussion**.
   * Test simulated 2-agent responses using Google Gemini API.
2. **Milestone 2 (Node.js Auth & Session Store):**
   * Setup Express server with MongoDB.
   * Build `POST /api/auth/login` and `POST /api/sessions/create`.
3. **Milestone 3 (Frontend Minimal Room):**
   * Build a single page that connects to the FastAPI WebSocket, records mic audio, and renders agent responses.
4. **Milestone 4 (Analytics & Report Generation):**
   * Implement the scoring prompt on session finish and display the results on the frontend report page.
