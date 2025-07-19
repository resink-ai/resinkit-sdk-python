#!/usr/bin/env python3
"""
HTTP MCP Server Integration Example

This example demonstrates how to connect to HTTP-based streamable MCP servers
and use their tools in the SQL Generator Workflow.
"""

import argparse
import asyncio
import logging
import sys
from typing import Any, Dict

from resinkit.ai.agents import (
    MCPManager,
    MCPServerConfig,
    MCPServerType,
    SqlGeneratorWorkflow,
    generate_sql_with_workflow,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def example_http_mcp_connection():
    """Example 1: Direct HTTP MCP server connection."""
    print("\n" + "=" * 80)
    print("🔧 Example 1: HTTP MCP Server Connection")
    print("=" * 80)

    # Create MCP manager
    mcp_manager = MCPManager(verbose=True)

    # Configure HTTP MCP server
    http_server_config = MCPServerConfig(
        name="localhost_mcp",
        server_type=MCPServerType.HTTP,
        url="http://localhost:8603/mcp-server/mcp",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ResinKit-MCP-Client/1.0",
        },
        timeout=30.0,
        enabled=True,
    )

    mcp_manager.add_server(http_server_config)

    try:
        print(f"\n🔗 Connecting to HTTP MCP server: {http_server_config.url}")

        # Connect to the server
        success = await mcp_manager.connect_server("localhost_mcp")

        if success:
            print("✅ Successfully connected to HTTP MCP server")

            # Load tools from the server
            print("\n🛠️ Loading tools from HTTP MCP server...")
            tools = await mcp_manager.load_tools_from_server("localhost_mcp")

            print(f"📦 Loaded {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.metadata.name}: {tool.metadata.description}")

            # Test using tools (if any are available)
            if tools:
                print(f"\n🧪 Testing first tool: {tools[0].metadata.name}")
                try:
                    # This would call the actual tool - adjust parameters as needed
                    # result = await tools[0].call({"example_param": "test"})
                    # print(f"Tool result: {result}")
                    print("(Tool execution skipped in example)")
                except Exception as e:
                    print(f"Tool execution error: {e}")

        else:
            print("❌ Failed to connect to HTTP MCP server")
            print(
                "   Make sure the server is running at http://localhost:8603/mcp-server/mcp"
            )

    except Exception as e:
        print(f"❌ Connection error: {e}")

    finally:
        # Clean up
        await mcp_manager.disconnect_all_servers()
        print("\n🧹 Disconnected from MCP servers")


async def example_workflow_with_http_mcp():
    """Example 2: SQL Generator Workflow with HTTP MCP integration."""
    print("\n" + "=" * 80)
    print("🔧 Example 2: SQL Workflow with HTTP MCP")
    print("=" * 80)

    # MCP configuration for HTTP server
    mcp_config = {
        "mcp_servers": {
            "http_localhost": {
                "server_type": "http",
                "url": "http://localhost:8603/mcp-server/mcp",
                "headers": {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                "timeout": 30.0,
                "enabled": True,
            }
        }
    }

    query = "What are the total sales by region for Q4 2024?"

    try:
        print(f"\n📝 User Query: {query}")
        print(f"\n🔄 Running SQL workflow with HTTP MCP integration...")

        # Generate SQL using workflow with HTTP MCP servers
        result = await generate_sql_with_workflow(
            query=query, mcp_config=mcp_config, enable_mcp=True, verbose=True
        )

        print(f"\n🗄️ Generated SQL:")
        print(result.get("generated_sql", "No SQL generated"))

        print(f"\n📖 Explanation:")
        print(result.get("explanation", "No explanation available"))

        print(
            f"\n✅ Workflow Status: {'✓ Completed' if result.get('workflow_completed') else '✗ Failed'}"
        )

        # Show execution details
        details = result.get("execution_details", {})
        if details:
            print(f"\n🔍 Execution Details:")
            for key, value in details.items():
                print(f"   - {key}: {value}")

    except Exception as e:
        print(f"❌ Workflow error: {e}")


async def example_multiple_http_servers():
    """Example 3: Multiple HTTP MCP servers."""
    print("\n" + "=" * 80)
    print("🔧 Example 3: Multiple HTTP MCP Servers")
    print("=" * 80)

    mcp_manager = MCPManager(verbose=True)

    # Configure multiple HTTP servers
    servers = [
        {
            "name": "local_dev",
            "config": MCPServerConfig(
                name="local_dev",
                server_type=MCPServerType.HTTP,
                url="http://localhost:8603/mcp-server/mcp",
                headers={"Content-Type": "application/json"},
                enabled=True,
            ),
        }
    ]

    # Add all servers
    for server in servers:
        mcp_manager.add_server(server["config"])

    print(f"\n🖥️ Configured {len(servers)} HTTP MCP servers:")
    for server in servers:
        config = server["config"]
        status = "✓ Enabled" if config.enabled else "⚪ Disabled"
        print(f"   - {config.name} ({config.server_type.value}): {status}")
        print(f"     URL: {config.url}")

    try:
        # Connect to all servers
        print(f"\n🔗 Connecting to all servers...")
        results = await mcp_manager.connect_all_servers()

        connected = [name for name, success in results.items() if success]
        failed = [name for name, success in results.items() if not success]

        if connected:
            print(f"✅ Connected: {', '.join(connected)}")
        if failed:
            print(f"❌ Failed: {', '.join(failed)}")

        # Load tools from connected servers
        if connected:
            print(f"\n🛠️ Loading tools from connected servers...")
            all_tools = await mcp_manager.load_all_tools()

            total_tools = sum(len(tools) for tools in all_tools.values())
            print(f"📦 Total tools loaded: {total_tools}")

            for server_name, tools in all_tools.items():
                if tools:
                    print(f"   - {server_name}: {len(tools)} tools")
                    for tool in tools[:2]:  # Show first 2 tools
                        print(f"     * {tool.metadata.name}")
                    if len(tools) > 2:
                        print(f"     ... and {len(tools) - 2} more")

    except Exception as e:
        print(f"❌ Error: {e}")

    finally:
        await mcp_manager.disconnect_all_servers()
        print(f"\n🧹 All connections closed")


async def example_sql_generator_workflow_class():
    """Example 4: Using SqlGeneratorWorkflow class directly with HTTP MCP."""
    print("\n" + "=" * 80)
    print("🔧 Example 4: SqlGeneratorWorkflow Class with HTTP MCP")
    print("=" * 80)

    # MCP configuration for HTTP server
    mcp_config = {
        "mcp_servers": {
            "http_localhost": {
                "server_type": "http",
                "url": "http://localhost:8603/mcp-server/mcp",
                "headers": {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                "timeout": 30.0,
                "enabled": True,
            }
        }
    }

    query = "Show me the monthly revenue trend broken down by product category"

    try:
        print(f"\n📝 User Query: {query}")
        print(f"\n🔄 Creating SqlGeneratorWorkflow instance...")

        # Create workflow instance directly
        workflow = SqlGeneratorWorkflow(
            mcp_config=mcp_config, enable_mcp=True, verbose=True
        )

        print(f"✅ SqlGeneratorWorkflow instance created")

        # Get available tools (including MCP tools)
        print(f"\n🛠️ Loading available tools...")
        tools = await workflow.get_available_tools()
        print(f"📦 Total tools available: {len(tools)}")

        # Show some tool names
        if tools:
            print("🔧 Available tools:")
            for i, tool in enumerate(tools[:5]):  # Show first 5 tools
                print(f"   {i+1}. {tool.metadata.name}")
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more")

        print(f"\n🔄 Running workflow...")

        # Run the workflow
        result = await workflow.run(query)

        print(f"\n🗄️ Generated SQL:")
        print(result.get("generated_sql", "No SQL generated"))

        print(f"\n📖 Explanation:")
        print(result.get("explanation", "No explanation available"))

        print(
            f"\n✅ Workflow Status: {'✓ Completed' if result.get('workflow_completed') else '✗ Failed'}"
        )

        # Show execution details
        details = result.get("execution_details", {})
        if details:
            print(f"\n🔍 Execution Details:")
            for key, value in details.items():
                print(f"   - {key}: {value}")

    except Exception as e:
        print(f"❌ Workflow error: {e}")
        import traceback

        print(f"📊 Full traceback:")
        traceback.print_exc()


async def example_http_mcp_configuration():
    """Example 5: Different HTTP MCP server configurations."""
    print("\n" + "=" * 80)
    print("🔧 Example 5: HTTP MCP Configuration Examples")
    print("=" * 80)

    configurations = [
        {
            "name": "Basic HTTP",
            "config": {
                "server_type": "http",
                "url": "http://localhost:8603/mcp-server/mcp",
                "headers": {"Content-Type": "application/json"},
                "timeout": 30.0,
                "enabled": True,
            },
        }
    ]

    print("📋 Example HTTP MCP Server Configurations:")
    print()

    for i, example in enumerate(configurations, 1):
        print(f"{i}. {example['name']}:")
        config = example["config"]
        print(f"   Type: {config['server_type']}")
        print(f"   URL: {config['url']}")
        print(f"   Headers: {list(config['headers'].keys())}")
        print(f"   Timeout: {config['timeout']}s")
        print(f"   Enabled: {config['enabled']}")
        print()

    print("💡 To use these configurations:")
    print("   1. Update the URLs to point to your actual MCP servers")
    print("   2. Replace API keys and tokens with real credentials")
    print("   3. Set enabled=True for servers you want to use")
    print("   4. Adjust timeouts based on your server response times")


async def main(example_number: int | None = None):
    """Run HTTP MCP examples."""
    examples = [
        ("HTTP MCP Connection", example_http_mcp_connection),
        ("Workflow with HTTP MCP", example_workflow_with_http_mcp),
        ("Multiple HTTP Servers", example_multiple_http_servers),
        ("SqlGeneratorWorkflow Class", example_sql_generator_workflow_class),
        ("Configuration Examples", example_http_mcp_configuration),
    ]

    print("🚀 HTTP MCP Server Integration Examples")
    print("=" * 80)
    print("These examples demonstrate connecting to HTTP-based streamable MCP servers")
    print("and using their tools in the ResinKit SQL Generator Workflow.")

    if example_number is not None:
        # Run specific example
        if 1 <= example_number <= len(examples):
            name, example_func = examples[example_number - 1]
            print(f"\n🎯 Running Example {example_number}: {name}")
            print("=" * 80)

            try:
                await example_func()
                print(f"\n✅ Completed: {name}")
            except Exception as e:
                print(f"\n❌ Failed: {name} - {e}")
                logger.exception(f"Example {name} failed")
                return 1
        else:
            print(f"\n❌ Invalid example number: {example_number}")
            print(f"Valid range: 1-{len(examples)}")
            print("\nAvailable examples:")
            for i, (name, _) in enumerate(examples, 1):
                print(f"  {i}. {name}")
            return 1
    else:
        # Run all examples
        print(f"\n📋 Running all {len(examples)} examples:")
        for i, (name, _) in enumerate(examples, 1):
            print(f"  {i}. {name}")

        for i, (name, example_func) in enumerate(examples, 1):
            try:
                print(f"\n🎯 Running Example {i}: {name}")
                print("-" * 60)
                await example_func()
                print(f"✅ Completed Example {i}: {name}")
            except Exception as e:
                print(f"❌ Failed Example {i}: {name} - {e}")
                logger.exception(f"Example {name} failed")

        print("\n" + "=" * 80)
        print("🎉 All HTTP MCP examples completed!")

    print()
    print("📝 Notes:")
    print("   - Examples will fail if no actual MCP servers are running")
    print("   - Update URLs and credentials for real servers")
    print("   - The HTTP MCP client supports JSON-RPC 2.0 protocol")
    print("   - Server-Sent Events (SSE) support is included for streaming")
    print("=" * 80)

    return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="HTTP MCP Server Integration Examples",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python http_mcp_example.py                    # Run all examples
  python http_mcp_example.py --example 1       # Run only example 1
  python http_mcp_example.py -e 4              # Run only example 4
  python http_mcp_example.py --list           # List available examples

Available Examples:
  1. HTTP MCP Connection
  2. Workflow with HTTP MCP  
  3. Multiple HTTP Servers
  4. SqlGeneratorWorkflow Class
  5. Configuration Examples
        """,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-e",
        "--example",
        type=int,
        metavar="N",
        help="Run specific example number (1-5)",
    )
    group.add_argument(
        "-l", "--list", action="store_true", help="List available examples and exit"
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    # List examples and exit
    if args.list:
        print("Available HTTP MCP Examples:")
        print("=" * 40)
        examples = [
            "HTTP MCP Connection",
            "Workflow with HTTP MCP",
            "Multiple HTTP Servers",
            "SqlGeneratorWorkflow Class",
            "Configuration Examples",
        ]
        for i, name in enumerate(examples, 1):
            print(f"  {i}. {name}")
        print("\nUsage:")
        print("  python http_mcp_example.py --example N  # Run specific example")
        print("  python http_mcp_example.py             # Run all examples")
        sys.exit(0)

    # Run the examples
    try:
        exit_code = asyncio.run(main(args.example))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Examples interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")
        logger.exception("Examples execution failed")
        sys.exit(1)
