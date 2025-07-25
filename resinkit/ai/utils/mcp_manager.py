"""
MCP Manager for Pydantic AI

This module provides an MCPManager class that manages MCP (Model Context Protocol)
server connections and toolsets across different transport types.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from pydantic_ai.mcp import (
    MCPServerSSE,
    MCPServerStdio,
    MCPServerStreamableHTTP,
    ProcessToolCallback,
    ToolDefinition,
)
from pydantic_ai.models import Model

from resinkit.core.settings import (
    MCPConfig,
    MCPManagerConfig,
    MCPSSEConfig,
    MCPStdioConfig,
    MCPStreamableHTTPConfig,
    get_settings,
)

logger = logging.getLogger(__name__)

# Type alias for MCP server instances
MCPServerInstance = Union[MCPServerStreamableHTTP, MCPServerSSE, MCPServerStdio]


class MCPManager:
    """
    Manager for MCP (Model Context Protocol) servers and toolsets.

    Supports all three MCP transport types:
    - Streamable HTTP Client
    - Server-Sent Events (SSE) Client
    - stdio Server
    """

    def __init__(
        self,
        config: Optional[MCPManagerConfig] = None,
        process_tool_call: Optional[ProcessToolCallback] = None,
        sampling_model: Optional[Model] = None,
    ):
        """
        Initialize the MCP Manager.

        Args:
            config: MCP manager configuration. Uses settings default if None.
            process_tool_call: Global tool call processor for all servers
            sampling_model: Model to use for sampling across all servers
        """
        self.config = config or get_settings().mcp_manager_config
        self.global_process_tool_call = process_tool_call
        self.global_sampling_model = sampling_model

        # Server instances and connection state
        self._servers: Dict[str, MCPServerInstance] = {}
        self._connected_servers: Dict[str, bool] = {}
        self._server_tools: Dict[str, List[ToolDefinition]] = {}
        self._connection_lock = asyncio.Lock()

    async def connect_server(
        self, server_name: str, config: Optional[MCPConfig] = None
    ) -> MCPServerInstance:
        """
        Connect to a specific MCP server.

        Args:
            server_name: Name of the server to connect
            config: Server configuration. Uses manager config if None.

        Returns:
            MCPServerInstance: Connected server instance

        Raises:
            ValueError: If server configuration not found
            ConnectionError: If connection fails
        """
        async with self._connection_lock:
            # Use provided config or get from manager config
            if config is None:
                if server_name not in self.config.servers:
                    raise ValueError(
                        f"Server '{server_name}' not found in configuration"
                    )
                config = self.config.servers[server_name]

            # Create server instance based on transport type
            server = self._create_server_instance(config)

            try:
                # Test connection by entering context
                await server.__aenter__()

                # Store server and mark as connected
                self._servers[server_name] = server
                self._connected_servers[server_name] = True

                # Load tools from server
                try:
                    tools = await server.list_tools()
                    self._server_tools[server_name] = tools
                    logger.info(
                        f"Connected to MCP server '{server_name}' with {len(tools)} tools"
                    )
                except Exception as e:
                    logger.warning(
                        f"Connected to server '{server_name}' but failed to list tools: {e}"
                    )
                    self._server_tools[server_name] = []

                return server

            except Exception as e:
                logger.error(f"Failed to connect to MCP server '{server_name}': {e}")
                raise ConnectionError(
                    f"Could not connect to MCP server '{server_name}': {e}"
                )

    def _create_server_instance(self, config: MCPConfig) -> MCPServerInstance:
        """Create an MCP server instance based on configuration."""

        # Common parameters for all server types
        common_params = {
            "tool_prefix": config.tool_prefix,
            "log_level": config.log_level,
            "timeout": config.timeout,
            "process_tool_call": self.global_process_tool_call,
            "allow_sampling": config.allow_sampling,
            "max_retries": config.max_retries,
            "sampling_model": self.global_sampling_model,
        }

        # Remove None values
        common_params = {k: v for k, v in common_params.items() if v is not None}

        if isinstance(config, MCPStreamableHTTPConfig):
            return MCPServerStreamableHTTP(
                url=config.url,
                headers=config.headers,
                sse_read_timeout=config.sse_read_timeout,
                **common_params,
            )

        elif isinstance(config, MCPSSEConfig):
            return MCPServerSSE(
                url=config.url,
                headers=config.headers,
                sse_read_timeout=config.sse_read_timeout,
                **common_params,
            )

        elif isinstance(config, MCPStdioConfig):
            return MCPServerStdio(
                command=config.command,
                args=config.args,
                env=config.env,
                cwd=config.cwd,
                **common_params,
            )

        else:
            raise ValueError(f"Unsupported MCP config type: {type(config)}")

    async def connect_all(self) -> Dict[str, bool]:
        """
        Connect to all configured servers.

        Returns:
            Dict[str, bool]: Map of server names to connection success status
        """
        results = {}

        for server_name in self.config.servers:
            try:
                await self.connect_server(server_name)
                results[server_name] = True
            except Exception as e:
                logger.error(f"Failed to connect to server '{server_name}': {e}")
                results[server_name] = False

        return results

    async def disconnect_server(self, server_name: str) -> None:
        """
        Disconnect from a specific MCP server.

        Args:
            server_name: Name of the server to disconnect
        """
        async with self._connection_lock:
            if server_name in self._servers:
                server = self._servers[server_name]
                try:
                    await server.__aexit__(None, None, None)
                except Exception as e:
                    logger.warning(
                        f"Error disconnecting from server '{server_name}': {e}"
                    )

                del self._servers[server_name]
                self._connected_servers[server_name] = False
                if server_name in self._server_tools:
                    del self._server_tools[server_name]

                logger.info(f"Disconnected from MCP server '{server_name}'")

    async def disconnect_all(self) -> None:
        """Disconnect from all connected servers."""
        server_names = list(self._servers.keys())
        for server_name in server_names:
            await self.disconnect_server(server_name)

    def get_server(self, server_name: str) -> Optional[MCPServerInstance]:
        """
        Get a connected server instance.

        Args:
            server_name: Name of the server

        Returns:
            MCPServerInstance: Server instance if connected, None otherwise
        """
        return self._servers.get(server_name)

    def get_connected_servers(self) -> List[str]:
        """
        Get list of connected server names.

        Returns:
            List[str]: Names of connected servers
        """
        return [
            name for name, connected in self._connected_servers.items() if connected
        ]

    def get_server_tools(self, server_name: str) -> List[ToolDefinition]:
        """
        Get tools available from a specific server.

        Args:
            server_name: Name of the server

        Returns:
            List[ToolDefinition]: Available tools from the server
        """
        return self._server_tools.get(server_name, [])

    def get_all_tools(self) -> Dict[str, List[ToolDefinition]]:
        """
        Get all tools from all connected servers.

        Returns:
            Dict[str, List[ToolDefinition]]: Map of server names to their tools
        """
        return dict(self._server_tools)

    def get_toolsets(self) -> List[MCPServerInstance]:
        """
        Get all connected server instances as toolsets for pydantic-ai agents.

        Returns:
            List[MCPServerInstance]: List of connected server instances
        """
        return list(self._servers.values())

    async def list_tools_from_server(self, server_name: str) -> List[ToolDefinition]:
        """
        Refresh and get tools from a specific server.

        Args:
            server_name: Name of the server

        Returns:
            List[ToolDefinition]: Updated tools from the server

        Raises:
            ValueError: If server not connected
        """
        if server_name not in self._servers:
            raise ValueError(f"Server '{server_name}' is not connected")

        server = self._servers[server_name]
        try:
            tools = await server.list_tools()
            self._server_tools[server_name] = tools
            return tools
        except Exception as e:
            logger.error(f"Failed to list tools from server '{server_name}': {e}")
            raise

    async def call_tool(self, server_name: str, tool_name: str, **kwargs) -> Any:
        """
        Call a tool on a specific server.

        Args:
            server_name: Name of the server
            tool_name: Name of the tool to call
            **kwargs: Tool arguments

        Returns:
            Any: Tool execution result

        Raises:
            ValueError: If server not connected
        """
        if server_name not in self._servers:
            raise ValueError(f"Server '{server_name}' is not connected")

        server = self._servers[server_name]
        try:
            result = await server.direct_call_tool(tool_name, kwargs)
            return result
        except Exception as e:
            logger.error(
                f"Failed to call tool '{tool_name}' on server '{server_name}': {e}"
            )
            raise

    def is_connected(self, server_name: str) -> bool:
        """
        Check if a server is connected.

        Args:
            server_name: Name of the server

        Returns:
            bool: True if connected, False otherwise
        """
        return self._connected_servers.get(server_name, False)

    def get_connection_status(self) -> Dict[str, bool]:
        """
        Get connection status for all configured servers.

        Returns:
            Dict[str, bool]: Map of server names to connection status
        """
        status = {}
        for server_name in self.config.servers:
            status[server_name] = self.is_connected(server_name)
        return status

    def get_manager_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the MCP manager state.

        Returns:
            Dict[str, Any]: Manager summary
        """
        return {
            "configured_servers": len(self.config.servers),
            "connected_servers": len(
                [s for s in self._connected_servers.values() if s]
            ),
            "total_tools": sum(len(tools) for tools in self._server_tools.values()),
            "connection_status": self.get_connection_status(),
            "server_tools": {
                name: len(tools) for name, tools in self._server_tools.items()
            },
            "auto_connect": self.config.auto_connect,
            "connection_timeout": self.config.connection_timeout,
        }

    async def __aenter__(self):
        """Async context manager entry."""
        if self.config.auto_connect:
            await self.connect_all()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        _ = exc_type, exc_val, exc_tb  # Required by protocol but not used
        await self.disconnect_all()


# Convenience functions
async def create_mcp_manager(
    config: Optional[MCPManagerConfig] = None, auto_connect: bool = True, **kwargs
) -> MCPManager:
    """
    Create and optionally connect an MCP manager.

    Args:
        config: MCP manager configuration
        auto_connect: Whether to auto-connect to all servers
        **kwargs: Additional MCPManager parameters

    Returns:
        MCPManager: Configured manager instance
    """
    manager = MCPManager(config=config, **kwargs)
    if auto_connect:
        await manager.connect_all()
    return manager


async def get_default_mcp_toolsets() -> List[MCPServerInstance]:
    """
    Get toolsets from the default MCP manager configuration.

    Returns:
        List[MCPServerInstance]: List of connected server instances
    """
    async with MCPManager() as manager:
        return manager.get_toolsets()
