import asyncio

import panel as pn
import param
import yaml

from resinkit.core.resinkit_api_client import ResinkitAPIClient


class SQLTaskUI(param.Parameterized):
    """Panel UI for submitting Flink SQL tasks."""

    current_view = param.String(default="submit")
    task_result = param.Parameter(default=None)

    def __init__(self, api_client, **params):
        super().__init__(**params)
        self.api_client: ResinkitAPIClient = api_client
        self.submit_view = self._create_submit_view()
        self.result_view = self._create_result_view()

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
        if self.current_view == "submit":
            return self.submit_view
        elif self.current_view == "result":
            return self.result_view
        else:
            return pn.Column("Invalid view")

    def _create_submit_view(self):
        """Create the SQL task submission view."""
        header = pn.pane.Markdown("# Submit Task", sizing_mode="stretch_width")

        # Task name input
        self.task_name_input = pn.widgets.TextInput(
            name="Task Name",
            value="A Flink SQL",
            width=300,
        )

        # Task timeout input
        self.timeout_input = pn.widgets.IntInput(
            name="Task Timeout (seconds)",
            value=30,
            start=1,
            width=200,
        )

        # SQL editor with example SQL
        example_sql = """SELECT * FROM (
VALUES
    (23, 'Alice Liddell', CAST('2024-12-29 10:30:00' AS TIMESTAMP)),
    (19, 'Bob Smith', CAST('2024-12-28 11:45:00' AS TIMESTAMP)),
    (27, 'Charlie Brown', CAST('2024-12-27 14:15:00' AS TIMESTAMP)),
    (31, 'David Jones', CAST('2024-12-26 16:20:00' AS TIMESTAMP))
) AS t(age, name, created_at);"""

        # Configure SQL editor with enhanced keyboard handling
        # Note: Enter key issue resolved by using compatible Jupyter Lab version
        self.sql_editor = pn.widgets.CodeEditor(
            value=example_sql,
            theme="textmate",
            language="sql",
            height=400,
            sizing_mode="stretch_width",
            disabled=False,
            readonly=False,
        )

        # Submit button
        self.submit_btn = pn.widgets.Button(
            name="Submit Task", button_type="primary", width=150
        )
        self.submit_btn.on_click(self._submit_sql_task)

        return pn.Column(
            header,
            pn.Row(self.task_name_input, self.timeout_input),
            pn.pane.Markdown("## SQL Query"),
            self.sql_editor,
            pn.Row(self.submit_btn, align="end"),
            sizing_mode="stretch_width",
        )

    def _create_result_view(self):
        """Create the result view showing task submission results."""
        header = pn.pane.Markdown("# Task Submitted", sizing_mode="stretch_width")

        # Result information pane
        self.result_info_pane = pn.pane.Markdown("", sizing_mode="stretch_width")

        # Submit another task button
        self.submit_another_btn = pn.widgets.Button(
            name="Submit Another Task",
            button_type="primary",
            width=200,
        )
        self.submit_another_btn.on_click(self._submit_another_task)

        return pn.Column(
            header,
            self.result_info_pane,
            pn.Row(self.submit_another_btn, align="center"),
            sizing_mode="stretch_width",
        )

    def _submit_sql_task(self, event):
        """Submit a new Flink SQL task."""
        # Disable the submit button and show submitting status
        self.submit_btn.disabled = True
        self.submit_btn.name = "Submitting..."

        try:
            # Get input values
            task_name = self.task_name_input.value or "A Flink SQL"
            timeout_seconds = self.timeout_input.value or 30
            sql_query = self.sql_editor.value

            # Assemble YAML configuration
            task_config = {
                "task_type": "flink_sql",
                "name": task_name,
                "description": task_name,
                "task_timeout_seconds": timeout_seconds,
                "job": {
                    "sql": sql_query,
                    "pipeline": {"name": task_name, "parallelism": 1},
                },
            }

            print(f"[DEBUG] task_config: {task_config}")
            # Convert to YAML string
            yaml_config = yaml.dump(task_config, default_flow_style=False)

            # Submit the task with proper async handling
            async def submit_task():
                return await self.api_client.submit_yaml_task(yaml_config)

            result = self._run_async(submit_task())

            # Store result and switch to result view
            self.task_result = result
            self._update_result_display()
            self.current_view = "result"
            self.param.trigger("current_view")

        except Exception as e:
            # Re-enable the button on error
            self.submit_btn.disabled = False
            self.submit_btn.name = "Submit Task"
            self._show_error(f"Error submitting task: {str(e)}")

    def _update_result_display(self):
        """Update the result display with task information."""
        if self.task_result:
            task_id = self.task_result.get("task_id", "Unknown")
            status = self.task_result.get("status", "Unknown")

            result_markdown = f"""
## Task Successfully Submitted!

**Task ID:** `{task_id}`  
**Status:** `{status}`  

Your Flink SQL task has been submitted and is being processed.
"""
            self.result_info_pane.object = result_markdown
        else:
            self.result_info_pane.object = "No task result available."

    def _submit_another_task(self, event):
        """Switch back to the submission view for another task."""
        # Reset the submit button state
        self.submit_btn.disabled = False
        self.submit_btn.name = "Submit Task"

        # Switch to submit view
        self.current_view = "submit"
        self.param.trigger("current_view")

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

    def _initialize_editor(self):
        """Initialize the SQL editor to ensure proper input handling."""
        # CodeEditor initialization to ensure proper keyboard handling
        try:
            self.sql_editor.disabled = False
            self.sql_editor.readonly = False
        except Exception:
            pass  # Fail silently if the editor isn't ready yet

    def show(self):
        """Display the UI."""
        # Initialize the editor to ensure proper keyboard handling
        self._initialize_editor()
        return self.main
