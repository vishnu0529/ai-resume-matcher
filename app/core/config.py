from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    LLM_PROVIDER: str = "google"
    LLM_MODEL: str = "gemini-3.6-flash"
    MAX_RESUME_SIZE_MB: int = 5
    LOG_LEVEL: str = "INFO"
    RAG_TOP_K: int = 2
    RAG_MIN_SIMILARITY: float = 0.35

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

settings = Settings()
