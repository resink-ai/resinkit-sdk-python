"""
LLM Manager Example

This example demonstrates how to use the LLMManager to create and manage
pydantic-ai model instances based on configuration from resinkit settings.

Requirements:
- API keys for desired providers (OpenAI, Anthropic, Google)
- pydantic-ai library (already included in dependencies)

Usage:
    python examples/llm_manager_example.py
"""

import os

from resinkit.ai.utils import (
    LLMManager,
    get_anthropic_model,
    get_default_model,
    get_openai_model,
)
from resinkit.core.settings import (
    ANTHROPIC_LLM_CONFIG,
    GOOGLE_LLM_CONFIG,
    OPENAI_LLM_CONFIG,
)


def demonstrate_llm_manager():
    """Demonstrate LLMManager capabilities."""
    print("🤖 LLM Manager Demo")
    print("=" * 50)

    # Create LLM Manager with default settings
    manager = LLMManager()

    print(f"\n📊 Default Configuration:")
    config = manager.get_config_summary()
    for key, value in config.items():
        print(f"  {key}: {value}")

    print(f"\n🔧 Available Providers: {manager.get_available_providers()}")

    # Test different provider configurations
    print(f"\n🧪 Testing Different Configurations:")

    configs = {
        "OpenAI": OPENAI_LLM_CONFIG,
        "Anthropic": ANTHROPIC_LLM_CONFIG,
        "Google": GOOGLE_LLM_CONFIG,
    }

    for name, config in configs.items():
        test_manager = LLMManager(config)
        summary = test_manager.get_config_summary()
        print(f"  {name}: {summary['provider']} / {summary['model']}")

    # Test model creation (will show warnings if API keys not set)
    print(f"\n🚀 Testing Model Creation:")

    # Test OpenAI
    try:
        if os.getenv("OPENAI_API_KEY"):
            openai_model = get_openai_model(model_name="gpt-4o-mini")
            print(f"  ✅ OpenAI model created: {type(openai_model).__name__}")
        else:
            print(f"  ⚠️  OpenAI: No API key set (OPENAI_API_KEY)")
    except Exception as e:
        print(f"  ❌ OpenAI error: {e}")

    # Test Anthropic
    try:
        if os.getenv("ANTHROPIC_API_KEY"):
            anthropic_model = get_anthropic_model(model_name="claude-3-5-sonnet-latest")
            print(f"  ✅ Anthropic model created: {type(anthropic_model).__name__}")
        else:
            print(f"  ⚠️  Anthropic: No API key set (ANTHROPIC_API_KEY)")
    except Exception as e:
        print(f"  ❌ Anthropic error: {e}")

    # Test Google
    try:
        if os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"):
            from resinkit.ai.utils import get_google_model

            google_model = get_google_model(model_name="gemini-1.5-flash")
            print(f"  ✅ Google model created: {type(google_model).__name__}")
        else:
            print(f"  ⚠️  Google: No API key set (GOOGLE_API_KEY or GEMINI_API_KEY)")
    except Exception as e:
        print(f"  ❌ Google error: {e}")

    # Test default model
    try:
        if any(
            os.getenv(key)
            for key in [
                "OPENAI_API_KEY",
                "ANTHROPIC_API_KEY",
                "GOOGLE_API_KEY",
                "GEMINI_API_KEY",
            ]
        ):
            default_model = get_default_model()
            print(f"  ✅ Default model created: {type(default_model).__name__}")
        else:
            print(f"  ⚠️  Default model: No API keys available")
    except Exception as e:
        print(f"  ❌ Default model error: {e}")


def demonstrate_advanced_usage():
    """Demonstrate advanced LLMManager features."""
    print(f"\n🔬 Advanced LLM Manager Features")
    print("=" * 50)

    # Create manager
    manager = LLMManager()

    # Test caching
    print(f"\n💾 Testing Model Caching:")
    print(f"  Cache size before: {manager.get_config_summary()['cached_models']}")

    # Create models with same parameters (should use cache)
    try:
        if os.getenv("ANTHROPIC_API_KEY"):
            model1 = manager.get_anthropic_model(model_name="claude-3-5-sonnet-latest")
            model2 = manager.get_anthropic_model(model_name="claude-3-5-sonnet-latest")
            print(f"  ✅ Two identical models created")
            print(
                f"  Cache size after: {manager.get_config_summary()['cached_models']}"
            )
            print(f"  Same instance: {model1 is model2}")
        else:
            print(f"  ⚠️  Caching test skipped: No ANTHROPIC_API_KEY")
    except Exception as e:
        print(f"  ❌ Caching test error: {e}")

    # Test cache clearing
    manager.clear_cache()
    print(f"  Cache size after clear: {manager.get_config_summary()['cached_models']}")

    # Test custom parameters
    print(f"\n⚙️  Testing Custom Parameters:")
    try:
        if os.getenv("ANTHROPIC_API_KEY"):
            custom_model = manager.get_model(
                provider="anthropic",
                model_name="claude-3-5-sonnet-latest",
                temperature=0.8,
                max_tokens=4000,
            )
            print(f"  ✅ Custom model created with temperature=0.8, max_tokens=4000")
        else:
            print(f"  ⚠️  Custom parameters test skipped: No ANTHROPIC_API_KEY")
    except Exception as e:
        print(f"  ❌ Custom parameters error: {e}")


def main():
    """Main demo function."""
    print("Welcome to the LLM Manager Demo!")
    print("This demo shows how to manage pydantic-ai models with configuration.")

    demonstrate_llm_manager()
    demonstrate_advanced_usage()

    print(f"\n🎉 Demo Complete!")
    print("\nTo use models with actual API calls:")
    print("1. Set your API keys in environment variables:")
    print("   - OPENAI_API_KEY for OpenAI models")
    print("   - ANTHROPIC_API_KEY for Anthropic models")
    print("   - GOOGLE_API_KEY or GEMINI_API_KEY for Google models")
    print("2. Use the LLMManager to create configured model instances")
    print("3. Pass the models to pydantic-ai Agents or use directly")


if __name__ == "__main__":
    main()
