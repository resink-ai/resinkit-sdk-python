"""
ResinkitApiTools Factory - Convert ResinKit API endpoints to LlamaIndex FunctionTools.

This factory provides a clean interface to create LlamaIndex FunctionTools from ResinKit API endpoints.
It uses async functions when possible and automatically extracts documentation from API methods.
"""

from typing import Any, Dict, List, Optional

from llama_index.core.tools import FunctionTool
from pydantic import BaseModel, Field

from resinkit.core.resinkit_api_client import ResinkitAPIClient
from resinkit.core.settings import get_settings


class ResinkitApiTools:
    """Factory for creating LlamaIndex FunctionTools from ResinKit API endpoints."""

    def __init__(self, client: Optional[ResinkitAPIClient] = None) -> None:
        """
        Initialize the factory with a ResinKit API client.

        Args:
            client: Optional ResinkitAPIClient instance. If None, creates one from settings.
        """
        if client is None:
            settings = get_settings()
            client = ResinkitAPIClient(
                base_url=settings.resinkit.base_url,
                access_token=settings.resinkit.access_token,
                session_id=settings.resinkit.session_id,
            )

        self._client = client

    def _extract_description(self, method) -> str:
        """
        Extract description from API method docstring.

        Args:
            method: The API method to extract description from

        Returns:
            Description string for the tool
        """
        if hasattr(method, "__doc__") and method.__doc__:
            # Extract the first line of the docstring as description
            lines = method.__doc__.strip().split("\n")
            if lines:
                return lines[0].strip()
        return "ResinKit API tool"

    def _create_async_tool(
        self,
        name: str,
        api_method,
        description: Optional[str] = None,
        parameter_schema: Optional[BaseModel] = None,
        **kwargs,
    ) -> FunctionTool:
        """
        Create an async FunctionTool from an API method.

        Args:
            name: Name of the tool
            api_method: The async API method to wrap
            description: Optional description override
            parameter_schema: Optional parameter schema
            **kwargs: Additional parameters for the API method

        Returns:
            FunctionTool instance
        """
        # Extract description from method if not provided
        if description is None:
            description = self._extract_description(api_method)

        async def tool_function(**params) -> str:
            """Async tool function wrapper."""
            try:
                # Merge kwargs with params
                all_params = {**kwargs, **params}
                result = await api_method(**all_params)

                # Handle different return types
                if isinstance(result, list):
                    if not result:
                        return "No results found."

                    # Handle structured models
                    if hasattr(result[0], "to_dict"):
                        return "Found {} items:\n{}".format(
                            len(result),
                            "\n".join(
                                f"- {item.name if hasattr(item, 'name') else str(item)}"
                                for item in result
                            ),
                        )
                    else:
                        return f"Found {len(result)} items: {result}"

                elif result is None:
                    return "No result returned."

                elif hasattr(result, "to_dict"):
                    # Handle structured models
                    return f"Result: {result.to_dict()}"

                else:
                    return f"Result: {result}"

            except Exception as e:
                return f"Error: {str(e)}"

        return FunctionTool.from_defaults(
            fn=tool_function,
            name=name,
            description=description,
            fn_schema=parameter_schema,
            async_fn=True,
        )

    # Tool creation methods for specific endpoints

    def tool_list_sql_sources(self, description: Optional[str] = None) -> FunctionTool:
        """
        Create a tool for listing SQL sources.

        Args:
            description: Optional description override

        Returns:
            FunctionTool for listing SQL sources
        """
        if description is None:
            description = (
                "List all available SQL data sources configured in the ResinKit system. "
                "This tool discovers what databases are available for querying, including "
                "connection details like host, port, database name, and database type."
            )

        async def list_sql_sources() -> str:
            """List all available SQL data sources."""
            try:
                sources = await self._client.list_sql_sources()

                if not sources:
                    return "📋 No SQL sources are currently configured in the system."

                response = f"📋 Found {len(sources)} SQL source(s):\n\n"

                for i, source in enumerate(sources, 1):
                    response += f"{i}. **{source.name}** ({source.kind})\n"
                    response += f"   • Host: {source.host}:{source.port}\n"
                    response += f"   • Database: {source.database}\n"
                    response += f"   • User: {source.user}\n"
                    response += (
                        f"   • Created: {source.created_at} by {source.created_by}\n\n"
                    )

                return response.strip()

            except Exception as e:
                return f"❌ Failed to list SQL sources: {str(e)}"

        return FunctionTool.from_defaults(
            fn=list_sql_sources,
            name="list_sql_sources",
            description=description,
            async_fn=True,
        )

    def tool_list_tasks(self, description: Optional[str] = None) -> FunctionTool:
        """
        Create a tool for listing tasks.

        Args:
            description: Optional description override

        Returns:
            FunctionTool for listing tasks
        """
        if description is None:
            description = (
                "List tasks in the ResinKit system with optional filtering. "
                "This tool helps discover what tasks are running, completed, or failed."
            )

        class ListTasksParams(BaseModel):
            """Parameters for listing tasks."""

            task_type: Optional[str] = Field(None, description="Filter by task type")
            status: Optional[str] = Field(
                None,
                description="Filter by status (e.g., 'running', 'completed', 'failed')",
            )
            limit: Optional[int] = Field(
                20, description="Maximum number of tasks to return"
            )

        async def list_tasks(
            task_type: Optional[str] = None,
            status: Optional[str] = None,
            limit: Optional[int] = 20,
        ) -> str:
            """List tasks with optional filtering."""
            try:
                # Filter None values
                params = {
                    k: v
                    for k, v in {
                        "task_type": task_type,
                        "status": status,
                        "limit": limit,
                    }.items()
                    if v is not None
                }

                result = await self._client.list_tasks(**params)

                if not result:
                    return "📋 No tasks found."

                # Handle the response format (usually a dict with tasks list)
                if isinstance(result, dict):
                    tasks = result.get("tasks", [])
                    total = result.get("total", len(tasks))

                    if not tasks:
                        return "📋 No tasks found."

                    response = f"📋 Found {len(tasks)} task(s) (total: {total}):\n\n"

                    for i, task in enumerate(tasks, 1):
                        task_id = task.get("task_id", "Unknown")
                        task_status = task.get("status", "Unknown")
                        task_name = task.get("task_name", "Unnamed")
                        created_at = task.get("created_at", "Unknown")

                        response += f"{i}. **{task_name}** ({task_id})\n"
                        response += f"   • Status: {task_status}\n"
                        response += f"   • Created: {created_at}\n\n"

                    return response.strip()
                else:
                    return f"Result: {result}"

            except Exception as e:
                return f"❌ Failed to list tasks: {str(e)}"

        return FunctionTool.from_defaults(
            fn=list_tasks,
            name="list_tasks",
            description=description,
            fn_schema=ListTasksParams,
            async_fn=True,
        )

    def tool_submit_task(self, description: Optional[str] = None) -> FunctionTool:
        """
        Create a tool for submitting tasks.

        Args:
            description: Optional description override

        Returns:
            FunctionTool for submitting tasks
        """
        if description is None:
            description = (
                "Submit a new task to the ResinKit system. "
                "This tool allows you to create and execute tasks with JSON configuration."
            )

        class SubmitTaskParams(BaseModel):
            """Parameters for submitting a task."""

            task_config: Dict[str, Any] = Field(
                ..., description="Task configuration as JSON"
            )

        async def submit_task(task_config: Dict[str, Any]) -> str:
            """Submit a new task with JSON configuration."""
            try:
                result = await self._client.submit_task(task_config)

                if isinstance(result, dict):
                    task_id = result.get("task_id", "Unknown")
                    status = result.get("status", "Unknown")

                    return f"✅ Task submitted successfully:\n• Task ID: {task_id}\n• Status: {status}"
                else:
                    return f"✅ Task submitted: {result}"

            except Exception as e:
                return f"❌ Failed to submit task: {str(e)}"

        return FunctionTool.from_defaults(
            fn=submit_task,
            name="submit_task",
            description=description,
            fn_schema=SubmitTaskParams,
            async_fn=True,
        )

    def tool_execute_sql_query(self, description: Optional[str] = None) -> FunctionTool:
        """
        Create a tool for executing SQL queries.

        Args:
            description: Optional description override

        Returns:
            FunctionTool for executing SQL queries
        """
        if description is None:
            description = (
                "Execute a SQL query against a data source in the ResinKit system. "
                "This tool allows you to run SQL queries and get results back."
            )

        class ExecuteSqlParams(BaseModel):
            """Parameters for executing SQL queries."""

            query: str = Field(..., description="SQL query to execute")
            source_name: str = Field(
                ..., description="Name of the SQL source to query against"
            )
            limit: Optional[int] = Field(
                100, description="Maximum number of rows to return"
            )

        async def execute_sql_query(
            query: str, source_name: str, limit: Optional[int] = 100
        ) -> str:
            """Execute a SQL query against a data source."""
            try:
                result = await self._client.execute_sql_query(
                    query=query, source_name=source_name, limit=limit
                )

                if result is None:
                    return "❌ No result returned from SQL query"

                if not result.rows:
                    return "📊 Query executed successfully but returned no results."

                response = f"📊 Query executed successfully in {result.execution_time_ms:.2f}ms, returned {result.row_count} row(s):\n\n"

                # Format as table
                if result.columns:
                    response += "| " + " | ".join(result.columns) + " |\n"
                    response += "|" + "|".join(["---"] * len(result.columns)) + "|\n"

                for row in result.rows[:10]:  # Limit display to first 10 rows
                    values = [str(v) if v is not None else "" for v in row]
                    response += "| " + " | ".join(values) + " |\n"

                if len(result.rows) > 10:
                    response += f"\n... and {len(result.rows) - 10} more rows"

                return response

            except Exception as e:
                return f"❌ Failed to execute SQL query: {str(e)}"

        return FunctionTool.from_defaults(
            fn=execute_sql_query,
            name="execute_sql_query",
            description=description,
            fn_schema=ExecuteSqlParams,
            async_fn=True,
        )

    def get_all_tools(self) -> List[FunctionTool]:
        """
        Get all available tools from this factory.

        Returns:
            List of all available FunctionTools
        """
        return [
            self.tool_list_sql_sources(),
            self.tool_list_tasks(),
            self.tool_submit_task(),
            self.tool_execute_sql_query(),
        ]


def get_resinkit_api_tools(
    client: Optional[ResinkitAPIClient] = None,
) -> ResinkitApiTools:
    """
    Create a default instance of ResinkitApiTools.

    Args:
        client: Optional ResinkitAPIClient instance. If None, creates one from settings.

    Returns:
        ResinkitApiTools instance
    """
    return ResinkitApiTools(client=client)
