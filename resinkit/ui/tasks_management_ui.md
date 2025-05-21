

### Task Management Endpoints

### 1. Submit a new Task

- **Endpoint:** `POST /agent/tasks`
- **Description:** Submits a new task for asynchronous execution. Supports variable resolution in the payload.
- **Request Body (`application/json`):**

  ```json
  {
    "task_type": "string (enum, required)",
    "task_name": "string (optional, user-friendly name)",
    "description": "string (optional)",
    "configs": "String (required, task-type specific configurations, base64 encoded)",
    "priority": "integer (optional, default: 0)",
    "notification_config": {
      // (optional)
      "webhook_url": "string (url)",
      "headers": { "header_name": "header_value" } // optional headers for webhook
    },
    "tags": ["string"] // (optional, for categorization/filtering)
  }
  ```

  **Example `configs` for `task_type: "flink_cdc_pipeline"` (it will be base64 encoded):**

  ```yaml
  task_type: flink_cdc_pipeline
  name: MySQL to Doris Sync Pipeline
  description: Synchronization of all MySQL tables to Doris
  task_timeout_seconds: 300

  job:
      ################################################################################
      # Description: Sync MySQL all tables to Doris
      ################################################################################
      source:
      type: mysql
      hostname: localhost
      port: 3306
      username: root
      password: 123456
      tables: app_db.\.*
      server-id: 5400-5404
      server-time-zone: UTC

      sink:
      type: doris
      fenodes: 127.0.0.1:8030
      username: root
      password: ""
      table.create.properties.light_schema_change: true
      table.create.properties.replication_num: 1

      pipeline:
      name: Sync MySQL Database to Doris
      parallelism: 2

  resources:
      flink_cdc_jars:
          - name: MySQL Pipeline Connector 3.3.0
          type: lib
          source: download
          location: https://repo1.maven.org/maven2/org/apache/flink/flink-cdc-pipeline-connector-mysql/3.3.0/flink-cdc-pipeline-connector-mysql-3.3.0.jar

          - name: Apache Doris Pipeline Connector 3.3.0
          type: lib
          source: download
          location: https://repo1.maven.org/maven2/org/apache/flink/flink-cdc-pipeline-connector-doris/3.3.0/flink-cdc-pipeline-connector-doris-3.3.0.jar

          - name: MySQL Connector Java
          type: classpath
          source: download
          location: https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.27/mysql-connector-java-8.0.27.jar
      flink_jars:
          - name: MySQL Connector Java
          download_link: https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.27/mysql-connector-java-8.0.27.jar

  # Flink environment settings
  environment:
      parallelism: 2
      checkpoint_interval: 60s
      restart_strategy: fixed-delay
      restart_attempts: 3
      restart_delay: 10s
      state_backend: rocksdb

  # Runtime configuration
  runtime:
      job_name: Sync MySQL Database to Doris
      savepoint_path: null
      allow_non_restored_state: false
  ```

  **Example `configs` for `task_type: "flink_sql"`:**

  ```yaml
  task_type: flink_sql
  name: MySQL CDC Order Processing
  description: Read orders from MySQL and process with SQL operations
  task_timeout_seconds: 300

  pipeline:
      sql: >
          -- checkpoint every 3000 milliseconds
          SET 'execution.checkpointing.interval' = '3s';

          -- register a MySQL table 'orders' in Flink SQL
          CREATE TABLE orders (
              order_id INT,
              order_date TIMESTAMP(0),
              customer_name STRING,
              price DECIMAL(10, 5),
              product_id INT,
              order_status BOOLEAN,
              PRIMARY KEY(order_id) NOT ENFORCED
              ) WITH (
              'connector' = 'mysql-cdc',
              'hostname' = 'localhost',
              'port' = '3306',
              'username' = 'root',
              'password' = '123456',
              'database-name' = 'mydb',
              'table-name' = 'orders');

          -- read snapshot and binlogs from orders table
          SELECT * FROM orders;

      sql_limit: 100

  resources:
      flink_jars:
          - name: MySQL Connector Java
          download_link: https://repo1.maven.org/maven2/mysql/mysql-connector-java/8.0.27/mysql-connector-java-8.0.27.jar
  # Flink environment settings
  environment:
  parallelism: 1
  checkpoint_interval: 3s
  execution_mode: streaming
  table_catalog: default_catalog
  table_database: default_database

  # Runtime configuration
  runtime:
  job_name: MySQL CDC SQL Processor
  result_storage:
      type: memory
      ttl: 3600
  ```

- **Success Response:** `202 Accepted`
  - **Headers:** `Location: /api/v1/agent/tasks/{task_id}`
  - **Body:**
    ```json
    {
      "task_id": "string (unique identifier for the task)",
      "status": "string (e.g., PENDING, SUBMITTED)",
      "message": "string (e.g., Task submitted successfully. Check status at the provided link.)",
      "created_at": "timestamp (ISO 8601)",
      "_links": {
        "self": { "href": "/api/v1/agent/tasks/{task_id}" }
      }
    }
    ```
- **Error Responses:** `400 Bad Request` (invalid input), `422 Unprocessable Entity` (semantically incorrect config), `500 Internal Server Error`.

### 2. Submit a Task with YAML

- **Endpoint:** `POST /agent/tasks/yaml`
- **Description:** Submits a new task using a YAML configuration string. Supports variable resolution in the YAML content.
- **Request Body (`text/plain`):** YAML string containing task configuration
- **Success Response:** `202 Accepted`
  - Same as the JSON submission endpoint
- **Error Responses:** `400 Bad Request` (invalid YAML format), `422 Unprocessable Entity` (semantically incorrect config), `500 Internal Server Error`.

---

### 3. Get Task Details

- **Endpoint:** `GET /agent/tasks/{task_id}`
- **Description:** Retrieves the current status, progress, and summary information of a specific task.
- **Path Parameters:** `task_id` (string, required)
- **Success Response:** `200 OK`
  ```json
  {
    "task_id": "string",
    "task_type": "string",
    "task_name": "string (optional)",
    "description": "string (optional)",
    "status": "string (current task status from enum)",
    "created_at": "timestamp (ISO 8601)",
    "updated_at": "timestamp (ISO 8601)",
    "started_at": "timestamp (ISO 8601, nullable)",
    "finished_at": "timestamp (ISO 8601, nullable)",
    "submitted_configs": "object (original configurations submitted by the user)",
    "priority": "integer",
    "tags": ["string"],
    "progress": {
      // (optional, present if task is running or has progress info)
      "percentage": "float (0-100, optional)",
      "current_step_key": "string (e.g., 'DEPLOYING_JOB', 'PROCESSING_DATA', 'UPLOADING_FILE')",
      "current_step_message": "string (user-friendly message for current step)",
      "details": "object (task-type specific progress data, e.g., records processed)"
    },
    "execution_details": {
      // (optional, task-type specific runtime identifiers)
      "flink_job_id": "string (optional, if applicable)",
      "flink_dashboard_url": "string (optional, if applicable)",
      "runner_instance_id": "string (optional, ID of the execution agent/pod)"
    },
    "log_summary": {
      // (optional, brief summary or recent critical logs)
      "info_snippets": ["string (recent info logs)"],
      "error_snippets": ["string (recent error logs)"]
    },
    "result_summary": {
      // (optional, summary or inline small results if applicable)
      "status_message": "string (e.g., 'Pipeline processed 1000 records', 'File uploaded successfully to /path/to/lib')",
      "data_preview": "object (small preview of data, if applicable and task produces data)"
    },
    "error_info": {
      // (optional, present if status is FAILED)
      "code": "string (internal error code, e.g., 'FLINK_SUBMISSION_ERROR')",
      "message": "string (detailed error message)",
      "details": "string (stack trace or further error context, can be extensive)"
    },
    "_links": {
      "self": { "href": "/api/v1/agent/tasks/{task_id}" },
      "cancel": {
        "href": "/api/v1/agent/tasks/{task_id}/cancel",
        "method": "POST"
      }, // if task is cancellable
      "logs": { "href": "/api/v1/agent/tasks/{task_id}/logs" },
      "results": { "href": "/api/v1/agent/tasks/{task_id}/results" } // if task produces retrievable results
    }
  }
  ```
- **Error Responses:** `404 Not Found`, `500 Internal Server Error`.

---

### 4. List Tasks

- **Endpoint:** `GET /agent/tasks`
- **Description:** Retrieves a list of tasks, with filtering and pagination.
- **Query Parameters:**
  - `task_type` (string, optional)
  - `status` (string, optional)
  - `task_name_contains` (string, optional, for partial name matching)
  - `tags_include_any` (string, optional, comma-separated list of tags)
  - `created_after` (timestamp ISO 8601, optional)
  - `created_before` (timestamp ISO 8601, optional)
  - `limit` (integer, optional, default: 20, max: 100)
  - `page_token` (string, optional, for pagination)
  - `sort_by` (string, optional, e.g., `created_at`, `updated_at`, `task_name`, default: `created_at`)
  - `sort_order` (string, optional, `asc` or `desc`, default: `desc`)
- **Success Response:** `200 OK`
  ```json
  {
    "tasks": [
      // Array of task summary objects (subset of fields from GET /agent/tasks/{task_id})
      {
        "task_id": "string",
        "task_type": "string",
        "task_name": "string (optional)",
        "status": "string",
        "created_at": "timestamp",
        "updated_at": "timestamp",
        "finished_at": "timestamp (nullable)",
        "_links": {
          "self": { "href": "/api/v1/agent/tasks/{task_id}" }
        }
      }
      // ... more tasks
    ],
    "total_count": "integer (total matching tasks if available without expensive full scan)",
    "next_page_token": "string (nullable, token for fetching the next page)"
  }
  ```
- **Error Responses:** `400 Bad Request` (e.g., invalid filter parameter), `500 Internal Server Error`.

---

### 5. Cancel a Task

- **Endpoint:** `POST /agent/tasks/{task_id}/cancel`
- **Description:** Requests cancellation of an ongoing task. This is an asynchronous operation.
- **Path Parameters:** `task_id` (string, required)
- **Request Body (`application/json`, optional):**
  ```json
  {
    "reason": "string (optional, reason for cancellation)",
    "force": "boolean (optional, default: false, whether to attempt forceful termination if graceful fails)"
  }
  ```
- **Success Response:** `202 Accepted`
  ```json
  {
    "task_id": "string",
    "status": "string (e.g., CANCELLING, or CANCELLED if immediate and successful)",
    "message": "string (e.g., Task cancellation initiated. Monitor task status for updates.)",
    "_links": {
      "task_status": { "href": "/api/v1/agent/tasks/{task_id}" }
    }
  }
  ```
- **Error Responses:** `404 Not Found`, `409 Conflict` (e.g., task already completed, failed, or not in a cancellable state), `500 Internal Server Error`.

---

### 6. Get Task Logs

- **Endpoint:** `GET /agent/tasks/{task_id}/logs`
- **Description:** Retrieves detailed logs for a specific task. Supports pagination and potentially streaming.
- **Path Parameters:** `task_id` (string, required)
- **Query Parameters:**
  - `log_type` (string, optional, e.g., `stdout`, `stderr`, `job_manager`, `task_manager`, `application`; default: combined application logs)
  - `since_timestamp` (timestamp ISO 8601, optional)
  - `since_token` (string, optional, pagination token from a previous log response)
  - `limit_lines` (integer, optional, default: 1000, max: 10000)
  - `stream` (boolean, optional, default: false. If true, API may use `text/event-stream`)
  - `log_level_filter` (string, optional, e.g. "INFO", "WARN", "ERROR", "DEBUG")
- **Success Response (if `stream=false`, `Content-Type: application/json`):**
  ```json
  {
    "task_id": "string",
    "log_entries": [
      {
        "timestamp": "timestamp (ISO 8601)",
        "level": "string (e.g., INFO, ERROR, DEBUG)",
        "source": "string (optional, e.g., 'flink_job_manager', 'cdc_pipeline_script', 'task_executor')",
        "message": "string (log line content)"
      }
      // ... more log entries
    ],
    "next_log_token": "string (nullable, for paginating to older logs if `since_token` not used for newer)",
    "previous_log_token": "string (nullable, for paginating to newer logs if applicable)"
  }
  ```
- **Success Response (if `stream=true`, `Content-Type: text/event-stream`):**

  ```text
  event: log_entry
  id: <unique_event_id_or_timestamp_nanos>
  data: {"timestamp": "...", "level": "INFO", "source": "...", "message": "Log line 1"}

  event: log_entry
  id: <unique_event_id_or_timestamp_nanos>
  data: {"timestamp": "...", "level": "ERROR", "source": "...", "message": "Error occurred"}
  ...
  # Stream may end with a special event or just close when logs are exhausted or task ends
  event: stream_control
  data: {"status": "LIVE_STREAMING_ENDED", "final_task_status": "COMPLETED"}
  ```

- **Error Responses:** `404 Not Found`, `500 Internal Server Error`.

---

### 7. Get Task Results

- **Endpoint:** `GET /agent/tasks/{task_id}/results`
- **Description:** Retrieves the results of a completed task. The format of the results is task-type dependent. This endpoint might return structured data, a link to download files, or directly stream file content.
- **Path Parameters:** `task_id` (string, required)
- **Success Response:** `200 OK`
  - **Content-Type:** Varies (e.g., `application/json`, `application/octet-stream`, or could be `302 Found` redirecting to a pre-signed URL for large files).
  - **Example for `application/json` result:**
    ```json
    {
      "task_id": "string",
      "task_type": "string",
      "status_at_retrieval": "COMPLETED", // Should generally only be available for COMPLETED tasks
      "result_type": "string (e.g., 'flink_sql_query_result_set', 'flink_cdc_job_metrics', 'file_upload_confirmation')",
      "data": "object | array (actual result data, if suitable for direct JSON response, e.g., SQL query output)",
      "artifacts": [
        // (optional, for larger results or multiple output files)
        {
          "name": "string (e.g., 'output.parquet', 'error_records.csv', 'job_metrics.json')",
          "type": "string (e.g., 'file', 'dataset_pointer', 'report')",
          "url": "string (pre-signed URL to download the artifact, or an API link to fetch it)",
          "size_bytes": "integer (optional)",
          "metadata": {
            // (optional, e.g., checksum, content_type if not implicit by URL)
            "content_type": "application/parquet"
          }
        }
      ],
      "summary": "string (optional, textual summary of results, e.g., 'Query returned 150 rows.', 'File 'my.jar' successfully deployed to Flink lib.')"
    }
    ```
  - If the result is a direct file download (e.g., for a single output artifact), headers like `Content-Disposition: attachment; filename="result.zip"` would be used.
- **Error Responses:** `404 Not Found`, `409 Conflict` (e.g., task not yet completed, failed, or has no retrievable results), `500 Internal Server Error`.

