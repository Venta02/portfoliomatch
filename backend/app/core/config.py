"""Application configuration using pydantic-settings."""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    github_token: str = ""
    gemini_api_key: str = ""
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    gemini_model: str = "gemini-flash-lite-latest"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def github_available(self) -> bool:
        return bool(self.github_token and self.github_token != "ghp_your_token_here")

    @property
    def gemini_available(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key != "your_gemini_key_here")


settings = Settings()
