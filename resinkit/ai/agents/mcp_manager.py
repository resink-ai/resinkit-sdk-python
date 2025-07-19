"""
MCP Manager for handling multiple MCP server connections and tool loading.

This module provides the MCPManager class that handles connecting to multiple
MCP servers, loading tools, and managing the lifecycle of MCP connections.
"""

import asyncio
import logging
from typing import Any, Dict, List

from llama_index.core.tools import FunctionTool

from .http_mcp_client import HTTPMCPClient
from .mcp_types import MCPServerConfig, MCPServerType

try:
    from llama_index.tools.mcp import MCPToolSpec

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPToolSpec = None

logger = logging.getLogger(__name__)


class MCPManager:
    """
    Manager for MCP server connections and tool loading.

    This class handles connecting to multiple MCP servers, loading tools,
    and managing the lifecycle of MCP connections.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the MCP Manager.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.servers: Dict[str, MCPServerConfig] = {}
        self.connected_servers: Dict[str, Any] = {}
        self.loaded_tools: Dict[str, List[FunctionTool]] = {}

        if not MCP_AVAILABLE:
            logger.warning(
                "MCP integration not available. Install 'llama-index-tools-mcp' package for MCP support."
            )

    def add_server(self, config: MCPServerConfig) -> None:
        """
        Add an MCP server configuration.

        Args:
            config: MCP server configuration
        """
        self.servers[config.name] = config
        if self.verbose:
            logger.info(f"Added MCP server config: {config.name}")

    def add_server_from_dict(self, name: str, config_dict: Dict[str, Any]) -> None:
        """
        Add an MCP server from a dictionary configuration.

        Args:
            name: Server name
            config_dict: Configuration dictionary
        """
        config = MCPServerConfig(name=name, **config_dict)
        self.add_server(config)

    async def connect_server(self, server_name: str) -> bool:
        """
        Connect to a specific MCP server.

        Args:
            server_name: Name of the server to connect to

        Returns:
            True if connection successful, False otherwise
        """
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found in configuration")
            return False

        config = self.servers[server_name]
        if not config.enabled:
            logger.info(f"Server {server_name} is disabled, skipping connection")
            return False

        try:
            if config.server_type == MCPServerType.STDIO:
                # STDIO-based MCP server
                if not MCP_AVAILABLE:
                    logger.warning(
                        "MCP not available, cannot connect to STDIO-based servers"
                    )
                    return False

                mcp_tool_spec = MCPToolSpec(
                    command=config.command, env=config.env or None, raise_on_error=False
                )

                # Store the connected server
                self.connected_servers[server_name] = mcp_tool_spec

            elif config.server_type in (MCPServerType.HTTP, MCPServerType.HTTP_SSE):
                # HTTP-based MCP server
                http_client = HTTPMCPClient(
                    url=config.url, headers=config.headers, timeout=config.timeout
                )

                # Connect to the HTTP server
                if await http_client.connect():
                    self.connected_servers[server_name] = http_client
                else:
                    logger.error(f"Failed to connect to HTTP MCP server {server_name}")
                    return False

            else:
                logger.error(
                    f"Unsupported server type {config.server_type} for server {server_name}"
                )
                return False

            if self.verbose:
                logger.info(
                    f"Successfully connected to {config.server_type} MCP server: {server_name}"
                )

            return True

        except Exception as e:
            logger.error(f"Failed to connect to MCP server {server_name}: {e}")
            return False

    async def connect_all_servers(self) -> Dict[str, bool]:
        """
        Connect to all configured MCP servers.

        Returns:
            Dict mapping server names to connection success status
        """
        if not MCP_AVAILABLE:
            logger.warning("MCP not available, cannot connect to servers")
            return {}

        results = {}

        # Connect to servers concurrently
        connection_tasks = [
            self.connect_server(server_name) for server_name in self.servers.keys()
        ]

        if connection_tasks:
            connection_results = await asyncio.gather(
                *connection_tasks, return_exceptions=True
            )

            for server_name, result in zip(self.servers.keys(), connection_results):
                if isinstance(result, Exception):
                    logger.error(f"Exception connecting to {server_name}: {result}")
                    results[server_name] = False
                else:
                    results[server_name] = bool(result)

        if self.verbose:
            connected_count = sum(results.values())
            total_count = len(results)
            logger.info(f"Connected to {connected_count}/{total_count} MCP servers")

        return results

    async def load_tools_from_server(self, server_name: str) -> List[FunctionTool]:
        """
        Load tools from a specific MCP server.

        Args:
            server_name: Name of the server to load tools from

        Returns:
            List of FunctionTool instances
        """
        if server_name not in self.connected_servers:
            logger.error(f"Server {server_name} is not connected")
            return []

        if server_name not in self.servers:
            logger.error(f"Server {server_name} configuration not found")
            return []

        try:
            server_client = self.connected_servers[server_name]
            config = self.servers[server_name]

            if config.server_type == MCPServerType.STDIO:
                # STDIO-based MCP server
                if not MCP_AVAILABLE:
                    logger.warning(
                        "MCP not available, cannot load tools from STDIO-based servers"
                    )
                    return []

                # Get tools from the MCP server
                tools = server_client.to_tool_list()

            elif config.server_type in (MCPServerType.HTTP, MCPServerType.HTTP_SSE):
                # HTTP-based MCP server
                tools = await server_client.load_tools()

            else:
                logger.error(
                    f"Unsupported server type {config.server_type} for server {server_name}"
                )
                return []

            # Store loaded tools
            self.loaded_tools[server_name] = tools

            if self.verbose:
                logger.info(
                    f"Loaded {len(tools)} tools from {config.server_type} MCP server: {server_name}"
                )
                for tool in tools:
                    logger.info(f"  - {tool.metadata.name}")

            return tools

        except Exception as e:
            logger.error(f"Failed to load tools from MCP server {server_name}: {e}")
            return []

    async def load_all_tools(self) -> Dict[str, List[FunctionTool]]:
        """
        Load tools from all connected MCP servers.

        Returns:
            Dict mapping server names to their tools
        """
        if not MCP_AVAILABLE:
            logger.warning("MCP not available, cannot load tools")
            return {}

        # Load tools from all connected servers concurrently
        load_tasks = [
            self.load_tools_from_server(server_name)
            for server_name in self.connected_servers.keys()
        ]

        if load_tasks:
            load_results = await asyncio.gather(*load_tasks, return_exceptions=True)

            for server_name, result in zip(self.connected_servers.keys(), load_results):
                if isinstance(result, Exception):
                    logger.error(
                        f"Exception loading tools from {server_name}: {result}"
                    )
                    self.loaded_tools[server_name] = []
                elif isinstance(result, list):
                    self.loaded_tools[server_name] = result

        total_tools = sum(len(tools) for tools in self.loaded_tools.values())
        if self.verbose:
            logger.info(f"Loaded {total_tools} total tools from MCP servers")

        return self.loaded_tools.copy()

    def get_all_tools(self) -> List[FunctionTool]:
        """
        Get all loaded tools from all MCP servers.

        Returns:
            Combined list of all tools
        """
        all_tools = []
        for tools in self.loaded_tools.values():
            all_tools.extend(tools)
        return all_tools

    def get_tools_by_server(self, server_name: str) -> List[FunctionTool]:
        """
        Get tools from a specific server.

        Args:
            server_name: Name of the server

        Returns:
            List of tools from the specified server
        """
        return self.loaded_tools.get(server_name, [])

    async def disconnect_server(self, server_name: str) -> None:
        """
        Disconnect from a specific MCP server.

        Args:
            server_name: Name of the server to disconnect from
        """
        if server_name in self.connected_servers:
            try:
                # Clean up the connection
                server_client = self.connected_servers[server_name]

                # Check if it's an HTTP client and close appropriately
                if hasattr(server_client, "close"):
                    await server_client.close()
                elif hasattr(server_client, "aclose"):
                    await server_client.aclose()

                del self.connected_servers[server_name]

                # Remove loaded tools
                if server_name in self.loaded_tools:
                    del self.loaded_tools[server_name]

                if self.verbose:
                    logger.info(f"Disconnected from MCP server: {server_name}")

            except Exception as e:
                logger.error(f"Error disconnecting from MCP server {server_name}: {e}")

    async def disconnect_all_servers(self) -> None:
        """Disconnect from all MCP servers."""
        disconnect_tasks = [
            self.disconnect_server(server_name)
            for server_name in list(self.connected_servers.keys())
        ]

        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks, return_exceptions=True)

        if self.verbose:
            logger.info("Disconnected from all MCP servers")

    async def initialize_from_config(self, config: Dict[str, Any]) -> None:
        """
        Initialize MCP servers from a configuration dictionary.

        Args:
            config: Configuration dictionary with server definitions
        """
        # Add servers from config
        servers_config = config.get("mcp_servers", {})
        for server_name, server_config in servers_config.items():
            self.add_server_from_dict(server_name, server_config)

        # Connect to servers
        await self.connect_all_servers()

        # Load tools
        await self.load_all_tools()
