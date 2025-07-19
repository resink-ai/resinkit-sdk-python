#!/usr/bin/env python3
"""
SQL Generator Workflow Example

This example demonstrates how to use the SQL Generator Workflow to convert
natural language queries into SQL statements using LlamaIndex Workflows
with MCP server integration.
"""

import asyncio
import logging
from typing import Any, Dict

from resinkit.ai.agents import (
    MCPManager,
    MCPServerConfig,
    SqlGeneratorWorkflow,
    generate_sql_with_workflow,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def example_basic_usage():
    """Example 1: Basic SQL generation without MCP."""
    print("\n" + "=" * 80)
    print("🔧 Example 1: Basic SQL Generation (No MCP)")
    print("=" * 80)

    query = "What were the total sales for each product category in the last quarter?"

    try:
        # Use the convenience function with MCP disabled
        result = await generate_sql_with_workflow(
            query=query, enable_mcp=False, verbose=True
        )

        print(f"\n📝 User Query:")
        print(f"   {query}")

        print(f"\n🗄️  Generated SQL:")
        print(result.get("generated_sql", "No SQL generated"))

        print(f"\n📖 Explanation:")
        print(result.get("explanation", "No explanation available"))

        print(
            f"\n✅ Workflow Status: {'✓ Completed' if result.get('workflow_completed') else '✗ Failed'}"
        )

    except Exception as e:
        print(f"❌ Error: {e}")


async def example_with_custom_mcp():
    """Example 2: SQL generation with custom MCP server configuration."""
    print("\n" + "=" * 80)
    print("🔧 Example 2: SQL Generation with Custom MCP Configuration")
    print("=" * 80)

    # Custom MCP server configuration
    mcp_config = {
        "mcp_servers": {
            "filesystem": {
                "command": [
                    "npx",
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "/tmp",
                ],
                "env": {},
                "timeout": 30.0,
                "enabled": False,  # Disabled for this example
            },
            "sqlite": {
                "command": [
                    "npx",
                    "-y",
                    "@modelcontextprotocol/server-sqlite",
                    "example.db",
                ],
                "env": {},
                "timeout": 30.0,
                "enabled": False,  # Disabled for this example
            },
        }
    }

    query = "Find the top 10 customers by total order value this year"

    try:
        result = await generate_sql_with_workflow(
            query=query, mcp_config=mcp_config, enable_mcp=True, verbose=True
        )

        print(f"\n📝 User Query:")
        print(f"   {query}")

        print(f"\n🛠️  MCP Configuration:")
        for server_name, config in mcp_config["mcp_servers"].items():
            status = "✓ Enabled" if config["enabled"] else "⚪ Disabled"
            print(f"   - {server_name}: {status}")

        print(f"\n🗄️  Generated SQL:")
        print(result.get("generated_sql", "No SQL generated"))

        print(f"\n📖 Explanation:")
        print(result.get("explanation", "No explanation available"))

        print(
            f"\n✅ Workflow Status: {'✓ Completed' if result.get('workflow_completed') else '✗ Failed'}"
        )

    except Exception as e:
        print(f"❌ Error: {e}")


async def example_direct_workflow_usage():
    """Example 3: Direct workflow instantiation and usage."""
    print("\n" + "=" * 80)
    print("🔧 Example 3: Direct Workflow Usage")
    print("=" * 80)

    query = "Show me the monthly revenue trend for the past 6 months with year-over-year comparison"

    try:
        # Create workflow instance directly
        workflow = SqlGeneratorWorkflow(
            enable_mcp=False,  # Disable MCP for this example
            verbose=True,
            timeout=120.0,
        )

        print(f"\n📝 User Query:")
        print(f"   {query}")

        print(f"\n🔄 Running workflow...")

        # Get available tools before running
        tools = await workflow.get_available_tools()
        print(f"\n🛠️  Available Tools: {len(tools)}")
        for tool in tools[:5]:  # Show first 5 tools
            print(f"   - {tool.metadata.name}")
        if len(tools) > 5:
            print(f"   ... and {len(tools) - 5} more")

        # Run the workflow
        result = await workflow.run(query)

        print(f"\n🗄️  Generated SQL:")
        print(result.get("generated_sql", "No SQL generated"))

        print(f"\n📖 Explanation:")
        print(result.get("explanation", "No explanation available"))

        print(f"\n🔍 Execution Details:")
        details = result.get("execution_details", {})
        for key, value in details.items():
            print(f"   - {key}: {value}")

        print(
            f"\n✅ Workflow Status: {'✓ Completed' if result.get('workflow_completed') else '✗ Failed'}"
        )

    except Exception as e:
        print(f"❌ Error: {e}")


async def example_mcp_manager_standalone():
    """Example 4: Standalone MCP Manager usage."""
    print("\n" + "=" * 80)
    print("🔧 Example 4: Standalone MCP Manager Usage")
    print("=" * 80)

    try:
        # Create MCP manager
        mcp_manager = MCPManager(verbose=True)

        # Add custom server configurations
        servers = [
            MCPServerConfig(
                name="test_filesystem",
                command=[
                    "npx",
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "/tmp",
                ],
                enabled=False,  # Disabled for this example
            ),
            MCPServerConfig(
                name="test_git",
                command=["npx", "-y", "@modelcontextprotocol/server-git", "."],
                enabled=False,  # Disabled for this example
            ),
        ]

        for server in servers:
            mcp_manager.add_server(server)

        print(f"\n🖥️  Configured MCP Servers:")
        for name, config in mcp_manager.servers.items():
            status = "✓ Enabled" if config.enabled else "⚪ Disabled"
            print(f"   - {name}: {status}")
            print(f"     Command: {' '.join(config.command)}")

        # Attempt to connect (will likely fail without actual MCP servers)
        print(f"\n🔗 Attempting to connect to MCP servers...")
        connection_results = await mcp_manager.connect_all_servers()

        for server_name, success in connection_results.items():
            status = "✓ Connected" if success else "✗ Failed"
            print(f"   - {server_name}: {status}")

        # Load tools
        print(f"\n🛠️  Loading tools from connected servers...")
        tools = await mcp_manager.load_all_tools()

        total_tools = sum(len(tool_list) for tool_list in tools.values())
        print(f"   Loaded {total_tools} tools total")

        for server_name, tool_list in tools.items():
            if tool_list:
                print(f"   - {server_name}: {len(tool_list)} tools")
                for tool in tool_list[:3]:  # Show first 3 tools
                    print(f"     * {tool.metadata.name}")
                if len(tool_list) > 3:
                    print(f"     ... and {len(tool_list) - 3} more")

        # Clean up
        await mcp_manager.disconnect_all_servers()
        print(f"\n🧹 Cleaned up MCP connections")

    except Exception as e:
        print(f"❌ Error: {e}")


async def example_complex_queries():
    """Example 5: Complex SQL generation scenarios."""
    print("\n" + "=" * 80)
    print("🔧 Example 5: Complex Query Scenarios")
    print("=" * 80)

    complex_queries = [
        {
            "title": "Multi-table Join with Aggregation",
            "query": "Find the top 5 product categories by total sales volume, including the average order size and number of unique customers for each category in the last 6 months",
        },
        {
            "title": "Time Series Analysis",
            "query": "Create a query to show daily sales trends with 7-day moving averages, including percentage change from the previous period",
        },
        {
            "title": "Advanced Filtering",
            "query": "Get all customers who have made purchases in at least 3 different product categories, with their total lifetime value and most recent purchase date",
        },
    ]

    for i, scenario in enumerate(complex_queries, 1):
        print(f"\n📊 Scenario {i}: {scenario['title']}")
        print("-" * 60)

        try:
            result = await generate_sql_with_workflow(
                query=scenario["query"],
                enable_mcp=False,  # Disable MCP for faster execution
                verbose=False,  # Reduce verbosity for cleaner output
            )

            print(f"Query: {scenario['query']}")
            print(f"\nGenerated SQL:")
            sql = result.get("generated_sql", "No SQL generated")
            # Show first few lines of SQL
            sql_lines = sql.split("\n")[:10]
            for line in sql_lines:
                if line.strip():
                    print(f"  {line}")
            if len(sql.split("\n")) > 10:
                print(f"  ... ({len(sql.split('\n')) - 10} more lines)")

            status = "✓ Success" if result.get("workflow_completed") else "✗ Failed"
            print(f"\nStatus: {status}")

        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Run all examples."""
    print("🚀 SQL Generator Workflow Examples")
    print("=" * 80)
    print("This example demonstrates the ResinKit SQL Generator Workflow")
    print("with various configurations and usage patterns.")

    examples = [
        ("Basic Usage", example_basic_usage),
        ("Custom MCP Configuration", example_with_custom_mcp),
        ("Direct Workflow Usage", example_direct_workflow_usage),
        ("MCP Manager Standalone", example_mcp_manager_standalone),
        ("Complex Query Scenarios", example_complex_queries),
    ]

    for name, example_func in examples:
        try:
            print(f"\n🎯 Running: {name}")
            await example_func()
            print(f"✅ Completed: {name}")
        except Exception as e:
            print(f"❌ Failed: {name} - {e}")
            logger.exception(f"Example {name} failed")

    print("\n" + "=" * 80)
    print("🎉 All examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    # Run the examples
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Examples failed: {e}")
        logger.exception("Examples execution failed")
