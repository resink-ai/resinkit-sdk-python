"""SQL query execution tool for llama-index agents."""

import sqlite3
import time
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
from llama_index.core.tools import FunctionTool
from pydantic import BaseModel, Field


class SQLQueryParams(BaseModel):
    """Parameters for SQL query execution."""

    query: str = Field(..., description="The SQL query to execute.")
    explanation: str = Field(
        ...,
        description="A one-sentence explanation as to why this query needs to be run and how it contributes to the goal.",
    )


class SQLQueryResult(BaseModel):
    """Result of SQL query execution."""

    success: bool = Field(..., description="Whether the query executed successfully")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Query results as list of dictionaries")
    row_count: int = Field(0, description="Number of rows returned")
    execution_time_ms: float = Field(0.0, description="Query execution time in milliseconds")
    error_message: Optional[str] = Field(None, description="Error message if query failed")
    query_executed: str = Field(..., description="The actual query that was executed")


class SQLCommandTool:
    """A tool for executing SQL queries with user approval workflow."""

    def __init__(
        self,
        connection_string: str,
        approval_callback: Optional[Callable[[str, str], tuple[bool, str]]] = None,
        auto_approve_safe_queries: bool = True,
        max_rows: int = 1000,
        timeout_seconds: int = 30,
    ):
        """
        Initialize the SQL command tool.

        Args:
            connection_string: Database connection string (currently supports SQLite)
            approval_callback: Function that takes (query, explanation) and returns (approved, modified_query)
            auto_approve_safe_queries: Whether to auto-approve safe SELECT queries with LIMIT
            max_rows: Maximum number of rows to return
            timeout_seconds: Query timeout in seconds
        """
        self.connection_string = connection_string
        self.approval_callback = approval_callback
        self.auto_approve_safe_queries = auto_approve_safe_queries
        self.max_rows = max_rows
        self.timeout_seconds = timeout_seconds

        # Create the llama-index tool
        self.tool = FunctionTool.from_defaults(
            fn=self._execute_sql_query,
            name="run_sql_query",
            description=(
                "PROPOSE a SQL query to run on behalf of the user.\n"
                "If you have this tool, note that you DO have the ability to run queries directly on the USER's database.\n"
                "Note that the user will have to approve the query before it is executed.\n"
                "The user may reject it if it is not to their liking, or may modify the query before approving it. If they do change it, take those changes into account.\n"
                "The actual query will NOT execute until the user approves it. The user may not approve it immediately. Do NOT assume the query has started running.\n"
                "If the step is WAITING for user approval, it has NOT started running.\n"
                "In using these tools, adhere to the following guidelines:\n"
                "1. Based on the contents of the conversation and any provided schema, you will generate a SQL query.\n"
                "2. Before generating complex queries, consider using simpler queries to inspect the database schema, tables, or data types to ensure correctness.\n"
                "3. Do NOT generate queries that could be destructive (e.g., DROP, DELETE, TRUNCATE) unless explicitly asked to do so by the user.\n"
                "4. Ensure the SQL dialect is appropriate for the target database if that information is available.\n"
                "5. Don't include any newlines in the query."
            ),
            fn_schema=SQLQueryParams,
        )

    def _is_safe_query(self, query: str) -> bool:
        """Check if a query is safe for auto-approval."""
        query_upper = query.upper().strip()

        # Only SELECT queries are considered safe
        if not query_upper.startswith("SELECT"):
            return False

        # Must have LIMIT clause for auto-approval
        if "LIMIT" not in query_upper:
            return False

        # No destructive operations
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT"]
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False

        return True

    def _get_user_approval(self, query: str, explanation: str) -> tuple[bool, str]:
        """Get user approval for query execution."""
        if self.auto_approve_safe_queries and self._is_safe_query(query):
            return True, query

        if self.approval_callback:
            return self.approval_callback(query, explanation)
        else:
            # Default behavior: print query and ask for approval
            print(f"\nSQL Query Proposed:")
            print(f"Explanation: {explanation}")
            print(f"Query: {query}")

            while True:
                response = input("\nApprove this query? (y/n/modify): ").lower().strip()
                if response in ["y", "yes"]:
                    return True, query
                elif response in ["n", "no"]:
                    return False, query
                elif response in ["m", "modify"]:
                    modified_query = input("Enter modified query: ").strip()
                    return True, modified_query
                else:
                    print("Please enter 'y' (yes), 'n' (no), or 'm' (modify)")

    def _execute_query(self, query: str) -> SQLQueryResult:
        """Execute the SQL query and return results."""
        start_time = time.time()

        try:
            # Currently only supports SQLite
            if not self.connection_string.startswith("jdbc:sqlite:"):
                raise ValueError("Currently only SQLite connections are supported")

            # Extract SQLite database path
            db_path = self.connection_string.replace("jdbc:sqlite:", "")

            # Connect and execute
            conn = sqlite3.connect(db_path, timeout=self.timeout_seconds)
            conn.row_factory = sqlite3.Row  # Enable column access by name

            cursor = conn.cursor()
            cursor.execute(query)

            # Fetch results
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            data = [dict(row) for row in rows[: self.max_rows]]

            execution_time = (time.time() - start_time) * 1000

            conn.close()

            return SQLQueryResult(
                success=True, data=data, row_count=len(data), execution_time_ms=execution_time, query_executed=query
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return SQLQueryResult(
                success=False, row_count=0, execution_time_ms=execution_time, error_message=str(e), query_executed=query
            )

    def _execute_sql_query(self, query: str, explanation: str) -> str:
        """Execute SQL query with approval workflow (llama-index tool function)."""
        # Get user approval
        approved, final_query = self._get_user_approval(query, explanation)

        if not approved:
            return "Query was not approved by the user."

        # Execute the query
        result = self._execute_query(final_query)

        if result.success:
            # Format successful result for agent consumption
            response = f"Query executed successfully in {result.execution_time_ms:.1f}ms.\n"
            response += f"Returned {result.row_count} rows.\n"

            if result.data:
                # Convert to DataFrame for better display
                df = pd.DataFrame(result.data)
                response += f"\nResults:\n{df.to_string(max_rows=10)}"

                if result.row_count > 10:
                    response += f"\n... (showing first 10 of {result.row_count} rows)"

            return response
        else:
            return f"Query failed: {result.error_message}"

    def call(self, sql_command: str, explanation: str) -> str:
        """Direct call interface for standalone usage."""
        return self._execute_sql_query(sql_command, explanation)

    def get_dataframe(self, query: str, explanation: str) -> Optional[pd.DataFrame]:
        """Execute query and return results as pandas DataFrame."""
        approved, final_query = self._get_user_approval(query, explanation)

        if not approved:
            return None

        result = self._execute_query(final_query)

        if result.success and result.data:
            return pd.DataFrame(result.data)
        else:
            return None


def create_sql_tool(
    connection_string: str,
    approval_callback: Optional[Callable[[str, str], tuple[bool, str]]] = None,
    auto_approve_safe_queries: bool = True,
    max_rows: int = 1000,
    timeout_seconds: int = 30,
) -> FunctionTool:
    """
    Create a SQL command tool for llama-index agents.

    Args:
        connection_string: Database connection string (currently supports SQLite)
        approval_callback: Function that takes (query, explanation) and returns (approved, modified_query)
        auto_approve_safe_queries: Whether to auto-approve safe SELECT queries with LIMIT
        max_rows: Maximum number of rows to return
        timeout_seconds: Query timeout in seconds

    Returns:
        FunctionTool instance for use with llama-index agents
    """
    sql_tool = SQLCommandTool(
        connection_string=connection_string,
        approval_callback=approval_callback,
        auto_approve_safe_queries=auto_approve_safe_queries,
        max_rows=max_rows,
        timeout_seconds=timeout_seconds,
    )
    return sql_tool.tool
