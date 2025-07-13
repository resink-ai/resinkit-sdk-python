from tests.e2e.e2e_base import E2eBase

"""
Run this test:

$ ./e2e.sh list examples
$ ./e2e.sh test_hello_world

# OR
$ pytest tests/e2e/test_examples.py::TestExamples::test_hello_world -v --capture=no --tb=short
"""


class TestExamples(E2eBase):
    """End-to-end tests for Examples endpoints"""

    def setup_method(self):
        """Setup test environment"""
        super().setup_method()

    def test_hello_world(self):
        """Dummy test to check if the service is running"""
        print("Hello, World!")
        assert True
