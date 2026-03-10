from pydantic_settings import BaseSettings, SettingsConfigDict


class AssistantConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ASSISTANT_")

    MAX_QUERIES: int
    MAX_K: int

config = AssistantConfig()