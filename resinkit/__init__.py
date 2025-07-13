import asyncio
import os
from typing import Any, Optional

from .core.resinkit_api_client import ResinkitAPIClient
from .core.task import Task
from .resinkit import Resinkit

# Module-level interface for callable behavior
_default_instance: Optional[Resinkit] = None
_agent_manager: Optional[Any] = None


def _get_default_instance() -> Resinkit:
    """Get or create the default Resinkit instance."""
    global _default_instance
    if _default_instance is None:
        base_url = os.getenv("RESINKIT_BASE_URL", "http://localhost:8603")
        session_id = os.getenv("RESINKIT_SESSION_ID")
        access_token = os.getenv("RESINKIT_ACCESS_TOKEN", "pat_cnk8_")
        _default_instance = Resinkit(
            base_url=base_url,
            resinkit_session=session_id,
            personal_access_token=access_token,
        )
    return _default_instance


def _get_agent_manager():
    """Get or create the AgentManager with SQL tools."""
    global _agent_manager
    if _agent_manager is None:
        try:
            from .ai.agent import AgentManager
            from .ai.tools.run_sql import SQLCommandTool

            sql_tool = SQLCommandTool(
                connection_string="sqlite:///:memory:",
                auto_approve_safe_queries=True,
            ).as_function_tool()
            tools = [sql_tool]
        except Exception:
            from .ai.agent import AgentManager

            tools = []
        _agent_manager = AgentManager(tools=tools)
    return _agent_manager


def __call__(query: str) -> Any:
    """
    Make the module callable for natural language queries.

    Usage: rsk("What were the total sales for each product category?")
    """
    agent_manager = _get_agent_manager()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            try:
                import nest_asyncio

                nest_asyncio.apply()
                return loop.run_until_complete(agent_manager.run_workflow(query))
            except ImportError:
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, agent_manager.run_workflow(query)
                    )
                    return future.result()
        else:
            return loop.run_until_complete(agent_manager.run_workflow(query))
    except RuntimeError:
        return asyncio.run(agent_manager.run_workflow(query))


def show_tasks_ui():
    """Show the tasks management UI."""
    return _get_default_instance().show_tasks_ui()


def show_vars_ui():
    """Show the variables management UI."""
    return _get_default_instance().show_vars_ui()


def show_sql_task_ui():
    """Show the SQL task submission UI."""
    return _get_default_instance().show_sql_task_ui()


def get_task(task_id: str):
    """Get a Task instance for the given task_id."""
    return _get_default_instance().get_task(task_id)


def configure(base_url=None, session_id=None, access_token=None):
    """Configure the default resinkit instance."""
    global _default_instance, _agent_manager
    if any([base_url, session_id, access_token]):
        _default_instance = Resinkit(
            base_url=base_url
            or os.getenv("RESINKIT_BASE_URL", "http://localhost:8080"),
            resinkit_session=session_id or os.getenv("RESINKIT_SESSION_ID"),
            personal_access_token=access_token or os.getenv("RESINKIT_ACCESS_TOKEN"),
        )
        _agent_manager = None


def config(
    base_url: Optional[str] = None,
    session_id: Optional[str] = None,
    access_token: Optional[str] = None,
    resinkit_session: Optional[str] = None,
    personal_access_token: Optional[str] = None,
):
    """
    Configure the default resinkit instance with improved parameter naming.

    Args:
        base_url: Base URL for the ResinKit API (e.g., "http://localhost:8080")
        session_id: Session ID for authentication (alias for resinkit_session)
        access_token: Personal access token for authentication (alias for personal_access_token)
        resinkit_session: ResinKit session ID for authentication
        personal_access_token: Personal access token for authentication

    Usage:
        rsk.config(base_url="http://localhost:8080", access_token="your_token")
        rsk.config(base_url="https://api.resinkit.ai", session_id="your_session")
    """
    global _default_instance, _agent_manager

    # Handle parameter aliases
    final_session_id = session_id or resinkit_session
    final_access_token = access_token or personal_access_token

    # Only reconfigure if at least one parameter is provided
    if any([base_url, final_session_id, final_access_token]):
        _default_instance = Resinkit(
            base_url=base_url
            or os.getenv("RESINKIT_BASE_URL", "http://localhost:8080"),
            resinkit_session=final_session_id or os.getenv("RESINKIT_SESSION_ID"),
            personal_access_token=final_access_token
            or os.getenv("RESINKIT_ACCESS_TOKEN"),
        )
        # Reset agent manager when configuration changes
        _agent_manager = None
        print(f"✓ ResinKit configured with base_url: {_default_instance._base_url}")
    else:
        # Show current configuration if no parameters provided
        instance = _get_default_instance()
        print("Current ResinKit configuration:")
        print(f"  Base URL: {instance._base_url}")
        print(f"  Session ID: {'***' if instance._resinkit_session_id else 'Not set'}")
        print(
            f"  Access Token: {'***' if instance._personal_access_token else 'Not set'}"
        )


# Import this module and make it callable
import sys
import types

# Get the current module
current_module = sys.modules[__name__]


# Create a new module class that supports __call__
class CallableModule(types.ModuleType):
    def __call__(self, query: str) -> Any:
        return __call__(query)


# Create new callable module instance
new_module = CallableModule(__name__)

# Copy all attributes from current module to new module
for attr_name in dir(current_module):
    if not attr_name.startswith("_") or attr_name in [
        "__name__",
        "__file__",
        "__package__",
    ]:
        setattr(new_module, attr_name, getattr(current_module, attr_name))

# Replace the module
sys.modules[__name__] = new_module

__all__ = (
    "Task",
    "ResinkitAPIClient",
    "Resinkit",
    "show_tasks_ui",
    "show_vars_ui",
    "show_sql_task_ui",
    "get_task",
    "configure",
    "config",
)
