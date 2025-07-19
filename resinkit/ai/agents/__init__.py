"""
AI Agents package for ResinKit.

This package contains specialized AI agent workflows for different tasks,
built using LlamaIndex Workflows framework with MCP server integration.
"""

from .http_mcp_client import HTTPMCPClient
from .mcp_defaults import create_mcp_manager_with_defaults
from .mcp_manager import MCPManager
from .mcp_types import MCPServerConfig, MCPServerType
from .sql_generator_workflow import SqlGeneratorWorkflow, generate_sql_with_workflow

__all__ = [
    "SqlGeneratorWorkflow",
    "generate_sql_with_workflow",
    "MCPManager",
    "MCPServerConfig",
    "MCPServerType",
    "HTTPMCPClient",
    "create_mcp_manager_with_defaults",
]
