from dataclasses import field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_")

    EMBEDDING_MODEL: str = field(default="Qwen/Qwen3-Embedding-0.6B")
    VECTOR_STORE_PATH: str = field(default="")

config = RAGConfig()