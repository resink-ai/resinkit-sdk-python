"""
ResInKit API Client for interacting with the ResInKit REST API.
"""

import asyncio
from typing import Any, Dict, List, Optional

from resinkit_api_client import AuthenticatedClient, Client
from resinkit_api_client.api.db_crawl import crawl_database_tables
from resinkit_api_client.api.sql_tools import (
    create_sql_source,
    delete_sql_source,
    execute_sql_query,
    get_sql_source,
    list_sql_sources,
    test_sql_connection,
    update_sql_source,
)
from resinkit_api_client.api.tasks import (
    cancel_resinkit_task,
    delete_resinkit_task_permanent,
    get_resinkit_task_details,
    get_resinkit_task_logs,
    get_resinkit_task_results,
    list_resinkit_tasks,
    submit_resinkit_task,
)
from resinkit_api_client.api.variables import (
    create_variable,
    delete_variable,
    get_variable,
    list_variables,
)
from resinkit_api_client.models.db_crawl_request import DbCrawlRequest
from resinkit_api_client.models.db_crawl_result import DbCrawlResult
from resinkit_api_client.models.log_entry import LogEntry
from resinkit_api_client.models.sql_connection_test_result import (
    SqlConnectionTestResult,
)
from resinkit_api_client.models.sql_query_request import SqlQueryRequest
from resinkit_api_client.models.sql_query_result import SqlQueryResult
from resinkit_api_client.models.sql_source_create import SqlSourceCreate
from resinkit_api_client.models.sql_source_response import SqlSourceResponse
from resinkit_api_client.models.sql_source_update import SqlSourceUpdate
from resinkit_api_client.models.submit_resinkit_task_payload import (
    SubmitResinkitTaskPayload,
)
from resinkit_api_client.models.task_result import TaskResult
from resinkit_api_client.models.variable_create import VariableCreate
from resinkit_api_client.models.variable_response import VariableResponse

from .settings import get_settings


class ResinkitAPIClient:
    """
    Async API client for ResInKit using the generated client.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        access_token: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        Initialize the API client.

        Args:
            base_url: Base URL for the API (defaults to settings)
            access_token: Access token for authentication (defaults to settings)
            session_id: Session ID for cookie-based authentication (defaults to settings)
        """
        settings = get_settings()

        self.base_url = base_url or settings.resinkit.base_url
        self.access_token = access_token or settings.resinkit.access_token
        self.session_id = session_id or settings.resinkit.session_id

        self._client = self._create_client()

    def _create_client(self) -> Client:
        """Create the underlying client instance."""
        if self.access_token:
            client = AuthenticatedClient(
                base_url=self.base_url,
                token=self.access_token,
                auth_header_name="Authorization",
                prefix="Bearer",
            )
        else:
            client = Client(base_url=self.base_url)

        if self.session_id:
            client = client.with_cookies({"resink_session": self.session_id})

        return client

    async def list_tasks(self, **kwargs) -> Dict[str, Any]:
        """List tasks with optional filtering."""
        result = await list_resinkit_tasks.asyncio(client=self._client, **kwargs)
        return result or {}

    async def submit_task(self, task_config: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new task with JSON configuration."""
        payload = SubmitResinkitTaskPayload.from_dict(task_config)
        result = await submit_resinkit_task.asyncio(client=self._client, body=payload)
        return result or {}

    async def submit_yaml_task(self, yaml_config: str) -> Dict[str, Any]:
        """Submit a new task with YAML configuration."""
        client_with_headers = self._client.with_headers({"Content-Type": "text/plain"})

        async with client_with_headers.get_async_httpx_client() as httpx_client:
            response = await httpx_client.post(
                "/api/v1/agent/tasks/yaml", content=yaml_config
            )
            response.raise_for_status()
            return response.json()

    async def get_task_details(self, task_id: str) -> Dict[str, Any]:
        """Get details of a specific task."""
        result = await get_resinkit_task_details.asyncio(
            task_id=task_id, client=self._client
        )
        return result or {}

    async def cancel_task(
        self, task_id: str, reason: Optional[str] = None, force: bool = False
    ) -> Dict[str, Any]:
        """Cancel a task."""
        result = await cancel_resinkit_task.asyncio(
            task_id=task_id, client=self._client, reason=reason, force=force
        )
        return result or {}

    async def get_task_logs(self, task_id: str, **kwargs) -> List[LogEntry]:
        """Get logs for a specific task."""
        result = await get_resinkit_task_logs.asyncio(
            task_id=task_id, client=self._client, **kwargs
        )
        if result and isinstance(result, list):
            return [
                LogEntry.from_dict(log) if isinstance(log, dict) else log
                for log in result
            ]
        return []

    async def get_task_results(self, task_id: str) -> Optional[TaskResult]:
        """Get results of a completed task."""
        result = await get_resinkit_task_results.asyncio(
            task_id=task_id, client=self._client
        )
        return result

    async def permanently_delete_task(self, task_id: str) -> Dict[str, Any]:
        """Permanently delete a task and its events if the task is in an end state."""
        result = await delete_resinkit_task_permanent.asyncio(
            task_id=task_id, client=self._client
        )
        return result or {"message": "Task deleted permanently."}

    async def list_variables(self) -> List[VariableResponse]:
        """List all variables."""
        result = await list_variables.asyncio(client=self._client)
        return result or []

    async def get_variable(self, name: str) -> Optional[VariableResponse]:
        """Get a specific variable including its value."""
        result = await get_variable.asyncio(name=name, client=self._client)
        return result

    async def create_variable(
        self, name: str, value: str, description: Optional[str] = None
    ) -> Optional[VariableResponse]:
        """Create a new variable."""
        variable_data = VariableCreate(name=name, value=value, description=description)
        result = await create_variable.asyncio(client=self._client, body=variable_data)
        return result

    async def delete_variable(self, name: str) -> Dict[str, Any]:
        """Delete a variable."""
        result = await delete_variable.asyncio(name=name, client=self._client)
        return result or {"message": f"Variable '{name}' deleted successfully."}

    # SQL Sources methods
    async def list_sql_sources(self) -> List[SqlSourceResponse]:
        """List all SQL sources."""
        result = await list_sql_sources.asyncio(client=self._client)
        return result or []

    async def get_sql_source(self, source_name: str) -> Optional[SqlSourceResponse]:
        """Get a specific SQL source."""
        result = await get_sql_source.asyncio(
            source_name=source_name, client=self._client
        )
        return result

    async def create_sql_source(
        self, source_data: Dict[str, Any]
    ) -> Optional[SqlSourceResponse]:
        """Create a new SQL source."""
        sql_source = SqlSourceCreate.from_dict(source_data)
        result = await create_sql_source.asyncio(client=self._client, body=sql_source)
        return result

    async def update_sql_source(
        self, source_name: str, source_data: Dict[str, Any]
    ) -> Optional[SqlSourceResponse]:
        """Update an existing SQL source."""
        sql_source = SqlSourceUpdate.from_dict(source_data)
        result = await update_sql_source.asyncio(
            source_name=source_name, client=self._client, body=sql_source
        )
        return result

    async def delete_sql_source(self, source_name: str) -> Dict[str, Any]:
        """Delete a SQL source."""
        result = await delete_sql_source.asyncio(
            source_name=source_name, client=self._client
        )
        return result or {
            "message": f"SQL source '{source_name}' deleted successfully."
        }

    async def crawl_database_tables(
        self, crawl_request: Dict[str, Any]
    ) -> Optional[DbCrawlResult]:
        """Crawl database tables for a SQL source."""
        crawl_req = DbCrawlRequest.from_dict(crawl_request)
        result = await crawl_database_tables.asyncio(
            client=self._client, body=crawl_req
        )
        return result

    async def test_sql_connection(
        self, source_data: Dict[str, Any]
    ) -> Optional[SqlConnectionTestResult]:
        """Test SQL database connection without persisting credentials."""
        sql_source = SqlSourceCreate.from_dict(source_data)
        result = await test_sql_connection.asyncio(client=self._client, body=sql_source)
        return result

    async def execute_sql_query(
        self, query: str, source_name: str, limit: Optional[int] = 1000
    ) -> Optional[SqlQueryResult]:
        """Execute a SQL query against a data source."""
        query_request = SqlQueryRequest(
            query=query, source_name=source_name, limit=limit
        )
        result = await execute_sql_query.asyncio(
            client=self._client, body=query_request
        )
        return result

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        _ = exc_type, exc_val, exc_tb  # Unused parameters
        pass

    async def __aenter__(self):
        """Async context manager entry."""
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.__aexit__(exc_type, exc_val, exc_tb)
