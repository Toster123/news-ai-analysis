from dataclasses import field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AssistantConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ASSISTANT_")

    MAX_QUERIES: int = field(default=5)
    MAX_K: int = field(default=20)

config = AssistantConfig()