from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to *this file*, not the working directory
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    DATABASE_URL: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    CHROMA_DB_PATH: str = "./chroma_db"
    SQL_ECHO: bool = False

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()