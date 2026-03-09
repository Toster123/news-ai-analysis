from pydantic_settings import BaseSettings, SettingsConfigDict


class RAGConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RAG_")

    EMBEDDING_MODEL: str
    VECTOR_STORE_PATH: str

config = RAGConfig()