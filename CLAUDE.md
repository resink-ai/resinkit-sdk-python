# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Package Management

- `uv install` - Install all dependencies including dev dependencies
- `uv add <package>` - Add a new dependency
- `uv add --dev <package>` - Add a development dependency

### Code Quality

- `uv run ruff check --select I --fix .` - Orgnize imports
- `uv run ruff format .` - format code
  **CRITICAL**: DO NOT use other linters, only use `ruff`

## Architecture Overview

### Module Interface Design (`resinkit/__init__.py`)

**CRITICAL**: The resinkit module implements a unique callable module pattern that transforms the entire module into a callable interface. This is achieved by:

1. **Module Replacement**: Uses `sys.modules[__name__] = CallableModule()` to replace the module with a callable instance
2. **Lazy Loading**: UI and agent components are lazily initialized to avoid import conflicts
3. **Global State Management**: Maintains `_default_instance` and `_agent_manager` as module-level globals
4. **Async Event Loop Handling**: Sophisticated async/await logic with fallbacks for Jupyter notebooks

**Key Usage Patterns**:

```python
import resinkit as rsk

# Direct callable for natural language queries
rsk("What were the total sales for each product category?")

# Module-level UI functions
rsk.show_tasks_ui()   # Task management UI
rsk.show_vars_ui()    # Variables management UI
rsk.config(base_url="http://localhost:8080", access_token="token")

# Advanced usage - access underlying classes
instance = rsk.Resinkit(base_url="...")
client = rsk.ResinkitAPIClient(base_url="...")
```

## Tests

The project relies mainly on end to end tests (e2e) test. Follow [end_to_end_test_guide.md](./tests/e2e/end_to_end_test_guide.md) on how to implement and run e2e tests.
