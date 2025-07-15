import asyncio

from resinkit.core.resinkit_api_client import ResinkitAPIClient
from tests.e2e.e2e_base import E2eBase

"""
Run this test:

$ ./e2e.sh test_list_tasks
$ ./e2e.sh test_list_variables

# OR
$ pytest tests/e2e/test_api_client.py::TestAPIClient::test_list_tasks -v --capture=no --tb=short
$ pytest tests/e2e/test_api_client.py::TestAPIClient::test_list_variables -v --capture=no --tb=short
"""


class TestAPIClient(E2eBase):
    """End-to-end tests for ResinkitAPIClient using the refactored async client"""

    def setup_method(self):
        """Setup test environment"""
        super().setup_method()
        self.client = ResinkitAPIClient(base_url=self.BASE_URL)

    def test_list_tasks(self):
        """Test that list_tasks returns expected task data structure"""

        async def run_test():
            result = await self.client.list_tasks()

            # Verify the response structure matches the expected format
            assert isinstance(result, dict), "Response should be a dictionary"
            assert "tasks" in result, "Response should contain 'tasks' key"
            assert "pagination" in result, "Response should contain 'pagination' key"

            # Verify tasks structure
            tasks = result["tasks"]
            assert isinstance(tasks, list), "Tasks should be a list"

            if tasks:  # If there are tasks, verify structure
                task = tasks[0]
                expected_fields = [
                    "task_id",
                    "task_type",
                    "name",
                    "description",
                    "status",
                    "priority",
                    "created_at",
                    "updated_at",
                    "created_by",
                    "_links",
                ]
                for field in expected_fields:
                    assert field in task, f"Task should contain '{field}' field"

                # Verify _links structure
                assert "self" in task["_links"], "Task should have self link"
                assert "href" in task["_links"]["self"], "Self link should have href"

            # Verify pagination structure
            pagination = result["pagination"]
            assert isinstance(pagination, dict), "Pagination should be a dictionary"
            pagination_fields = ["limit", "has_more", "next_page_token"]
            for field in pagination_fields:
                assert field in pagination, f"Pagination should contain '{field}' field"

            print(f"✅ Successfully retrieved {len(tasks)} tasks")
            print(
                f"   Pagination: limit={pagination['limit']}, has_more={pagination['has_more']}"
            )

            return result

        # Run the async test
        result = asyncio.run(run_test())

        # Additional verification using the base class methods for comparison
        response = self.get("/agent/tasks")
        self.assert_status_code(response, 200)
        expected_data = self.assert_json_response(response)

        # Compare async client result with direct API response
        assert (
            result == expected_data
        ), "Async client result should match direct API response"

    def test_list_variables(self):
        """Test that list_variables returns expected variable data structure"""

        async def run_test():
            result = await self.client.list_variables()

            # Verify the response structure
            assert isinstance(result, list), "Response should be a list"

            if result:  # If there are variables, verify structure
                variable = result[0]
                expected_fields = [
                    "name",
                    "description",
                    "created_at",
                    "updated_at",
                    "created_by",
                ]
                for field in expected_fields:
                    assert hasattr(
                        variable, field
                    ), f"Variable should contain '{field}' attribute"

                # Verify field types
                assert isinstance(
                    variable.name, str
                ), "Variable name should be a string"
                assert isinstance(
                    variable.created_at, str
                ), "Created_at should be a string"
                assert isinstance(
                    variable.updated_at, str
                ), "Updated_at should be a string"
                assert isinstance(
                    variable.created_by, str
                ), "Created_by should be a string"
                # description can be None, so we don't assert its type

            print(f"✅ Successfully retrieved {len(result)} variables")
            if result:
                variable_names = [var.name for var in result]
                print(f"   Variables: {', '.join(variable_names)}")

            return result

        # Run the async test
        result = asyncio.run(run_test())

        # Additional verification using the base class methods for comparison
        response = self.get("/agent/variables")
        self.assert_status_code(response, 200)
        expected_data = self.assert_json_response(response)

        # Compare async client result with direct API response
        # Convert structured models to dict for comparison
        result_dicts = [var.to_dict() for var in result]
        assert (
            result_dicts == expected_data
        ), "Async client result should match direct API response"

    def test_list_tasks_with_filters(self):
        """Test that list_tasks works with query parameters"""

        async def run_test():
            # Test with limit parameter
            result = await self.client.list_tasks(limit=5)

            assert isinstance(result, dict), "Response should be a dictionary"
            assert "tasks" in result, "Response should contain 'tasks' key"
            assert "pagination" in result, "Response should contain 'pagination' key"

            # Verify the limit is respected in pagination
            pagination = result["pagination"]
            assert (
                pagination["limit"] == 5
            ), "Pagination limit should match requested limit"

            # Verify we don't get more tasks than requested
            tasks = result["tasks"]
            assert len(tasks) <= 5, "Should not return more tasks than limit"

            print(f"✅ Successfully retrieved {len(tasks)} tasks with limit=5")

            return result

        # Run the async test
        asyncio.run(run_test())

    def teardown_method(self):
        """Cleanup after each test"""
        # No explicit cleanup needed as async context managers
        # are handled within individual test methods
        pass
