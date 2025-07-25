"""
AI Agents for ResinKit

This module provides AI agents and their management infrastructure
implemented using pydantic-ai framework.
"""

from .agent_manager import AgentManager, create_agent_manager, get_default_agent_manager
from .sql_gen_agent import DEFAULT_SQL_SYSTEM_PROMPT, create_sql_generation_agent

__all__ = [
    "AgentManager",
    "create_agent_manager",
    "get_default_agent_manager",
    "create_sql_generation_agent",
    "DEFAULT_SQL_SYSTEM_PROMPT",
]
