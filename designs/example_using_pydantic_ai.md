Implement an example SQL gen agent using `pydantic-ai` library.

REQUIREMENTS:

- Implement the code in examples folder
- Official doc of MCP client of `pydantic-ai` can be found at https://ai.pydantic.dev/mcp/client/#streamable-http-client
- Use DATA_ANALYSIS_SYSTEM_PROMPT from prompt.py as the prompt template, and user query is

```
"Can you provide the top 9 directors by movie count, including their ID, name, number of movies,"
" average inter-movie duration (rounded to the nearest integer), average rating (rounded to 2 decimals),"
" total votes, minimum and maximum ratings, and total movie duration? Sort the output first by"
" movie count in descending order and then by total movie duration in descending order."
```

- Follwing is an example for your reference. Different from the example, let's connect to http://localhost:8603/mcp-server/mcp which is an MCP server running in streamable http protocol.

```python
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStreamableHTTP

server = MCPServerStreamableHTTP('http://localhost:8000/mcp')
agent = Agent('openai:gpt-4o', toolsets=[server])

async def main():
    async with agent:
        result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
    print(result.output)
```
