from dataclasses import field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_")

    MODEL_REPO: str = field(default="Qwen/Qwen3-8B-GGUF")
    MODEL: str = field(default="Qwen3-8B-Q4_K_M.gguf")

config = LLMConfig()