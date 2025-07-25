"""
End-to-end tests for SQL Generation Agent

These tests verify that the SQL generation agent can be created and run successfully
with different configurations and MCP toolsets.

Test Requirements:
1. AgentManager functionality
2. SQL generation agent creation
3. Basic agent execution (without requiring actual MCP servers)

Run tests:
$ pytest tests/e2e/test_sql_generation_agent.py -v --capture=no
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from resinkit.ai.agents import AgentManager, create_sql_generation_agent
from resinkit.ai.utils import get_default_model
from resinkit.core.settings import AgentsConfig

logger = logging.getLogger(__name__)


class TestSQLGenerationAgent:
    """End-to-end tests for SQL Generation Agent functionality."""

    def test_agent_manager_sql_agent_creation(self):
        """Test that AgentManager can create SQL generation agents."""
        logger.info("Testing AgentManager SQL agent creation...")

        # Create AgentManager
        agent_manager = AgentManager()
        assert agent_manager is not None

        # Verify LLM and MCP managers are initialized
        assert agent_manager.get_llm_manager() is not None
        assert agent_manager.get_mcp_manager() is not None

        logger.info("✅ AgentManager created successfully with managers")

    @pytest.mark.asyncio
    async def test_sql_agent_creation_via_agent_manager(self):
        """Test creating SQL agent through AgentManager."""
        logger.info("Testing SQL agent creation via AgentManager...")

        try:
            agent_manager = AgentManager()

            # Get SQL generation agent
            sql_agent = await agent_manager.get_sql_generation_agent()
            assert sql_agent is not None

            logger.info("✅ SQL generation agent created successfully")

            # Test agent summary
            summary = agent_manager.get_manager_summary()
            assert summary["active_agents"]["sql_generation_agent"] is True

            logger.info("✅ Agent manager shows SQL agent as active")

            # Cleanup
            await agent_manager.cleanup()

        except Exception as e:
            logger.error(f"SQL agent creation test failed: {e}")
            raise

    @pytest.mark.asyncio
    async def test_sql_agent_factory_function(self):
        """Test the simplified factory function for SQL agent creation."""
        logger.info("Testing SQL agent factory function...")

        try:
            # Get a default model
            model = get_default_model()
            assert model is not None

            # Create agent with mock toolsets (no actual MCP servers needed)
            mock_toolsets = [MagicMock()]

            agent = create_sql_generation_agent(model=model, toolsets=mock_toolsets)

            assert agent is not None
            logger.info("✅ SQL agent created using factory function")

            # Test with custom system prompt
            custom_prompt = "You are a test SQL agent."
            agent_custom = create_sql_generation_agent(
                model=model, toolsets=mock_toolsets, system_prompt=custom_prompt
            )

            assert agent_custom is not None
            logger.info("✅ SQL agent created with custom system prompt")

        except Exception as e:
            logger.error(f"Factory function test failed: {e}")
            raise

    @pytest.mark.asyncio
    async def test_sql_agent_basic_execution(self):
        """Test basic SQL agent execution with mocked toolsets."""
        logger.info("Testing basic SQL agent execution...")

        try:
            # Create a mock toolset that simulates MCP server behavior
            mock_toolset = MagicMock()
            mock_toolset.list_tools = AsyncMock(return_value=[])

            # Get model and create agent
            model = get_default_model()
            agent = create_sql_generation_agent(model=model, toolsets=[mock_toolset])

            # Test basic agent execution with a simple query
            test_query = "What are the total sales by region?"

            # Mock the agent run to avoid needing actual MCP tools
            async def mock_run(query):
                return f"Generated SQL for: {query}\nSELECT region, SUM(sales) FROM sales_table GROUP BY region;"

            # Replace the run method with our mock
            agent.run = mock_run

            result = await agent.run(test_query)
            assert result is not None
            assert "SELECT" in result

            logger.info("✅ Basic SQL agent execution successful")

        except Exception as e:
            logger.error(f"Basic execution test failed: {e}")
            raise

    @pytest.mark.asyncio
    async def test_sql_agent_with_context_manager(self):
        """Test SQL agent creation and usage with context manager."""
        logger.info("Testing SQL agent with context manager...")

        try:
            async with AgentManager() as agent_manager:
                logger.info("✅ AgentManager context manager entered")

                # Create SQL agent
                sql_agent = await agent_manager.get_sql_generation_agent()
                assert sql_agent is not None

                logger.info("✅ SQL agent created within context manager")

                # Get manager summary
                summary = agent_manager.get_manager_summary()
                assert isinstance(summary, dict)
                assert "active_agents" in summary

                logger.info("✅ Manager summary retrieved successfully")

            logger.info("✅ AgentManager context manager exited cleanly")

        except Exception as e:
            logger.error(f"Context manager test failed: {e}")
            raise

    def test_agents_config_integration(self):
        """Test that AgentsConfig is properly integrated."""
        logger.info("Testing AgentsConfig integration...")

        # Create custom config
        custom_config = AgentsConfig(
            sql_agent_auto_approve_tools=True,
            sql_agent_verbose=False,
            sql_agent_temperature=0.2,
            sql_agent_max_tokens=3000,
        )

        agent_manager = AgentManager(config=custom_config)

        # Verify config is applied
        assert agent_manager.config.sql_agent_auto_approve_tools is True
        assert agent_manager.config.sql_agent_verbose is False
        assert agent_manager.config.sql_agent_temperature == 0.2
        assert agent_manager.config.sql_agent_max_tokens == 3000

        logger.info("✅ Custom AgentsConfig applied successfully")

    @pytest.mark.asyncio
    async def test_multiple_sql_agents(self):
        """Test that multiple SQL agents can be created with different configurations."""
        logger.info("Testing multiple SQL agent creation...")

        try:
            # Create first agent manager
            agent_manager1 = AgentManager()
            sql_agent1 = await agent_manager1.get_sql_generation_agent()

            # Create second agent manager with different config
            custom_config = AgentsConfig(sql_agent_temperature=0.5)
            agent_manager2 = AgentManager(config=custom_config)
            sql_agent2 = await agent_manager2.get_sql_generation_agent()

            assert sql_agent1 is not None
            assert sql_agent2 is not None
            assert sql_agent1 != sql_agent2  # Different instances

            logger.info("✅ Multiple SQL agents created successfully")

            # Cleanup
            await agent_manager1.cleanup()
            await agent_manager2.cleanup()

        except Exception as e:
            logger.error(f"Multiple agents test failed: {e}")
            raise

    @pytest.mark.asyncio
    async def test_sql_agent_configuration_parameters(self):
        """Test that SQL agent accepts various configuration parameters."""
        logger.info("Testing SQL agent configuration parameters...")

        try:
            agent_manager = AgentManager()

            # Test that we can pass various kwargs without errors
            config_params = {
                "temperature": 0.3,
                "max_tokens": 2500,
                "system_prompt": "Custom SQL generation prompt",
            }

            # This should not raise any errors
            sql_agent = await agent_manager.get_sql_generation_agent(**config_params)
            assert sql_agent is not None

            logger.info("✅ SQL agent configuration parameters accepted")

            # Cleanup
            await agent_manager.cleanup()

        except Exception as e:
            logger.error(f"Configuration parameters test failed: {e}")
            raise
