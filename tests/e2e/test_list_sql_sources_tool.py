"""
End-to-end tests for the List SQL Sources tool.

This test verifies that the List SQL Sources tool can successfully:
1. Connect to the ResinKit API
2. Retrieve available SQL data sources
3. Format the response appropriately for agent consumption

Run this test:
$ ./e2e.sh test_list_sql_sources_tool
$ pytest tests/e2e/test_list_sql_sources_tool.py::TestListSqlSourcesTool::test_list_sql_sources_real_data -v --capture=no --tb=short
"""

import logging

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
        # Use a dummy access token since the tool requires authentication configured
        # even though the API itself doesn't require it
        update_settings(base_url=self.BASE_URL, access_token="dummy_token_for_e2e")

    def teardown_method(self):
        """Cleanup after each test"""
        # Reset settings to avoid affecting other tests
        reset_settings()

    def test_list_sql_sources_real_data(self):
        """Test listing SQL sources with real API data"""
        logger.info("Testing List SQL Sources tool with real data")

        # First, verify the API endpoint works directly
        response = self.get("/agent/sql/sources")
        self.assert_status_code(response, 200)
        api_sources = self.assert_json_response(response)

        logger.info(f"Direct API found {len(api_sources)} SQL sources")

        # Verify the expected data structure from curl response
        if api_sources:
            source = api_sources[0]
            expected_fields = [
                "name",
                "kind",
                "host",
                "port",
                "database",
                "user",
                "query_timeout",
                "extra_params",
                "created_at",
                "updated_at",
                "created_by",
            ]
            for field in expected_fields:
                assert field in source, f"SQL source should contain '{field}' field"

            logger.info(
                f"Example source: {source['name']} ({source['kind']}) at {source['host']}:{source['port']}"
            )

        # Now test the tool
        tool = ListSqlSourcesTool()
        result = tool._list_sql_sources()

        # Verify the result structure
        assert hasattr(result, "success"), "Result should have 'success' attribute"
        assert hasattr(result, "sources"), "Result should have 'sources' attribute"
        assert hasattr(result, "count"), "Result should have 'count' attribute"

        # Tool should succeed with real data
        assert result.success, f"Tool should succeed, but got error: {getattr(result, 'error_message', 'Unknown error')}"
        assert result.count == len(
            api_sources
        ), f"Tool count ({result.count}) should match API response ({len(api_sources)})"

        logger.info(f"✅ Tool successfully retrieved {result.count} SQL sources")

        # Verify source structure matches API data
        for i, source in enumerate(result.sources):
            api_source = api_sources[i]

            # Check that tool source has required attributes
            assert hasattr(source, "name"), "Source should have 'name' attribute"
            assert hasattr(source, "kind"), "Source should have 'kind' attribute"
            assert hasattr(source, "host"), "Source should have 'host' attribute"
            assert hasattr(source, "port"), "Source should have 'port' attribute"
            assert hasattr(
                source, "database"
            ), "Source should have 'database' attribute"

            # Verify values match API response
            assert (
                source.name == api_source["name"]
            ), f"Source name should match API data"
            assert (
                source.kind == api_source["kind"]
            ), f"Source kind should match API data"
            assert (
                source.host == api_source["host"]
            ), f"Source host should match API data"
            assert (
                source.port == api_source["port"]
            ), f"Source port should match API data"
            assert (
                source.database == api_source["database"]
            ), f"Source database should match API data"

            logger.info(
                f"  ✅ {source.name} ({source.kind}) at {source.host}:{source.port}/{source.database}"
            )

    def test_function_tool_interface_real_data(self):
        """Test the LlamaIndex FunctionTool interface with real data"""
        logger.info("Testing List SQL Sources FunctionTool interface with real data")

        # First get the expected data from direct API call
        response = self.get("/agent/sql/sources")
        self.assert_status_code(response, 200)
        api_sources = self.assert_json_response(response)

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
        response = function_tool.fn()

        # Verify response is a string (as expected by LlamaIndex)
        assert isinstance(response, str), "Function should return a string response"
        logger.info(f"Function tool response: {response}")

        # Verify response format based on actual data
        if api_sources:
            # Should have sources, verify the response mentions them
            assert "📋" in response, "Response should contain emoji formatting"
            assert (
                f"Found {len(api_sources)} SQL source" in response
            ), "Response should show correct count"

            # Verify each source is mentioned in the response
            for source in api_sources:
                assert (
                    source["name"] in response
                ), f"Response should mention source '{source['name']}'"
                assert (
                    source["kind"] in response
                ), f"Response should mention kind '{source['kind']}'"

            logger.info(
                f"✅ Tool successfully listed {len(api_sources)} SQL sources with proper formatting"
            )
        else:
            # No sources case
            assert (
                "No SQL sources are currently configured" in response
            ), "Response should indicate no sources"
            assert "📋" in response, "Response should contain emoji formatting"
            logger.info("✅ Tool successfully reported no sources configured")

    def test_tool_response_formatting(self):
        """Test that the tool properly formats response for different scenarios"""
        logger.info("Testing List SQL Sources tool response formatting")

        # Get actual API data
        response = self.get("/agent/sql/sources")
        self.assert_status_code(response, 200)
        api_sources = self.assert_json_response(response)

        # Create and test the tool
        tool = ListSqlSourcesTool()

        # Test the as_function_tool method
        function_tool = tool.as_function_tool()
        formatted_response = function_tool.fn()

        # Verify response structure and formatting
        assert isinstance(formatted_response, str), "Response should be a string"
        assert "📋" in formatted_response, "Response should contain emoji formatting"

        if api_sources:
            # With real data, verify proper formatting
            assert (
                f"Found {len(api_sources)} SQL source" in formatted_response
            ), "Should show correct count"

            # Verify each source appears in formatted output
            for source in api_sources:
                assert (
                    source["name"] in formatted_response
                ), f"Should mention source name '{source['name']}'"
                assert (
                    source["kind"] in formatted_response
                ), f"Should mention source kind '{source['kind']}'"
                assert (
                    f"{source['host']}:{source['port']}" in formatted_response
                ), "Should show host:port"

            logger.info(
                f"✅ Tool properly formatted response for {len(api_sources)} real SQL sources"
            )
        else:
            # No sources case
            assert (
                "No SQL sources" in formatted_response
            ), "Should indicate no sources when none exist"
            logger.info("✅ Tool properly formatted response for empty sources list")

    def test_tool_error_handling_invalid_config(self):
        """Test the tool's error handling with invalid configuration"""
        logger.info("Testing List SQL Sources tool error handling with invalid config")

        # Test with invalid base URL by temporarily updating settings
        original_settings = update_settings(base_url="http://invalid-url:9999")

        try:
            tool = ListSqlSourcesTool()
            result = tool._list_sql_sources()

            # Should fail gracefully with invalid URL
            assert not result.success, "Should fail with invalid base URL"
            assert hasattr(result, "error_message"), "Should have error message"
            logger.info(
                f"✅ Tool correctly handled invalid config: {result.error_message}"
            )

        finally:
            # Restore original settings
            update_settings(base_url=self.BASE_URL)

    def test_tool_integration_basic(self):
        """Test basic tool integration without complex dependencies"""
        logger.info("Testing basic tool integration")

        # Test tool creation
        sql_sources_tool = create_list_sql_sources_tool()

        # Verify tool properties
        assert (
            sql_sources_tool.metadata.name == "list_sql_sources"
        ), "Tool should have correct name"
        assert callable(sql_sources_tool.fn), "Tool function should be callable"

        # Test that tool can be called and returns string response
        response = sql_sources_tool.fn()
        assert isinstance(response, str), "Tool should return string response"
        assert len(response) > 0, "Response should not be empty"

        logger.info("✅ Tool integration basic test passed")

    def test_api_consistency(self):
        """Test that tool results are consistent with direct API calls"""
        logger.info("Testing API consistency between tool and direct calls")

        # Get data via direct API call
        api_response = self.get("/agent/sql/sources")
        self.assert_status_code(api_response, 200)
        api_data = self.assert_json_response(api_response)

        # Get data via tool
        tool = ListSqlSourcesTool()
        tool_result = tool._list_sql_sources()

        # Both should succeed
        assert tool_result.success, f"Tool should succeed like direct API call"

        # Data should be consistent
        assert tool_result.count == len(
            api_data
        ), "Tool count should match API response count"

        if api_data:
            # Verify source details match
            for i, api_source in enumerate(api_data):
                tool_source = tool_result.sources[i]
                assert (
                    tool_source.name == api_source["name"]
                ), "Source names should match"
                assert (
                    tool_source.kind == api_source["kind"]
                ), "Source kinds should match"
                assert (
                    tool_source.host == api_source["host"]
                ), "Source hosts should match"
                assert (
                    tool_source.port == api_source["port"]
                ), "Source ports should match"

        logger.info(f"✅ Tool and API data are consistent ({len(api_data)} sources)")
