import asyncio
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import panel as pn

from resinkit_api_client.models.database_kind import DatabaseKind

from ..core.resinkit_api_client import ResinkitAPIClient


class SourcesUI:
    def __init__(
        self,
        base_url: str,
        session_id: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        self.base_url = base_url
        self.session_id = session_id
        self.access_token = access_token
        self.sources = []
        self.selected_sources = set()

        # Initialize API client
        self.api_client = ResinkitAPIClient(
            base_url=base_url, access_token=access_token, session_id=session_id
        )

        # Initialize Panel components
        self._create_table_components()
        self._create_form_components()
        self._create_views()
        self._setup_callbacks()

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

    def _create_table_components(self):
        """Create table-related components"""
        self.sources_table = pn.widgets.Tabulator(
            height=400,
            layout="fit_columns",
            sizing_mode="stretch_width",
            selectable="checkbox",
        )

        # Configure table columns
        self.sources_table.formatters = {"actions": {"type": "html"}}
        self.sources_table.widths = {"actions": 150, "kind": 100, "port": 80}
        self.sources_table.titles = {
            "name": "Name",
            "kind": "Type",
            "host": "Host",
            "port": "Port",
            "database": "Database",
            "user": "User",
            "actions": "Actions",
        }

        # Buttons
        self.add_button = pn.widgets.Button(
            name="+ Add Source", button_type="primary", width=150
        )
        self.refresh_button = pn.widgets.Button(
            name="↻ Refresh", button_type="default", width=100
        )
        self.delete_selected_button = pn.widgets.Button(
            name="🗑 Delete Selected", button_type="default", width=150
        )

    def _create_form_components(self):
        """Create form components"""
        # Form inputs
        self.name_input = pn.widgets.TextInput(
            name="Name", placeholder="Enter source name"
        )
        self.kind_select = pn.widgets.Select(
            name="Database Type",
            options=[kind.value for kind in DatabaseKind],
            value=DatabaseKind.POSTGRESQL.value,
        )
        self.host_input = pn.widgets.TextInput(
            name="Host", placeholder="Enter database host", value="localhost"
        )
        self.port_input = pn.widgets.IntInput(
            name="Port", value=5432, start=1, end=65535
        )
        self.database_input = pn.widgets.TextInput(
            name="Database", placeholder="Enter database name"
        )
        self.user_input = pn.widgets.TextInput(
            name="User", placeholder="Enter username"
        )
        self.password_input = pn.widgets.PasswordInput(
            name="Password", placeholder="Enter password"
        )
        self.query_timeout_input = pn.widgets.TextInput(
            name="Query Timeout", value="30s", placeholder="e.g., 30s, 1m"
        )

        # Form buttons
        self.submit_button = pn.widgets.Button(name="Submit", button_type="primary")
        self.cancel_button = pn.widgets.Button(name="Cancel", button_type="default")
        self.test_connection_button = pn.widgets.Button(
            name="🔗 Test Connection", button_type="default", width=150
        )

    def _create_views(self):
        """Create different views"""
        # Status notification
        self.notification = pn.widgets.StaticText(value="", styles={"color": "red"})

        # Table view
        self.table_view = pn.Column(
            pn.Row(
                pn.pane.Markdown("# SQL Sources", sizing_mode="stretch_width"),
                pn.Row(
                    self.refresh_button,
                    self.delete_selected_button,
                    self.add_button,
                    sizing_mode="fixed",
                ),
                sizing_mode="stretch_width",
            ),
            self.notification,
            self.sources_table,
        )

        # Form view
        self.form_view = pn.Column(
            pn.pane.Markdown("# Add SQL Source"),
            pn.Row(
                pn.Column(
                    self.name_input,
                    self.kind_select,
                    self.host_input,
                    self.port_input,
                ),
                pn.Column(
                    self.database_input,
                    self.user_input,
                    self.password_input,
                    self.query_timeout_input,
                ),
            ),
            self.notification,
            pn.Row(
                self.cancel_button,
                self.test_connection_button,
                self.submit_button,
                align="end",
            ),
        )

        self.main = pn.Column(self.table_view)

    def _setup_callbacks(self):
        """Setup event callbacks"""
        self.add_button.on_click(self._show_add_form)
        self.refresh_button.on_click(self._refresh_sources)
        self.delete_selected_button.on_click(self._delete_selected_sources)
        self.submit_button.on_click(self._submit_source)
        self.cancel_button.on_click(self._show_sources_table)
        self.test_connection_button.on_click(self._test_connection)
        self.kind_select.param.watch(self._update_default_port, "value")

    def _update_default_port(self, event):
        """Update default port based on database type"""
        port_defaults = {
            "postgresql": 5432,
            "mysql": 3306,
            "mssql": 1433,
            "oracle": 1521,
            "sqlite": 0,  # SQLite doesn't use ports
            "starrocks": 9030,
        }
        self.port_input.value = port_defaults.get(event.new, 5432)

    def _load_sources(self) -> List[Dict[str, Any]]:
        """Fetch sources from API"""
        try:
            # Use async API client
            async def fetch_sources():
                return await self.api_client.list_sql_sources()

            # Run async function
            sources = self._run_async(fetch_sources())

            # Add action buttons to each row
            for source in sources:
                source["actions"] = (
                    f'<button class="btn btn-primary btn-sm crawl-btn" data-source-name="{source["name"]}">🔍 Crawl</button> '
                    f'<button class="btn btn-danger btn-sm delete-btn" data-source-name="{source["name"]}">🗑️ Delete</button>'
                )

            return sources
        except Exception as e:
            self.notification.value = f"Error loading sources: {e}"
            return []

    def _refresh_sources(self, event=None):
        """Refresh the sources table"""
        self.notification.value = ""
        self.sources = self._load_sources()

        # Convert list of dictionaries to pandas DataFrame
        if self.sources:
            df = pd.DataFrame(self.sources)
            # Only show relevant columns in the table
            display_columns = [
                "name",
                "kind",
                "host",
                "port",
                "database",
                "user",
                "actions",
            ]
            df = df[display_columns]
            self.sources_table.value = df
        else:
            self.sources_table.value = pd.DataFrame(
                columns=["name", "kind", "host", "port", "database", "user", "actions"]
            )

        # Set up table click handler
        self.sources_table.on_click(self._table_action_callback)

        # Track selections
        self.sources_table.param.watch(self._on_selection_change, "selection")

    def _on_selection_change(self, event):
        """Track selected rows"""
        if event.new:
            # Get selected source names
            if (
                self.sources_table.value is not None
                and len(self.sources_table.value) > 0
            ):
                self.selected_sources = {
                    self.sources_table.value.iloc[i]["name"] for i in event.new
                }
        else:
            self.selected_sources = set()

    def _table_action_callback(self, event):
        """Handle table row action button clicks"""
        if event.column == "actions" and event.value:
            if (
                self.sources_table.value is not None
                and len(self.sources_table.value) > 0
            ):
                try:
                    source_name = self.sources_table.value.iloc[event.row]["name"]

                    if "crawl-btn" in event.value:
                        self._crawl_source(source_name)
                    elif "delete-btn" in event.value:
                        self._delete_source(source_name)
                except (IndexError, Exception) as e:
                    self.notification.value = f"Error processing action: {e}"

    def _crawl_source(self, source_name: str):
        """Crawl a database source and save results"""
        try:

            async def do_crawl():
                # Create crawl request with correct structure
                crawl_request = {
                    "config": {
                        "source": source_name,
                        "tables": [
                            {
                                "name_regex": ".*"  # Select all tables using regex
                            }
                        ],
                    }
                }

                # Execute crawl
                return await self.api_client.crawl_database_tables(crawl_request)

            self.notification.value = f"Crawling source '{source_name}'..."
            crawl_result = self._run_async(do_crawl())

            if crawl_result:
                self._save_crawl_results(source_name, crawl_result)
                self.notification.value = f"Successfully crawled '{source_name}' and saved results to .rsk/sources/"
            else:
                self.notification.value = f"Failed to crawl source '{source_name}'"

        except Exception as e:
            self.notification.value = f"Error crawling source {source_name}: {e}"

    def _save_crawl_results(self, source_name: str, crawl_result: Dict[str, Any]):
        """Save crawl results to .rsk/sources/ directory"""
        try:
            # Create .rsk/sources directory
            rsk_dir = Path(".rsk/sources")
            rsk_dir.mkdir(parents=True, exist_ok=True)

            # Save retrieval metadata
            metadata_file = rsk_dir / ".retrieval_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(crawl_result.get("retrieval_metadata", {}), f, indent=2)

            # Save each table's results
            tables = crawl_result.get("tables", [])
            for table in tables:
                table_name = table.get("table_name", "unknown")
                table_dir = rsk_dir / table_name
                table_dir.mkdir(exist_ok=True)

                # Save DDL
                ddl_file = table_dir / "ddl.sql"
                with open(ddl_file, "w") as f:
                    f.write(table.get("ddl", ""))

                # Save sample data as CSV
                sample_data = table.get("sample_data", [])
                if sample_data:
                    sample_file = table_dir / "sample.csv"
                    with open(sample_file, "w", newline="") as f:
                        if sample_data and isinstance(sample_data[0], dict):
                            # Data is already in dict format
                            writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
                            writer.writeheader()
                            writer.writerows(sample_data)

                # Save DSDS (Descriptive Sample Data Schema)
                dsds = table.get("dsds")
                if dsds:
                    dsds_file = table_dir / "dsds.txt"
                    with open(dsds_file, "w") as f:
                        f.write(str(dsds))

        except Exception as e:
            raise Exception(f"Failed to save crawl results: {e}")

    def _delete_source(self, source_name: str):
        """Delete a single source"""
        try:

            async def delete_source():
                return await self.api_client.delete_sql_source(source_name)

            self._run_async(delete_source())
            self.notification.value = f"Source '{source_name}' deleted successfully"
            self._refresh_sources()
        except Exception as e:
            self.notification.value = f"Error deleting source {source_name}: {e}"

    def _delete_selected_sources(self, event=None):
        """Delete all selected sources"""
        if not self.selected_sources:
            self.notification.value = "No sources selected for deletion"
            return

        try:

            async def delete_sources():
                results = []
                for source_name in self.selected_sources:
                    try:
                        result = await self.api_client.delete_sql_source(source_name)
                        results.append((source_name, True))
                    except Exception as e:
                        results.append((source_name, False, str(e)))
                return results

            results = self._run_async(delete_sources())

            deleted_count = sum(1 for r in results if r[1])
            failed_sources = [r[0] for r in results if not r[1]]

            if failed_sources:
                self.notification.value = f"Deleted {deleted_count} source(s), failed: {', '.join(failed_sources)}"
            else:
                self.notification.value = (
                    f"Deleted {deleted_count} source(s) successfully"
                )

            self.selected_sources.clear()
            self._refresh_sources()

        except Exception as e:
            self.notification.value = f"Error during bulk deletion: {e}"

    def _show_add_form(self, event=None):
        """Show the add source form"""
        self.notification.value = ""
        self._clear_form()
        self.name_input.disabled = False
        self.form_view[0] = pn.pane.Markdown("# Add SQL Source")
        self.main.clear()
        self.main.append(self.form_view)

    def _show_sources_table(self, event=None):
        """Show the sources table"""
        self.notification.value = ""
        self.main.clear()
        self.main.append(self.table_view)
        self._refresh_sources()

    def _clear_form(self):
        """Clear all form inputs"""
        self.name_input.value = ""
        self.kind_select.value = DatabaseKind.POSTGRESQL.value
        self.host_input.value = "localhost"
        self.port_input.value = 5432
        self.database_input.value = ""
        self.user_input.value = ""
        self.password_input.value = ""
        self.query_timeout_input.value = "30s"

    def _submit_source(self, event=None):
        """Submit a new or updated source"""
        name = self.name_input.value
        kind = self.kind_select.value
        host = self.host_input.value
        port = self.port_input.value
        database = self.database_input.value
        user = self.user_input.value
        password = self.password_input.value
        query_timeout = self.query_timeout_input.value

        # Validation
        if not all([name, kind, host, database, user]):
            self.notification.value = (
                "Name, kind, host, database, and user are required"
            )
            return

        if not password:
            self.notification.value = "Password is required"
            return

        try:
            # Create new source
            async def create_source():
                source_data = {
                    "name": name,
                    "kind": kind,
                    "host": host,
                    "port": port,
                    "database": database,
                    "user": user,
                    "password": password,
                    "query_timeout": query_timeout,
                }

                return await self.api_client.create_sql_source(source_data)

            self._run_async(create_source())
            self.notification.value = f"Source '{name}' created successfully"

            # Return to table view
            self._show_sources_table()

        except Exception as e:
            self.notification.value = f"Error saving source: {e}"

    def _test_connection(self, event=None):
        """Test the database connection with current form values"""
        name = self.name_input.value
        kind = self.kind_select.value
        host = self.host_input.value
        port = self.port_input.value
        database = self.database_input.value
        user = self.user_input.value
        password = self.password_input.value
        query_timeout = self.query_timeout_input.value

        # Validation - require all fields except name for connection test
        if not all([kind, host, database, user, password]):
            self.notification.value = "Kind, host, database, user, and password are required for connection test"
            return

        # Disable button during test
        self.test_connection_button.disabled = True
        self.test_connection_button.name = "Testing..."
        self.notification.value = "Testing connection..."

        try:

            async def test_connection():
                connection_data = {
                    "name": name or "test_connection",  # Use dummy name for test
                    "kind": kind,
                    "host": host,
                    "port": port,
                    "database": database,
                    "user": user,
                    "password": password,
                    "query_timeout": query_timeout,
                }
                return await self.api_client.test_sql_connection(connection_data)

            result = self._run_async(test_connection())

            if result.get("success", False):
                self.notification.value = "✅ Connection successful!"
            else:
                error_msg = result.get("error", "Unknown connection error")
                self.notification.value = f"❌ Connection failed: {error_msg}"

        except Exception as e:
            self.notification.value = f"❌ Connection test failed: {str(e)}"
        finally:
            # Re-enable button
            self.test_connection_button.disabled = False
            self.test_connection_button.name = "🔗 Test Connection"

    def show(self):
        """Display the UI"""
        self._refresh_sources()
        return self.main
