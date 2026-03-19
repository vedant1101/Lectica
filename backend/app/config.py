from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"
    DATABASE_URL: str = ""
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    HF_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]
    EMBEDDING_DIM: int = 384
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CLAUDE_VISION_MODEL: str = "claude-sonnet-4-5"
    CLAUDE_FAST_MODEL: str = "claude-haiku-4-5-20251001"
    WHISPER_MODEL_SIZE: str = "base"

    class Config:
        env_file = ".env"


settings = Settings()