# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management
- `uv install` - Install all dependencies including dev dependencies
- `uv add <package>` - Add a new dependency
- `uv add --dev <package>` - Add a development dependency

### Testing
- `uv run pytest` - Run all tests
- `uv run pytest path/to/test.py` - Run a specific test file
- `uv run pytest -v` - Run tests with verbose output

### Code Quality
- `uv run black .` - Format code using Black (line length: 120)
- `uv run isort .` - Sort imports using isort (black profile)
- `uv run flake8` - Run linting checks

### Running Development
- Use Jupyter notebooks for interactive development (see `sample_notebooks/`)
- Main notebook: `resinkit_localhost.ipynb`

## Architecture Overview

### Core Components

#### 1. ResinkitAPIClient (`resinkit/core/resinkit_api_client.py`)
- REST API client for interacting with ResinKit API
- Handles authentication via API key or session ID
- Provides methods for task management, variables, and results
- Key methods: `submit_task()`, `list_tasks()`, `get_task_details()`, `get_task_results()`

#### 2. Task (`resinkit/core/task.py`)
- Wrapper for individual task operations
- Converts task results to pandas DataFrames via `get_result_df()`
- Handles task status checking and error handling
- Caches task details and results for performance

#### 3. Main Resinkit Class (`resinkit/resinkit.py`)
- Primary SDK entry point
- Integrates with Flink SQL Gateway API
- Provides UI components for Jupyter notebooks
- Authentication methods: session ID or personal access token

### UI Components (`resinkit/ui/`)
- `sql_task_ui.py` - Panel-based UI for submitting SQL tasks
- `tasks_management_ui.py` - UI for managing and monitoring tasks
- `variables_ui.py` - UI for managing ResinKit variables
- All UIs are Panel-based and designed for Jupyter notebooks

### Key Dependencies
- `pandas` - DataFrame operations for task results
- `flink-sql-gateway-api` - Flink SQL Gateway integration
- `panel` - Interactive UIs for Jupyter notebooks
- `requests` - HTTP client (used in API client)

## Common Patterns

### Task Submission
Tasks can be submitted in two ways:
1. JSON format via `submit_task()`
2. YAML format via `submit_yaml_task()`

### Result Handling
- Task results are filtered to only include query results (`is_query=True`)
- Multiple SQL statements return List[DataFrame]
- Single query returns DataFrame directly

### Authentication
- Session-based: Use `resinkit_session` parameter
- Token-based: Use `personal_access_token` parameter
- Both can be combined depending on API requirements

### Error Handling
- Tasks check completion status before returning results
- Raises `RuntimeError` for incomplete tasks
- Raises `ValueError` for failed tasks or no results

## Development Notes

- Python 3.10+ required
- Uses `uv` for dependency management (faster than pip)
- UI components require Jupyter environment
- API client methods import `requests` locally (lazy loading)
- Task class uses `__slots__` for memory efficiency