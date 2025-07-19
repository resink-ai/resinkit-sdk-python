"""
MCP (Model Context Protocol) Type Definitions and Configuration.

This module contains the core type definitions and configuration classes
for MCP server integration.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MCPServerType(str, Enum):
    """Types of MCP server connections."""

    STDIO = "stdio"  # Standard input/output (command-based)
    HTTP = "http"
    HTTP_SSE = "http_sse"


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server connection."""

    name: str = Field(..., description="Name identifier for the MCP server")
    server_type: MCPServerType = Field(
        default=MCPServerType.STDIO, description="Type of MCP server"
    )

    # STDIO-based server configuration
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
        if self.server_type == MCPServerType.STDIO and not self.command:
            raise ValueError("Command is required for STDIO-based MCP servers")
        elif (
            self.server_type in (MCPServerType.HTTP, MCPServerType.HTTP_SSE)
            and not self.url
        ):
            raise ValueError("URL is required for HTTP-based MCP servers")
