from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = Field(default="DevOps Practice API")
    app_env: str = Field(default="local")
    log_level: str = Field(default="INFO")

    database_url: str = Field(
        default="postgresql+psycopg://devops:devops@localhost:5432/devops_practice"
    )

    startup_delay_seconds: int = Field(default=0, ge=0, le=120)
    fail_readiness: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
