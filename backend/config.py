"""Application configuration loaded from environment variables."""

from pathlib import Path
from pydantic_settings import BaseSettings

# Resolve project root (one level up from backend/)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Central configuration for the SEAM Assessment application."""

    # --- LLM Provider (OpenRouter) ---
    openai_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    llm_model: str = "openai/gpt-oss-120b:free"

    # --- Security ---
    app_secret_key: str = "dev-secret-change-me"
    consultant_password: str = "admin123"
    access_token_expire_minutes: int = 480  # 8 hours

    # --- Database ---
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'seam.db'}"

    # --- NLP Models ---
    spacy_model: str = "en_core_web_sm"
    sentence_transformer_model: str = "paraphrase-multilingual-MiniLM-L12-v2"

    # --- App ---
    app_title: str = "SEAM Assessment Chatbot"
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"


settings = Settings()
