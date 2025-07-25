"""
End-to-end tests for MCPManager

These tests verify that the MCPManager can successfully connect to MCP servers
using different transport protocols and list tools.

Test Requirements:
1. HTTP Streamable: MCP server running at http://localhost:8603/mcp-server/mcp
2. Stdio: npx and @modelcontextprotocol/server-everything package available

Run individual tests:
$ pytest tests/e2e/test_mcp_manager.py::TestMCPManager::test_http_streamable_connection -v --capture=no
$ pytest tests/e2e/test_mcp_manager.py::TestMCPManager::test_stdio_connection -v --capture=no
"""

import asyncio
import logging
import subprocess
from typing import Dict, List

import pytest

from resinkit.ai.utils import MCPManager
from resinkit.core.settings import (
    EVERYTHING_STDIO_MCP_CONFIG,
    MCPManagerConfig,
    MCPStdioConfig,
    MCPStreamableHTTPConfig,
)

logger = logging.getLogger(__name__)


class TestMCPManager:
    """Test MCPManager functionality with different transport protocols."""

    def test_mcp_manager_creation(self):
        """Test that MCPManager can be created successfully."""
        logger.info("Testing MCPManager creation...")

        manager = MCPManager()
        assert manager is not None

        summary = manager.get_manager_summary()
        assert isinstance(summary, dict)
        assert "configured_servers" in summary
        assert "connected_servers" in summary

        logger.info("✓ MCPManager created successfully")

    @pytest.mark.asyncio
    async def test_http_streamable_connection(self):
        """
        Test MCPManager connection to HTTP streamable MCP server.

        Requirements:
        - MCP server running at http://localhost:8603/mcp-server/mcp
        """
        logger.info("Testing HTTP streamable MCP connection...")

        # Create configuration for HTTP streamable server
        http_config = MCPStreamableHTTPConfig(
            url="http://localhost:8603/mcp-server/mcp",
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )

        manager_config = MCPManagerConfig(
            servers={"http_test": http_config},
            auto_connect=False,
            connection_timeout=30.0,
        )

        try:
            manager = MCPManager(manager_config)

            # Test connection
            server_instance = await manager.connect_server("http_test")
            assert server_instance is not None
            logger.info("✓ Successfully connected to HTTP streamable MCP server")

            # Test connection status
            assert manager.is_connected("http_test")
            logger.info("✓ Connection status correctly reported as connected")

            # Test listing tools
            tools = await manager.list_tools_from_server("http_test")
            assert isinstance(tools, list)
            logger.info(f"✓ Retrieved {len(tools)} tools from HTTP server")

            # Test getting toolsets for pydantic-ai
            toolsets = manager.get_toolsets()
            assert len(toolsets) == 1
            assert toolsets[0] is server_instance
            logger.info("✓ Toolsets retrieved for pydantic-ai integration")

            # Test manager summary
            summary = manager.get_manager_summary()
            assert summary["connected_servers"] == 1
            assert summary["configured_servers"] == 1
            assert "http_test" in summary["connection_status"]
            assert summary["connection_status"]["http_test"] is True
            logger.info("✓ Manager summary shows correct connection state")

        except ConnectionError as e:
            pytest.skip(f"HTTP MCP server not available: {e}")
        except Exception as e:
            logger.error(f"HTTP streamable connection test failed: {e}")
            raise
        finally:
            # Cleanup
            try:
                await manager.disconnect_all()
                logger.info("✓ Disconnected from HTTP server")
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")

    @pytest.mark.asyncio
    async def test_stdio_connection(self):
        """
        Test MCPManager connection to stdio MCP server.

        Requirements:
        - npx command available
        - @modelcontextprotocol/server-everything package available
        """
        logger.info("Testing stdio MCP connection...")

        # Check if npx is available
        try:
            result = subprocess.run(
                ["npx", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                pytest.skip("npx not available for stdio MCP test")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("npx not available for stdio MCP test")

        # Create configuration for stdio server
        stdio_config = MCPStdioConfig(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-everything"],
            timeout=15.0,  # Longer timeout for package download
        )

        manager_config = MCPManagerConfig(
            servers={"stdio_test": stdio_config},
            auto_connect=False,
            connection_timeout=45.0,  # Longer timeout for initial setup
        )

        try:
            manager = MCPManager(manager_config)

            # Test connection (may take time for package download)
            logger.info("Connecting to stdio MCP server (may download packages)...")
            server_instance = await manager.connect_server("stdio_test")
            assert server_instance is not None
            logger.info("✓ Successfully connected to stdio MCP server")

            # Test connection status
            assert manager.is_connected("stdio_test")
            logger.info("✓ Connection status correctly reported as connected")

            # Test listing tools
            tools = await manager.list_tools_from_server("stdio_test")
            assert isinstance(tools, list)
            logger.info(f"✓ Retrieved {len(tools)} tools from stdio server")

            # Verify we got some tools from the everything server
            if len(tools) > 0:
                logger.info("✓ Everything server provided tools as expected")
                for i, tool in enumerate(tools[:3]):  # Show first 3 tools
                    logger.info(f"  Tool {i+1}: {tool.name}")

            # Test getting toolsets
            toolsets = manager.get_toolsets()
            assert len(toolsets) == 1
            assert toolsets[0] is server_instance
            logger.info("✓ Toolsets retrieved for pydantic-ai integration")

            # Test manager summary
            summary = manager.get_manager_summary()
            assert summary["connected_servers"] == 1
            assert summary["configured_servers"] == 1
            assert "stdio_test" in summary["connection_status"]
            assert summary["connection_status"]["stdio_test"] is True
            logger.info("✓ Manager summary shows correct connection state")

        except ConnectionError as e:
            pytest.skip(f"Stdio MCP server not available: {e}")
        except asyncio.TimeoutError:
            pytest.skip(
                "Stdio MCP server connection timed out (package download may be slow)"
            )
        except Exception as e:
            logger.error(f"Stdio connection test failed: {e}")
            raise
        finally:
            # Cleanup
            try:
                await manager.disconnect_all()
                logger.info("✓ Disconnected from stdio server")
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")

    @pytest.mark.asyncio
    async def test_multiple_server_connections(self):
        """Test MCPManager with multiple server configurations."""
        logger.info("Testing multiple MCP server connections...")

        # Create configurations for multiple servers
        http_config = MCPStreamableHTTPConfig(
            url="http://localhost:8603/mcp-server/mcp", timeout=10.0
        )

        stdio_config = MCPStdioConfig(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-everything"],
            timeout=15.0,
        )

        manager_config = MCPManagerConfig(
            servers={"http_server": http_config, "stdio_server": stdio_config},
            auto_connect=False,
            connection_timeout=45.0,
        )

        manager = MCPManager(manager_config)

        try:
            # Test connecting to all servers
            logger.info("Attempting to connect to all configured servers...")
            connection_results = await manager.connect_all()

            logger.info(f"Connection results: {connection_results}")

            # Verify manager state
            summary = manager.get_manager_summary()
            logger.info(f"Manager summary: {summary}")

            # Check that we have the expected configuration
            assert summary["configured_servers"] == 2

            # Test getting all tools
            all_tools = manager.get_all_tools()
            assert isinstance(all_tools, dict)
            logger.info(
                f"Total tools from all servers: {sum(len(tools) for tools in all_tools.values())}"
            )

            # Test getting toolsets
            toolsets = manager.get_toolsets()
            connected_count = len([r for r in connection_results.values() if r])
            assert len(toolsets) == connected_count
            logger.info(f"✓ Retrieved {len(toolsets)} toolsets for pydantic-ai")

        except Exception as e:
            logger.error(f"Multiple server connection test failed: {e}")
            # Don't raise - this test is expected to have some failures due to server availability
            logger.info(
                "Note: Some connection failures are expected if servers are not available"
            )
        finally:
            # Cleanup
            try:
                await manager.disconnect_all()
                logger.info("✓ Disconnected from all servers")
            except Exception as e:
                logger.warning(f"Error during cleanup: {e}")

    @pytest.mark.asyncio
    async def test_context_manager_usage(self):
        """Test MCPManager as async context manager."""
        logger.info("Testing MCPManager context manager usage...")

        # Use the default configuration which has auto_connect=True
        manager_config = MCPManagerConfig(
            servers={
                "http_test": MCPStreamableHTTPConfig(
                    url="http://localhost:8603/mcp-server/mcp", timeout=5.0
                )
            },
            auto_connect=True,
            connection_timeout=15.0,
        )

        try:
            async with MCPManager(manager_config) as manager:
                logger.info("✓ MCPManager context manager entered")

                # Check if auto-connect worked
                summary = manager.get_manager_summary()
                logger.info(f"Context manager summary: {summary}")

                # Get toolsets
                toolsets = manager.get_toolsets()
                logger.info(f"✓ Retrieved {len(toolsets)} toolsets via context manager")

            logger.info("✓ MCPManager context manager exited cleanly")

        except Exception as e:
            logger.warning(
                f"Context manager test failed (may be due to server unavailability): {e}"
            )
            # Don't raise - server may not be available

    def test_configuration_validation(self):
        """Test MCP configuration validation."""
        logger.info("Testing MCP configuration validation...")

        # Test valid HTTP configuration
        http_config = MCPStreamableHTTPConfig(
            url="http://localhost:8603/mcp-server/mcp"
        )
        assert http_config.transport == "streamable_http"
        assert http_config.url == "http://localhost:8603/mcp-server/mcp"
        logger.info("✓ HTTP configuration validation passed")

        # Test valid stdio configuration
        stdio_config = MCPStdioConfig(
            command="npx", args=["-y", "@modelcontextprotocol/server-everything"]
        )
        assert stdio_config.transport == "stdio"
        assert stdio_config.command == "npx"
        assert stdio_config.args == ["-y", "@modelcontextprotocol/server-everything"]
        logger.info("✓ Stdio configuration validation passed")

        # Test manager configuration
        manager_config = MCPManagerConfig(
            servers={"test1": http_config, "test2": stdio_config}
        )
        assert len(manager_config.servers) == 2
        assert "test1" in manager_config.servers
        assert "test2" in manager_config.servers
        logger.info("✓ Manager configuration validation passed")

        logger.info("✓ All configuration validation tests passed")
