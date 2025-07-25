"""
End-to-end tests for UI initialization and components.

This test verifies that all UI components can be successfully initialized without exceptions:
1. Tasks management UI (show_tasks_ui)
2. Variables management UI (show_vars_ui)
3. SQL task submission UI (show_sql_task_ui)
4. SQL sources management UI (show_sources_ui)

Run this test:
$ ./e2e.sh test_all_ui_components_initialize
$ ./e2e.sh test_ui_components_with_custom_settings
$ ./e2e.sh test_async_compatibility
$ pytest tests/e2e/test_ui_initialization.py::TestUIInitialization::test_all_ui_components_initialize -v --capture=no --tb=short
"""

import logging

import resinkit as rsk
from resinkit.core.settings import reset_settings, update_settings
from tests.e2e.e2e_base import E2eBase

logger = logging.getLogger(__name__)


class TestUIInitialization(E2eBase):
    """End-to-end tests for UI component initialization"""

    def setup_method(self):
        """Setup test environment"""
        super().setup_method()

        # Reset settings to ensure clean state
        reset_settings()

        # Configure settings for testing
        update_settings(
            base_url=self.BASE_URL,
            access_token="dummy_token_for_ui_test",  # UI tests don't need real auth
            session_id="test_session_id",
        )

        logger.info(f"Testing UI initialization with base URL: {self.BASE_URL}")

    def test_all_ui_components_initialize(self):
        """Test that all UI components can be initialized without exceptions"""
        logger.info("Testing UI component initialization...")

        # Test tasks management UI
        try:
            tasks_ui = rsk.show_tasks_ui()
            logger.info("✓ Tasks UI initialized successfully")
            assert tasks_ui is not None, "Tasks UI should return a Panel component"
        except Exception as e:
            logger.error(f"✗ Tasks UI failed to initialize: {e}")
            raise AssertionError(f"Tasks UI initialization failed: {e}")

        # Test variables management UI
        try:
            vars_ui = rsk.show_vars_ui()
            logger.info("✓ Variables UI initialized successfully")
            assert vars_ui is not None, "Variables UI should return a Panel component"
        except Exception as e:
            logger.error(f"✗ Variables UI failed to initialize: {e}")
            raise AssertionError(f"Variables UI initialization failed: {e}")

        # Test SQL task submission UI
        try:
            sql_task_ui = rsk.show_sql_task_ui()
            logger.info("✓ SQL Task UI initialized successfully")
            assert (
                sql_task_ui is not None
            ), "SQL Task UI should return a Panel component"
        except Exception as e:
            logger.error(f"✗ SQL Task UI failed to initialize: {e}")
            raise AssertionError(f"SQL Task UI initialization failed: {e}")

        # Test SQL sources management UI
        try:
            sources_ui = rsk.show_sources_ui()
            logger.info("✓ Sources UI initialized successfully")
            assert sources_ui is not None, "Sources UI should return a Panel component"
        except Exception as e:
            logger.error(f"✗ Sources UI failed to initialize: {e}")
            raise AssertionError(f"Sources UI initialization failed: {e}")

        logger.info("🎉 All UI components initialized successfully!")

    def test_ui_components_with_custom_settings(self):
        """Test UI initialization with custom Resinkit instance"""
        logger.info("Testing UI components with custom Resinkit instance...")

        # Create custom Resinkit instance
        custom_rsk = rsk.Resinkit(
            base_url=self.BASE_URL,
            personal_access_token="custom_dummy_token",
            resinkit_session="custom_session_id",
        )

        # Test each UI component with custom instance
        try:
            tasks_ui = custom_rsk.show_tasks_ui()
            logger.info("✓ Custom Tasks UI initialized successfully")
            assert tasks_ui is not None
        except Exception as e:
            logger.error(f"✗ Custom Tasks UI failed: {e}")
            raise AssertionError(f"Custom Tasks UI initialization failed: {e}")

        try:
            vars_ui = custom_rsk.show_vars_ui()
            logger.info("✓ Custom Variables UI initialized successfully")
            assert vars_ui is not None
        except Exception as e:
            logger.error(f"✗ Custom Variables UI failed: {e}")
            raise AssertionError(f"Custom Variables UI initialization failed: {e}")

        try:
            sql_task_ui = custom_rsk.show_sql_task_ui()
            logger.info("✓ Custom SQL Task UI initialized successfully")
            assert sql_task_ui is not None
        except Exception as e:
            logger.error(f"✗ Custom SQL Task UI failed: {e}")
            raise AssertionError(f"Custom SQL Task UI initialization failed: {e}")

        try:
            sources_ui = custom_rsk.show_sources_ui()
            logger.info("✓ Custom Sources UI initialized successfully")
            assert sources_ui is not None
        except Exception as e:
            logger.error(f"✗ Custom Sources UI failed: {e}")
            raise AssertionError(f"Custom Sources UI initialization failed: {e}")

        # AI Tools UI has been completely removed along with llama-index dependencies
        logger.info("✓ AI Tools UI has been removed (llama-index dependencies removed)")

        logger.info("🎉 All custom UI components initialized successfully!")

    def test_async_compatibility(self):
        """Test that UI components handle async/sync compatibility correctly"""
        logger.info("Testing async/sync compatibility...")

        # This test ensures that the UI components can handle cases where
        # there might be an existing event loop (like in Jupyter notebooks)

        # Test without running event loop (standard case)
        try:
            ui = rsk.show_tasks_ui()
            logger.info("✓ UI works without running event loop")
            assert ui is not None
        except Exception as e:
            logger.error(f"✗ UI failed without running event loop: {e}")
            raise AssertionError(f"UI failed in standard environment: {e}")

        # Test that the _run_async helper method exists and works
        from resinkit.core.resinkit_api_client import ResinkitAPIClient
        from resinkit.ui.tasks_management_ui import TasksManagementUI

        api_client = ResinkitAPIClient(
            base_url=self.BASE_URL, access_token="dummy_token"
        )

        ui_instance = TasksManagementUI(api_client=api_client)
        assert hasattr(
            ui_instance, "_run_async"
        ), "UI should have _run_async helper method"

        logger.info("✓ Async compatibility helper methods are present")

    def teardown_method(self):
        """Cleanup after test"""
        # Reset settings after test
        reset_settings()
        logger.info("Test cleanup completed")
