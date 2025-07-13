## Resinkit API backed tools

Tools in this category are backed by REST APIs of the resinkit api service.

- Configs for connecting to resinkit API service is in settings.py::ResinkitConfig
- Python clients from OpenAPI spec are generated under [resinkit_api_client](../../../resinkit_api_client/) module, which contains typed data models and supports both sync and async operations. See [README.md](../../../resinkit_api_client/README.md) for instructions on how to use the generated client.
- By default, API backedn tools uses the API doc as the tools' descriptions, for example both `asyncio_detailed` and `asyncio` methods contains explainations on how to [crawl database tables.](../../../resinkit_api_client/api/db_crawl/crawl_database_tables.py) . 
- Tool doc can also be manually overwritten for better tool calling instructions. 