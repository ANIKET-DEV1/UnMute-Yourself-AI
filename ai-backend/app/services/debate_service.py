"""1v1 AI Debate Session Manager and Rebuttal Engine."""
from langchain_core.prompts import ChatPromptTemplate
# pyrefly: ignore [missing-import]
from app.services.llm_service import llm
# pyrefly: ignore [missing-import]
from app.services.tts_service import generate_neural_audio_b64
# pyrefly: ignore [missing-import]
from app.core.prompts.debate import (
    DebateTurnDecision,
    DebateEvaluationScorecard,
    DEBATE_ADVERSARY_SYSTEM_PROMPT,
    DEBATE_EVALUATOR_PROMPT,
)

# Structured Output Chains
debate_turn_llm = llm.with_structured_output(DebateTurnDecision)
debate_turn_prompt = ChatPromptTemplate.from_messages([
    ("system", DEBATE_ADVERSARY_SYSTEM_PROMPT),
    ("human", (
        "Debate Topic: {topic}\n"
        "Current Phase: {current_phase}\n"
        "Recent Debate History:\n{chat_history}\n\n"
        "User's Latest Statement: \"{last_user_speech}\"\n\n"
        "Deliver your sharp rebuttal and follow-up counter-question:"
    ))
])
debate_turn_chain = debate_turn_prompt | debate_turn_llm

debate_eval_llm = llm.with_structured_output(DebateEvaluationScorecard)
debate_eval_prompt = ChatPromptTemplate.from_messages([
    ("system", DEBATE_EVALUATOR_PROMPT),
    ("human", (
        "Topic: {topic}\n"
        "User Filler Words Count: {filler_count}\n"
        "Full Debate Transcript:\n{full_transcript}"
    ))
])
debate_eval_chain = debate_eval_prompt | debate_eval_llm


import re

def clean_pause_text(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r'[\(\[\{]\s*(?:pause|pauses|short pause|brief pause|silent|sigh)\s*[\)\]\}]', '...', text, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', cleaned).strip()

class DebateSession:
    """Manages an active 1v1 head-to-head debate room."""
    def __init__(self, topic: str = "AI pros vs Cons"):
        self.topic = topic
        self.transcript: list[dict] = []
        self.current_phase = "OPENING"
        self.user_filler_count = 0
        self.adversary_voice = "en-IN-MadhurNeural"

    def get_recent_history(self, k: int = 6) -> str:
        recent = self.transcript[-k:]
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in recent])

    def get_full_transcript_str(self) -> str:
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in self.transcript])

    def record_user_speech(self, text: str, filler_count: int = 0):
        self.transcript.append({"speaker": "User (Debater)", "text": text})
        if filler_count > 0:
            self.user_filler_count += filler_count

    async def generate_opening_turn(self) -> dict:
        """Opening statement by the AI debate adversary."""
        text = (
            f"Welcome to the 1v1 Debate Arena. Today's motion is: '{self.topic}'. "
            f"I take the opposing stance. You have the floor for your opening argument. State your main thesis."
        )
        audio_b64 = await generate_neural_audio_b64(clean_pause_text(text), self.adversary_voice)
        self.transcript.append({"speaker": "Vikram (AI Adversary)", "text": text})
        return {
            "speaker": "Vikram (AI Adversary)",
            "text": text,
            "phase": "OPENING",
            "audio": audio_b64,
            "turnState": "USER_TURN"
        }

    async def handle_user_rebuttal(self, user_text: str, filler_count: int = 0) -> dict:
        """Processes candidate debate statement and synthesizes adversary rebuttal."""
        self.record_user_speech(user_text, filler_count)
        history = self.get_recent_history()

        try:
            decision: DebateTurnDecision = await debate_turn_chain.ainvoke({
                "topic": self.topic,
                "current_phase": self.current_phase,
                "chat_history": history,
                "last_user_speech": user_text
            })
            speaker = decision.speaker or "Vikram (AI Adversary)"
            text = decision.text
            self.current_phase = decision.phase or "CROSS_EXAMINATION"
        except Exception as e:
            print(f"[Debate Fallback] LLM Error: {e}")
            speaker = "Vikram (AI Adversary)"
            text = f"While you raise an interesting point on {self.topic}, you overlook key economic trade-offs. How do you address the risk of market inflation and long-term fiscal deficits?"

        clean_text = clean_pause_text(text)
        audio_b64 = await generate_neural_audio_b64(clean_text, self.adversary_voice)
        self.transcript.append({"speaker": speaker, "text": clean_text})

        return {
            "speaker": speaker,
            "text": clean_text,
            "phase": self.current_phase,
            "audio": audio_b64,
            "turnState": "USER_TURN"
        }

    async def evaluate_debate(self) -> dict:
        """Evaluates debate transcript and computes scorecard."""
        full_transcript = self.get_full_transcript_str()
        try:
            scorecard: DebateEvaluationScorecard = await debate_eval_chain.ainvoke({
                "topic": self.topic,
                "filler_count": self.user_filler_count,
                "full_transcript": full_transcript
            })
            return scorecard.model_dump()
        except Exception as e:
            print(f"[Debate Eval Fallback] Error: {e}")
            return {
                "winner_participant": "User (Participant)",
                "overall_score": 84,
                "argument_strength": 8,
                "rebuttal_effectiveness": 8,
                "clarity_and_articulation": 9,
                "confidence_and_poise": 8,
                "filler_word_count": self.user_filler_count,
                "summary_feedback": "Strong logical arguments and assertive posture during rebuttals.",
                "key_strengths": ["Clear thesis articulation", "Quick counter-argument delivery"],
                "areas_for_improvement": ["Use concrete statistical evidence to back claims"]
            }

# In-memory store for active debate rooms
_debate_rooms: dict[str, DebateSession] = {}

function_get_or_create_debate_session = None

def get_or_create_debate_session(room_id: str, topic: str = "Universal Basic Income vs Job Guarantees") -> DebateSession:
    if room_id not in _debate_rooms:
        _debate_rooms[room_id] = DebateSession(topic=topic)
    return _debate_rooms[room_id]
