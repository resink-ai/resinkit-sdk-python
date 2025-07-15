
# Sources UI

Build a panel based UI for interacting with SQL sources via following rest endpoints:

POST /api/v1/agent/sql/sources, Create Sql Source
GET /api/v1/agent/sql/sources, List Sql Sources
GET /api/v1/agent/sql/sources/{source_name}, Get Sql Source
PUT /api/v1/agent/sql/sources/{source_name}, Update Sql Source
DELETE /api/v1/agent/sql/sources/{source_name}, Delete Sql Source
GET /api/v1/agent/sql/sources/{source_name}/databases, List Databases
POST /api/v1/agent/db-crawl/crawl, Crawl database tables

Core UIs:
1. A table that list all the available SQL sources.
2. A button that allows adding new sources
3. Rows of the table are selectable, allow batch deleting the sources.
4. Each row has a crawl button, allow crawling the DB to fetch the knowledge of the tables. 
   - Crawl results are saved to `.rsk/sources/` folder in the current working directory. 
   - Below is the data modol of the crawl result. Save results to different files
      * save the `retrieval_metadata` to `.rsk/sources/.retrieval_metadata.json`
      * for each table: TableCrawlResult in tables:
         - save table.ddl to `.rsk/sources/.${table_name}/ddl.sql`
         - save sample data to `.rsk/sources/.${table_name}/sample.csv`
         - save dsds to `.rsk/sources/.${table_name}/dsds.txt`

```python
@_attrs_define
class DbCrawlResult:
    """Complete result of database crawling operation

    Attributes:
        retrieval_metadata (RetrievalMetadata): Metadata about the crawl operation
        tables (list['TableCrawlResult']): Results for each crawled table
    """

    retrieval_metadata: "RetrievalMetadata"
    tables: list["TableCrawlResult"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)
    ...

@_attrs_define
class TableCrawlResult:
    """Result of crawling a single table

    Attributes:
        table_name (str): Name of the table
        full_path (str): Full path including schema if applicable
        ddl (str): DDL (CREATE TABLE statement) for the table
        sample_data (list['TableCrawlResultSampleDataItem']): Sample data from the table
        dsds (Union['TableCrawlResultDsdsType0', None, Unset]): Descriptive Sample Data Schema
    """

    table_name: str
    full_path: str
    ddl: str
    sample_data: list["TableCrawlResultSampleDataItem"]
    dsds: Union["TableCrawlResultDsdsType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)
```


**IMPORTANT NOTEs**
- Following the same coding style as in [variables_ui.py](./variables_ui.py)
- Put the implementation under [ui](../ui/) module


