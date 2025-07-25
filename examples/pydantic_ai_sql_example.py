"""
Pydantic AI SQL Generation Example

This example demonstrates how to use pydantic-ai with MCP (Model Context Protocol)
client to generate SQL queries for data analysis. It connects to a local MCP server
running on HTTP and uses the data analysis system prompt.

Requirements:
- MCP server running at http://localhost:8603/mcp-server/mcp
- pydantic-ai library (already included in dependencies)
- OpenAI API key for GPT-4o model

Usage:
    python examples/pydantic_ai_sql_example.py
"""

import asyncio
import logging
import os

from pydantic_ai import Agent
from pydantic_ai.mcp import CallToolFunc, MCPServerStreamableHTTP
from pydantic_ai.messages import ToolReturn
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.tools import RunContext

from resinkit.ai.prompt import SQL_GENERATION_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User query from the requirements
USER_QUERY = (
    "Can you provide the top 9 directors by movie count, including their ID, name, number of movies,"
    " average inter-movie duration (rounded to the nearest integer), average rating (rounded to 2 decimals),"
    " total votes, minimum and maximum ratings, and total movie duration? Sort the output first by"
    " movie count in descending order and then by total movie duration in descending order."
)


async def process_tool_call(
    ctx: RunContext, call_tool: CallToolFunc, name: str, tool_args: dict
) -> ToolReturn:
    # ctx parameter is required by the API but not used in this implementation
    _ = ctx
    """
    Process tool calls with user confirmation.
    
    Args:
        ctx: Run context
        call_tool: Function to call the actual tool
        name: Tool name
        tool_args: Tool arguments
        
    Returns:
        ToolReturn: Result of tool execution or error if cancelled
    """
    print("\n🔍 Tool Execution Request:")
    print(f"Tool: {name}")
    print(f"Arguments: {tool_args}")
    print("-" * 40)

    while True:
        response = input("Do you approve this tool execution? (y/n): ").strip().lower()
        if response == "y":
            print(f"✅ Executing {name}...")
            return await call_tool(name, tool_args)
        elif response == "n":
            print("❌ Tool execution cancelled by user")
            return ToolReturn(return_value="Tool execution cancelled by user")
        else:
            print("Please enter 'y' for yes or 'n' for no.")


async def create_sql_agent() -> Agent:
    """
    Create a pydantic-ai agent with MCP server integration.

    Returns:
        Agent: Configured pydantic-ai agent with MCP tools
    """
    try:
        # Connect to the MCP server running on localhost:8603 with custom tool processing
        server = MCPServerStreamableHTTP(
            "http://localhost:8603/mcp-server/mcp", process_tool_call=process_tool_call
        )

        # Create agent with Anthropic model and MCP server tools
        model = AnthropicModel(
            "claude-3-5-sonnet-latest",
            provider=AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY")),
        )

        logger.info(
            "Successfully created pydantic-ai agent with MCP integration and user approval"
        )
        return Agent(model, toolsets=[server])

    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise


async def main():
    """
    Main function demonstrating the pydantic-ai SQL generation workflow.
    """
    print("🚀 Pydantic AI SQL Generation Example")
    print("=" * 50)

    try:
        # Create the SQL generation agent
        print("\n🔧 Creating pydantic-ai agent with MCP integration...")
        agent = await create_sql_agent()

        print("\n📝 User Query:")
        print(f"{USER_QUERY}")

        # Generate SQL query
        print("\n🧠 Processing with DATA_ANALYSIS_SYSTEM_PROMPT...")
        async with agent:
            result = await agent.run(
                SQL_GENERATION_SYSTEM_PROMPT.format(user_query=USER_QUERY)
            )

        print("\n✅ Generated SQL Analysis:")
        print("=" * 50)
        print(result)
        print("=" * 50)

    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print(
            "Make sure the MCP server is running at http://localhost:8603/mcp-server/mcp"
        )
        print("You can start a local MCP server using the appropriate setup commands.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your configuration and try again.")


def run_example():
    """
    Convenience function to run the example.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Example interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    run_example()
