

Resinkit MCP service with SSE protocol is running at backend URL: http://localhost:8603/mcp, add a python script to connect to this mcp server and expose MCP tools as llama-index tools. 

Let's use llama-index-tools-mcp package (already installed), code examples can be found at https://docs.llamaindex.ai/en/stable/examples/tools/mcp/

Do not test the connectivity using curl, the service is confirmed health with following connections properties:
- Transport Type: SSE
- URL: http://localhost:8603/mcp
- Authentication Header: "X-ResinKit-Api-Token: test-token"
