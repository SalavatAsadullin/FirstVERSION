from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", ".env.local"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="water-delivery-api", alias="APP_NAME")
    env: str = Field(default="dev", alias="ENV")
    debug: bool = Field(default=True, alias="DEBUG")

    database_url: str = Field(alias="DATABASE_URL")

    bot_token: str = Field(alias="BOT_TOKEN")

    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60 * 24 * 30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    operator_bootstrap_secret: str = Field(alias="OPERATOR_BOOTSTRAP_SECRET")

    price_per_bottle: int = Field(default=120, alias="PRICE_PER_BOTTLE")
    timezone: str = Field(default="Europe/Moscow", alias="TIMEZONE")


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    return AppSettings()  # type: ignore[arg-type]
