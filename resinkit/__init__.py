import asyncio
import os
from typing import Any, Optional

from .core.resinkit_api_client import ResinkitAPIClient
from .core.settings import get_settings, update_settings
from .core.task import Task
from .resinkit import Resinkit

# Module-level interface for callable behavior
_default_instance: Optional[Resinkit] = None
_agent_manager: Optional[Any] = None


def _get_default_instance() -> Resinkit:
    """Get or create the default Resinkit instance."""
    global _default_instance
    if _default_instance is None:
        # Use settings instead of direct environment variable access
        _default_instance = Resinkit()
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
    """Configure the default resinkit instance (legacy method)."""
    return config(base_url=base_url, session_id=session_id, access_token=access_token)


def config(
    base_url: Optional[str] = None,
    session_id: Optional[str] = None,
    access_token: Optional[str] = None,
    resinkit_session: Optional[str] = None,
    personal_access_token: Optional[str] = None,
    sql_gateway_url: Optional[str] = None,
    **kwargs,
):
    """
    Configure the default resinkit instance with improved parameter naming.

    Args:
        base_url: Base URL for the ResinKit API (e.g., "http://localhost:8080")
        session_id: Session ID for authentication (alias for resinkit_session)
        access_token: Personal access token for authentication (alias for personal_access_token)
        resinkit_session: ResinKit session ID for authentication
        personal_access_token: Personal access token for authentication
        sql_gateway_url: SQL Gateway URL
        **kwargs: Additional configuration parameters

    Usage:
        rsk.config(base_url="http://localhost:8080", access_token="your_token")
        rsk.config(base_url="https://api.resinkit.ai", session_id="your_session")
    """
    global _default_instance, _agent_manager

    # Handle parameter aliases
    final_session_id = session_id or resinkit_session
    final_access_token = access_token or personal_access_token

    # Only reconfigure if at least one parameter is provided
    if any([base_url, final_session_id, final_access_token, sql_gateway_url]) or kwargs:
        # Update settings first
        update_settings(
            base_url=base_url,
            session_id=final_session_id,
            access_token=final_access_token,
            sql_gateway_url=sql_gateway_url,
            **kwargs,
        )

        # Reset instances to pick up new settings
        _default_instance = None
        _agent_manager = None

        # Create new instance to confirm configuration
        instance = _get_default_instance()
        print(f"✓ ResinKit configured with base_url: {instance._base_url}")
    else:
        # Show current configuration if no parameters provided
        settings = get_settings()
        print("Current ResinKit configuration:")
        print(f"  Base URL: {settings.resinkit.base_url}")
        print(f"  Session ID: {'***' if settings.resinkit.session_id else 'Not set'}")
        print(
            f"  Access Token: {'***' if settings.resinkit.access_token else 'Not set'}"
        )
        if settings.resinkit.sql_gateway_url:
            print(f"  SQL Gateway URL: {settings.resinkit.sql_gateway_url}")


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
