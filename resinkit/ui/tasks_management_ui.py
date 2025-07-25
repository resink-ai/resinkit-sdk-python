import asyncio
import datetime

import pandas as pd
import panel as pn
import param
import yaml

from resinkit.core.resinkit_api_client import ResinkitAPIClient


class TasksManagementUI(param.Parameterized):
    """Panel UI for managing ResInKit tasks."""

    current_view = param.String(default="task_list")
    selected_task_id = param.String(default=None)

    def __init__(self, api_client, **params):
        super().__init__(**params)
        self.api_client: ResinkitAPIClient = api_client
        self.task_list_view = self._create_task_list_view()
        self.task_submit_view = self._create_task_submit_view()
        self.task_detail_view = self._create_task_detail_view()

        # Main layout that switches between views
        self.main = pn.Column(self._get_current_view)

    def _run_async(self, coro):
        """Helper to run async code properly whether in notebook or not."""
        try:
            # Try to get the current event loop
            loop = asyncio.get_running_loop()
            # If we're in a running loop, use nest_asyncio or create task
            try:
                import nest_asyncio

                nest_asyncio.apply()
                return asyncio.run(coro)
            except ImportError:
                # If nest_asyncio not available, use a thread
                import concurrent.futures
                import threading

                result = [None]
                exception = [None]

                def run_in_thread():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result[0] = new_loop.run_until_complete(coro)
                        new_loop.close()
                    except Exception as e:
                        exception[0] = e
                    finally:
                        asyncio.set_event_loop(loop)

                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()

                if exception[0]:
                    raise exception[0]
                return result[0]
        except RuntimeError:
            # No event loop running, use asyncio.run
            return asyncio.run(coro)

    def _get_current_view(self):
        if self.current_view == "task_list":
            return self.task_list_view
        elif self.current_view == "task_submit":
            return self.task_submit_view
        elif self.current_view == "task_detail":
            return self.task_detail_view
        else:
            return pn.Column("Invalid view")

    def _create_task_list_view(self):
        """Create the task list view with a table of tasks and action buttons."""
        # Header with title and buttons
        header = pn.Row(
            pn.pane.Markdown("# Tasks", sizing_mode="stretch_width"),
            pn.Row(
                pn.widgets.Button(
                    name="↻ Refresh",
                    button_type="default",
                    width=100,
                    on_click=self._refresh_tasks,
                ),
                pn.widgets.Button(
                    name="+ Submit New",
                    button_type="primary",
                    width=150,
                    on_click=self._switch_to_submit,
                ),
                pn.widgets.Button(
                    name="✗ Cancel",
                    button_type="danger",
                    width=100,
                    on_click=self._cancel_selected_tasks,
                ),
                pn.widgets.Button(
                    name="🗑 Delete",
                    button_type="danger",
                    width=100,
                    on_click=self._delete_selected_tasks,
                ),
                sizing_mode="fixed",
            ),
            sizing_mode="stretch_width",
        )

        # Create empty table initially
        self.tasks_table = pn.widgets.Tabulator(
            pagination="remote",
            page_size=10,
            sizing_mode="stretch_width",
            height=500,
            layout="fit_columns",
            selectable="checkbox",
            show_index=False,
            configuration={
                "resizableColumns": True,
                "selectableCheck": """function(row) { return true; }""",
            },
            buttons={
                "view": '<button class="task-view-btn">View</button>',
            },
        )

        # Register click handler for action buttons
        self.tasks_table.on_click(self._on_table_action_click)

        # Initial load of tasks
        self._refresh_tasks(None)

        return pn.Column(header, self.tasks_table, sizing_mode="stretch_width")

    def _on_table_action_click(self, event):
        """Handle clicks on the actions column buttons."""
        try:
            # Check if table has data and event has valid row index
            if (
                self.tasks_table.value is None
                or len(self.tasks_table.value) == 0
                or event.row < 0
                or event.row >= len(self.tasks_table.value)
            ):
                self._show_error("Invalid table selection or no data available")
                return

            task_id = self.tasks_table.value.iloc[event.row]["task_id"]
            if event.column == "view":
                self._view_task_details(task_id)
        except Exception as e:
            self._show_error(f"Error processing table action: {e}")
            # Refresh the table to reset its state
            self._refresh_tasks(None)

    def _cancel_selected_tasks(self, event):
        """Cancel all selected tasks."""
        selected_indices = self.tasks_table.selection
        if not selected_indices:
            self._show_info("No tasks selected for cancellation.")
            return

        try:
            selected_tasks = self.tasks_table.value.iloc[selected_indices]
            task_ids = selected_tasks["task_id"].tolist()

            async def cancel_tasks():
                success_count = 0
                for task_id in task_ids:
                    try:
                        result = await self.api_client.cancel_task(task_id, force=False)
                        success_count += 1
                    except Exception as e:
                        self._show_error(f"Error cancelling task {task_id}: {str(e)}")
                return success_count

            success_count = self._run_async(cancel_tasks())

            self._show_info(
                f"Successfully initiated cancellation for {success_count} out of {len(task_ids)} tasks."
            )
            self._refresh_tasks(None)
        except Exception as e:
            self._show_error(f"Error processing task cancellation: {str(e)}")

    def _delete_selected_tasks(self, event):
        """Permanently delete all selected tasks."""
        selected_indices = self.tasks_table.selection
        if not selected_indices:
            self._show_info("No tasks selected for deletion.")
            return

        try:
            selected_tasks = self.tasks_table.value.iloc[selected_indices]
            task_ids = selected_tasks["task_id"].tolist()

            async def delete_tasks():
                success_count = 0
                for task_id in task_ids:
                    try:
                        result = await self.api_client.permanently_delete_task(task_id)
                        success_count += 1
                    except Exception as e:
                        self._show_error(f"Error deleting task {task_id}: {str(e)}")
                return success_count

            success_count = self._run_async(delete_tasks())

            self._show_info(
                f"Successfully deleted {success_count} out of {len(task_ids)} tasks."
            )
            self._refresh_tasks(None)
        except Exception as e:
            self._show_error(f"Error processing task deletion: {str(e)}")

    def _refresh_tasks(self, event):
        """Fetch the latest tasks and update the table."""
        try:

            async def fetch_tasks():
                return await self.api_client.list_tasks()

            tasks = self._run_async(fetch_tasks())
            processed_tasks = []
            for task in tasks.get("tasks", []):
                # Convert timestamps
                created_at = self._format_timestamp(task.get("created_at"))
                updated_at = self._format_timestamp(task.get("updated_at"))

                processed_tasks.append(
                    {
                        "task_id": task.get("task_id"),
                        "task_name": task.get("name", ""),
                        "task_type": task.get("task_type"),
                        "status": task.get("status"),
                        "created_at": created_at,
                        "updated_at": updated_at,
                    }
                )
            # Update the table
            self.tasks_table.value = pd.DataFrame(processed_tasks)
        except Exception as e:
            self._show_error(f"Error loading tasks: {str(e)}")

    def _format_timestamp(self, timestamp_str):
        """Format timestamp string to a readable format."""
        if not timestamp_str:
            return ""
        try:
            dt = datetime.datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp_str

    def _switch_to_submit(self, event):
        """Switch to the task submission view."""
        # Reset the submit button state when entering the view
        self.submit_btn.disabled = False
        self.submit_btn.name = "Submit Task"
        self.current_view = "task_submit"
        self.param.trigger("current_view")

    def _view_task_details(self, task_id):
        """Switch to the task detail view for a specific task."""
        self.selected_task_id = task_id
        self._load_task_details()
        self.current_view = "task_detail"
        self.param.trigger("current_view")

    def _create_task_submit_view(self):
        """Create the task submission view with YAML input."""
        header = pn.Row(
            pn.pane.Markdown("# Submit New Task", sizing_mode="stretch_width"),
            pn.Row(
                pn.widgets.Button(
                    name="← Back to Tasks",
                    button_type="default",
                    width=150,
                    on_click=self._back_to_list,
                ),
                sizing_mode="fixed",
            ),
            sizing_mode="stretch_width",
        )

        example_yaml = """
task_type: flink_sql
name: select_literal
description: select from constants
task_timeout_seconds: 30

job:
  sql: |
    SELECT 
      42 AS user_id,
      'John Doe' AS full_name,
      CAST('1990-05-15' AS DATE) AS birth_date,
      TIMESTAMP '2025-05-15 14:30:00' AS registration_time,
      true AS is_active,
      CAST(3.14159 AS DECIMAL(10,5)) AS pi_value,
      ARRAY['red', 'green', 'blue'] AS favorite_colors,
      MAP['language', 'SQL', 'level', 'advanced'] AS skills,
      ROW('New York', 'USA', 10001) AS address;
  pipeline:
    name: select one row
    parallelism: 1
"""
        self.yaml_input = pn.widgets.CodeEditor(
            value=example_yaml,
            theme="textmate",
            language="yaml",
            height=400,
            sizing_mode="stretch_width",
        )

        self.submit_btn = pn.widgets.Button(
            name="Submit Task", button_type="primary", width=150
        )
        self.submit_btn.on_click(self._submit_yaml_task)

        cancel_btn = pn.widgets.Button(name="Cancel", button_type="default", width=100)
        cancel_btn.on_click(self._back_to_list)

        return pn.Column(
            header,
            pn.pane.Markdown("## Task Configuration (YAML)"),
            self.yaml_input,
            pn.Row(cancel_btn, self.submit_btn, align="end"),
            sizing_mode="stretch_width",
        )

    def _submit_yaml_task(self, event):
        """Submit a new task with YAML configuration."""
        # Disable the submit button to prevent multiple submissions
        self.submit_btn.disabled = True
        self.submit_btn.name = "Submitting..."

        try:
            # Validate YAML
            yaml_config = self.yaml_input.value
            yaml.safe_load(yaml_config)  # Just to validate

            # Submit the task
            async def submit_task():
                return await self.api_client.submit_yaml_task(yaml_config)

            result = self._run_async(submit_task())

            # Show success and go back to task list
            self._show_info(
                f"Task submitted successfully. Task ID: {result.get('task_id')}"
            )
            self._back_to_list(None)
            self._refresh_tasks(None)
        except Exception as e:
            # Re-enable the button on error so user can try again
            self.submit_btn.disabled = False
            self.submit_btn.name = "Submit Task"
            self._show_error(f"Error submitting task: {str(e)}")

    def _back_to_list(self, event):
        """Navigate back to the task list view."""
        self.current_view = "task_list"
        self.param.trigger("current_view")
        # Refresh the tasks table when returning to ensure it's in a good state
        self._refresh_tasks(None)

    def _create_task_detail_view(self):
        """Create the task detail view."""
        header = pn.Row(
            pn.pane.Markdown("# Task Details", sizing_mode="stretch_width"),
            pn.Row(
                pn.widgets.Button(
                    name="← Back to Tasks",
                    button_type="default",
                    width=150,
                    on_click=self._back_to_list,
                ),
                pn.widgets.Button(
                    name="↻ Refresh",
                    button_type="default",
                    width=100,
                    on_click=self._load_task_details,
                ),
                sizing_mode="fixed",
            ),
            sizing_mode="stretch_width",
        )

        # Task info section
        self.task_info_pane = pn.pane.Markdown("Loading task details...")

        # Tabs for logs and results
        self.task_logs = pn.widgets.CodeEditor(
            value="Loading logs...",
            theme="textmate",
            readonly=True,
            height=300,
            sizing_mode="stretch_width",
        )

        self.task_results = pn.pane.JSON(
            object={}, depth=2, height=300, sizing_mode="stretch_width"
        )

        tabs = pn.Tabs(
            ("Summary", pn.Column(self.task_info_pane)),
            ("Logs", pn.Column(self.task_logs)),
            ("Results", pn.Column(self.task_results)),
            dynamic=True,
        )

        return pn.Column(header, tabs, sizing_mode="stretch_width")

    def _load_task_details(self, event=None):
        """Load and display task details, logs, and results."""
        if not self.selected_task_id:
            return

        try:
            # Get task details
            async def get_task():
                return await self.api_client.get_task_details(self.selected_task_id)

            task = self._run_async(get_task())

            # Format the task info as markdown
            task_info = f"""
## {task.get('task_name', 'Task')} ({task.get('task_id')})

**Status:** {task.get('status', 'Unknown')}  
**Type:** {task.get('task_type', 'Unknown')}  
**Created:** {self._format_timestamp(task.get('created_at'))}  
**Updated:** {self._format_timestamp(task.get('updated_at'))}  
**Started:** {self._format_timestamp(task.get('started_at'))}  
**Finished:** {self._format_timestamp(task.get('finished_at'))}  

**Description:** {task.get('description', 'No description')}  
"""
            if task.get("progress"):
                prog = task["progress"]
                task_info += f"""
### Progress
**Progress:** {prog.get('percentage', 0)}%  
**Current Step:** {prog.get('current_step_message', 'Unknown')}  
"""

            if task.get("error_info"):
                err = task["error_info"]
                # Support both 'error' and 'message' keys
                error_message = err.get("error") or err.get("message", "Unknown error")
                error_code = err.get("code", "Unknown") if "code" in err else ""
                error_timestamp = err.get("timestamp", "")
                task_info += f"""
### Error Information
**Error:** {error_message}  
"""
                if error_code:
                    task_info += f"**Code:** {error_code}  \n"
                if error_timestamp:
                    task_info += f"**Timestamp:** {error_timestamp}  \n"

            self.task_info_pane.object = task_info

            # Get logs
            try:

                async def get_logs():
                    return await self.api_client.get_task_logs(self.selected_task_id)

                logs = self._run_async(get_logs())

                # Handle both dict and list responses, and LogEntry objects
                if isinstance(logs, dict):
                    log_entries = logs.get("log_entries", [])
                elif isinstance(logs, list):
                    log_entries = logs
                else:
                    log_entries = []

                # Convert LogEntry objects to dicts if needed
                processed_entries = []
                for entry in log_entries:
                    if hasattr(entry, "to_dict"):
                        # It's a LogEntry object, convert to dict
                        processed_entries.append(entry.to_dict())
                    elif isinstance(entry, dict):
                        # It's already a dict
                        processed_entries.append(entry)
                    else:
                        # Convert to string representation
                        processed_entries.append({"message": str(entry)})

                log_text = "\n".join(
                    [
                        f"{e.get('timestamp', '')} [{e.get('level', 'INFO')}] {e.get('source', '')}: {e.get('message', '')}"
                        for e in processed_entries
                    ]
                )
                self.task_logs.value = log_text or "No logs available"

            except Exception as e:
                error_msg = f"Error loading logs: {str(e)}"
                self.task_logs.value = error_msg
                print(
                    f"DEBUG: Logs loading error for task {self.selected_task_id}: {e}"
                )

            # Get results if task is completed
            try:

                async def get_results():
                    return await self.api_client.get_task_results(self.selected_task_id)

                results = self._run_async(get_results())

                # Convert TaskResult object to dictionary for JSON display
                if results is not None:
                    if hasattr(results, "to_dict"):
                        # It's a TaskResult object, convert to dict
                        try:
                            results_dict = results.to_dict()
                            self.task_results.object = results_dict
                        except Exception as e:
                            # If to_dict fails, try to access object properties directly
                            fallback_dict = {}
                            for attr in ["task_id", "result_type", "data", "summary"]:
                                try:
                                    fallback_dict[attr] = getattr(results, attr, None)
                                except:
                                    fallback_dict[attr] = None
                            # Add any additional properties
                            if hasattr(results, "additional_properties"):
                                fallback_dict.update(results.additional_properties)
                            self.task_results.object = fallback_dict
                    else:
                        # It's already a dict or other JSON-serializable object
                        self.task_results.object = results
                else:
                    self.task_results.object = {
                        "message": "No results available for this task"
                    }

            except Exception as e:
                # Handle specific case where result_type field is missing
                error_msg = str(e)
                if "'result_type'" in error_msg:
                    # Try to make a direct API call and handle the raw response
                    try:
                        import httpx

                        # Access the raw API response to see what we actually get
                        async def get_raw_results():
                            client = self.api_client._client
                            response = await client.get_async_httpx_client().get(
                                f"/api/v1/agent/tasks/{self.selected_task_id}/results"
                            )
                            if response.status_code == 200:
                                return response.json()
                            else:
                                return None

                        raw_results = self._run_async(get_raw_results())
                        if raw_results:
                            # Display the raw results even if they don't match the model
                            self.task_results.object = raw_results
                        else:
                            self.task_results.object = {
                                "error": "Task results endpoint returned empty response",
                                "details": "The task may not have completed yet or may not have generated results.",
                            }
                    except Exception as raw_e:
                        self.task_results.object = {
                            "error": f"Failed to load results due to model mismatch: {error_msg}",
                            "raw_error": str(raw_e),
                            "help": "This usually means the task hasn't completed yet or the result format doesn't match the expected model.",
                        }
                else:
                    # For other errors, show the standard error message
                    self.task_results.object = {
                        "error": f"Error loading results: {error_msg}"
                    }

                print(
                    f"DEBUG: Results loading error for task {self.selected_task_id}: {e}"
                )

        except Exception as e:
            self._show_error(f"Error loading task details: {str(e)}")
            self.task_info_pane.object = f"Error loading task details: {str(e)}"

    def _show_error(self, message):
        """Show an error notification."""
        if hasattr(pn.state, "notifications") and pn.state.notifications is not None:
            pn.state.notifications.error(message, duration=5000)
        else:
            print(f"ERROR: {message}")

    def _show_info(self, message):
        """Show an info notification."""
        if hasattr(pn.state, "notifications") and pn.state.notifications is not None:
            pn.state.notifications.info(message, duration=5000)
        else:
            print(f"INFO: {message}")

    def show(self):
        """Display the UI."""
        return self.main
