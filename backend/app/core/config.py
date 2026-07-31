from pathlib import Path
from pydantic import field_validator
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

    @field_validator("OPENAI_API_KEY", mode="before")
    @classmethod
    def sanitize_openai_api_key(cls, v: str) -> str:
        if isinstance(v, str):
            # Take only the first non-empty line if multiple lines were pasted into env var
            lines = [line.strip() for line in v.strip().splitlines() if line.strip()]
            if lines:
                key = lines[0].strip('"').strip("'")
                if " " in key:
                    key = key.split()[0]
                return key
        return v

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()