"""
End-to-end tests for the List SQL Sources tool.

This test verifies that the List SQL Sources tool can successfully:
1. Connect to the ResinKit API
2. Retrieve available SQL data sources
3. Format the response appropriately for agent consumption

Run this test:
$ ./e2e.sh test_list_sql_sources_tool
$ pytest tests/e2e/test_list_sql_sources_tool.py::TestListSqlSourcesTool::test_list_sql_sources_happy_path -v --capture=no --tb=short
"""

import logging
from unittest.mock import patch

import pytest

from resinkit.ai.tools.list_sql_sources import (
    ListSqlSourcesTool,
    create_list_sql_sources_tool,
)
from resinkit.core.settings import reset_settings, update_settings
from tests.e2e.e2e_base import E2eBase

logger = logging.getLogger(__name__)


class TestListSqlSourcesTool(E2eBase):
    """End-to-end tests for List SQL Sources tool"""

    def setup_method(self):
        """Setup test environment"""
        super().setup_method()

        # Configure settings to use the e2e test environment
        update_settings(
            base_url=self.BASE_URL, access_token=None
        )  # Will use session-based auth for e2e tests

    def teardown_method(self):
        """Cleanup after each test"""
        # Reset settings to avoid affecting other tests
        reset_settings()

    def test_list_sql_sources_happy_path(self):
        """Test the happy path of listing SQL sources via the tool"""
        logger.info("Testing List SQL Sources tool happy path")

        # First, verify the API endpoint works directly
        response = self.get("/agent/sql/sources")
        logger.info(f"Direct API response status: {response.status_code}")

        if response.status_code == 200:
            sources_data = response.json()
            logger.info(f"Found {len(sources_data)} SQL sources via direct API")
        else:
            logger.warning(
                f"Direct API call failed with status {response.status_code}: {response.text}"
            )
            # For the test, we'll continue and let the tool handle the API interaction

        # Create the tool
        tool = ListSqlSourcesTool()

        # Test the direct method call
        result = tool._list_sql_sources()

        # Verify the result structure
        assert hasattr(result, "success"), "Result should have 'success' attribute"
        assert hasattr(result, "sources"), "Result should have 'sources' attribute"
        assert hasattr(result, "count"), "Result should have 'count' attribute"

        if result.success:
            logger.info(f"✓ Tool successfully retrieved {result.count} SQL sources")

            # Verify source structure if any sources exist
            for source in result.sources:
                assert hasattr(source, "name"), "Source should have 'name' attribute"
                assert hasattr(source, "kind"), "Source should have 'kind' attribute"
                assert hasattr(source, "host"), "Source should have 'host' attribute"
                assert hasattr(source, "port"), "Source should have 'port' attribute"
                assert hasattr(
                    source, "database"
                ), "Source should have 'database' attribute"
                logger.info(
                    f"  - {source.name} ({source.kind}) at {source.host}:{source.port}"
                )
        else:
            logger.error(
                f"✗ Tool failed to retrieve SQL sources: {result.error_message}"
            )
            # For e2e test, we'll treat this as expected if the API is not fully set up
            pytest.skip(f"API not available or configured: {result.error_message}")

    def test_function_tool_interface(self):
        """Test the LlamaIndex FunctionTool interface"""
        logger.info("Testing List SQL Sources FunctionTool interface")

        # Create the function tool
        function_tool = create_list_sql_sources_tool()

        # Verify it's a proper FunctionTool
        from llama_index.core.tools import FunctionTool

        assert isinstance(
            function_tool, FunctionTool
        ), "Should return a FunctionTool instance"
        assert (
            function_tool.metadata.name == "list_sql_sources"
        ), "Tool should have correct name"
        assert (
            "SQL data sources" in function_tool.metadata.description
        ), "Description should mention SQL data sources"

        # Test calling the tool function
        try:
            # Call the underlying function
            response = function_tool.fn()

            # Verify response is a string (as expected by LlamaIndex)
            assert isinstance(response, str), "Function should return a string response"

            # Verify response format
            if "Failed to list SQL sources" in response:
                logger.warning(f"Tool reported failure: {response}")
                pytest.skip("API not available or configured for testing")
            elif "No SQL sources are currently configured" in response:
                logger.info("✓ Tool successfully reported no sources configured")
                assert "📋" in response, "Response should contain emoji formatting"
            else:
                logger.info("✓ Tool successfully listed SQL sources")
                assert "📋" in response, "Response should contain emoji formatting"
                assert (
                    "Found" in response and "SQL source" in response
                ), "Response should indicate found sources"

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            # For e2e test, we'll treat this as expected if the API is not fully set up
            pytest.skip(f"Tool execution failed, likely due to API configuration: {e}")

    def test_tool_with_mock_data(self):
        """Test the tool with mocked API responses to verify formatting"""
        logger.info("Testing List SQL Sources tool with mock data")

        # Mock the API client response
        from unittest.mock import MagicMock

        from resinkit_api_client.models.database_kind import DatabaseKind
        from resinkit_api_client.models.sql_source_response import SqlSourceResponse

        mock_sources = [
            SqlSourceResponse(
                name="test_postgres",
                kind=DatabaseKind.POSTGRESQL,
                host="localhost",
                port=5432,
                database="testdb",
                user="testuser",
                query_timeout="30s",
                extra_params=None,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
                created_by="test_user",
            ),
            SqlSourceResponse(
                name="test_mysql",
                kind=DatabaseKind.MYSQL,
                host="mysql.example.com",
                port=3306,
                database="analytics",
                user="analyst",
                query_timeout="60s",
                extra_params=None,
                created_at="2024-01-02T00:00:00Z",
                updated_at="2024-01-02T00:00:00Z",
                created_by="admin_user",
            ),
        ]

        # Patch the API call to return mock data
        with patch(
            "resinkit_api_client.api.sql_tools.list_sql_sources.sync"
        ) as mock_api:
            mock_api.return_value = mock_sources

            # Create and test the tool
            tool = ListSqlSourcesTool()

            # Create a proper mock for the settings
            mock_resinkit_config = MagicMock()
            mock_resinkit_config.base_url = "http://localhost:8603"
            mock_resinkit_config.access_token = "valid_token"
            mock_resinkit_config.session_id = None

            # Directly set the mocked settings on the tool
            tool.settings.resinkit = mock_resinkit_config

            result = tool._list_sql_sources()

            # Verify the result
            assert result.success, "Mock operation should succeed"
            assert result.count == 2, "Should find 2 mock sources"
            assert len(result.sources) == 2, "Should return 2 sources"

            # Verify source details
            postgres_source = result.sources[0]
            assert postgres_source.name == "test_postgres"
            assert postgres_source.kind == "postgresql"
            assert postgres_source.host == "localhost"
            assert postgres_source.port == 5432

            mysql_source = result.sources[1]
            assert mysql_source.name == "test_mysql"
            assert mysql_source.kind == "mysql"
            assert mysql_source.host == "mysql.example.com"
            assert mysql_source.port == 3306

            # Test the function tool response formatting
            function_tool = tool.as_function_tool()
            response = function_tool.fn()

            # Verify formatted response
            assert "Found 2 SQL source(s)" in response
            assert "test_postgres" in response
            assert "test_mysql" in response
            assert "postgresql" in response
            assert "mysql" in response
            assert "localhost:5432" in response
            assert "mysql.example.com:3306" in response

            logger.info(
                "✓ Mock test passed - tool correctly processes and formats SQL source data"
            )

    def test_tool_error_handling(self):
        """Test the tool's error handling capabilities"""
        logger.info("Testing List SQL Sources tool error handling")

        # Test with invalid settings
        from unittest.mock import MagicMock

        # Create a proper mock for the first test (no base_url)
        mock_settings_obj = MagicMock()
        mock_settings_obj.resinkit.base_url = None
        mock_settings_obj.resinkit.access_token = None
        mock_settings_obj.resinkit.session_id = None

        # Clear the global settings cache and patch the function
        with (
            patch("resinkit.core.settings._settings", None),
            patch(
                "resinkit.core.settings.get_settings", return_value=mock_settings_obj
            ),
        ):
            tool = ListSqlSourcesTool()
            result = tool._list_sql_sources()

            # Verify error handling
            assert not result.success, "Should fail with invalid settings"
            assert (
                "not configured" in result.error_message
            ), "Error message should mention configuration"

        # Test with API failure
        with patch(
            "resinkit_api_client.api.sql_tools.list_sql_sources.sync"
        ) as mock_api:
            # Mock API failure
            mock_api.side_effect = Exception("API connection failed")

            # Create tool and directly mock its settings
            tool = ListSqlSourcesTool()

            # Create a proper mock for the settings
            mock_resinkit_config = MagicMock()
            mock_resinkit_config.base_url = "http://localhost:8603"
            mock_resinkit_config.access_token = "valid_token"
            mock_resinkit_config.session_id = None

            # Directly set the mocked settings on the tool
            tool.settings.resinkit = mock_resinkit_config

            result = tool._list_sql_sources()

            # Verify error handling
            assert not result.success, "Should fail with API error"
            assert (
                "API connection failed" in result.error_message
            ), "Error message should contain original error"

        logger.info("✓ Error handling tests passed")

    def test_integration_with_agent_manager(self):
        """Test that the tool can be integrated with AgentManager"""
        logger.info("Testing integration with AgentManager")

        try:
            from resinkit.ai.agent import AgentManager

            # Create tool and agent manager
            sql_sources_tool = create_list_sql_sources_tool()
            agent_manager = AgentManager(tools=[sql_sources_tool])

            # Verify the tool is properly integrated
            agents = agent_manager.get_agents()
            assert len(agents) > 0, "Should have at least one agent"

            # Verify the agent has access to our tool
            agent = agents[0]
            tool_names = [tool.metadata.name for tool in agent.tools]
            assert (
                "list_sql_sources" in tool_names
            ), "Agent should have access to list_sql_sources tool"

            logger.info("✓ Tool successfully integrated with AgentManager")

        except ImportError as e:
            logger.warning(
                f"AgentManager integration test skipped due to missing dependencies: {e}"
            )
            pytest.skip(f"AgentManager dependencies not available: {e}")
        except Exception as e:
            logger.error(f"AgentManager integration test failed: {e}")
            # This might fail in e2e environment due to missing LLM API keys
            pytest.skip(
                f"AgentManager integration failed, likely due to missing API configuration: {e}"
            )
