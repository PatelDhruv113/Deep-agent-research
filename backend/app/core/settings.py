from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str

    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    MAX_CONCURRENT_AGENTS: int = 8
    MAX_SESSION_COST: float = 2.0
    MAX_AGENT_INVOCATIONS: int = 25
    MAX_CRITIC_ROUNDS: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()