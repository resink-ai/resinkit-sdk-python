import os
from typing import Optional

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

_CURRENT_ENV = os.getenv("ENV", "dev")


class DeepSubModel(BaseModel):
    v4: str


class SubModel(BaseModel):
    v1: str
    v2: bytes
    v3: int
    deep: DeepSubModel


class LLMConfig(BaseModel):
    provider: str = "openai"  # openai, anthropic, google
    model: str = "gpt-4-turbo"
    temperature: float = 0.1
    max_tokens: int = 2000
    embedding_model: str = "text-embedding-ada-002"
    embedding_dimension: int = 1536


class Settings(BaseSettings):
    # Pydantic's internal mechanisms specifically look for a class variable named `model_config`
    # to determine the settings source.
    model_config = SettingsConfigDict(
        env_file=(".env.common", f".env.{_CURRENT_ENV}"),
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
    )

    sub_model: SubModel
    llm_config: LLMConfig = LLMConfig()


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
