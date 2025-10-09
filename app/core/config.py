from functools import lru_cache
from typing import List, Literal
import os

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Water Delivery API"
    environment: Literal["development", "staging", "production"] = "development"
    database_url: str = "sqlite:///./orders.db"
    allowed_origins: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def split_allowed_origins(cls, value):
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()