from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()  # explicitly load .env before Settings initializes


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"

    langsmith_api_key: Optional[str] = None
    langsmith_tracing: bool = False
    langsmith_project: str = "med-checker"

    ocr_confidence_threshold: float = 0.55
    ocr_max_retries: int = 2

    low_confidence_routes_to_review: bool = True


settings = Settings()