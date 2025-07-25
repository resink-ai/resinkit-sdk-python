import asyncio
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


def _get_agent_manager() -> Any:
    """Get or create the agent manager."""
    global _agent_manager
    if _agent_manager is None:
        # AgentManager has been removed along with llama-index dependencies
        raise ImportError(
            "AgentManager is no longer available. llama-index dependencies have been removed."
        )
    return _agent_manager


def task(
    task_name: str, payload: Optional[dict] = None, source_name: str = None
) -> Task:
    """
    Submit a task to the Resinkit API.

    Args:
        task_name: Name of the task to submit
        payload: Optional task payload
        source_name: Optional source name

    Returns:
        Task object for tracking the submitted task
    """
    return _get_default_instance().task(task_name, payload, source_name)


def __call__(query: str) -> Any:
    """
    Make the module callable for natural language queries.

    Usage: rsk("What were the total sales for each product category?")
    """
    agent_manager = _get_agent_manager()

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import nest_asyncio

            nest_asyncio.apply()
            return loop.run_until_complete(agent_manager.run_workflow(query))
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


def show_sources_ui():
    """Show the sources management UI."""
    return _get_default_instance().show_sources_ui()


def show_sql_task_ui():
    """Show the SQL task management UI."""
    return _get_default_instance().show_sql_task_ui()


def sql_task_ui():
    """Show the SQL task management UI."""
    return _get_default_instance().show_sql_task_ui()


# Make the module callable
class CallableModule:
    def __init__(self, module_name):
        self.__name__ = module_name

    def __call__(self, query: str) -> Any:
        return __call__(query)

    def task(
        self, task_name: str, payload: Optional[dict] = None, source_name: str = None
    ) -> Task:
        return task(task_name, payload, source_name)

    def show_tasks_ui(self):
        return show_tasks_ui()

    def show_vars_ui(self):
        return show_vars_ui()

    def show_sources_ui(self):
        return show_sources_ui()

    def show_sql_task_ui(self):
        return show_sql_task_ui()

    def sql_task_ui(self):
        return sql_task_ui()

    def __getattr__(self, name):
        # Dynamic import for submodules
        if name in [
            "ai",
            "client",
            "core",
            "ui",
            "resinkit_api_client",
        ]:
            import importlib

            full_module_name = f"{self.__name__}.{name}"
            try:
                submodule = importlib.import_module(full_module_name)
                setattr(self, name, submodule)
                return submodule
            except ImportError:
                pass

        # Fall back to original module attributes
        original_module = sys.modules.get(f"_original_{self.__name__}")
        if original_module and hasattr(original_module, name):
            attr = getattr(original_module, name)
            setattr(self, name, attr)
            return attr

        # Standard attributes
        if name == "ResinkitAPIClient":
            return ResinkitAPIClient
        elif name == "Resinkit":
            return Resinkit
        elif name == "Task":
            return Task
        elif name == "get_settings":
            return get_settings
        elif name == "update_settings":
            return update_settings

        raise AttributeError(f"module '{self.__name__}' has no attribute '{name}'")


# Replace the module in sys.modules
import sys  # noqa: E402

# Store original module
sys.modules[f"_original_{__name__}"] = sys.modules[__name__]

# Replace with callable version
sys.modules[__name__] = CallableModule(__name__)

# Export the main components
__all__ = [
    "ResinkitAPIClient",
    "Resinkit",
    "Task",
    "get_settings",
    "update_settings",
    "task",
    "show_tasks_ui",
    "show_vars_ui",
    "show_sources_ui",
    "show_sql_task_ui",
    "sql_task_ui",
]
