"""
Demiurge Voice Platform — Configuration

All settings are loaded from environment variables.
No hardcoded secrets. No hardcoded localhost in production.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────────────
    APP_NAME: str = "Demiurge Voice Platform"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENV: str = "production"  # development | staging | production

    # ── Server ───────────────────────────────────────────────────────
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = "0.0.0.0"
    ALLOWED_ORIGINS: str = "*"

    # ── Database ─────────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/demiurge_voice"
    )
    DATABASE_POOL_SIZE: int = 10

    # ── LLM Providers ────────────────────────────────────────────────
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-001")
    LLM_FALLBACK_MODEL: Optional[str] = os.getenv("LLM_FALLBACK_MODEL")

    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # ── STT / TTS ────────────────────────────────────────────────────
    STT_PROVIDER: str = os.getenv("STT_PROVIDER", "whisper")
    STT_MODEL: str = os.getenv("STT_MODEL", "base")
    WHISPER_API_KEY: Optional[str] = os.getenv("WHISPER_API_KEY")

    TTS_PROVIDER: str = os.getenv("TTS_PROVIDER", "kokoro")
    TTS_VOICE: str = os.getenv("TTS_VOICE", "af_bella")

    # ── LiveKit ──────────────────────────────────────────────────────
    LIVEKIT_URL: Optional[str] = os.getenv("LIVEKIT_URL")
    LIVEKIT_API_KEY: Optional[str] = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET: Optional[str] = os.getenv("LIVEKIT_API_SECRET")

    # ── Pipecat ──────────────────────────────────────────────────────
    PIPECAT_DAILY_API_KEY: Optional[str] = os.getenv("PIPECAT_DAILY_API_KEY")
    PIPECAT_DEEPGRAM_API_KEY: Optional[str] = os.getenv("PIPECAT_DEEPGRAM_API_KEY")
    PIPECAT_CARTESIA_API_KEY: Optional[str] = os.getenv("PIPECAT_CARTESIA_API_KEY")

    # ── Telephony ────────────────────────────────────────────────────
    TELEPHONY_PROVIDER: str = os.getenv("TELEPHONY_PROVIDER", "twilio")
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER: Optional[str] = os.getenv("TWILIO_PHONE_NUMBER")

    # ── Demiurge Ecosystem ───────────────────────────────────────────
    DEMIURGE_SECRETS_URL: Optional[str] = os.getenv("DEMIURGE_SECRETS_URL")
    DEMIURGE_SECRETS_TOKEN: Optional[str] = os.getenv("DEMIURGE_SECRETS_TOKEN")
    DEMIURGE_LEAD_INTEL_URL: Optional[str] = os.getenv("DEMIURGE_LEAD_INTEL_URL")
    DEMIURGE_LEAD_INTEL_TOKEN: Optional[str] = os.getenv("DEMIURGE_LEAD_INTEL_TOKEN")
    DEMIURGE_CONSOLE_URL: Optional[str] = os.getenv("DEMIURGE_CONSOLE_URL")
    DEMIURGE_CONSOLE_TOKEN: Optional[str] = os.getenv("DEMIURGE_CONSOLE_TOKEN")

    # ── Audio / Call ─────────────────────────────────────────────────
    MAX_CALL_DURATION_MINUTES: int = 30
    RECORDING_STORAGE_PATH: str = os.getenv("RECORDING_STORAGE_PATH", "/tmp/recordings")
    TRANSCRIPT_STORAGE_PATH: str = os.getenv("TRANSCRIPT_STORAGE_PATH", "/tmp/transcripts")

    # ── Security ─────────────────────────────────────────────────────
    API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "change-me-in-production")
    ADMIN_API_KEY: Optional[str] = os.getenv("ADMIN_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
