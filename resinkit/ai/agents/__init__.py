"""
AI Agents package for ResinKit.

This package contains specialized AI agent workflows for different tasks,
built using LlamaIndex Workflows framework with MCP server integration.
"""

from resinkit.ai.agents.http_mcp_client import HTTPMCPClient
from resinkit.ai.agents.mcp_defaults import create_mcp_manager_with_defaults
from resinkit.ai.agents.mcp_manager import MCPManager
from resinkit.ai.agents.mcp_types import MCPServerConfig, MCPServerType
from resinkit.ai.agents.sql_generator_workflow import (
    SqlGeneratorWorkflow,
    generate_sql_with_workflow,
)

__all__ = [
    "SqlGeneratorWorkflow",
    "generate_sql_with_workflow",
    "MCPManager",
    "MCPServerConfig",
    "MCPServerType",
    "HTTPMCPClient",
    "create_mcp_manager_with_defaults",
]
