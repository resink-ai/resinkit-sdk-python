"""
MCP (Model Context Protocol) Integration for ResinKit AI Agents.

This module provides integration with MCP servers to dynamically load tools
and extend the capabilities of AI workflows. It serves as the main interface
for MCP functionality by importing from specialized modules.
"""

import logging

# Import from specialized modules
from resinkit.ai.agents.http_mcp_client import HTTPMCPClient
from resinkit.ai.agents.mcp_defaults import (
    DEFAULT_MCP_SERVERS,
    create_mcp_manager_with_defaults,
)
from resinkit.ai.agents.mcp_manager import MCPManager
from resinkit.ai.agents.mcp_types import MCPServerConfig, MCPServerType

logger = logging.getLogger(__name__)

# Export all the main components for backward compatibility
__all__ = [
    "MCPServerType",
    "MCPServerConfig",
    "HTTPMCPClient",
    "MCPManager",
    "DEFAULT_MCP_SERVERS",
    "create_mcp_manager_with_defaults",
]
