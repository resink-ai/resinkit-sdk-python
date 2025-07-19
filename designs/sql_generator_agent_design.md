Implement a AI agent workflow that takes user query, calls a list of tools and output a SQL. Following is an example user flow:

1. user feed in a comprehensive prompt, like below, details are hidden, but notice it consists of severl xml denoted sections.

```
You are a proficient data scientist, specialize in converting natural language queries into accurate SQL statements and managing database operations.

You work collaboratively with a USER to understand their data requirements and generate appropriate SQL queries. Your main goal is to follow the USER's instructions at each message, denoted by the <user_query> tag.
<tool_calling>...</tool_calling>
<search_and_discovery>...</search_and_discovery>
<user_query>...</user_query>
```

2. the AI agent then worked step by step like:
   1. > I'll help you generate a SQL query to find the top 9 directors by movie count with all the requested metrics. Let me start by exploring the available data sources and understanding the database schema. <tool_call>list_data_sources</tool_call>
   2. > Now let me explore the table schemas in the IMDb movies database to understand the structure: <tool_call>list_table_schemas</tool_call>
   3. > Perfect! I can see the database structure. Now let me examine the relationships more closely to understand how to calculate the inter-movie duration. I need to look at the director_mapping table to understand how directors are connected to movies: <tool_call>execute_sql_query</tool_call>
   4. > Now let me check the date information to understand how to calculate inter-movie duration: <tool_call>execute_sql_query</tool_call>
   5. > Great! Now I understand the data structure. Let me create a comprehensive SQL query to get all the requested metrics for the top 9 directors. The inter-movie duration will be calculated as the average number of days between consecutive movie releases for each director. <tool_call>execute_sql_query</tool_call>
   6. > Perfect! I have successfully generated the SQL query that provides the top 9 directors by movie count with all the requested metrics. Here's the complete SQL query: <tool_call>canvas_presentation</tool_call>
   7. > Query Results Summary: ...(details hidden)...
   8. > Key Query Features: ...(details hidden)...

Implementation requirements:

- All the tools are provided by MCP server, make sure the AI agent is able to connect to different MCP servers.
- Use llamam-index framework, more specifically `Workflows`
- The implementation should be extensible to other customized workflows as well.
- The work flow starts by taking user's query, then builds the complete query uisng string template, and then make plans and then execute plans.
- Place the implementation inside resinkit/ai/agents folder
