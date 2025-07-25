import os
from typing import Dict, List, Literal, Optional, Sequence, Union

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_CURRENT_ENV = os.getenv("ENV", "dev")


class DeepSubModel(BaseModel):
    v4: str


class SubModel(BaseModel):
    v1: str
    v2: bytes
    v3: int
    deep: DeepSubModel


class EmbeddingConfig(BaseModel):
    provider: str = "google"  # google, openai
    model: str = "models/embedding-001"  # Google Gemini embedding model
    dimension: int = 768  # Google Gemini embedding dimension


class KnowledgeBaseConfig(BaseModel):
    persist_root_dir: str = (
        "./knowledge_base_data"  # Root directory for knowledge base persistence
    )
    auto_persist: bool = (
        True  # Whether to automatically persist state after modifications
    )


class LLMConfig(BaseModel):
    provider: str = "openai"  # openai, anthropic, google
    model: str = "gpt-4-turbo"
    temperature: float = 0.1
    max_tokens: int = 2000


# MCP Configuration Classes
MCPTransportType = Literal["streamable_http", "sse", "stdio"]
MCPLogLevel = Literal[
    "debug", "info", "notice", "warning", "error", "critical", "alert", "emergency"
]


class MCPConfigBase(BaseModel):
    """Base configuration for MCP servers with common fields."""

    # Common MCP server configuration fields
    tool_prefix: Optional[str] = None
    log_level: Optional[MCPLogLevel] = None
    timeout: float = 5.0
    allow_sampling: bool = True
    max_retries: int = 1

    # Transport type identifier
    transport: MCPTransportType


class MCPStreamableHTTPConfig(MCPConfigBase):
    """Configuration for MCP Streamable HTTP transport."""

    transport: Literal["streamable_http"] = "streamable_http"
    url: str
    headers: Optional[Dict[str, str]] = None
    sse_read_timeout: float = 300.0


class MCPSSEConfig(MCPConfigBase):
    """Configuration for MCP Server-Sent Events transport."""

    transport: Literal["sse"] = "sse"
    url: str
    headers: Optional[Dict[str, str]] = None
    sse_read_timeout: float = 300.0


class MCPStdioConfig(MCPConfigBase):
    """Configuration for MCP stdio transport."""

    transport: Literal["stdio"] = "stdio"
    command: str
    args: List[str] = Field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    cwd: Optional[str] = None


# Union type for all MCP configurations
MCPConfig = Union[MCPStreamableHTTPConfig, MCPSSEConfig, MCPStdioConfig]


class MCPManagerConfig(BaseModel):
    """Configuration for the MCP Manager containing multiple MCP server configurations."""

    servers: Dict[str, MCPConfig] = Field(default_factory=dict)
    auto_connect: bool = True
    connection_timeout: float = 30.0


# Predefined LLM configurations for different providers
OPENAI_LLM_CONFIG = LLMConfig(
    provider="openai", model="gpt-4o-mini", temperature=0.1, max_tokens=2000
)

ANTHROPIC_LLM_CONFIG = LLMConfig(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    temperature=0.1,
    max_tokens=2000,
)

GOOGLE_LLM_CONFIG = LLMConfig(
    provider="google",
    model="gemini-1.5-flash",
    temperature=0.1,
    max_tokens=2000,
)


# Predefined MCP configurations
DEFAULT_HTTP_MCP_CONFIG = MCPStreamableHTTPConfig(
    url="http://localhost:8603/mcp-server/mcp",
    headers={"Content-Type": "application/json"},
    timeout=10.0,
)

EVERYTHING_STDIO_MCP_CONFIG = MCPStdioConfig(
    command="npx", args=["-y", "@modelcontextprotocol/server-everything"], timeout=10.0
)

DEFAULT_MCP_MANAGER_CONFIG = MCPManagerConfig(
    servers={
        "local_http": DEFAULT_HTTP_MCP_CONFIG,
        "everything": EVERYTHING_STDIO_MCP_CONFIG,
    },
    auto_connect=True,
    connection_timeout=30.0,
)


class AgentsConfig(BaseModel):
    """Configuration for AI Agents Manager."""

    # Default model configuration for agents
    default_llm_config: LLMConfig = Field(default_factory=lambda: ANTHROPIC_LLM_CONFIG)

    # SQL Generation Agent specific settings
    sql_agent_auto_approve_tools: bool = False
    sql_agent_verbose: bool = True
    sql_agent_temperature: float = 0.1
    sql_agent_max_tokens: int = 4000

    # Agent initialization settings
    auto_connect_mcp: bool = True
    enable_tool_approval: bool = True


class ResinkitConfig(BaseModel):
    """Configuration for ResinKit API client and core functionality."""

    base_url: str = "http://localhost:8603"
    session_id: Optional[str] = None
    access_token: Optional[str] = None
    sql_gateway_url: Optional[str] = None

    # Local storage configuration
    local_storage_dir: str = ".rsk"

    @property
    def sources_dir(self) -> str:
        """Directory for storing source data."""
        return f"{self.local_storage_dir}/sources"


class Settings(BaseSettings):
    # Pydantic's internal mechanisms specifically look for a class variable named `model_config`
    # to determine the settings source.
    model_config = SettingsConfigDict(
        env_file=(".env.common", f".env.{_CURRENT_ENV}"),
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    sub_model: Optional[SubModel] = None

    # ResinKit configuration
    resinkit: ResinkitConfig = ResinkitConfig()

    # AI configuration
    llm_config: LLMConfig = LLMConfig()
    embedding_config: EmbeddingConfig = EmbeddingConfig()
    knowledge_base_config: KnowledgeBaseConfig = KnowledgeBaseConfig()
    mcp_manager_config: MCPManagerConfig = MCPManagerConfig()
    agents_config: AgentsConfig = AgentsConfig()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override with environment variables if they exist
        if os.getenv("RESINKIT_BASE_URL"):
            self.resinkit.base_url = os.getenv("RESINKIT_BASE_URL")
        if os.getenv("RESINKIT_SESSION_ID"):
            self.resinkit.session_id = os.getenv("RESINKIT_SESSION_ID")
        if os.getenv("RESINKIT_ACCESS_TOKEN"):
            self.resinkit.access_token = os.getenv("RESINKIT_ACCESS_TOKEN")


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def update_settings(
    base_url: Optional[str] = None,
    session_id: Optional[str] = None,
    access_token: Optional[str] = None,
    sql_gateway_url: Optional[str] = None,
    **kwargs,
) -> Settings:
    """
    Update global settings with new configuration values.

    Args:
        base_url: Base URL for the ResinKit API
        session_id: Session ID for authentication
        access_token: Personal access token for authentication
        sql_gateway_url: SQL Gateway URL
        **kwargs: Additional settings to update

    Returns:
        Updated Settings instance
    """
    global _settings

    # Get current settings or create new ones
    current_settings = get_settings()

    # Update ResinKit configuration
    if base_url is not None:
        current_settings.resinkit.base_url = base_url
    if session_id is not None:
        current_settings.resinkit.session_id = session_id
    if access_token is not None:
        current_settings.resinkit.access_token = access_token
    if sql_gateway_url is not None:
        current_settings.resinkit.sql_gateway_url = sql_gateway_url

    # Update any other settings passed via kwargs
    for key, value in kwargs.items():
        if hasattr(current_settings, key):
            setattr(current_settings, key, value)

    return current_settings


def reset_settings() -> None:
    """Reset the global settings instance."""
    global _settings
    _settings = None
