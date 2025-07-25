"""
LLM Manager for Pydantic AI Models

This module provides an LLMManager class that creates and manages pydantic-ai model instances
based on the configuration from resinkit.core.settings.
"""

import logging
import os
from typing import Any, Dict, Optional

from pydantic_ai.models import Model
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from resinkit.core.settings import LLMConfig, get_settings

logger = logging.getLogger(__name__)


class LLMManager:
    """
    Manager for creating and configuring pydantic-ai LLM models.

    This manager provides instance methods that return pydantic-ai model instances
    based on the LLM configuration from resinkit settings.
    """

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        Initialize the LLM Manager.

        Args:
            llm_config: Optional LLM configuration. If None, uses settings from get_settings()
        """
        self.llm_config = llm_config or get_settings().llm_config
        self._cached_models: Dict[str, Any] = {}

    def get_model(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> Model:
        """
        Get a pydantic-ai model instance based on configuration.

        Args:
            provider: LLM provider ("openai", "anthropic", "google"). Uses config default if None.
            model_name: Model name. Uses config default if None.
            temperature: Model temperature. Uses config default if None.
            max_tokens: Maximum tokens. Uses config default if None.
            api_key: API key for the provider. Auto-detected from environment if None.
            **kwargs: Additional provider-specific parameters

        Returns:
            Model: Configured pydantic-ai model instance

        Raises:
            ValueError: If provider is not supported or configuration is invalid
            ImportError: If required provider dependencies are not available
        """
        # Use provided values or fall back to config defaults
        provider = provider or self.llm_config.provider
        model_name = model_name or self.llm_config.model
        temperature = (
            temperature if temperature is not None else self.llm_config.temperature
        )
        max_tokens = (
            max_tokens if max_tokens is not None else self.llm_config.max_tokens
        )

        # Create cache key
        cache_key = (
            f"{provider}:{model_name}:{temperature}:{max_tokens}:{hash(str(kwargs))}"
        )

        # Return cached model if available
        if cache_key in self._cached_models:
            return self._cached_models[cache_key]

        # Create model based on provider
        if provider.lower() == "openai":
            model = self._create_openai_model(
                model_name, temperature, max_tokens, api_key, **kwargs
            )
        elif provider.lower() == "anthropic":
            model = self._create_anthropic_model(
                model_name, temperature, max_tokens, api_key, **kwargs
            )
        elif provider.lower() == "google":
            model = self._create_google_model(
                model_name, temperature, max_tokens, api_key, **kwargs
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

        # Cache and return model
        self._cached_models[cache_key] = model
        logger.debug(f"Created {provider} model: {model_name}")

        return model

    def _create_openai_model(
        self,
        model_name: str,
        temperature: float,
        max_tokens: int,
        api_key: Optional[str],
        **kwargs,
    ) -> OpenAIModel:
        """Create an OpenAI model instance."""
        # Auto-detect API key if not provided
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "OpenAI API key not provided and OPENAI_API_KEY environment variable not set"
                )

        # Create provider with configuration
        provider_kwargs = {"api_key": api_key, **kwargs}
        provider = OpenAIProvider(**provider_kwargs)

        # Create model settings
        settings = ModelSettings(temperature=temperature, max_tokens=max_tokens)

        # Create model
        return OpenAIModel(model_name, provider=provider, settings=settings)

    def _create_anthropic_model(
        self,
        model_name: str,
        temperature: float,
        max_tokens: int,
        api_key: Optional[str],
        **kwargs,
    ) -> AnthropicModel:
        """Create an Anthropic model instance."""
        # Auto-detect API key if not provided
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError(
                    "Anthropic API key not provided and ANTHROPIC_API_KEY environment variable not set"
                )

        # Create provider with configuration
        provider_kwargs = {"api_key": api_key, **kwargs}
        provider = AnthropicProvider(**provider_kwargs)

        # Create model settings
        settings = ModelSettings(temperature=temperature, max_tokens=max_tokens)

        # Create model
        return AnthropicModel(model_name, provider=provider, settings=settings)

    def _create_google_model(
        self,
        model_name: str,
        temperature: float,
        max_tokens: int,
        api_key: Optional[str],
        **kwargs,
    ) -> GoogleModel:
        """Create a Google model instance."""
        # Auto-detect API key if not provided
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "Google API key not provided and GOOGLE_API_KEY/GEMINI_API_KEY environment variable not set"
                )

        # Create provider with configuration
        provider_kwargs = {"api_key": api_key, **kwargs}
        provider = GoogleProvider(**provider_kwargs)

        # Create model settings
        settings = ModelSettings(temperature=temperature, max_tokens=max_tokens)

        # Create model
        return GoogleModel(model_name, provider=provider, settings=settings)

    def get_openai_model(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> OpenAIModel:
        """
        Get an OpenAI model instance.

        Args:
            model_name: OpenAI model name (e.g., "gpt-4o", "gpt-4o-mini")
            temperature: Model temperature
            max_tokens: Maximum tokens
            api_key: OpenAI API key
            **kwargs: Additional OpenAI-specific parameters

        Returns:
            OpenAIModel: Configured OpenAI model instance
        """
        return self.get_model(
            provider="openai",
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            **kwargs,
        )

    def get_anthropic_model(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> AnthropicModel:
        """
        Get an Anthropic model instance.

        Args:
            model_name: Anthropic model name (e.g., "claude-3-5-sonnet-latest")
            temperature: Model temperature
            max_tokens: Maximum tokens
            api_key: Anthropic API key
            **kwargs: Additional Anthropic-specific parameters

        Returns:
            AnthropicModel: Configured Anthropic model instance
        """
        return self.get_model(
            provider="anthropic",
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            **kwargs,
        )

    def get_google_model(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        api_key: Optional[str] = None,
        **kwargs,
    ) -> GoogleModel:
        """
        Get a Google model instance.

        Args:
            model_name: Google model name (e.g., "gemini-1.5-pro", "gemini-1.5-flash")
            temperature: Model temperature
            max_tokens: Maximum tokens
            api_key: Google API key
            **kwargs: Additional Google-specific parameters

        Returns:
            GoogleModel: Configured Google model instance
        """
        return self.get_model(
            provider="google",
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            **kwargs,
        )

    def update_config(self, llm_config: LLMConfig) -> None:
        """
        Update the LLM configuration and clear model cache.

        Args:
            llm_config: New LLM configuration
        """
        self.llm_config = llm_config
        self._cached_models.clear()
        logger.debug("LLM configuration updated and model cache cleared")

    def clear_cache(self) -> None:
        """Clear the model cache."""
        self._cached_models.clear()
        logger.debug("Model cache cleared")

    def get_available_providers(self) -> list[str]:
        """
        Get list of available LLM providers.

        Returns:
            list[str]: List of supported provider names
        """
        return ["openai", "anthropic", "google"]

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current LLM configuration.

        Returns:
            Dict[str, Any]: Configuration summary
        """
        return {
            "provider": self.llm_config.provider,
            "model": self.llm_config.model,
            "temperature": self.llm_config.temperature,
            "max_tokens": self.llm_config.max_tokens,
            "cached_models": len(self._cached_models),
            "available_providers": self.get_available_providers(),
        }


# Convenience functions for quick access
def get_default_model(
    provider: Optional[str] = None, model_name: Optional[str] = None, **kwargs
) -> Model:
    """
    Get a model instance using default configuration.

    Args:
        provider: LLM provider. Uses settings default if None.
        model_name: Model name. Uses settings default if None.
        **kwargs: Additional model parameters

    Returns:
        Model: Configured pydantic-ai model instance
    """
    manager = LLMManager()
    return manager.get_model(provider=provider, model_name=model_name, **kwargs)


def get_openai_model(**kwargs) -> OpenAIModel:
    """Get an OpenAI model with default configuration."""
    manager = LLMManager()
    return manager.get_openai_model(**kwargs)


def get_anthropic_model(**kwargs) -> AnthropicModel:
    """Get an Anthropic model with default configuration."""
    manager = LLMManager()
    return manager.get_anthropic_model(**kwargs)


def get_google_model(**kwargs) -> GoogleModel:
    """Get a Google model with default configuration."""
    manager = LLMManager()
    return manager.get_google_model(**kwargs)
