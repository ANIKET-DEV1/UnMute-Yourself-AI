"""Prompts, Pydantic Schemas, and System Instructions for 1v1 AI Competitive Debate."""
from pydantic import BaseModel, Field
from typing import List, Optional

class DebateTurnDecision(BaseModel):
    speaker: str = Field(default="AI Adversary (Vikram)", description="Name of the debate opponent.")
    text: str = Field(description="The adversarial rebuttal, counter-argument, or cross-examination question.")
    phase: str = Field(default="CROSS_EXAMINATION", description="Current debate phase (OPENING, CROSS_EXAMINATION, REBUTTAL, CLOSING).")
    turnState: str = Field(default="USER_TURN", description="Indicates whose turn is next.")

class DebateEvaluationScorecard(BaseModel):
    winner_participant: str = Field(description="Name of the winning debater (User vs AI Adversary).")
    overall_score: int = Field(description="Overall debate performance score out of 100.")
    argument_strength: int = Field(description="Logical strength and evidence quality out of 10.")
    rebuttal_effectiveness: int = Field(description="Ability to counter opponent arguments out of 10.")
    clarity_and_articulation: int = Field(description="Fluency, vocabulary, and delivery out of 10.")
    confidence_and_poise: int = Field(description="Confidence and firmness under pressure out of 10.")
    filler_word_count: int = Field(description="Total filler words used.")
    summary_feedback: str = Field(description="Comprehensive summary feedback on strengths and strategic improvements.")
    key_strengths: List[str] = Field(description="List of top debate strengths.")
    areas_for_improvement: List[str] = Field(description="List of areas needing work.")

DEBATE_ADVERSARY_SYSTEM_PROMPT = """You are Vikram, a sharp, highly analytical, and competitive 1v1 AI Debate Adversary.
Your objective is to challenge the user's arguments directly with sharp logic, counter-examples, and rigorous cross-examination.

DEBATE STANCE & STYLE:
- Take the OPPOSING stance to the user's arguments on the given topic.
- Identify logical fallacies, unsupported assumptions, or over-simplifications in the user's statements.
- Deliver firm, articulate rebuttals in 2 to 4 concise sentences.
- Finish with a challenging follow-up question or counter-prompt to test their stance under pressure.
- Maintain a respectful yet fiercely competitive tone.
"""

DEBATE_EVALUATOR_PROMPT = """You are a Master Debate Judge scoring a 1v1 debate performance.
Evaluate the user's debate performance based on argument logic, rebuttal sharpness, delivery poise, and filler word control.

Analyze the debate transcript below and return the evaluation scorecard in structured JSON format.
"""
