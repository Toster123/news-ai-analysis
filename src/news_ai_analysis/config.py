# Настройка конфигурации проекта
from dataclasses import field

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class DatabaseConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    PASSWORD: str
    USER: str
    DB: str
    HOST: str
    PORT: int

    @property
    def db_url(self):
        return (f"postgresql+asyncpg://{self.USER}:{self.PASSWORD}@"
                f"{self.HOST}:{self.PORT}/{self.DB}")


class Config(BaseSettings):
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    DISABLE_LOCAL_MODELS: bool = field(default=True)

    @classmethod
    def load(cls) -> "Config":
        return cls()


config = Config().load()
