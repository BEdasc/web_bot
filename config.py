"""Configuration management for the AI web reader."""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    target_url: str = Field(..., env="TARGET_URL")
    update_frequency: int = Field(60, env="UPDATE_FREQUENCY")
    chroma_persist_directory: str = Field("./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    verify_ssl: bool = Field(True, env="VERIFY_SSL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
