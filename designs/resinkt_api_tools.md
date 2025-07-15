## Resinkit API backed tools factory

Using factory design pattern and implement logic to convert resinkit API rest endpoints into LlamaIndex FunctionTools:

- Configs for connecting to resinkit API service is in settings.py::ResinkitConfig
- A wrapped client class is provided at [resinkit_api_client.py](../../core/resinkit_api_client.py)
- By default, API backedn tools uses the API doc as the tools' descriptions, for example both `asyncio_detailed` and `asyncio` methods contains explainations on how to [crawl database tables.](../../../resinkit_api_client/api/db_crawl/crawl_database_tables.py) . 
- Tool doc can also be manually overwritten for better tool calling instructions. 

The expected usage is something like below:

```python
ResinkitApiTools.init()
list_sql_tool = ResinkitApiTools.tool_list_sql_sources()
# OR one can override tool description
list_sql_tool = ResinkitApiTools.tool_list_sql_sources(description="List all available SQL data sources configured in the ResinKit system. ")
```


Requirements:
1. use aysnc function when possible, avoid converting async functions to sync functions or nested asyncio event loop wrestling
2. do not create tools for all endpoints, focus on following endpoints for now:
     - GET /api/v1/agent/tasks. List Tasks
     - POST /api/v1/agent/tasks. Submit Task
     - GET /api/v1/agent/sql/sources. List Sql Sources
     - POST /api/v1/agent/sql/query. Execute Sql Query
3. Avoid duplicated code, provide commonly used function if the same logic is used multiple times.

