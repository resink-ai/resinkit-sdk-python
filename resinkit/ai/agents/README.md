# SQL Generator Agent Workflow

## Overview

The SQL Generator Agent Workflow is a sophisticated text-to-SQL AI agent implementation built using LlamaIndex Workflows framework with MCP (Model Context Protocol) server integration. It follows a structured approach to convert natural language queries into accurate SQL statements through discovery, planning, execution, and presentation phases.

## Architecture

### Core Components

1. **SqlGeneratorWorkflow**: Main workflow class implementing the 5-phase SQL generation process
2. **MCPManager**: Handles MCP server connections and tool loading
3. **Event System**: Custom events for each workflow phase
4. **Template System**: Comprehensive prompt templates for different phases

### Workflow Phases

```
User Query → Analysis → Discovery → Planning → Execution → Presentation → SQL Result
```

1. **Query Analysis**: Understand user requirements and data needs
2. **Discovery**: Explore available data sources and schemas
3. **Planning**: Create detailed execution plan for SQL generation
4. **Execution**: Generate and optionally validate SQL queries
5. **Presentation**: Format and present final results

## Features

### ✅ Implemented Features

- **LlamaIndex Workflows Integration**: Built on the robust LlamaIndex Workflows framework
- **MCP Server Support**: Dynamic tool loading from multiple MCP servers
- **Multi-Phase Processing**: Structured 5-phase approach for comprehensive SQL generation
- **Template System**: Configurable prompt templates for each workflow phase
- **Tool Integration**: Seamless integration with ResinKit API tools and MCP tools
- **Error Handling**: Robust error handling with graceful fallbacks
- **Async Support**: Full async/await support for optimal performance
- **Extensible Design**: Easy to extend with additional phases or tools
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

### 🔧 Configuration Options

- **LLM Selection**: Support for OpenAI, Anthropic, and Google LLMs
- **MCP Configuration**: Flexible MCP server configuration
- **Tool Management**: Custom tool addition and configuration
- **Timeout Settings**: Configurable workflow timeouts
- **Verbosity Control**: Adjustable logging verbosity

## Usage

### Basic Usage

```python
from resinkit.ai.agents import generate_sql_with_workflow

# Simple SQL generation
result = await generate_sql_with_workflow(
    query="What were the total sales for each product category?",
    verbose=True
)

print(result['generated_sql'])
```

### Advanced Usage with MCP

#### Command-Based MCP Server
```python
from resinkit.ai.agents import SqlGeneratorWorkflow

# Command-based MCP configuration
mcp_config = {
    "mcp_servers": {
        "postgres": {
            "server_type": "command",
            "command": ["npx", "-y", "@modelcontextprotocol/server-postgres"],
            "env": {"POSTGRES_CONNECTION_STRING": "postgresql://..."},
            "enabled": True
        }
    }
}

# Create workflow with command-based MCP integration
workflow = SqlGeneratorWorkflow(
    mcp_config=mcp_config,
    enable_mcp=True,
    verbose=True
)

result = await workflow.run("Find top customers by revenue")
```

#### HTTP Streamable MCP Server
```python
from resinkit.ai.agents import SqlGeneratorWorkflow

# HTTP-based MCP configuration
mcp_config = {
    "mcp_servers": {
        "http_localhost": {
            "server_type": "http",
            "url": "http://localhost:8603/mcp-server/mcp",
            "headers": {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            "timeout": 30.0,
            "enabled": True
        },
        "analytics_api": {
            "server_type": "http",
            "url": "https://api.analytics.com/mcp/v1",
            "headers": {
                "Authorization": "Bearer your-api-key"
            },
            "enabled": True
        }
    }
}

# Create workflow with HTTP MCP integration
workflow = SqlGeneratorWorkflow(
    mcp_config=mcp_config,
    enable_mcp=True,
    verbose=True
)

result = await workflow.run("Analyze quarterly sales trends")
```

### Direct Workflow Control

```python
from resinkit.ai.agents import SqlGeneratorWorkflow

# Create workflow instance
workflow = SqlGeneratorWorkflow(verbose=True)

# Get available tools
tools = await workflow.get_available_tools()
print(f"Available tools: {len(tools)}")

# Run workflow
result = await workflow.run("Show monthly sales trends")

# Access detailed results
print(f"SQL: {result['generated_sql']}")
print(f"Explanation: {result['explanation']}")
print(f"Completed: {result['workflow_completed']}")
```

## MCP Integration

### Supported MCP Servers

The workflow supports integration with both command-based and HTTP-based MCP servers:

#### Command-Based Servers
- **Filesystem**: File system access for data and documentation
- **SQLite**: Local SQLite database operations
- **PostgreSQL**: PostgreSQL database integration
- **Git**: Version control and repository access
- **Custom Command Servers**: Support for custom subprocess MCP servers

#### HTTP-Based Servers
- **HTTP MCP Servers**: RESTful MCP servers over HTTP/HTTPS
- **Streamable HTTP Servers**: Support for streaming responses
- **Server-Sent Events (SSE)**: Event streaming MCP servers
- **Authenticated APIs**: API key and token-based authentication
- **Custom HTTP Servers**: Support for any HTTP MCP server implementation

### MCP Configuration

#### Command-Based Server Configuration
```json
{
  "mcp_servers": {
    "postgres": {
      "server_type": "command",
      "command": ["npx", "-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost/db"
      },
      "timeout": 60.0,
      "enabled": true
    },
    "filesystem": {
      "server_type": "command",
      "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem", "/data"],
      "env": {},
      "timeout": 30.0,
      "enabled": true
    }
  }
}
```

#### HTTP-Based Server Configuration
```json
{
  "mcp_servers": {
    "http_localhost": {
      "server_type": "http",
      "url": "http://localhost:8603/mcp-server/mcp",
      "headers": {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      "timeout": 30.0,
      "enabled": true
    },
    "http_authenticated": {
      "server_type": "http",
      "url": "https://api.company.com/mcp/v1",
      "headers": {
        "Content-Type": "application/json",
        "Authorization": "Bearer YOUR_API_KEY",
        "X-Client-Version": "1.0.0"
      },
      "timeout": 60.0,
      "enabled": true
    },
    "http_sse_streaming": {
      "server_type": "http_sse",
      "url": "https://stream.company.com/mcp/events",
      "headers": {
        "Accept": "text/event-stream",
        "Authorization": "Bearer streaming-token"
      },
      "timeout": 120.0,
      "enabled": true
    }
  }
}
```

## File Structure

```
resinkit/ai/agents/
├── __init__.py                    # Package exports
├── README.md                      # This documentation
├── sql_generator_workflow.py     # Main workflow implementation
└── mcp_integration.py            # MCP server integration

examples/
├── sql_generator_workflow_example.py  # Comprehensive examples
└── mcp_config_example.json            # MCP configuration template
```

## Event System

The workflow uses a custom event system for phase transitions:

- `QueryAnalysisEvent`: Analysis phase completion
- `DiscoveryEvent`: Data source discovery completion
- `PlanningEvent`: Execution plan creation
- `ExecutionEvent`: SQL generation completion
- `PresentationEvent`: Final result presentation

## Error Handling

The workflow includes comprehensive error handling:

- **Graceful Degradation**: Continues operation when non-critical components fail
- **MCP Fallbacks**: Falls back to default tools if MCP servers are unavailable
- **Timeout Management**: Proper timeout handling for long-running operations
- **Error Context**: Detailed error information for debugging

## Performance Features

- **Parallel Tool Execution**: Maximizes efficiency with parallel tool calls
- **Async/Await**: Full async support for optimal performance
- **Tool Caching**: Efficient tool loading and caching
- **Connection Pooling**: Optimized MCP connection management

## Extending the Workflow

### Adding Custom Phases

```python
from resinkit.ai.agents.sql_generator_workflow import SqlGeneratorWorkflow

class CustomSqlWorkflow(SqlGeneratorWorkflow):
    @step
    async def custom_validation_step(self, ctx: Context, ev: ExecutionEvent) -> StopEvent:
        # Custom validation logic
        return StopEvent(result=validated_result)
```

### Adding Custom Tools

```python
from llama_index.core.tools import FunctionTool

def custom_tool():
    # Custom tool implementation
    pass

custom_function_tool = FunctionTool.from_defaults(fn=custom_tool)

workflow = SqlGeneratorWorkflow(tools=[custom_function_tool])
```

## Troubleshooting

### Common Issues

1. **MCP Connection Failures**: Ensure MCP servers are properly installed and configured
2. **Tool Loading Errors**: Verify tool dependencies and API credentials
3. **Timeout Issues**: Adjust timeout settings for complex queries
4. **Memory Issues**: Monitor memory usage with large datasets

### Debug Mode

Enable debug mode for detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

workflow = SqlGeneratorWorkflow(verbose=True)
```

## Examples

See `examples/sql_generator_workflow_example.py` for comprehensive usage examples including:

- Basic SQL generation
- MCP server integration
- Complex query scenarios
- Error handling patterns
- Performance optimization

## Dependencies

- `llama-index-core>=0.12.48`
- `llama-index-tools-mcp>=0.2.6`
- `resinkit` (current package)

## License

This implementation is part of the ResinKit SDK and follows the same licensing terms.