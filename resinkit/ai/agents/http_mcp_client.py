"""
HTTP MCP Client for connecting to streamable MCP servers over HTTP.

This module provides an HTTP client implementation for the Model Context Protocol
that supports JSON-RPC 2.0 communication over HTTP/HTTPS.
"""

import logging
from typing import Any, Dict, List, Optional

from llama_index.core.tools import FunctionTool

try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

logger = logging.getLogger(__name__)


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
