"""
PSICOVOZ - Configuracoes
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    WHISPER_MODEL: str = "tiny"  # tiny = mais rapido, base = mais preciso
    TTS_MODEL: str = "edge-tts"
    REDIS_URL: str = "redis://localhost:6379"
    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS: int = 1024

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
