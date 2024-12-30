import json
import unittest
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock, patch

from flink_gateway_api.models import FetchResultsResponseBody, RowFormat

from resinkit.async_resinkit_client import fetch_results_async_gen
from .sample_responses import FETCH_RESULT_1_NOT_READY, FETCH_RESULT_1_PAYLOAD, FETCH_RESULT_1_EOS


class MockResponse:
    def __init__(self, status_code: int, json_data: Dict[str, Any]):
        self.status_code = status_code
        self._json_data = json_data
        self.content = str(json_data).encode()
        self.headers = {}

    def json(self) -> Dict[str, Any]:
        return self._json_data


class TestFetchResultsAsyncGen(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # Create mock client
        self.mock_client = Mock()
        self.mock_client.raise_on_unexpected_status = True

        # Mock the httpx client
        self.mock_httpx_client = AsyncMock()
        self.mock_client.get_async_httpx_client.return_value = self.mock_httpx_client

        # Set up test data
        self.session_handle = "7625ad82-b23b-4118-9683-4a46b7c5022a"
        self.operation_handle = "353994b9-532d-4c0e-9258-688ec777f948"

        # Create response objects
        self.response1 = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_1_NOT_READY))
        self.response2 = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_1_PAYLOAD))
        self.response3 = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_1_EOS))
        self.mock_fetch_results = AsyncMock()

    async def test_fetch_results_async_gen_success(self):
        with patch(
                "resinkit.async_resinkit_client.fetch_results.asyncio", self.mock_fetch_results
        ):
            # Simulate first call to fetch_results.asyncio
            self.mock_fetch_results.return_value = self.response1

            # Set up the mock responses for subsequent calls
            self.mock_httpx_client.request.side_effect = [
                MockResponse(200, json.loads(FETCH_RESULT_1_PAYLOAD)),
                MockResponse(200, json.loads(FETCH_RESULT_1_EOS))
            ]

            # Execute the generator
            results = []
            async for result in fetch_results_async_gen(
                    client=self.mock_client,
                    session_handle=self.session_handle,
                    operation_handle=self.operation_handle,
                    row_format=RowFormat.JSON
            ):
                results.append(result)

            # Verify the calls
            self.assertEqual(self.mock_fetch_results.call_count, 1)
            self.assertEqual(self.mock_httpx_client.request.call_count, 2)

            # Verify the results
            self.assertEqual(len(results), 1)  # Should only get one result with data

            # Verify the data in the result
            self.assertEqual(results[0].data[0], [23, "Alice Liddel"])
            self.assertEqual(len(results[0].columns), 2)
            self.assertEqual(results[0].columns[0]["name"], "age")
            self.assertEqual(results[0].columns[1]["name"], "name")

            # Verify the next_url was correctly used
            expected_url = "/v2/sessions/7625ad82-b23b-4118-9683-4a46b7c5022a/operations/353994b9-532d-4c0e-9258-688ec777f948/result/1?rowFormat=JSON"
            self.mock_httpx_client.request.assert_called_with(
                method='GET',
                url=expected_url,
                params={'rowFormat': RowFormat.JSON}
            )


if __name__ == '__main__':
    unittest.main()
