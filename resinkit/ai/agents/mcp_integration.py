"""
MCP (Model Context Protocol) Integration for ResinKit AI Agents.

This module provides integration with MCP servers to dynamically load tools
and extend the capabilities of AI workflows.
"""

import asyncio
import logging
from enum import Enum
from typing import Any, Dict, List, Optional

from llama_index.core.tools import FunctionTool
from pydantic import BaseModel, Field

try:
    from llama_index.tools.mcp import MCPToolSpec

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    MCPToolSpec = None

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)


class MCPServerType(str, Enum):
    """Types of MCP server connections."""

    COMMAND = "command"
    HTTP = "http"
    HTTP_SSE = "http_sse"


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server connection."""

    name: str = Field(..., description="Name identifier for the MCP server")
    server_type: MCPServerType = Field(
        default=MCPServerType.COMMAND, description="Type of MCP server"
    )

    # Command-based server configuration
    command: Optional[List[str]] = Field(
        default=None, description="Command to start the MCP server"
    )
    env: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="Environment variables"
    )

    # HTTP-based server configuration
    url: Optional[str] = Field(
        default=None, description="HTTP endpoint URL for the MCP server"
    )
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict, description="HTTP headers"
    )

    # Common configuration
    timeout: float = Field(default=30.0, description="Connection timeout in seconds")
    enabled: bool = Field(default=True, description="Whether this server is enabled")

    def model_post_init(self, __context: Any) -> None:
        """Validate configuration based on server type."""
        if self.server_type == MCPServerType.COMMAND and not self.command:
            raise ValueError("Command is required for command-based MCP servers")
        elif (
            self.server_type in (MCPServerType.HTTP, MCPServerType.HTTP_SSE)
            and not self.url
        ):
            raise ValueError("URL is required for HTTP-based MCP servers")


class HTTPMCPClient:
    """
    HTTP client for connecting to streamable MCP servers over HTTP.

    This class provides an interface similar to MCPToolSpec but for HTTP-based
    MCP servers that support streaming connections.
    """

    def __init__(
        self, url: str, headers: Optional[Dict[str, str]] = None, timeout: float = 30.0
    ):
        """
        Initialize the HTTP MCP client.

        Args:
            url: HTTP endpoint URL for the MCP server
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
        """
        self.url = url
        self.headers = headers or {}
        self.timeout = timeout
        self.client = None
        self._tools_cache = []

        if not HTTPX_AVAILABLE:
            raise ImportError(
                "httpx is required for HTTP MCP connections. Install with: pip install httpx"
            )

    async def connect(self) -> bool:
        """
        Connect to the HTTP MCP server.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = httpx.AsyncClient(timeout=self.timeout)

            # Test connection with a capabilities request
            response = await self.client.post(
                self.url,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "clientInfo": {
                            "name": "resinkit-mcp-client",
                            "version": "1.0.0",
                        },
                    },
                },
                headers=self.headers,
            )

            if response.status_code == 200:
                logger.info(f"Successfully connected to HTTP MCP server: {self.url}")
                return True
            else:
                logger.error(
                    f"Failed to connect to HTTP MCP server {self.url}: HTTP {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"Error connecting to HTTP MCP server {self.url}: {e}")
            return False

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the HTTP MCP server.

        Returns:
            List of tool definitions
        """
        if not self.client:
            logger.error("HTTP MCP client not connected")
            return []

        try:
            response = await self.client.post(
                self.url,
                json={"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
                headers=self.headers,
            )

            if response.status_code == 200:
                data = response.json()
                if "result" in data and "tools" in data["result"]:
                    return data["result"]["tools"]

            logger.warning(f"Failed to list tools from HTTP MCP server {self.url}")
            return []

        except Exception as e:
            logger.error(f"Error listing tools from HTTP MCP server {self.url}: {e}")
            return []

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on the HTTP MCP server.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        if not self.client:
            logger.error("HTTP MCP client not connected")
            return None

        try:
            response = await self.client.post(
                self.url,
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": name, "arguments": arguments},
                },
                headers=self.headers,
            )

            if response.status_code == 200:
                data = response.json()
                if "result" in data:
                    return data["result"]

            logger.warning(f"Failed to call tool {name} on HTTP MCP server {self.url}")
            return None

        except Exception as e:
            logger.error(
                f"Error calling tool {name} on HTTP MCP server {self.url}: {e}"
            )
            return None

    def to_tool_list(self) -> List[FunctionTool]:
        """
        Convert HTTP MCP tools to LlamaIndex FunctionTools.

        Returns:
            List of FunctionTool instances
        """
        return self._tools_cache

    async def load_tools(self) -> List[FunctionTool]:
        """
        Load tools from the HTTP MCP server and convert to FunctionTools.

        Returns:
            List of FunctionTool instances
        """
        tools_data = await self.list_tools()
        function_tools = []

        for tool_data in tools_data:
            try:
                # Create a FunctionTool from the MCP tool definition
                tool_name = tool_data.get("name", "unknown_tool")
                tool_description = tool_data.get(
                    "description", f"Tool from HTTP MCP server: {tool_name}"
                )

                # Create async function that calls the HTTP MCP server
                # Use closure to capture tool_name correctly
                def make_tool_function(name: str):
                    async def tool_function(**kwargs):
                        return await self.call_tool(name, kwargs)

                    return tool_function

                # Create the FunctionTool
                function_tool = FunctionTool.from_defaults(
                    fn=make_tool_function(tool_name),
                    name=tool_name,
                    description=tool_description,
                    async_fn=True,
                )

                function_tools.append(function_tool)

            except Exception as e:
                logger.error(
                    f"Error creating FunctionTool from HTTP MCP tool {tool_data}: {e}"
                )

        self._tools_cache = function_tools
        return function_tools

    async def close(self):
        """Close the HTTP client connection."""
        if self.client:
            await self.client.aclose()
            self.client = None


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
            if config.server_type == MCPServerType.COMMAND:
                # Command-based MCP server
                if not MCP_AVAILABLE:
                    logger.warning(
                        "MCP not available, cannot connect to command-based servers"
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

            if config.server_type == MCPServerType.COMMAND:
                # Command-based MCP server
                if not MCP_AVAILABLE:
                    logger.warning(
                        "MCP not available, cannot load tools from command-based servers"
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


# Default MCP server configurations
DEFAULT_MCP_SERVERS = {
    # Command-based servers
    "filesystem": {
        "server_type": "command",
        "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "env": {},
        "timeout": 30.0,
        "enabled": False,  # Disabled by default
    },
    "sqlite": {
        "server_type": "command",
        "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite", "database.db"],
        "env": {},
        "timeout": 30.0,
        "enabled": False,  # Disabled by default
    },
    "git": {
        "server_type": "command",
        "command": ["npx", "-y", "@modelcontextprotocol/server-git", "."],
        "env": {},
        "timeout": 30.0,
        "enabled": False,  # Disabled by default
    },
    # HTTP-based servers (examples)
    "http_mcp_localhost": {
        "server_type": "http",
        "url": "http://localhost:8603/mcp-server/mcp",
        "headers": {"Content-Type": "application/json", "Accept": "application/json"},
        "timeout": 30.0,
        "enabled": False,  # Disabled by default
    },
    "http_mcp_remote": {
        "server_type": "http",
        "url": "https://api.example.com/mcp/v1",
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer YOUR_API_KEY",
        },
        "timeout": 60.0,
        "enabled": False,  # Disabled by default
    },
}


async def create_mcp_manager_with_defaults(verbose: bool = False) -> MCPManager:
    """
    Create an MCP manager with default server configurations.

    Args:
        verbose: Enable verbose logging

    Returns:
        Configured MCPManager instance
    """
    manager = MCPManager(verbose=verbose)

    # Add default servers
    for server_name, config in DEFAULT_MCP_SERVERS.items():
        manager.add_server_from_dict(server_name, config)

    return manager


# Example usage for testing MCP integration
async def example_mcp_usage():
    """Example usage of MCP integration with both command and HTTP servers."""

    print("Initializing MCP Manager...")
    manager = await create_mcp_manager_with_defaults(verbose=True)

    # Example custom command-based server configuration
    custom_command_config = {
        "server_type": "command",
        "command": ["python", "-m", "custom_mcp_server"],
        "env": {"API_KEY": "test"},
        "timeout": 60.0,
        "enabled": False,  # Disabled for example
    }
    manager.add_server_from_dict("custom_command_server", custom_command_config)

    # Example HTTP MCP server configuration
    http_config = {
        "server_type": "http",
        "url": "http://localhost:8603/mcp-server/mcp",
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": "Bearer your-api-key",
        },
        "timeout": 30.0,
        "enabled": False,  # Disabled for example (would need actual server)
    }
    manager.add_server_from_dict("http_localhost", http_config)

    print(f"\nConfigured MCP Servers:")
    for name, config in manager.servers.items():
        status = "✓ Enabled" if config.enabled else "⚪ Disabled"
        server_type = config.server_type.value
        print(f"  - {name} ({server_type}): {status}")
        if config.server_type == MCPServerType.COMMAND and config.command:
            print(f"    Command: {' '.join(config.command[:3])}...")
        elif (
            config.server_type in (MCPServerType.HTTP, MCPServerType.HTTP_SSE)
            and config.url
        ):
            print(f"    URL: {config.url}")

    try:
        # Connect to servers (this will likely fail without actual MCP servers)
        print(f"\nConnecting to MCP servers...")
        results = await manager.connect_all_servers()

        connected_servers = [name for name, success in results.items() if success]
        failed_servers = [name for name, success in results.items() if not success]

        if connected_servers:
            print(f"✓ Connected servers: {', '.join(connected_servers)}")
        if failed_servers:
            print(f"✗ Failed connections: {', '.join(failed_servers)}")

        # Load tools from connected servers
        if connected_servers:
            print(f"\nLoading tools from connected servers...")
            tools = await manager.load_all_tools()

            total_tools = sum(len(tool_list) for tool_list in tools.values())
            print(f"Loaded {total_tools} tools total")

            for server_name, tool_list in tools.items():
                if tool_list:
                    print(f"  - {server_name}: {len(tool_list)} tools")
                    for tool in tool_list[:3]:  # Show first 3 tools
                        print(f"    * {tool.metadata.name}")
                    if len(tool_list) > 3:
                        print(f"    ... and {len(tool_list) - 3} more")

            # Get all tools
            all_tools = manager.get_all_tools()
            if all_tools:
                print(
                    f"\nAll available tools: {[tool.metadata.name for tool in all_tools]}"
                )
        else:
            print("\nNo servers connected, cannot load tools.")

    except Exception as e:
        print(f"Error during MCP operations: {e}")

    finally:
        # Clean up
        print(f"\nCleaning up connections...")
        await manager.disconnect_all_servers()
        print("✓ All connections closed.")


if __name__ == "__main__":
    asyncio.run(example_mcp_usage())
