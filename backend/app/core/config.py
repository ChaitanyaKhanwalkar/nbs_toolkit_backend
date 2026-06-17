"""Application settings loaded from environment variables.

Beginners: database settings should be changed in `backend/.env`, not by
editing Python code. Start by copying `backend/.env.example` to `backend/.env`.
Never put production Azure credentials in this repository.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the backend application."""

    app_name: str = Field(default="Narmada NbS Backend", alias="APP_NAME")
    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    # Comma-separated allowed CORS origins. Default "*" lets the Flutter web app
    # (which runs on a random localhost port, or via a Cloudflare tunnel) reach
    # the API during development. Set an explicit list for production.
    cors_allow_origins: str = Field(default="*", alias="CORS_ALLOW_ORIGINS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse the comma-separated CORS origins into a list."""

        raw = (self.cors_allow_origins or "").strip()
        if not raw or raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings so all modules read the same configuration."""

    return Settings()
