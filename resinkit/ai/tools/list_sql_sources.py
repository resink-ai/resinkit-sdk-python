"""
List SQL Sources tool for LlamaIndex agents.

This tool is backed by the ResinKit API and allows agents to discover
available SQL data sources that have been configured in the system.
"""

import asyncio
from typing import List, Optional

from llama_index.core.tools import FunctionTool
from pydantic import BaseModel, Field

from resinkit.core.resinkit_api_client import ResinkitAPIClient
from resinkit.core.settings import get_settings


class ListSqlSourcesParams(BaseModel):
    """Parameters for listing SQL sources (no parameters needed)."""

    # No parameters needed for this endpoint
    pass


class SqlSourceInfo(BaseModel):
    """Information about a SQL data source."""

    name: str = Field(..., description="Name of the SQL data source")
    kind: str = Field(..., description="Type of database (e.g., postgres, mysql, etc.)")
    host: str = Field(..., description="Database host")
    port: int = Field(..., description="Database port")
    database: str = Field(..., description="Database name")
    user: str = Field(..., description="Database user")
    created_at: str = Field(..., description="When the source was created")
    created_by: str = Field(..., description="Who created the source")


class ListSqlSourcesResult(BaseModel):
    """Result of listing SQL sources."""

    success: bool = Field(..., description="Whether the operation was successful")
    sources: List[SqlSourceInfo] = Field(
        default_factory=list, description="List of available SQL sources"
    )
    count: int = Field(0, description="Number of sources found")
    error_message: Optional[str] = Field(
        None, description="Error message if operation failed"
    )


class ListSqlSourcesTool:
    """A tool for listing available SQL data sources."""

    def __init__(self):
        """Initialize the List SQL Sources tool."""
        self.settings = get_settings()
        self.api_client = ResinkitAPIClient(
            base_url=self.settings.resinkit.base_url,
            access_token=self.settings.resinkit.access_token,
            session_id=self.settings.resinkit.session_id,
        )

    async def _list_sql_sources(self) -> ListSqlSourcesResult:
        """
        List all available SQL data sources.

        Returns:
            ListSqlSourcesResult with information about available SQL sources
        """
        try:
            # Call the wrapper API client method
            response = await self.api_client.list_sql_sources()

            if not response:
                return ListSqlSourcesResult(
                    success=False,
                    error_message="Failed to retrieve SQL sources from API",
                )

            # Convert API response to our structured format
            sources = []
            for source_dict in response:
                source_info = SqlSourceInfo(
                    name=source_dict["name"],
                    kind=source_dict["kind"],
                    host=source_dict["host"],
                    port=source_dict["port"],
                    database=source_dict["database"],
                    user=source_dict["user"],
                    created_at=source_dict["created_at"],
                    created_by=source_dict["created_by"],
                )
                sources.append(source_info)

            return ListSqlSourcesResult(
                success=True, sources=sources, count=len(sources)
            )

        except Exception as e:
            return ListSqlSourcesResult(
                success=False, error_message=f"Error listing SQL sources: {str(e)}"
            )

    def _run_async(self, coro):
        """Helper to run async code."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # If we're in a Jupyter notebook or similar
            try:
                import nest_asyncio

                nest_asyncio.apply()
            except ImportError:
                pass
            return loop.run_until_complete(coro)
        else:
            return loop.run_until_complete(coro)

    def list_sql_sources_sync(self) -> ListSqlSourcesResult:
        """Synchronous wrapper for listing SQL sources."""
        return self._run_async(self._list_sql_sources())

    def as_function_tool(self) -> FunctionTool:
        """
        Convert this tool to a LlamaIndex FunctionTool.

        Returns:
            FunctionTool instance for use with LlamaIndex agents
        """

        def list_sql_sources_func() -> str:
            """
            List all available SQL data sources configured in the system.

            This tool helps discover what SQL databases and data sources are available
            for querying. Each source includes connection details like host, port,
            database name, and the type of database system.

            Returns:
                Formatted string with information about available SQL sources
            """
            result = self.list_sql_sources_sync()

            if not result.success:
                return f"❌ Failed to list SQL sources: {result.error_message}"

            if result.count == 0:
                return "📋 No SQL sources are currently configured in the system."

            # Format the response for agent consumption
            response = f"📋 Found {result.count} SQL source(s):\n\n"

            for i, source in enumerate(result.sources, 1):
                response += f"{i}. **{source.name}** ({source.kind})\n"
                response += f"   • Host: {source.host}:{source.port}\n"
                response += f"   • Database: {source.database}\n"
                response += f"   • User: {source.user}\n"
                response += (
                    f"   • Created: {source.created_at} by {source.created_by}\n\n"
                )

            return response.strip()

        return FunctionTool.from_defaults(
            fn=list_sql_sources_func,
            name="list_sql_sources",
            description=(
                "List all available SQL data sources configured in the ResinKit system. "
                "This tool discovers what databases are available for querying, including "
                "connection details like host, port, database name, and database type. "
                "Use this tool when you need to understand what data sources are available "
                "before executing SQL queries or when a user asks about available databases."
            ),
            fn_schema=ListSqlSourcesParams,
        )

    def get_sources_list(self) -> List[SqlSourceInfo]:
        """
        Get the raw list of SQL sources.

        Returns:
            List of SqlSourceInfo objects
        """
        result = self.list_sql_sources_sync()
        return result.sources if result.success else []


def create_list_sql_sources_tool() -> FunctionTool:
    """
    Create a List SQL Sources tool for LlamaIndex agents.

    Returns:
        FunctionTool instance for use with LlamaIndex agents
    """
    tool = ListSqlSourcesTool()
    return tool.as_function_tool()
