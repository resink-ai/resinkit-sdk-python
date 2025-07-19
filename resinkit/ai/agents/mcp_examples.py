"""
Example Usage of MCP Integration.

This module provides examples and demo functions for using MCP integration
with both STDIO (command-based) and HTTP MCP servers using BasicMCPClient.
"""

import asyncio

from llama_index.tools.mcp import BasicMCPClient

from resinkit.ai.agents.mcp_defaults import create_mcp_manager_with_defaults
from resinkit.ai.agents.mcp_types import MCPServerType


async def example_mcp_usage():
    """Example usage of MCP integration with both command and HTTP servers."""

    print("Initializing MCP Manager...")
    manager = await create_mcp_manager_with_defaults(verbose=True)

    # Example custom STDIO-based server configuration
    custom_command_config = {
        "server_type": "stdio",
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
        if config.server_type == MCPServerType.STDIO and config.command:
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


async def example_basic_mcp_client_usage():
    """Example of using BasicMCPClient directly (from LlamaIndex documentation)."""

    print("=== Direct BasicMCPClient Usage Examples ===\n")

    # Example configurations that would work with actual MCP servers
    examples = [
        {
            "name": "HTTP Streamable",
            "client": lambda: BasicMCPClient("https://example.com/mcp"),
            "description": "HTTP streamable MCP server",
        },
        {
            "name": "Server-Sent Events",
            "client": lambda: BasicMCPClient("https://example.com/sse"),
            "description": "Server-Sent Events MCP server",
        },
        {
            "name": "Local STDIO",
            "client": lambda: BasicMCPClient("python", args=["server.py"]),
            "description": "Local STDIO MCP server",
        },
    ]

    for example in examples:
        print(f"\n--- {example['name']} ---")
        print(f"Description: {example['description']}")

        try:
            client = example["client"]()
            print(f"✓ Created BasicMCPClient instance")

            # These would work with actual MCP servers
            print("Example operations (would require actual server):")
            print("  - tools = await client.list_tools()")
            print("  - result = await client.call_tool('calculate', {'x': 5, 'y': 10})")
            print("  - resources = await client.list_resources()")
            print("  - content, mime_type = await client.read_resource('config://app')")
            print("  - prompts = await client.list_prompts()")
            print(
                "  - prompt_result = await client.get_prompt('greet', {'name': 'World'})"
            )

            # Clean up
            if hasattr(client, "close"):
                await client.close()

        except Exception as e:
            print(f"✗ Error creating client: {e}")

    print("\n=== Integration with MCPManager ===")
    print("The MCPManager class now uses BasicMCPClient internally for all transports.")
    print(
        "This provides a unified interface regardless of whether you use STDIO, HTTP, or SSE."
    )


async def run_all_examples():
    """Run all MCP examples."""
    await example_mcp_usage()
    print("\n" + "=" * 80 + "\n")
    await example_basic_mcp_client_usage()


if __name__ == "__main__":
    asyncio.run(run_all_examples())
