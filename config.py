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

    # Crawler settings
    crawl_mode: str = Field("single", env="CRAWL_MODE")  # 'single' or 'full'
    max_pages: int = Field(100, env="MAX_PAGES")
    max_depth: int = Field(3, env="MAX_DEPTH")
    crawl_delay: float = Field(1.0, env="CRAWL_DELAY")
    same_domain_only: bool = Field(True, env="SAME_DOMAIN_ONLY")
    exclude_patterns: str = Field(".pdf,.jpg,.png,.gif,/admin,/login", env="EXCLUDE_PATTERNS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
