"""
Default MCP Server Configurations.

This module contains default configurations for common MCP servers
including both STDIO (command-based) and HTTP-based servers.
"""

from .mcp_manager import MCPManager

# Default MCP server configurations
DEFAULT_MCP_SERVERS = {
    # STDIO-based servers
    "filesystem": {
        "server_type": "stdio",
        "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        "env": {},
        "timeout": 30.0,
        "enabled": False,  # Disabled by default
    },
    "sqlite": {
        "server_type": "stdio",
        "command": ["npx", "-y", "@modelcontextprotocol/server-sqlite", "database.db"],
        "env": {},
        "timeout": 30.0,
        "enabled": False,  # Disabled by default
    },
    "git": {
        "server_type": "stdio",
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
