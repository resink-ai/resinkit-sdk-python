"""
AI Agents package for ResinKit.

This package contains specialized AI agent workflows for different tasks,
built using LlamaIndex Workflows framework with MCP server integration.
"""

from .mcp_integration import (
    MCPManager,
    MCPServerConfig,
    create_mcp_manager_with_defaults,
)
from .sql_generator_workflow import SqlGeneratorWorkflow, generate_sql_with_workflow

__all__ = [
    "SqlGeneratorWorkflow",
    "generate_sql_with_workflow",
    "MCPManager",
    "MCPServerConfig",
    "create_mcp_manager_with_defaults",
]
