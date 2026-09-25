import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Mshauri Kiswahili Backend"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Database Configuration (Neon PostgreSQL or SQLite fallback)
    DATABASE_URL: str = "postgresql://neondb_owner:npg_gS8RCOhpTYK3@ep-soft-fog-b5gas5gq.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    # Gemini API settings
    GEMINI_API_KEY: str = "AIzaSyDzGMRdNTzGIfywesPmqKEUa1Uo87_Z5tY"
    GEMINI_MODEL: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
