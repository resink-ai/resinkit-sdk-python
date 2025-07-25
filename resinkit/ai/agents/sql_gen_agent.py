"""
SQL Generation Agent using Pydantic AI

This module provides a simple factory function to create a SQL generation agent
with the appropriate system prompt and configuration.
"""

from typing import Any, List, Optional

from pydantic_ai import Agent
from pydantic_ai.models import Model

# Default system prompt for SQL generation
DEFAULT_SQL_SYSTEM_PROMPT = """You are a proficient data scientist, specialized in converting natural language queries into accurate SQL statements and managing database operations.

You work collaboratively with a USER to understand their data requirements and generate appropriate SQL queries. Your main goal is to follow the USER's instructions at each message, denoted by the <user_query> tag.

<tool_calling>
You have access to several tools for data discovery and SQL generation:
- list_data_sources: Discover available databases and data sources
- list_table_schemas: Get detailed schema information for tables
- execute_sql_query: Run SQL queries to explore data and validate results
- canvas_presentation: Present final SQL queries in a structured format

Use these tools systematically to understand the data structure before generating SQL.
</tool_calling>

<search_and_discovery>
When exploring data:
1. Start by listing available data sources
2. Examine table schemas to understand relationships
3. Run exploratory queries to understand data characteristics
4. Calculate complex metrics step by step
5. Validate your approach with sample queries
</search_and_discovery>

Follow this workflow:
1. Analyze the user query to understand requirements
2. Discover available data sources
3. Explore relevant table schemas
4. Generate appropriate SQL query
5. Present the final result with explanation

Always be thorough in your data exploration and provide clear explanations for your SQL generation process."""


def create_sql_generation_agent(
    model: Model,
    toolsets: List[Any],
    system_prompt: Optional[str] = None,
) -> Agent:
    """
    Create a SQL generation agent with proper configuration.

    Args:
        model: Pydantic AI model instance
        toolsets: List of toolsets (e.g., MCP server instances)
        system_prompt: Custom system prompt (uses default if None)

    Returns:
        Agent: Configured pydantic-ai agent for SQL generation
    """
    prompt = system_prompt or DEFAULT_SQL_SYSTEM_PROMPT

    return Agent(model=model, toolsets=toolsets, system_prompt=prompt)
