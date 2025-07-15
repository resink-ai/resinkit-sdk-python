#!/usr/bin/env python3
"""
Example usage of the ResinkitApiTools factory.

This demonstrates how to use the factory to create LlamaIndex FunctionTools
from ResinKit API endpoints.
"""

from resinkit.ai.tools.resinkit_api_tools import (
    ResinkitApiTools,
    get_resinkit_api_tools,
)

# Method 1: Create instance directly
print("🔧 Method 1: Creating instance directly")
api_tools = ResinkitApiTools()

# Create tools with default descriptions
list_sql_tool = api_tools.tool_list_sql_sources()
list_tasks_tool = api_tools.tool_list_tasks()
submit_task_tool = api_tools.tool_submit_task()
execute_sql_tool = api_tools.tool_execute_sql_query()

# Create a tool with custom description
custom_list_sql_tool = api_tools.tool_list_sql_sources(
    description="List all available SQL data sources configured in the ResinKit system."
)

print("✅ Created tools:")
print(f"- {list_sql_tool.metadata.name}")
print(f"- {list_tasks_tool.metadata.name}")
print(f"- {submit_task_tool.metadata.name}")
print(f"- {execute_sql_tool.metadata.name}")
print(f"- {custom_list_sql_tool.metadata.name} (custom description)")

# Method 2: Using the factory function
print("\n🔧 Method 2: Using factory function")
api_tools2 = get_resinkit_api_tools()

# Get all tools at once
all_tools = api_tools2.get_all_tools()
print(f"✅ Got {len(all_tools)} tools:")
for tool in all_tools:
    print(f"- {tool.metadata.name}")

# Method 3: Mix and match
print("\n🔧 Method 3: Mix and match individual tools")
api_tools3 = get_resinkit_api_tools()
some_tools = [
    api_tools3.tool_list_sql_sources(),
    api_tools3.tool_execute_sql_query(),
]
print(f"✅ Created {len(some_tools)} specific tools:")
for tool in some_tools:
    print(f"- {tool.metadata.name}")

# Tools can be used with LlamaIndex agents
print("\n🚀 All tools ready for use with LlamaIndex agents!")
print("Example usage with agents:")
print("  from llama_index.core.agent import FunctionAgent")
print("  agent = FunctionAgent.from_tools(all_tools)")
