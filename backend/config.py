import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    LLM_PROVIDER: str = "gemini"
    GEMINI_API_KEY: str | None = None
    LOG_LEVEL: str = "INFO"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    KNOWLEDGE_BASE_PATH: str = os.path.join(BASE_DIR, "data", "knowledge.txt")
    VECTOR_DB_PATH: str = os.path.join(BASE_DIR, "faiss_index")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache()
def get_settings():
    return Settings()
