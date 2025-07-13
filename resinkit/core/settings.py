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


class EmbeddingConfig(BaseModel):
    provider: str = "google"  # google, openai
    model: str = "models/embedding-001"  # Google Gemini embedding model
    dimension: int = 768  # Google Gemini embedding dimension


class KnowledgeBaseConfig(BaseModel):
    persist_root_dir: str = "./knowledge_base_data"  # Root directory for knowledge base persistence
    auto_persist: bool = True  # Whether to automatically persist state after modifications


class LLMConfig(BaseModel):
    provider: str = "openai"  # openai, anthropic, google
    model: str = "gpt-4-turbo"
    temperature: float = 0.1
    max_tokens: int = 2000


# Predefined LLM configurations for different providers
OPENAI_LLM_CONFIG = LLMConfig(provider="openai", model="gpt-4o-mini", temperature=0.1, max_tokens=2000)

ANTHROPIC_LLM_CONFIG = LLMConfig(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    temperature=0.1,
    max_tokens=2000,
)

GOOGLE_LLM_CONFIG = LLMConfig(
    provider="google",
    model="gemini-1.5-flash",
    temperature=0.1,
    max_tokens=2000,
)


class Settings(BaseSettings):
    # Pydantic's internal mechanisms specifically look for a class variable named `model_config`
    # to determine the settings source.
    model_config = SettingsConfigDict(
        env_file=(".env.common", f".env.{_CURRENT_ENV}"),
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
    )

    sub_model: Optional[SubModel] = None

    llm_config: LLMConfig = LLMConfig()
    embedding_config: EmbeddingConfig = EmbeddingConfig()
    knowledge_base_config: KnowledgeBaseConfig = KnowledgeBaseConfig()


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
