"""Configuration module for AI Backend (FastAPI)."""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "UnMute-Yourself AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # LLM Service
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")  # "ollama", "gemini", "openai"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    #LLM API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    #Node.js Backend Integration
    NODE_BACKEND_URL: str = os.getenv("NODE_BACKEND_URL", "http://localhost:5000")
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        case_sensitive = True
        extra = "allow"

settings = Settings()
