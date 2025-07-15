## Impelment a llama-index `FunctionTool` whose description is as below

```json
{
  "description": "PROPOSE a SQL query to run on behalf of the user.\nIf you have this tool, note that you DO have the ability to run queries directly on the USER's database.\nNote that the user will have to approve the query before it is executed.\nThe user may reject it if it is not to their liking, or may modify the query before approving it. If they do change it, take those changes into account.\nThe actual query will NOT execute until the user approves it. The user may not approve it immediately. Do NOT assume the query has started running.\nIf the step is WAITING for user approval, it has NOT started running.\nIn using these tools, adhere to the following guidelines:\n1. Based on the contents of the conversation and any provided schema, you will generate a SQL query.\n2. Before generating complex queries, consider using simpler queries to inspect the database schema, tables, or data types to ensure correctness.\n3. Do NOT generate queries that could be destructive (e.g., DROP, DELETE, TRUNCATE) unless explicitly asked to do so by the user.\n4. Ensure the SQL dialect is appropriate for the target database if that information is available.\n5. Don't include any newlines in the query.",
  "name": "run_sql_query",
  "parameters": {
    "properties": {
      "query": {
        "description": "The SQL query to execute.",
        "type": "string"
      },
      "explanation": {
        "description": "A one-sentence explanation as to why this query needs to be run and how it contributes to the goal.",
        "type": "string"
      }
    },
    "required": ["query", "explanation"],
    "type": "object"
  }
}
```

## Key Features to be Implementetd

1. LlamaIndex Tool Integration

   - Inherits from FunctionTool for seamless agent integration
   - Uses Pydantic schemas for type safety and validation
   - Supports both sync and async execution

2. User Approval Workflow

   - Configurable approval callback system
   - Support for query modification during approval
   - Auto-approval for safe SELECT queries with LIMIT

3. Smart Result Handling
   - Pandas integration for data manipulation
   - Automatic result truncation for large datasets
   - Structured JSON output for agent consumption
   - Performance metrics (execution time, row counts)

## Quick Start Examples

```python
# 1. Basic standalone usage
sql_tool = SQLCommandTool("jdbc:sqlite::memory;")
result = sql_tool.call(
    sql_command="SELECT * FROM users LIMIT 10",
    explanation="Get sample user data"
)
```
