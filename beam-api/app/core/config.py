from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../beam-config/env/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    PROJECT_NAME: str = "BEAM AI"
    PROJECT_VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    BACKEND_CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"]
    )

    POSTGRES_SERVER: str = "postgres"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "beam_db"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    LOG_LEVEL: str = "INFO"

    JWT_SECRET_KEY: SecretStr = Field(default=SecretStr("beam-ai-development-super-secret-key-2026"))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    JWT_ISSUER: str = "beam-api"

    # Analysis input limits
    MAX_ANALYSIS_TEXT_CHARS: int = Field(default=20000, gt=0)
    ANALYSIS_LIST_PAGE_SIZE_MAX: int = Field(default=100, gt=0)

    GEMINI_API_KEY: str = Field(default="")
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
