"""
SQL Generation Agent Example

This example demonstrates how to use the SQL Generation Agent to convert
natural language queries into SQL statements using pydantic-ai and MCP tools.

Requirements:
- MCP server running at http://localhost:8603/mcp-server/mcp
- Anthropic API key set in environment variables
- pydantic-ai library (already included in dependencies)

Usage:
    python examples/sql_generation_agent_example.py
"""

import asyncio
import logging
import os

from resinkit.ai.agents import SQLGenerationAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Example user queries for testing
EXAMPLE_QUERIES = [
    "Can you provide the top 9 directors by movie count, including their ID, name, number of movies, average inter-movie duration (rounded to the nearest integer), average rating (rounded to 2 decimals), total votes, minimum and maximum ratings, and total movie duration? Sort the output first by movie count in descending order and then by total movie duration in descending order.",
    "Show me the top 10 highest rated movies with more than 1000 votes",
    "What are the most popular genres based on average ratings and number of movies?",
    "Find movies released in the last 5 years with ratings above 8.0",
]


async def demonstrate_sql_generation():
    """Demonstrate the SQL Generation Agent capabilities."""
    print("🎬 SQL Generation Agent Demo")
    print("=" * 60)

    # Configuration
    mcp_server_url = "http://localhost:8603/mcp-server/mcp"
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not anthropic_api_key:
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Please set your Anthropic API key:")
        print("export ANTHROPIC_API_KEY=your_api_key_here")
        return

    # Create SQL Generation Agent
    try:
        async with SQLGenerationAgent(
            mcp_server_url=mcp_server_url,
            anthropic_api_key=anthropic_api_key,
            auto_approve_tools=False,  # Require manual approval for demo
            verbose=True,
        ) as agent:
            print(f"✅ SQL Generation Agent initialized")
            print(f"🔗 Connected to MCP server: {mcp_server_url}")
            print("\n" + "=" * 60)

            # Let user choose a query or enter their own
            print("Available example queries:")
            for i, query in enumerate(EXAMPLE_QUERIES, 1):
                print(f"{i}. {query[:80]}...")

            print(f"{len(EXAMPLE_QUERIES) + 1}. Enter custom query")

            while True:
                try:
                    choice = input(
                        f"\nSelect query (1-{len(EXAMPLE_QUERIES) + 1}): "
                    ).strip()

                    if choice.isdigit():
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(EXAMPLE_QUERIES):
                            user_query = EXAMPLE_QUERIES[choice_num - 1]
                            break
                        elif choice_num == len(EXAMPLE_QUERIES) + 1:
                            user_query = input("Enter your query: ").strip()
                            if user_query:
                                break

                    print(
                        f"Please enter a number between 1 and {len(EXAMPLE_QUERIES) + 1}"
                    )

                except (ValueError, KeyboardInterrupt):
                    print("\n👋 Demo cancelled by user")
                    return

            print(f"\n🎯 Selected Query: {user_query}")
            print("\n" + "=" * 60)

            # Generate SQL
            try:
                result = await agent.generate_sql(user_query)

                # Display results
                print("\n🎉 SQL Generation Results:")
                print("=" * 60)

                print(f"\n📝 Generated SQL Query:")
                print("-" * 30)
                print(result.sql_query)

                print(f"\n💡 Explanation:")
                print("-" * 30)
                print(
                    result.explanation[:500] + "..."
                    if len(result.explanation) > 500
                    else result.explanation
                )

                if result.execution_steps:
                    print(f"\n🔄 Execution Steps:")
                    print("-" * 30)
                    for i, step in enumerate(result.execution_steps, 1):
                        print(f"{i}. {step}")

                if result.data_sources_used:
                    print(f"\n📊 Data Sources Used:")
                    print("-" * 30)
                    for source in result.data_sources_used:
                        print(f"  - {source}")

                print(f"\n📈 Metadata:")
                print("-" * 30)
                print(f"  - Model: {result.metadata.get('model_used', 'N/A')}")
                print(
                    f"  - Response Length: {result.metadata.get('response_length', 0)} characters"
                )
                print(
                    f"  - Original Query: {result.metadata.get('original_query', 'N/A')[:50]}..."
                )

                print("\n" + "=" * 60)
                print("✅ SQL Generation Demo Complete!")

            except Exception as e:
                print(f"\n❌ Error during SQL generation: {e}")
                logger.error(f"SQL generation failed: {e}")

    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print(
            "Make sure the MCP server is running at http://localhost:8603/mcp-server/mcp"
        )
        print("You can start a local MCP server using the appropriate setup commands.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Demo failed: {e}")


async def quick_sql_generation_example():
    """Quick example using the convenience function."""
    print("\n🚀 Quick SQL Generation Example")
    print("=" * 40)

    # Import the convenience function
    from resinkit.ai.agents.sql_gen_agent import generate_sql_query

    query = "Show me the top 5 movies by rating"

    try:
        result = await generate_sql_query(
            user_query=query,
            auto_approve_tools=True,  # Auto-approve for quick demo
            verbose=False,  # Less verbose for quick demo
        )

        print(f"Query: {query}")
        print(f"Generated SQL: {result.sql_query}")
        print("✅ Quick generation complete!")

    except Exception as e:
        print(f"❌ Quick generation failed: {e}")


def main():
    """Main function to run the demo."""
    print("Welcome to the SQL Generation Agent Demo!")
    print("This demo will show you how to convert natural language to SQL.")
    print("\nChoose demo type:")
    print("1. Interactive Demo (with manual tool approval)")
    print("2. Quick Demo (auto-approve tools)")
    print("3. Both")

    try:
        choice = input("Enter choice (1-3): ").strip()

        if choice == "1":
            asyncio.run(demonstrate_sql_generation())
        elif choice == "2":
            asyncio.run(quick_sql_generation_example())
        elif choice == "3":
            asyncio.run(demonstrate_sql_generation())
            asyncio.run(quick_sql_generation_example())
        else:
            print("Invalid choice. Running interactive demo.")
            asyncio.run(demonstrate_sql_generation())

    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        print(f"\n❌ Demo failed: {e}")


if __name__ == "__main__":
    main()
