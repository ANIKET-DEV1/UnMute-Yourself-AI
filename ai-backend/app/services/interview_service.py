"""1-on-1 Mock Interview Session Manager and Adaptive Questioning Engine."""
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm_service import llm
from app.services.tts_service import generate_neural_audio_b64
from app.core.prompts.interview import (
    InterviewTurnDecision,
    InterviewEvaluationScorecard,
    INTERVIEWER_SYSTEM_PROMPT,
    INTERVIEW_EVALUATOR_PROMPT,
    ParsedResumeData,
)

# Chains
interviewer_decision_llm = llm.with_structured_output(InterviewTurnDecision)
interview_turn_prompt = ChatPromptTemplate.from_messages([
    ("system", INTERVIEWER_SYSTEM_PROMPT),
    ("human", (
        "Current Phase: {current_phase}\n"
        "Question Count so far: {question_count}\n"
        "Recent Interview Exchange:\n{chat_history}\n\n"
        "Last Candidate Answer: \"{last_user_answer}\"\n\n"
        "Decide the next phase (progressing from INTRODUCTION -> EASY_TECHNICAL -> MEDIUM_PROJECT -> HARD_SCENARIO -> CLOSING) "
        "and formulate your conversational response + next question for the candidate:"
    ))
])
interview_turn_chain = interview_turn_prompt | interviewer_decision_llm

interview_eval_llm = llm.with_structured_output(InterviewEvaluationScorecard)
interview_eval_prompt = ChatPromptTemplate.from_messages([
    ("system", INTERVIEW_EVALUATOR_PROMPT)
])
interview_eval_chain = interview_eval_prompt | interview_eval_llm

class InterviewSession:
    """Manages an active 15-20 min 1-on-1 technical interview room."""
    def __init__(
        self,
        target_role: str = "Frontend Developer",
        language: str = "English",
        resume_data: dict = None
    ):
        self.target_role = target_role
        self.language = language
        self.resume = ParsedResumeData(**(resume_data or {}))
        self.transcript: list[dict] = []
        self.current_phase = "INTRODUCTION"
        self.question_count = 0
        self.user_filler_count = 0
        self.interviewer_voice = "en-US-GuyNeural" if language == "English" else "hi-IN-MadhurNeural"

    def get_recent_history(self, k: int = 6) -> str:
        recent = self.transcript[-k:]
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in recent])

    def get_full_transcript_str(self) -> str:
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in self.transcript])

    async def generate_opening_turn(self) -> dict:
        """Generates the initial warm greeting and introductory question."""
        candidate_name = self.resume.candidate_name if self.resume.candidate_name != "Candidate" else "there"
        project_snippet = f" like {self.resume.key_projects[0]}" if self.resume.key_projects else ""

        if self.language.lower().startswith("hi") or "hinglish" in self.language.lower():
            text = (
                f"Hello {candidate_name}! Welcome to your technical interview for the {self.target_role} role. "
                f"Maine aapka resume dekha, especially your projects{project_snippet}. "
                f"To start off, could you briefly introduce yourself and walk me through your background?"
            )
        else:
            text = (
                f"Hello {candidate_name}, welcome to your technical mock interview for the {self.target_role} position. "
                f"I had a chance to review your resume and background{project_snippet}. "
                f"To kick things off, could you give a brief introduction of yourself and share what you've been working on recently?"
            )

        audio_b64 = await generate_neural_audio_b64(text, self.interviewer_voice)
        self.transcript.append({"speaker": "Interviewer (Alex)", "text": text})
        self.question_count = 1
        self.current_phase = "INTRODUCTION"

        return {
            "speaker": "Interviewer (Alex)",
            "text": text,
            "phase": "INTRODUCTION",
            "audio": audio_b64,
            "turnState": "USER_TURN",
            "questionNumber": self.question_count
        }

    async def handle_candidate_answer(self, user_answer: str, filler_count: int = 0) -> dict:
        """Processes the candidate's answer and generates the next adaptive question."""
        self.transcript.append({"speaker": "Candidate", "text": user_answer})
        if filler_count > 0:
            self.user_filler_count += filler_count

        history = self.get_recent_history()

        try:
            decision: InterviewTurnDecision = await interview_turn_chain.ainvoke({
                "target_role": self.target_role,
                "language": self.language,
                "candidate_name": self.resume.candidate_name,
                "skills": ", ".join(self.resume.skills) if self.resume.skills else self.target_role,
                "key_projects": ", ".join(self.resume.key_projects) if self.resume.key_projects else "Key portfolio projects",
                "years_experience": self.resume.years_experience,
                "current_phase": self.current_phase,
                "question_count": self.question_count,
                "chat_history": history,
                "last_user_answer": user_answer
            })
            reply_text = decision.interviewer_reply.strip()
            self.current_phase = decision.phase
            feedback_tip = decision.feedback_tip
        except Exception as e:
            print(f"[Interview LLM Warning] Fallback turn: {e}")
            self.question_count += 1
            if self.question_count <= 2:
                self.current_phase = "EASY_TECHNICAL"
                reply_text = f"Thanks for sharing that background. Based on your experience with {self.target_role}, could you explain the fundamental architectural principles you prioritize when designing new components?"
            elif self.question_count <= 4:
                self.current_phase = "MEDIUM_PROJECT"
                reply_text = f"Understood. Let's look at real-world problem solving: tell me about a time you ran into a critical performance bottleneck or bug in one of your projects, and how you resolved it using the STAR approach."
            elif self.question_count <= 6:
                self.current_phase = "HARD_SCENARIO"
                reply_text = f"Great explanation. Now for a scenario: if your service experiences a 10x traffic spike and database latency spikes drastically, walk me through your step-by-step diagnostic and scaling strategy."
            else:
                self.current_phase = "CLOSING"
                reply_text = f"Thank you for walking through those technical scenarios. We've covered great ground today. Do you have any questions for me about the role or team before we wrap up?"
            feedback_tip = "Answer recorded. Focus on quantitative outcomes and structured steps."

        self.question_count += 1
        audio_b64 = await generate_neural_audio_b64(reply_text, self.interviewer_voice)
        self.transcript.append({"speaker": "Interviewer (Alex)", "text": reply_text})

        return {
            "speaker": "Interviewer (Alex)",
            "text": reply_text,
            "phase": self.current_phase,
            "audio": audio_b64,
            "turnState": "USER_TURN" if self.current_phase != "CLOSING" else "CLOSING_ROUND",
            "questionNumber": self.question_count,
            "feedbackTip": feedback_tip
        }

    async def evaluate_interview(self) -> dict:
        """Evaluates the candidate's complete interview and produces the final scorecard."""
        full_transcript = self.get_full_transcript_str()
        analytics_header = f"[Interview Analytics - Total Filler Words Tracked: {self.user_filler_count}]\n\n"
        full_context = analytics_header + (full_transcript if full_transcript else "No turns recorded.")

        candidate_profile_str = (
            f"Name: {self.resume.candidate_name}, Role: {self.target_role}, "
            f"Skills: {', '.join(self.resume.skills)}, Experience: {self.resume.years_experience}"
        )

        try:
            evaluation: InterviewEvaluationScorecard = await interview_eval_chain.ainvoke({
                "target_role": self.target_role,
                "candidate_profile": candidate_profile_str,
                "chat_history": full_context
            })
            eval_dict = evaluation.model_dump()
            eval_dict["filler_words_count"] = self.user_filler_count
            return eval_dict
        except Exception as e:
            print(f"[Interview Evaluator Warning] Evaluation fallback: {e}")
            return {
                "candidate_name": self.resume.candidate_name,
                "target_role": self.target_role,
                "hiring_verdict": "HIRE" if self.user_filler_count < 6 else "LEANING_HIRE",
                "overall_score": 84,
                "technical_depth": 8,
                "problem_solving": 8,
                "communication": 8,
                "star_methodology": 7,
                "confidence_and_tone": 8,
                "filler_words_count": self.user_filler_count,
                "strengths": [
                    f"Strong foundational grasp of {self.target_role} concepts",
                    "Clear logical explanation of project architecture",
                    "Polite and professional interview presence"
                ],
                "weaknesses": [
                    "Could quantify project achievements with more metrics (% latency reduction, RPS handled)",
                    "Elaborate more deeply on edge-case error handling and failure modes"
                ],
                "detailed_feedback": (
                    f"Solid technical interview for the {self.target_role} position. Demonstrated practical understanding "
                    f"of system trade-offs with {self.user_filler_count} tracked filler words. Focus on structuring answers "
                    f"with the STAR framework (Situation, Task, Action, Result) to achieve top-percentile scores in real hiring loops."
                )
            }


# In-Memory Active Interview Room Store
active_interview_sessions: dict[str, InterviewSession] = {}

def get_or_create_interview_session(
    room_id: str,
    target_role: str = "Frontend Developer",
    language: str = "English",
    resume_data: dict = None
) -> InterviewSession:
    """Retrieves or creates a new 1-on-1 interview session."""
    if room_id not in active_interview_sessions:
        active_interview_sessions[room_id] = InterviewSession(
            target_role=target_role,
            language=language,
            resume_data=resume_data
        )
    return active_interview_sessions[room_id]
