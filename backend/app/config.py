"""PSICOVOZ - Configuracoes"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379"
    LOG_LEVEL: str = "INFO"
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS: int = 1024
    WHISPER_MODEL: str = "base"
    TTS_MODEL: str = "none"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
