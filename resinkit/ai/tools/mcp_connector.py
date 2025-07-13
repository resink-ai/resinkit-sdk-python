"""
MCP Tools Connector for ResinKit

This module provides functionality to connect to ResinKit MCP service
and expose MCP tools as llama-index FunctionTool objects.
"""

from typing import List, Optional

from llama_index.core.tools.function_tool import FunctionTool
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

_sse_client = None


def get_sse_client():
    """Get the SSE client."""
    global _sse_client
    if _sse_client is None:
        _sse_client = BasicMCPClient(
            command_or_url="http://localhost:8603/mcp",
            headers={"X-ResinKit-Api-Token": "test-token"},
        )
    return _sse_client


def get_resinkit_mcp_tools(
    mcp_url: str = "http://localhost:8603/mcp",
    api_token: str = "test-token",
    allowed_tools: Optional[List[str]] = None,
) -> List[FunctionTool]:
    """
    Convenience function to get ResinKit MCP tools.

    Args:
        mcp_url: URL of the ResinKit MCP service
        api_token: API token for authentication
        allowed_tools: Optional list of tool names to filter

    Returns:
        List of LlamaIndex FunctionTool objects
    """
    tool_spec = McpToolSpec(
        get_sse_client(),
        allowed_tools=allowed_tools,
    )
    return tool_spec.to_tool_list()


async def get_resinkit_mcp_tools_async(
    mcp_url: str = "http://localhost:8603/mcp",
    api_token: str = "test-token",
    allowed_tools: Optional[List[str]] = None,
) -> List[FunctionTool]:
    """
    Async convenience function to get ResinKit MCP tools.

    Args:
        mcp_url: URL of the ResinKit MCP service
        api_token: API token for authentication
        allowed_tools: Optional list of tool names to filter

    Returns:
        List of LlamaIndex FunctionTool objects
    """
    tool_spec = McpToolSpec(
        get_sse_client(),
        allowed_tools=allowed_tools,
    )
    return await tool_spec.to_tool_list_async()
