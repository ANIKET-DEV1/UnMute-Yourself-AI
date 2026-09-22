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

```mermaid
flowchart TB
    subgraph Client["Frontend (React / Vite)"]
        UI[User Dashboard & Rooms]
        AudioClient[MediaRecorder & Audio Player]
        WSClient[WebSocket Client Hook]
    end

    subgraph NodeBackend["Node.js Backend (Port 5000)"]
        AuthService[Auth & JWT Controller]
        UserDBHandler[User Profile & Streak Tracker]
        SessionService[Session Lifecycle Manager]
        DB[(Database: MongoDB / PostgreSQL)]
    end

    subgraph AIBackend["Python AI Backend (FastAPI - Port 8000)"]
        WSRouter[WebSocket Room Manager]
        GDEngine[Multi-Agent GD Orchestrator]
        DebateEngine[Debate & Rebuttal Engine]
        InterviewEngine[Adaptive Interviewer Engine]
        SpeechService[STT Whisper & TTS Engine]
        EvalEngine[Scoring & Analytics Engine]
        LLM[LLM: Gemini Flash / Groq / OpenAI]
    end

    %% Client to Node
    UI -->|1. Auth, Profile, History (REST)| NodeBackend
    NodeBackend -->|CRUD Operations| DB
    UI -->|2. Request Session Creation| SessionService
    SessionService -->|Return Session ID & Token| UI

    %% Client to AI Backend
    WSClient <-->|3. Live Audio/Text Stream (15-20 min WS)| WSRouter
    AudioClient <-->|Raw Audio / STT & TTS Playback| SpeechService

    %% AI Internal
    WSRouter --> GDEngine & DebateEngine & InterviewEngine
    GDEngine & DebateEngine & InterviewEngine --> LLM
    SpeechService <--> WSRouter

    %% AI to Node Report Push
    EvalEngine -->|4. Push Final Metrics & Scorecard (REST)| SessionService
```

---

## 👥 3. Team Division & Required Skillsets

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

## 🔌 4. Detailed API Specifications

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
| `POST` | `/api/sessions/create` | Initialize a new session | `{ userId, mode, topic, durationMins, difficulty }` | `{ sessionId, sessionToken, topic, expiresAt }` |
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

##### A. Group Discussion Room
* **URI:** `ws://localhost:8000/ws/gd/{sessionId}`
* **Connection Lifecycle:**
  1. Handshake & Room initialization (Spawns Moderator AI + 2-3 AI participants).
  2. Moderator introduces the topic.
  3. Turn-taking loop: User speaks $\rightarrow$ AI agents respond dynamically.
  4. At Minute 18 (or 2 mins before session end): Moderator warns the room and initiates the closing phase.
  5. Session ends $\rightarrow$ Final evaluation generated and returned via WS and saved to Node backend.

##### B. Debate Arena
* **URI:** `ws://localhost:8000/ws/debate/{sessionId}`
* **Workflow:** Round 1 (Opening Statements) $\rightarrow$ Round 2 & 3 (Rebuttals & Cross-examination) $\rightarrow$ Round 4 (Closing Statements) $\rightarrow$ Verdict & Scorecard.

##### C. Mock Interview
* **URI:** `ws://localhost:8000/ws/interview/{sessionId}`
* **Workflow:** Greeting & Resume context $\rightarrow$ Dynamic technical/behavioral questions $\rightarrow$ Follow-up probes based on weak answers $\rightarrow$ Structured interview scorecard.

---

## 📡 5. WebSocket Message Protocol (JSON Schemas)

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

## 📁 6. Recommended Repository Structure

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

## 🚀 7. Step-by-Step Prototype Roadmap

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
