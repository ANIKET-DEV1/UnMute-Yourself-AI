"""Centralized LLM Factory and Chains for AI Backend."""
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import settings
from app.core.prompts.gd import (
    GDRouterDecision,
    GDEvaluationScorecard,
    DIRECTOR_SYSTEM_PROMPT,
    EVALUATOR_SYSTEM_PROMPT,
)

# 1. Initialize Base Chat Model
llm = ChatOllama(
    model=settings.OLLAMA_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0.75,
)

# 2. Director Chain (Speaker Routing Decision)
director_llm = llm.with_structured_output(GDRouterDecision)
director_prompt = ChatPromptTemplate.from_messages([
    ("system", DIRECTOR_SYSTEM_PROMPT),
    ("human", "Recent Discussion:\n{chat_history}\n\nLast Speaker was: {last_speaker}\nWho should speak next?")
])
director_chain = director_prompt | director_llm

# 3. Agent Utterance Chain (Generates realistic student peer turn with breath pauses & fillers)
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "{persona_prompt}"),
    ("human", (
        "Topic: {topic}\n"
        "Recent Transcript:\n{chat_history}\n\n"
        "Your Directive This Turn: {intent}\n"
        "Speak your line casually, organically, and intelligently like a smart college student sitting at the table. "
        "Include natural thinking pauses (...) or vocal fillers like 'Um,', 'Oh,', 'Well,', 'Hmm,', 'Look,' when appropriate. "
        "Strictly 1 to 2 spoken sentences (never write essay paragraphs):"
    ))
])
agent_chain = agent_prompt | llm | StrOutputParser()

# 4. Evaluator Chain (Structured Output for final scorecard)
evaluator_llm = llm.with_structured_output(GDEvaluationScorecard)
evaluator_prompt = ChatPromptTemplate.from_messages([
    ("system", EVALUATOR_SYSTEM_PROMPT)
])
evaluator_chain = evaluator_prompt | evaluator_llm