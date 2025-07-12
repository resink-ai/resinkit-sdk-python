import os
from typing import Any, List, Optional

from llama_index.core.agent.workflow import AgentWorkflow, FunctionAgent
from llama_index.core.base.llms.base import BaseLLM
from llama_index.llms.openai import OpenAI

from resinkit.ai.prompt import SQL_GENERATION_SYSTEM_PROMPT
from resinkit.core.settings import get_settings


class AgentManager:
    def __init__(self, tools: Optional[List[Any]] = None):
        self.settings = get_settings()
        self.tools = tools or []
        self._llm = None
        self._workflow = None

    def create_openai_llm(self) -> BaseLLM:
        return OpenAI(
            model=self.settings.llm_config.model,
            temperature=self.settings.llm_config.temperature,
            max_tokens=self.settings.llm_config.max_tokens,
        )

    def create_anthropic_llm(self) -> BaseLLM:
        try:
            from llama_index.llms.anthropic import Anthropic

            return Anthropic(
                model=self.settings.llm_config.model,
                temperature=self.settings.llm_config.temperature,
                max_tokens=self.settings.llm_config.max_tokens,
            )
        except ImportError:
            raise ImportError(
                "Anthropic LLM requires 'llama-index-llms-anthropic' package"
            )

    def create_google_llm(self) -> BaseLLM:
        try:
            from llama_index.llms.gemini import Gemini

            return Gemini(
                model=self.settings.llm_config.model,
                temperature=self.settings.llm_config.temperature,
                max_tokens=self.settings.llm_config.max_tokens,
            )
        except ImportError:
            raise ImportError(
                "Google Gemini LLM requires 'llama-index-llms-gemini' package"
            )

    def create_llm(self) -> BaseLLM:
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

    def get_agents(self) -> List[FunctionAgent]:
        return [
            FunctionAgent(
                name="DataEngineer",
                description="A data engineer agent that converts natural language queries into accurate SQL statements and manages database operations.",
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
        user_query = "What were the total sales for each product category in the last quarter?"
        response = await agent_manager.run_workflow(user_query)
        print(f"✓ Workflow executed successfully: {response}")
    except Exception as e:
        print(f"✗ Error running workflow: {e}")


# Example usage
if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
