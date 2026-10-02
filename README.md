# 🎙️ UnMute-Yourself AI
> **An intelligent, real-time multi-agent communication training platform for Group Discussions (GD), 1v1 Debates, and Adaptive Mock Interviews.**

---

## 📌 1. Project Overview & Vision

**UnMute-Yourself AI** is an advanced AI-powered communication and public speaking training platform designed to eliminate speaking anxiety, hone debate strategy, and prepare candidates for high-stakes interviews and GD rounds.

The system features real-time voice-and-text interactive environments powered by Google Gemini 2.0 Flash LLM, Edge Neural Text-to-Speech (TTS), and Web Speech API:
- **Group Discussion (GD Studio):** Interactive 2D round table with 4 distinct AI personas (Rohan S. - The Analyst, Kavita R. - The Moderator, Sneha P. - The Peacemaker, Aarav M. - The Contrarian) with automated turn-taking, inter-speaker pauses, position badges, and animated talking indicators.
- **1-on-1 AI Debate Arena:** A structured, high-stakes 1v1 debate simulator against **Vikram (The Opposer)** powered by realistic neural voice (`en-US-ChristopherNeural`), featuring topic shuffle reels, timer tracking, and automated argument evaluation.
- **Adaptive Mock Interview:** Tailored interview simulator supporting brief professional summary / resume text copy-pasting and PDF parsing, domain-specific job role customization, and STAR framework-based feedback scoring.
- **Continuous Speech Recognition & Input Flow:** Real-time speech transcription continuously fills the message input box without auto-sending, allowing users to edit or refine before dispatching.
- **Automated Audio Cleaning & TTS:** Regex-based stage direction filtering (`clean_pause_text`) strips annotations like `(pause)` or `[sigh]` to ensure crystal-clear neural speech synthesis.
- **Lucide SVG UI Design System:** Clean, modern interface powered by Lucide icons and vibrant responsive CSS.

---

## 🏗️ 2. System Architecture & Tech Stack

UnMute-Yourself AI operates on a high-performance **Decoupled Two-Backend Architecture**:

```text
+-----------------------------------------------------------------------------------------------+
|                                    FRONTEND (HTML5 / Vanilla JS)                              |
|   - Multi-Page Navigation          - Web Speech API (Continuous STT)   - Web Audio API        |
|   - Lucide SVG Icon System        - Live WebSocket UI Client          - API Client (api.js)  |
+-----------------------------------------------+-----------------------------------------------+
                        |                       |                       ^
                        | 1. Auth, Routes,      | 2. Create Session     | 3. Real-Time WS Stream
                        |    History (REST)     |    (Get Session ID)   |    (Audio + JSON Stream)
                        v                       v                       v
+-----------------------------------------------+     +-----------------------------------------+
|      NODE.JS REST BACKEND (Port 5000)         |     |   PYTHON FASTAPI AI ENGINE (Port 8000)  |
|                                               |     |                                         |
|  [ Auth Routes & JWT Middleware ]             |     |  [ Real-Time WebSocket Router ]         |
|  [ User & Session Controllers ]               |     |  [ GD Multi-Agent Simulation Engine ]   |
|  [ Static HTML Page Server ]                  |     |  [ 1v1 Debate Engine (Vikram Opposer) ] |
|  [ SQLite Database (Sequelize ORM) ]          |     |  [ Interview & Resume Parser (PyPDF) ]  |
|  [ Internal Sync Endpoint ]                   |     |  [ Gemini 2.0 LLM & Edge-TTS Engine ]   |
|                                               |     |  [ Speech Sanitizer & Scoring Engine ]  |
|  +-----------------------------------------+  |     +--------------------+--------------------+
|  | Database File: database.sqlite          |  |                          |
|  +-----------------------------------------+  |                          |
|                       ^                       |                          |
|                       | 4. Push Final Report  |                          |
|                       +-----------------------+--------------------------+
+-----------------------------------------------+
                                                                           |
                                                                           v
                                                              +-------------------------+
                                                              |    Cloud AI Infrastructure|
                                                              | Google Gemini 2.0 Flash |
                                                              | Microsoft Edge Neural   |
                                                              +-------------------------+
```

### 🛠️ Technology Stack Breakdown
- **Frontend:** HTML5, Vanilla CSS3 (Glassmorphism design, responsive grid), JavaScript (ES6+), Lucide Icons CDN, Web Speech API (`webkitSpeechRecognition`), HTML5 Audio (`AudioContext`).
- **REST & Auth Backend (Node.js):** Express.js, Sequelize ORM, SQLite (`database.sqlite`), JWT Authentication (`jsonwebtoken`), `bcryptjs`, CORS middleware.
- **AI & WebSocket Engine (Python):** FastAPI, Uvicorn, WebSockets (`asyncio`), `google-genai` (Gemini 2.0 Flash), `edge-tts` (Microsoft Edge Neural Voices), `pypdf` (Resume processing).

---

## 📁 3. Repository Directory Structure

```
PBL/
├── ai-backend/                      # Python FastAPI AI Engine
│   ├── app/
│   │   ├── api/                     # WebSocket Handlers
│   │   │   ├── debate_socket.py     # 1v1 Debate WebSocket router & room manager
│   │   │   ├── gd_socket.py         # Group Discussion WebSocket router & turn orchestrator
│   │   │   └── interview_socket.py  # Mock Interview WebSocket router
│   │   ├── core/                    # Core Configuration & Environment Setup
│   │   │   └── config.py            # API Keys, LLM parameters, persona settings
│   │   ├── services/                # Business Logic & AI Engines
│   │   │   ├── debate_service.py    # Vikram debate rebuttal logic & state machine
│   │   │   ├── gd_service.py        # 4-Persona GD orchestration & pause cleaning
│   │   │   ├── interview_service.py # Adaptive interview engine & STAR evaluation
│   │   │   ├── llm_service.py       # Google Gemini 2.0 Flash SDK client wrapper
│   │   │   ├── resume_service.py    # PyPDF text extraction & profile analysis
│   │   │   └── tts_service.py       # Edge-TTS voice generation & audio base64 encoder
│   │   └── app.py                   # FastAPI Application initialization
│   └── requirements.txt             # Python backend dependencies
│
├── node_backend/                    # Node.js Express Server & Auth Gateway
│   ├── src/
│   │   ├── config/                  # Sequelize SQLite database configuration (`db.js`)
│   │   ├── controllers/             # Auth & Session business controllers
│   │   ├── middleware/              # JWT verification middleware (`authMiddleware.js`)
│   │   ├── models/                  # Sequelize Models (`User.js`, `Session.js`)
│   │   └── routes/                  # Express endpoints (`authRoutes.js`, `sessionRoutes.js`, `internalRoutes.js`)
│   ├── package.json                 # Node.js dependencies
│   └── server.js                    # Node.js main server entry point (Port 5000)
│
├── frontend/                        # Frontend Application UI
│   ├── html/                        # HTML Pages with Lucide SVG Icons
│   │   ├── landing.html             # Platform hero & features landing page
│   │   ├── index.html               # Main User Dashboard & practice launch hub
│   │   ├── login.html               # User authentication login page
│   │   ├── register.html            # New user registration page
│   │   ├── gd.html                  # Interactive 2D GD Studio (5 Personas + Audio Visualizer)
│   │   ├── debate.html              # 1v1 AI Debate Arena (You vs. Vikram + Topic Shuffle)
│   │   ├── interview.html           # Adaptive Mock Interview Studio & Resume Upload
│   │   └── test_gd_websocket.html   # Standalone WebSocket debugging playground
│   └── js/
│       └── api.js                   # Client REST API wrapper, token storage, & global utils
│
├── database.sqlite                  # Local SQLite Database (auto-generated by Sequelize)
├── main.py                          # Python launcher script for FastAPI (`uvicorn app.app:app`)
├── requirements.txt                 # Root Python requirements file
├── package.json                     # Root configuration file
└── README.md                        # Project documentation
```

---

## 🔄 4. Detailed End-to-End Execution Flow

```text
[ USER UI / BROWSER ]                     [ NODE.JS BACKEND (5000) ]           [ PYTHON FASTAPI (8000) ]
         |                                             |                                    |
         | -- 1. POST /api/auth/login standard ------->|                                    |
         | <--- Returns JWT Token & User Info ---------|                                    |
         |                                             |                                    |
         | -- 2. POST /api/sessions/create ----------->|                                    |
         |    (Body: mode="GD", topic="AI Jobs")       |                                    |
         |                                             | -- Creates DB Session Record       |
         |                                             |    Status: "IN_PROGRESS"           |
         | <--- Returns { session_id: "sess_abc123" } -|                                    |
         |                                             |                                    |
         | ========================= WEBSOCKET HANDOFF ===================================== |
         |                                                                                  |
         | -- 3. Connect WS: ws://127.0.0.1:8000/gd/ws/sess_abc123 ------------------------> |
         |                                                                                  |
         |                                                                       4. Spawns Room Engine
         |                                                                          Loads 4 Personas
         | <--- 5. Moderator Intro Message (Text + Base64 Edge-TTS Voice) ----------------- |
         |                                                                                  |
         | ================= LIVE INTERACTIVE SPEECH & VOICE LOOP ========================== |
         |                                                                                  |
         | -- 6. Mic Open -> Transcribes continuously into input box (Web Speech API) ----> |
         | -- 7. User clicks Send / Enter -> WS Sends USER_MESSAGE -----------------------> |
         |                                                                                  |
         |                                                                       8. Gemini 2.0 Flash
         |                                                                          Generates AI response
         |                                                                          Applies clean_pause_text
         |                                                                          Generates Edge-TTS
         | <--- 9. Stream AGENT_SPEECH (Speaker Name + Script + Base64 Audio) ------------- |
         |                                                                                  |
         | ================= SESSION FINALIZATION & REPORT SYNC ============================ |
         |                                                                                  |
         | -- 10. Session Ends -> WS triggers Evaluator Engine ----------------------------> |
         |                                             | <--- 11. POST /api/internal/... ----|
         |                                             |     (Pushes Evaluation Metrics)    |
         |                                             |     (Status: "COMPLETED")          |
         | <--- 12. Receives Final Scorecard Modal JSON ------------------------------------ |
```

---

## 🗣️ 5. Curated Topics & Module Configurations

### 💬 A. Group Discussion Topics (17 Curated Topics)
1. `AI: Opportunity or Threat to Jobs`
2. `Technology Makes Life Better or Worse`
3. `Importance of Communication Skills`
4. `Hard Work vs. Smart Work`
5. `Teamwork vs. Individual Work`
6. `Money vs. Job Satisfaction`
7. `Leadership vs. Teamwork`
8. `Should College Students Have Part-Time Jobs?`
9. `Is Attendance Necessary in College?`
10. `Impact of Mobile Phones on Students`
11. `Online Shopping vs. Offline Shopping`
12. `Should Exams Be Replaced by Continuous Assessment?`
13. `Is Social Media Good for Students?`
14. `Success: Hard Work or Luck?`
15. `Should Students Be Allowed to Use AI for Assignments?`
16. `Is Competition Good for Students?`
17. `Importance of Soft Skills vs. Technical Skills`

### ⚔️ B. 1v1 Debate Motions (11 Curated Topics)
1. `Skills Are More Important Than Degrees`
2. `Technical Skills Are More Important Than Soft Skills`
3. `Work From Home is Better Than Work From Office`
4. `Job Security is More Important Than Salary`
5. `Entrepreneurship is Better Than a Job`
6. `Part-Time Jobs Are Beneficial for College Students`
7. `Internships Should Be Mandatory for College Students`
8. `College Education Should Focus More on Practical Skills`
9. `Marks Do Not Define a Student's Ability`
10. `Experience is More Important Than Qualification`
11. `AI: Pros vs Cons`

---

## 🎭 6. AI Personas & Voice Specifications

| Room / Role | Persona Name | Trait / Stance | Edge Neural Voice Model |
| :--- | :--- | :--- | :--- |
| **GD Moderator** | Kavita R. | Neutral steer, timing, structured summary | `en-IN-NeerjaExpressiveNeural` / `en-US-AvaNeural` |
| **GD Analyst** | Rohan S. | Data-driven, balanced, logical examples | `en-US-GuyNeural` |
| **GD Peacemaker** | Sneha P. | Consensual, bridging opposing viewpoints | `en-US-EmmaNeural` |
| **GD Contrarian** | Aarav M. | Counter-arguments, challenging assumptions | `en-US-EricNeural` |
| **1v1 Debate** | Vikram | Opposer, sharp rebuttals, direct counter-attacks | `en-US-ChristopherNeural` |

---

## 🔌 7. Key API Endpoint Reference

### 🟢 Node.js REST Endpoints (`http://localhost:5000`)
- **`POST /api/auth/register`**: Creates new user account in SQLite DB.
- **`POST /api/auth/login`**: Authenticates user and returns signed JWT token.
- **`GET /api/auth/me`**: Fetches active authenticated user profile details.
- **`POST /api/sessions/create`**: Creates new session document in DB with `IN_PROGRESS` status.
- **`GET /api/sessions/user/:userId`**: Retrieves full past session history and scorecards.
- **`POST /api/internal/sessions/:id/report`**: Internal callback for Python AI backend to save final evaluation report.

### 🟣 Python FastAPI WebSocket Endpoints (`ws://127.0.0.1:8000`)
- **`ws://127.0.0.1:8000/gd/ws/{room_id}`**: Group Discussion 4-Persona WebSocket studio.
- **`ws://127.0.0.1:8000/debate/ws/{room_id}`**: 1v1 Debate Arena WebSocket stream.
- **`ws://127.0.0.1:8000/interview/ws/{room_id}`**: Adaptive Mock Interview WebSocket stream.

---

## 💻 8. Installation & Setup Guide

### 📋 Prerequisites
- **Node.js**: v18.0.0 or higher
- **Python**: v3.10 or higher
- **Google Gemini API Key** (set in environment file)

### 1️⃣ Environment Configuration
Create a `.env` file in the root / `ai-backend` directory:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
PORT=5000
JWT_SECRET=your_jwt_secret_key_here
```

### 2️⃣ Setting Up & Running the Node.js Backend
```bash
cd node_backend
npm install
node server.js
```
*The Node.js server will run on `http://localhost:5000` and serve both REST endpoints and frontend pages.*

### 3️⃣ Setting Up & Running the Python AI Engine
Open a second terminal window in the project root:
```bash
# Create and activate python virtual environment (Optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Python AI Engine launcher
python main.py
```
*The Python FastAPI Engine will start on `http://127.0.0.1:8000`.*

### 4️⃣ Accessing the Application
Open your browser and navigate to:
```text
http://localhost:5000
```
- Click **Get Started / Register** to create an account.
- Choose between **Group Discussion Studio**, **1v1 AI Debate Arena**, or **Mock Interview Prep**.
- Grant microphone access when prompted to experience real-time speech transcription and neural voice responses!

---

## ⚡ 9. Verification & Testing

- **Backend Health Check:** `http://localhost:5000/health`
- **AI Engine Health Check:** `http://127.0.0.1:8000/health`
- **Standalone WebSocket Debugger:** `http://localhost:5000/html/test_gd_websocket.html`

---

> **UnMute-Yourself AI** — *Master your voice, command the room.*
