# ResinKit SDK Examples

This directory contains example implementations demonstrating various features and capabilities of the ResinKit SDK.

## Available Examples

### 1. SQL Generation Agent (`sql_generation_agent_example.py`)

**New!** Complete SQL generation agent using pydantic-ai framework with step-by-step workflow.

**Features:**

- Interactive SQL generation from natural language queries
- Step-by-step data discovery and exploration workflow
- Human-in-the-loop tool approval system
- Structured result parsing and presentation
- Support for multiple MCP server connections
- Comprehensive error handling and logging

**Usage:**
```bash
python examples/sql_generation_agent_example.py
```

**Requirements:**
- MCP server running at `http://localhost:8603/mcp-server/mcp`
- Anthropic API key set in environment variables
- Tools available: `list_data_sources`, `list_table_schemas`, `execute_sql_query`, `canvas_presentation`

### 2. Basic Pydantic AI SQL Example (`pydantic_ai_sql_example.py`)

**New!** Demonstrates SQL generation using the `pydantic-ai` library with MCP (Model Context Protocol) integration.

**Features:**

- Uses `pydantic-ai` Agent with OpenAI GPT-4o
- Connects to MCP server via HTTP Streamable protocol
- Implements the `DATA_ANALYSIS_SYSTEM_PROMPT` for comprehensive data analysis
- Generates SQL for complex analytical queries

**Requirements:**

- MCP server running at `http://localhost:8603/mcp-server/mcp`
- OpenAI API key set as environment variable
- `pydantic-ai` library (included in dependencies)

**Usage:**

```bash
export OPENAI_API_KEY="your-api-key-here"
python examples/pydantic_ai_sql_example.py
```

**Example Query:**
The example processes a complex analytical query asking for the top 9 directors by movie count, including various metrics like average inter-movie duration, ratings, and vote counts.

### 2. MCP Agent SQL Example (`mcp_agent_sql_example.py`)

Demonstrates SQL generation using the existing ResinKit agent workflow with MCP integration.

**Features:**

- Uses LlamaIndex-based agents
- MCP server integration for dynamic tool loading
- SQL generation workflow with discovery, planning, and execution phases

### 3. HTTP MCP Example (`http_mcp_example.py`)

Shows how to use HTTP-based MCP servers with ResinKit agents.

**Features:**

- HTTP MCP client implementation
- Custom tool integration
- Error handling and connection management

### 4. Factory Usage Example (`factory_usage.py`)

Demonstrates the factory pattern for creating and configuring agents.

### 5. MCP UI Example (`mcp_ui_example.py`)

Shows how to create user interfaces for MCP-enabled agents using Panel.

## Quick Start

1. **Install Dependencies:**

   ```bash
   pip install -e .
   ```

2. **Set Environment Variables:**

   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export ANTHROPIC_API_KEY="your-anthropic-api-key"  # Optional
   export GOOGLE_API_KEY="your-google-api-key"        # Optional
   ```

3. **Run an Example:**
   ```bash
   python examples/pydantic_ai_sql_example.py
   ```

## MCP Server Setup

Several examples require an MCP server running locally. Here are common setup options:

### Option 1: ResinKit MCP Server

```bash
# Start the ResinKit MCP server (if available)
python -m resinkit.mcp.server --port 8603
```

### Option 2: Standard MCP Servers

```bash
# PostgreSQL MCP server
npx -y @modelcontextprotocol/server-postgres

# SQLite MCP server
npx -y @modelcontextprotocol/server-sqlite database.db

# Filesystem MCP server
npx -y @modelcontextprotocol/server-filesystem /path/to/directory
```

## Configuration

### MCP Configuration (`mcp_config_example.json`)

The `mcp_config_example.json` file provides template configurations for various MCP servers:

- **Command-based servers**: PostgreSQL, SQLite, Git, Filesystem
- **HTTP-based servers**: Local and remote HTTP endpoints
- **Authentication**: Bearer token and API key examples

## Common Issues & Troubleshooting

### Connection Errors

- Ensure MCP server is running and accessible
- Check firewall settings for local connections
- Verify API keys are correctly set

### Import Errors

- Ensure all dependencies are installed: `pip install -e .`
- Check Python version compatibility (>=3.10 required)

### Tool Loading Issues

- Verify MCP server is properly configured
- Check MCP server logs for initialization errors
- Ensure required tools are available in the MCP server

## Development

To add a new example:

1. Create a new Python file in this directory
2. Follow the naming convention: `feature_type_example.py`
3. Include comprehensive docstrings and error handling
4. Add usage instructions to this README
5. Test with the provided test utilities

## Additional Resources

- [ResinKit Documentation](../README.md)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
