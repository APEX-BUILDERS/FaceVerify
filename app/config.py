from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
FACES_DIR = STORAGE_DIR / "faces"
DB_PATH = STORAGE_DIR / "faceverify.sqlite3"


class Settings(BaseSettings):
    serpapi_api_key: str = ""
    app_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[1] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
