"""
Agent Manager for AI Agents

This module provides an AgentManager class that manages agent instances,
LLM models, and MCP server connections for various AI agents.
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic_ai import Agent
from pydantic_ai.mcp import ProcessToolCallback

from resinkit.ai.utils import LLMManager, MCPManager
from resinkit.core.settings import AgentsConfig, get_settings

logger = logging.getLogger(__name__)


class AgentManager:
    """
    Manager for AI agents and their dependencies.

    This class manages:
    - LLM model instances via LLMManager
    - MCP server connections via MCPManager
    - Agent construction and lifecycle
    """

    def __init__(
        self,
        config: Optional[AgentsConfig] = None,
        llm_manager: Optional[LLMManager] = None,
        mcp_manager: Optional[MCPManager] = None,
        global_process_tool_call: Optional[ProcessToolCallback] = None,
    ):
        """
        Initialize the Agent Manager.

        Args:
            config: Agents configuration. Uses settings default if None.
            llm_manager: Pre-configured LLM manager. Creates new one if None.
            mcp_manager: Pre-configured MCP manager. Creates new one if None.
            global_process_tool_call: Global tool call processor for all agents
        """
        self.config = config or get_settings().agents_config
        self.global_process_tool_call = global_process_tool_call

        # Initialize managers
        self.llm_manager = llm_manager or LLMManager()
        self.mcp_manager = mcp_manager or MCPManager(
            process_tool_call=global_process_tool_call
        )

        # Agent instances cache
        self._sql_generation_agent: Optional[Agent] = None

        logger.info("AgentManager initialized")

    async def get_sql_generation_agent(self, **kwargs) -> Agent:
        """
        Get or create a SQL Generation Agent.

        Args:
            **kwargs: Additional agent configuration parameters

        Returns:
            Agent: Configured SQL generation agent
        """
        if self._sql_generation_agent is None:
            from .sql_gen_agent import create_sql_generation_agent

            # Get configured model for SQL agent using LLMManager directly
            llm_config = self.config.default_llm_config
            model = self.llm_manager.get_model(
                provider=llm_config.provider,
                model_name=llm_config.model,
                temperature=kwargs.get(
                    "temperature", self.config.sql_agent_temperature
                ),
                max_tokens=kwargs.get("max_tokens", self.config.sql_agent_max_tokens),
                **{
                    k: v
                    for k, v in kwargs.items()
                    if k
                    not in [
                        "temperature",
                        "max_tokens",
                        "system_prompt",
                    ]
                },
            )

            # Get MCP toolsets
            toolsets = self.mcp_manager.get_toolsets()

            # Create agent using the factory function
            self._sql_generation_agent = create_sql_generation_agent(
                model=model,
                toolsets=toolsets,
                system_prompt=kwargs.get("system_prompt"),
            )

            logger.info("SQL Generation Agent created")

        return self._sql_generation_agent

    async def connect_mcp_servers(self) -> Dict[str, bool]:
        """
        Connect to all configured MCP servers.

        Returns:
            Dict[str, bool]: Connection status for each server
        """
        if self.config.auto_connect_mcp:
            return await self.mcp_manager.connect_all()
        return {}

    def get_mcp_manager(self) -> MCPManager:
        """Get the MCP manager instance."""
        return self.mcp_manager

    def get_llm_manager(self) -> LLMManager:
        """Get the LLM manager instance."""
        return self.llm_manager

    def get_available_mcp_tools(self) -> Dict[str, List[Any]]:
        """
        Get all available MCP tools from connected servers.

        Returns:
            Dict[str, List[Any]]: Map of server names to their available tools
        """
        return self.mcp_manager.get_all_tools()

    def get_connected_servers(self) -> List[str]:
        """
        Get list of connected MCP server names.

        Returns:
            List[str]: Names of connected MCP servers
        """
        return self.mcp_manager.get_connected_servers()

    def get_manager_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the agent manager state.

        Returns:
            Dict[str, Any]: Manager state summary
        """
        mcp_summary = self.mcp_manager.get_manager_summary()

        return {
            "agents_config": {
                "auto_connect_mcp": self.config.auto_connect_mcp,
                "enable_tool_approval": self.config.enable_tool_approval,
                "sql_agent_auto_approve_tools": self.config.sql_agent_auto_approve_tools,
                "sql_agent_verbose": self.config.sql_agent_verbose,
            },
            "mcp_manager": mcp_summary,
            "active_agents": {
                "sql_generation_agent": self._sql_generation_agent is not None,
            },
            "llm_manager": {
                "cached_models": len(self.llm_manager._cached_models),
            },
        }

    async def cleanup(self):
        """Clean up resources and connections."""
        try:
            # Clean up agents
            if self._sql_generation_agent:
                self._sql_generation_agent = None

            # Disconnect MCP servers
            await self.mcp_manager.disconnect_all()

            # Clear LLM cache
            self.llm_manager.clear_cache()

            logger.info("AgentManager cleanup completed")

        except Exception as e:
            logger.warning(f"Error during AgentManager cleanup: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        if self.config.auto_connect_mcp:
            await self.connect_mcp_servers()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        _ = exc_type, exc_val, exc_tb  # Required by protocol but not used
        await self.cleanup()


# Convenience functions
async def create_agent_manager(
    config: Optional[AgentsConfig] = None, auto_connect_mcp: bool = True, **kwargs
) -> AgentManager:
    """
    Create and optionally connect an agent manager.

    Args:
        config: Agents configuration
        auto_connect_mcp: Whether to auto-connect to MCP servers
        **kwargs: Additional AgentManager parameters

    Returns:
        AgentManager: Configured manager instance
    """
    # Override config auto_connect if specified
    if config and auto_connect_mcp != config.auto_connect_mcp:
        import copy

        config = copy.deepcopy(config)
        config.auto_connect_mcp = auto_connect_mcp

    manager = AgentManager(config=config, **kwargs)

    if auto_connect_mcp:
        await manager.connect_mcp_servers()

    return manager


async def get_default_agent_manager() -> AgentManager:
    """
    Get a default agent manager instance with auto-connection.

    Returns:
        AgentManager: Default configured manager
    """
    async with AgentManager() as manager:
        return manager
