from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables where available.
    """

    APP_NAME: str = "Scam Detection API"
    ENVIRONMENT: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # URL reputation settings
    SUSPICIOUS_SHORT_DOMAINS: List[str] = [
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "goo.gl",
        "ow.ly",
        "is.gd",
        "buff.ly",
        "cutt.ly",
        "bit.do",
        "rebrand.ly",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance for reuse across the application.
    """

    return Settings()


settings = get_settings()
