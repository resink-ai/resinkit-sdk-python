import os
from typing import Any, Dict, List, Optional

from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.core.base.llms.base import BaseLLM
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

# Import LLM classes with try/except for optional dependencies
try:
    from llama_index.llms.anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    from llama_index.llms.google_genai import GoogleGenAI
except ImportError:
    GoogleGenAI = None

from resinkit.ai.prompt import SQL_GENERATION_SYSTEM_PROMPT
from resinkit.core.settings import get_settings


class AgentManager:
    def __init__(self, tools: Optional[List[Any]] = None):
        self.settings = get_settings()
        self.tools = tools or []
        self._llm = None
        self._workflow = None
        self._available_llms = self._get_available_llms()

    def _get_available_llms(self) -> Dict[str, Dict[str, Any]]:
        """Get available LLM models based on API key availability."""
        llms = {}

        # OpenAI models
        if os.getenv("OPENAI_API_KEY"):
            llms.update(
                {
                    "gpt-4o": {"provider": "openai", "model": "gpt-4o"},
                    "gpt-4o-mini": {"provider": "openai", "model": "gpt-4o-mini"},
                    "gpt-4-turbo": {"provider": "openai", "model": "gpt-4-turbo"},
                    "gpt-3.5-turbo": {"provider": "openai", "model": "gpt-3.5-turbo"},
                }
            )

        # Anthropic models
        if Anthropic is not None and os.getenv("ANTHROPIC_API_KEY"):
            llms.update(
                {
                    "claude-3-5-sonnet-20241022": {
                        "provider": "anthropic",
                        "model": "claude-3-5-sonnet-20241022",
                    },
                    "claude-3-haiku-20240307": {
                        "provider": "anthropic",
                        "model": "claude-3-haiku-20240307",
                    },
                    "claude-3-opus-20240229": {
                        "provider": "anthropic",
                        "model": "claude-3-opus-20240229",
                    },
                }
            )

        # Google Gemini models
        if GoogleGenAI is not None and os.getenv("GOOGLE_API_KEY"):
            llms.update(
                {
                    "models/gemini-1.5-pro": {
                        "provider": "google",
                        "model": "models/gemini-1.5-pro",
                    },
                    "models/gemini-1.5-flash": {
                        "provider": "google",
                        "model": "models/gemini-1.5-flash",
                    },
                    "models/gemini-pro": {
                        "provider": "google",
                        "model": "models/gemini-pro",
                    },
                }
            )

        return llms

    def get_available_llms(self) -> Dict[str, Dict[str, Any]]:
        """Get available LLM models."""
        return self._available_llms

    def create_openai_llm(self, model: str = None, temperature: float = 0.1) -> BaseLLM:
        model = model or self.settings.llm_config.model
        temperature = (
            temperature
            if temperature is not None
            else self.settings.llm_config.temperature
        )
        return OpenAI(
            model=model,
            temperature=temperature,
            max_tokens=self.settings.llm_config.max_tokens,
        )

    def create_anthropic_llm(
        self, model: str = None, temperature: float = 0.1
    ) -> BaseLLM:
        if Anthropic is None:
            raise ImportError(
                "Anthropic LLM requires 'llama-index-llms-anthropic' package"
            )
        model = model or self.settings.llm_config.model
        temperature = (
            temperature
            if temperature is not None
            else self.settings.llm_config.temperature
        )
        return Anthropic(
            model=model,
            temperature=temperature,
            max_tokens=self.settings.llm_config.max_tokens,
        )

    def create_google_llm(self, model: str = None, temperature: float = 0.1) -> BaseLLM:
        if GoogleGenAI is None:
            raise ImportError(
                "Google Gemini LLM requires 'llama-index-llms-google-genai' package"
            )
        model = model or self.settings.llm_config.model
        temperature = (
            temperature
            if temperature is not None
            else self.settings.llm_config.temperature
        )
        return GoogleGenAI(
            model=model,
            temperature=temperature,
            max_tokens=self.settings.llm_config.max_tokens,
        )

    def create_llm(self, model_name: str = None, temperature: float = None) -> BaseLLM:
        """Create LLM instance based on model name or settings."""
        if model_name:
            if model_name not in self._available_llms:
                raise ValueError(f"Model {model_name} not available")

            config = self._available_llms[model_name]
            provider = config["provider"]
            model = config["model"]

            if provider == "openai":
                return self.create_openai_llm(model, temperature)
            elif provider == "anthropic":
                return self.create_anthropic_llm(model, temperature)
            elif provider == "google":
                return self.create_google_llm(model, temperature)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        else:
            # Use settings-based creation
            provider = self.settings.llm_config.provider.lower()
            if provider == "openai":
                return self.create_openai_llm()
            elif provider == "anthropic":
                return self.create_anthropic_llm()
            elif provider == "google":
                return self.create_google_llm()
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")

    def get_llm(self) -> BaseLLM:
        if self._llm is None:
            self._llm = self.create_llm()
        return self._llm

    def create_function_agent(
        self,
        tools: Optional[List[FunctionTool]] = None,
        llm: Optional[BaseLLM] = None,
        system_prompt: str = "",
        verbose: bool = True,
    ) -> FunctionAgent:
        """Create a single FunctionAgent with specified tools and LLM."""
        agent_tools = tools or self.tools
        agent_llm = llm or self.get_llm()

        return FunctionAgent(
            tools=agent_tools,
            llm=agent_llm,
            system_prompt=system_prompt,
            verbose=verbose,
        )

    def get_agents(self) -> List[FunctionAgent]:
        return [
            FunctionAgent(
                name="AI Data Expert",
                description="A data expert who can use tools to accomplish data engineering or data science tasks as per user's request.",
                tools=self.tools,
                llm=self.get_llm(),
                system_prompt=SQL_GENERATION_SYSTEM_PROMPT,
                verbose=True,
            )
        ]

    def create_workflow(
        self, system_prompt: str = SQL_GENERATION_SYSTEM_PROMPT, verbose: bool = True
    ) -> AgentWorkflow:
        agents = self.get_agents()
        root_agent = agents[0].name if agents else None
        self._workflow = AgentWorkflow(
            agents=agents, root_agent=root_agent, verbose=verbose
        )
        return self._workflow

    def get_workflow(self) -> AgentWorkflow:
        if self._workflow is None:
            self._workflow = self.create_workflow()
        return self._workflow

    async def run_workflow(self, query: str) -> Any:
        workflow = self.get_workflow()
        return await workflow.run(user_msg=query)

    async def run_function_agent(
        self,
        query: str,
        tools: Optional[List[FunctionTool]] = None,
        model_name: str = None,
        system_prompt: str = "",
        verbose: bool = True,
    ) -> Any:
        """Run a single FunctionAgent with specified configuration."""
        llm = self.create_llm(model_name) if model_name else self.get_llm()
        agent = self.create_function_agent(
            tools=tools, llm=llm, system_prompt=system_prompt, verbose=verbose
        )

        # Use run() method and await the handler
        handler = agent.run(user_msg=query)
        result = await handler
        return result


async def main():
    agent_manager = AgentManager()

    # Test that we can create the workflow without errors
    try:
        workflow = agent_manager.get_workflow()
        print("✓ AgentWorkflow created successfully!")
        print(f"Workflow has {len(workflow.agents)} agent(s)")

        # Show agent details
        for name, agent in workflow.agents.items():
            print(f"Agent '{name}': {type(agent).__name__}")
            print(f"  Description: {agent.description[:80]}...")

    except Exception as e:
        print(f"✗ Error creating workflow: {e}")
        return

    try:
        user_query = (
            "What were the total sales for each product category in the last quarter?"
        )
        response = await agent_manager.run_workflow(user_query)
        print(f"✓ Workflow executed successfully: {response}")
    except Exception as e:
        print(f"✗ Error running workflow: {e}")


# Example usage
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
