"""Prompts and Pydantic Schemas for 1-on-1 AI Mock Interview System."""
from typing import Literal
from pydantic import BaseModel, Field

# 1. Resume Extraction Schema
class ParsedResumeData(BaseModel):
    candidate_name: str = Field(default="Candidate", description="Full name of the candidate if found, else Candidate.")
    target_role: str = Field(default="Software Engineer", description="Target role or primary profession inferred from resume.")
    years_experience: str = Field(default="0-1 years", description="Estimated years of experience (e.g. Fresher, 1-2 years, 3+ years).")
    skills: list[str] = Field(default_factory=list, description="Top 5-8 technical and soft skills extracted from the resume.")
    key_projects: list[str] = Field(default_factory=list, description="Top 2-3 project names or key achievements.")
    education: str = Field(default="Computer Science / Engineering", description="Highest degree or university background.")
    summary: str = Field(default="", description="A 2-sentence summary of the candidate's core profile.")

# 2. Adaptive Interview Turn Schema
class InterviewTurnDecision(BaseModel):
    phase: Literal["INTRODUCTION", "EASY_TECHNICAL", "MEDIUM_PROJECT", "HARD_SCENARIO", "CLOSING"] = Field(
        description="Current phase and difficulty level of the interview."
    )
    interviewer_reply: str = Field(
        description="The interviewer's spoken response: acknowledges previous candidate answer and poses the next question (strictly 1-3 spoken sentences)."
    )
    is_follow_up: bool = Field(
        default=False,
        description="Whether this is a follow-up probing question because the candidate's answer was brief or lacked detail."
    )
    feedback_tip: str = Field(
        default="",
        description="Real-time short coaching note on the candidate's last answer (e.g., 'Good STAR structure', 'Consider adding quantitative impact')."
    )

# 3. Comprehensive Interview Evaluation Scorecard
class InterviewEvaluationScorecard(BaseModel):
    candidate_name: str = Field(default="Candidate")
    target_role: str = Field(default="Software Engineer")
    hiring_verdict: Literal["STRONG_HIRE", "HIRE", "LEANING_HIRE", "NO_HIRE"] = Field(
        description="The final hiring recommendation."
    )
    overall_score: int = Field(description="Overall composite interview score from 1 to 100.")
    technical_depth: int = Field(description="Score 1-10 on domain expertise, accurate terminology, and architectural grasp.")
    problem_solving: int = Field(description="Score 1-10 on analytical approach, debugging logic, and handling difficult scenarios.")
    communication: int = Field(description="Score 1-10 on clarity, conciseness, and articulation.")
    star_methodology: int = Field(description="Score 1-10 evaluating Situation, Task, Action, and Result structure.")
    confidence_and_tone: int = Field(description="Score 1-10 on composure, pace, and reduced filler words.")
    filler_words_count: int = Field(default=0, description="Total count of filler words tracked during the session.")
    strengths: list[str] = Field(description="List of 3 primary strengths observed in technical or behavioral answers.")
    weaknesses: list[str] = Field(description="List of 3 specific technical gaps or answer deficiencies to work on.")
    detailed_feedback: str = Field(description="Comprehensive assessor feedback with clear guidance on how to ace the next real interview.")

# 4. Prompts
RESUME_PARSER_PROMPT = """
You are an expert Technical HR Recruiter and Resume Parser.
Extract the key candidate data from the provided raw resume text into the structured format.
If certain fields are missing, infer reasonable values from the available text.

Raw Resume Content:
{resume_text}
"""

INTERVIEWER_SYSTEM_PROMPT = """
You are Alex, a seasoned Lead Technical Interviewer conducting a realistic 1-on-1 mock interview.
Target Role: {target_role}
Preferred Language: {language}
Candidate Profile:
- Name: {candidate_name}
- Skills: {skills}
- Key Projects: {key_projects}
- Experience: {years_experience}

Interview Progression Rules (15-20 Min Structured Flow):
1. INTRODUCTION (Easy): Warm greeting, welcome the candidate by name, and ask for a quick self-introduction and their favorite project from their resume.
2. EASY_TECHNICAL: Foundational questions on their core listed skills ({skills}) and role fundamentals.
3. MEDIUM_PROJECT: Dive into a specific project from their resume ({key_projects}) or behavioral question using the STAR method (Handling challenges, conflicts, trade-offs).
4. HARD_SCENARIO (Difficult): System design, concurrency, scalability, architectural failure handling, or edge-case troubleshooting.
5. CLOSING: Acknowledge their effort and invite any candidate questions before concluding.

Tone & Behavior:
- You are a supportive yet discerning senior engineering leader.
- Speak conversationally, using natural pauses (...), encouraging acknowledgments ("That's a great example...", "Understood...", "Let's dig a bit deeper into that...").
- If the candidate gives a shallow or textbook-only answer, ask a targeted follow-up probe!
- Keep each interviewer response strictly to 1 to 3 spoken sentences.
- Speak in {language} (if Hinglish, mix natural conversational English with Hindi phrases naturally).
"""

INTERVIEW_EVALUATOR_PROMPT = """
You are an Executive Hiring Committee Lead reviewing the complete transcript of a 1-on-1 Technical Mock Interview.
Target Role: {target_role}
Candidate Profile: {candidate_profile}

Analyze the full interview transcript below and evaluate the candidate across technical depth, problem-solving, STAR format, and communication clarity.
Assign a realistic hiring verdict (STRONG_HIRE, HIRE, LEANING_HIRE, NO_HIRE) with clear, constructive feedback.

Full Interview Transcript & Audio Metrics:
{chat_history}
"""
