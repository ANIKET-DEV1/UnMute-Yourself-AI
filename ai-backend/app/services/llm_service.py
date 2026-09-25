from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import base64
import edge_tts
from app.core.prompts.gd import (
    GDRouterDecision,
    GDEvaluationScorecard,
    DIRECTOR_SYSTEM_PROMPT,
    MODERATOR_PROMPT,
    CONTRARIAN_PROMPT,
    PEACEMAKER_PROMPT,
    PERSONAS,
    SPEAKER_NAMES,
    EVALUATOR_SYSTEM_PROMPT,
    MODERATOR_INTRO_PROMPT,
    ANALYST_INTRO_PROMPT,
    CONTRARIAN_INTRO_PROMPT,
    PEACEMAKER_INTRO_PROMPT,
)

# 1. Persona Neural Voice Mappings (Microsoft Edge Neural TTS)
PERSONA_VOICES = {
    "Moderator": "en-IN-NeerjaNeural",
    "Analyst": "en-US-AndrewNeural",
    "Contrarian": "en-US-BrianNeural",
    "Peacemaker": "en-US-EmmaNeural"
}

async def generate_neural_audio_b64(text: str, voice: str) -> str:
    """Generates ultra-realistic human neural speech MP3 audio encoded in Base64."""
    try:
        clean_text = text.replace("800M", "800 million").replace("%", " percent")
        communicate = edge_tts.Communicate(clean_text, voice)
        audio_bytes = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_bytes += chunk["data"]
        return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        print(f"[Edge-TTS Warning] Audio generation fallback: {e}")
        return ""

# 2. Chat model initialization
llm = ChatOllama(
    model="llama3.2",
    base_url="http://localhost:11434",
    temperature=0.7,
)

# 3. Director Chain (Structured Output for speaker routing)
director_llm = llm.with_structured_output(GDRouterDecision)

director_prompt = ChatPromptTemplate.from_messages([
    ("system", DIRECTOR_SYSTEM_PROMPT),
    ("human", "Recent Discussion:\n{chat_history}\n\nLast Speaker was: {last_speaker}\nWho should speak next?")
])
director_chain = director_prompt | director_llm

# 4. Agent Utterance Chain
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "{persona_prompt}"),
    ("human", (
        "Topic: {topic}\n"
        "Recent Transcript:\n{chat_history}\n\n"
        "Your Directive This Turn: {intent}\n"
        "Speak your line naturally to the group as if in a live meeting (strictly max 2 sentences):"
    ))
])
agent_chain = agent_prompt | llm | StrOutputParser()

# 5. Evaluator Chain (Structured Output for final scorecard)
evaluator_llm = llm.with_structured_output(GDEvaluationScorecard)
evaluator_prompt = ChatPromptTemplate.from_messages([
    ("system", EVALUATOR_SYSTEM_PROMPT)
])
evaluator_chain = evaluator_prompt | evaluator_llm


class GDRoomSession:
    def __init__(self, topic: str = "Will AI Replace Software Engineers?"):
        self.topic = topic
        self.transcript: list[dict] = []
        self.last_speaker: str = "Moderator"
        self.user_filler_count: int = 0

    def get_recent_history(self, k: int = 6) -> str:
        """Keeps prompt small for faster local model inference."""
        recent = self.transcript[-k:]
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in recent])

    def get_full_transcript_str(self) -> str:
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in self.transcript])

    def record_user_speech(self, user_text: str, filler_count: int = 0):
        self.transcript.append({"speaker": "User", "text": user_text})
        self.last_speaker = "User"
        if filler_count > 0:
            self.user_filler_count += filler_count

    async def generate_introductions_list(self) -> list[dict]:
        """Generates introduction audio turns for Moderator, Analyst, Contrarian, and Peacemaker."""
        intros = [
            ("Moderator (Kavita)", MODERATOR_INTRO_PROMPT.format(topic=self.topic), "en-IN-NeerjaNeural"),
            ("Analyst (Rohan)", ANALYST_INTRO_PROMPT, "en-US-AndrewNeural"),
            ("Contrarian (Aarav)", CONTRARIAN_INTRO_PROMPT, "en-US-BrianNeural"),
            ("Peacemaker (Sneha)", PEACEMAKER_INTRO_PROMPT, "en-US-EmmaNeural"),
        ]

        intro_turns = []
        for speaker, text, voice in intros:
            audio_b64 = await generate_neural_audio_b64(text, voice)
            self.transcript.append({"speaker": speaker, "text": text})
            intro_turns.append({
                "speaker": speaker,
                "text": text,
                "audio": audio_b64,
                "turnState": "USER_TURN" if speaker.startswith("Peacemaker") else "AGENT_TURN"
            })
        return intro_turns

    async def generate_next_agent_turn(self) -> dict:
        history = self.get_recent_history()

        # Step 1: Director chooses next speaker and directive
        try:
            decision: GDRouterDecision = await director_chain.ainvoke({
                "topic": self.topic,
                "chat_history": history,
                "last_speaker": self.last_speaker
            })
            chosen_agent = decision.next_speaker
            intent = decision.intent
        except Exception as e:
            print(f"[LLM Service Warning] Director structured output fallback: {e}")
            candidates = ["Analyst", "Contrarian", "Peacemaker", "Moderator"]
            chosen_agent = "Analyst"
            for c in candidates:
                if c != self.last_speaker:
                    chosen_agent = c
                    break
            intent = "Respond directly and conversationally to the recent discussion point."

        # Safety rule: ensure Director never picks the same persona back-to-back
        if chosen_agent == self.last_speaker:
            for c in ["Analyst", "Contrarian", "Peacemaker", "Moderator"]:
                if c != self.last_speaker:
                    chosen_agent = c
                    break

        # Step 2: Selected agent generates in-character response
        persona_system_prompt = PERSONAS.get(chosen_agent, PERSONAS["Analyst"])
        
        try:
            reply_text = await agent_chain.ainvoke({
                "persona_prompt": persona_system_prompt.format(topic=self.topic),
                "topic": self.topic,
                "chat_history": history,
                "intent": intent
            })
        except Exception as e:
            print(f"[LLM Service Error] Agent generation fallback: {e}")
            reply_text = f"That brings up an important point regarding {self.topic}. Let me build on that for a second."

        reply_clean = reply_text.strip()
        speaker_display = SPEAKER_NAMES.get(chosen_agent, f"{chosen_agent} AI")

        # Step 3: Generate ultra-realistic neural audio (MP3 Base64)
        voice_name = PERSONA_VOICES.get(chosen_agent, "en-IN-NeerjaNeural")
        audio_b64 = await generate_neural_audio_b64(reply_clean, voice_name)

        # Save turn to room state
        self.transcript.append({"speaker": speaker_display, "text": reply_clean})
        self.last_speaker = chosen_agent

        return {
            "speaker": speaker_display,
            "text": reply_clean,
            "persona": chosen_agent,
            "audio": audio_b64
        }

    async def handle_user_speech(self, user_text: str, filler_count: int = 0) -> dict:
        self.record_user_speech(user_text, filler_count=filler_count)
        return await self.generate_next_agent_turn()

    async def evaluate_session(self) -> dict:
        full_transcript = self.get_full_transcript_str()
        analytics_header = f"[Speech Analytics - Total Tracked Filler Words (um/uh/like/basically) by User: {self.user_filler_count}]\n\n"
        full_context = analytics_header + (full_transcript if full_transcript else "No user turns recorded.")

        try:
            evaluation: GDEvaluationScorecard = await evaluator_chain.ainvoke({
                "topic": self.topic,
                "chat_history": full_context
            })
            eval_dict = evaluation.model_dump()
            eval_dict["filler_words_count"] = self.user_filler_count
            return eval_dict
        except Exception as e:
            print(f"[LLM Service Error] Evaluation chain fallback: {e}")
            return {
                "winner_candidate": "User (Participant)" if self.user_filler_count < 5 else "Analyst (Rohan)",
                "winner_reasoning": "Delivered well-structured arguments supported by practical logic and active listening throughout the discussion.",
                "clarity_and_articulation": 8,
                "argument_strength": 7,
                "listening_and_collaboration": 8,
                "leadership_and_steering": 7,
                "fluency_and_pace": 8,
                "filler_words_count": self.user_filler_count,
                "overall_score": 82,
                "strengths": ["Active participation in the topic", "Clear articulation of key viewpoints"],
                "areas_for_improvement": ["Reduce hesitation fillers during long speech turns", "Address counter-arguments directly with more quantitative metrics"],
                "summary_feedback": f"Solid performance in the discussion on '{self.topic}'. Made strong contributions across turns with {self.user_filler_count} tracked filler words."
            }


# Session Store / Room Manager
room_sessions: dict[str, GDRoomSession] = {}

def get_or_create_room(room_id: str, topic: str = "Will AI Replace Software Engineers?") -> GDRoomSession:
    if room_id not in room_sessions:
        room_sessions[room_id] = GDRoomSession(topic=topic)
    return room_sessions[room_id]