from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Life-OS"
    environment: str = "local"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://life_os:life_os@localhost:5432/life_os"
    redis_url: str = "redis://localhost:6379/0"
    short_term_ttl_seconds: int = 3600
    short_term_max_messages: int = 20
    consolidation_turn_threshold: int = 10
    openai_api_key: str | None = None
    openai_chat_model: str = "gpt-4o-mini"
    openai_summary_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
