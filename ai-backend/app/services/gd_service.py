"""Group Discussion (GD) Multi-Agent Session Orchestrator & State Machine."""
# pyrefly: ignore [missing-import]
from app.services.llm_service import director_chain, agent_chain, evaluator_chain
# pyrefly: ignore [missing-import]
from app.services.tts_service import generate_neural_audio_b64, PERSONA_VOICES
# pyrefly: ignore [missing-import]
from app.core.prompts.gd import (
    GDRouterDecision,
    GDEvaluationScorecard,
    PERSONAS,
    SPEAKER_NAMES,
    MODERATOR_INTRO_PROMPT,
    ANALYST_INTRO_PROMPT,
    CONTRARIAN_INTRO_PROMPT,
    PEACEMAKER_INTRO_PROMPT,
)

class GDRoomSession:
    """Manages live conversation memory, turn taking, neural TTS, and evaluations for a GD room."""
    def __init__(self, topic: str = "Will AI Replace Software Engineers?"):
        self.topic = topic
        self.transcript: list[dict] = []
        self.last_speaker: str = "Moderator"
        self.user_filler_count: int = 0
        self.phase: str = "INTRODUCTIONS"

    def get_recent_history(self, k: int = 6) -> str:
        """Returns the most recent k conversation turns."""
        recent = self.transcript[-k:]
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in recent])

    def get_full_transcript_str(self) -> str:
        """Returns the complete formatted conversation transcript."""
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in self.transcript])

    def record_user_speech(self, user_text: str, filler_count: int = 0):
        """Records user speech utterance and filler word metrics."""
        self.transcript.append({"speaker": "User", "text": user_text})
        self.last_speaker = "User"
        if filler_count > 0:
            self.user_filler_count += filler_count

    async def generate_introductions_list(self) -> list[dict]:
        """Generates introduction turns and neural audio for all 4 AI personas."""
        self.phase = "INTRODUCTIONS"
        intros = [
            ("Moderator (Kavita)", MODERATOR_INTRO_PROMPT.format(topic=self.topic), PERSONA_VOICES["Moderator"]),
            ("Analyst (Rohan)", ANALYST_INTRO_PROMPT, PERSONA_VOICES["Analyst"]),
            ("Contrarian (Aarav)", CONTRARIAN_INTRO_PROMPT, PERSONA_VOICES["Contrarian"]),
            ("Peacemaker (Sneha)", PEACEMAKER_INTRO_PROMPT, PERSONA_VOICES["Peacemaker"]),
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

    async def handle_user_introduction_response(self, user_text: str, filler_count: int = 0) -> dict:
        """Handles user's introduction speech utterance and transitions smoothly into open discussion."""
        self.record_user_speech(user_text, filler_count=filler_count)
        self.phase = "OPEN_DISCUSSION"

        text = (
            f"Thanks for introducing yourself! Now that everyone around the table has introduced themselves, "
            f"our discussion on '{self.topic}' is officially open. Who would like to start off with the first main argument?"
        )
        audio_b64 = await generate_neural_audio_b64(text, PERSONA_VOICES["Moderator"])
        self.transcript.append({"speaker": "Moderator (Kavita)", "text": text})
        self.last_speaker = "Moderator"

        return {
            "speaker": "Moderator (Kavita)",
            "text": text,
            "persona": "Moderator",
            "audio": audio_b64,
            "turnState": "USER_TURN"
        }

    async def generate_next_agent_turn(self) -> dict:
        """Orchestrates next speaker selection, speech generation, and neural audio synthesis."""
        history = self.get_recent_history()

        # Step 1: Director decides which AI persona speaks next
        try:
            decision: GDRouterDecision = await director_chain.ainvoke({
                "topic": self.topic,
                "chat_history": history,
                "last_speaker": self.last_speaker
            })
            chosen_agent = decision.next_speaker
            intent = decision.intent
        except Exception as e:
            print(f"[GD Service Warning] Director structured fallback: {e}")
            candidates = ["Analyst", "Contrarian", "Peacemaker", "Moderator"]
            chosen_agent = "Analyst"
            for c in candidates:
                if c != self.last_speaker:
                    chosen_agent = c
                    break
            intent = "Respond directly and conversationally to the recent discussion point."

        # Safety rule: Never allow the same persona to speak back-to-back
        if chosen_agent == self.last_speaker:
            for c in ["Analyst", "Contrarian", "Peacemaker", "Moderator"]:
                if c != self.last_speaker:
                    chosen_agent = c
                    break

        # Step 2: Persona generates in-character utterance
        persona_system_prompt = PERSONAS.get(chosen_agent, PERSONAS["Analyst"])
        try:
            reply_text = await agent_chain.ainvoke({
                "persona_prompt": persona_system_prompt.format(topic=self.topic),
                "topic": self.topic,
                "chat_history": history,
                "intent": intent
            })
        except Exception as e:
            print(f"[GD Service Error] Agent generation fallback: {e}")
            reply_text = f"That brings up a crucial point regarding {self.topic}. Let me build on that for a second."

        reply_clean = reply_text.strip()
        # Remove literal stage directions like (pause), [pause], (pauses) so TTS doesn't speak "pause"
        import re
        reply_clean = re.sub(r'[\(\[\{]\s*(?:pause|pauses|short pause|brief pause|silent|sigh)\s*[\)\]\}]', '...', reply_clean, flags=re.IGNORECASE)
        reply_clean = re.sub(r'\s+', ' ', reply_clean).strip()

        speaker_display = SPEAKER_NAMES.get(chosen_agent, f"{chosen_agent} AI")

        # Step 3: Neural Voice Synthesis
        voice_name = PERSONA_VOICES.get(chosen_agent, "en-IN-NeerjaNeural")
        audio_b64 = await generate_neural_audio_b64(reply_clean, voice_name)

        # Save turn to session transcript
        self.transcript.append({"speaker": speaker_display, "text": reply_clean})
        self.last_speaker = chosen_agent

        return {
            "speaker": speaker_display,
            "text": reply_clean,
            "persona": chosen_agent,
            "audio": audio_b64
        }

    async def evaluate_session(self) -> dict:
        """Evaluates discussion performance using the AI Evaluator model."""
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
            print(f"[GD Service Error] Evaluation fallback: {e}")
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
                "areas_for_improvement": ["Reduce hesitation fillers during long speech turns", "Address counter-arguments directly with quantitative metrics"],
                "summary_feedback": f"Solid performance in the discussion on '{self.topic}'. Made strong contributions across turns with {self.user_filler_count} tracked filler words."
            }


# In-Memory Active GD Room Store
room_sessions: dict[str, GDRoomSession] = {}

def get_or_create_room(room_id: str, topic: str = "Will AI Replace Software Engineers?") -> GDRoomSession:
    """Retrieves an existing room session or initializes a new one."""
    if room_id not in room_sessions:
        room_sessions[room_id] = GDRoomSession(topic=topic)
    return room_sessions[room_id]
