"""
MCP (Model Context Protocol) Integration for ResinKit AI Agents.

This module provides integration with MCP servers to dynamically load tools
and extend the capabilities of AI workflows. It serves as the main interface
for MCP functionality by importing from specialized modules.
"""

import logging

# Import from specialized modules
from .http_mcp_client import HTTPMCPClient
from .mcp_defaults import DEFAULT_MCP_SERVERS, create_mcp_manager_with_defaults
from .mcp_manager import MCPManager
from .mcp_types import MCPServerConfig, MCPServerType

# Check for optional dependencies
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

# Export all the main components for backward compatibility
__all__ = [
    "MCPServerType",
    "MCPServerConfig",
    "HTTPMCPClient",
    "MCPManager",
    "DEFAULT_MCP_SERVERS",
    "create_mcp_manager_with_defaults",
    "MCP_AVAILABLE",
    "HTTPX_AVAILABLE",
]
