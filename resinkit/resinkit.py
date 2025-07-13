from typing import Optional

from resinkit.core.task import Task
from resinkit.ui.sql_task_ui import SQLTaskUI
from resinkit.ui.tasks_management_ui import ResinkitAPIClient, TasksManagementUI
from resinkit.ui.variables_ui import VariablesUI


class Resinkit:
    def __init__(
        self,
        resinkit_session: Optional[str] = None,
        personal_access_token: Optional[str] = None,
        sql_gateway_url: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self._base_url = base_url
        self._sql_gateway_url = sql_gateway_url
        self._resinkit_session_id = resinkit_session
        self._personal_access_token = personal_access_token
        self.api_client = ResinkitAPIClient(
            base_url=base_url,
            api_key=self._personal_access_token,
        )
        self._ui_setup_done = False

    def ui_setup(self):
        """
        Setup Panel extensions required for UI components.
        This method is called automatically before displaying any UI components.
        """
        if not self._ui_setup_done:
            import panel as pn

            pn.extension("tabulator")
            pn.extension("codeeditor")
            self._ui_setup_done = True

    def show_vars_ui(self) -> None:
        """
        Display a UI for managing variables.

        Args:
        Returns:
            A Panel UI component that can be displayed in a notebook.
        """
        self.ui_setup()
        ui = VariablesUI(
            base_url=self._base_url,
            session_id=self._resinkit_session_id,
            personal_access_token=self._personal_access_token,
        )
        return ui.show()

    def show_tasks_ui(self) -> None:
        """
        Display a UI for managing tasks.

        Args:
        Returns:
            A Panel UI component that can be displayed in a notebook.
        """
        self.ui_setup()
        ui = TasksManagementUI(api_client=self.api_client)
        return ui.show()

    def get_task(self, task_id: str) -> Task:
        """
        Get a Task instance for the given task_id.

        Args:
            task_id: The unique identifier for the task

        Returns:
            Task: A Task instance configured with the appropriate API client
        """
        return Task(
            task_id=task_id,
            api_client=self.api_client,
        )

    def show_sql_task_ui(self) -> None:
        """
        Display a UI for submitting Flink SQL tasks.
        """
        self.ui_setup()
        ui = SQLTaskUI(api_client=self.api_client)
        return ui.show()
