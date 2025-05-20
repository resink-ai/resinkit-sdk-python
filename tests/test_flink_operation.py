import unittest
from unittest.mock import Mock, patch, AsyncMock
import pandas as pd

from resinkit.flink_operation import (
    FlinkOperation, FlinkCompositeOperation, ResultsFetchOpts,
    OperationFetch, OperationClose
)

class TestResultsFetchOpts(unittest.TestCase):
    def test_valid_init(self):
        opts = ResultsFetchOpts(0.1, 10, 500)
        self.assertEqual(opts.poll_interval_secs, 0.1)
        self.assertEqual(opts.max_poll_secs, 10)
        self.assertEqual(opts.n_row_limit, 500)

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            ResultsFetchOpts(poll_interval_secs=-1)
        with self.assertRaises(ValueError):
            ResultsFetchOpts(max_poll_secs=-1)
        with self.assertRaises(ValueError):
            ResultsFetchOpts(n_row_limit=-1)

class TestFlinkOperation(unittest.TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_session.client = Mock()
        self.mock_session.session_handle = "test_session"
        self.operation = FlinkOperation(self.mock_session, "test_operation")

    def test_init(self):
        self.assertEqual(self.operation.session, self.mock_session)
        self.assertEqual(self.operation.operation_handle, "test_operation")
        self.assertEqual(self.operation.client, self.mock_session.client)

    def test_context_managers(self):
        with patch.object(OperationClose, 'sync') as mock_close:
            with self.operation:
                pass
            mock_close.assert_called_once()

class TestFlinkOperationAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_session.client = Mock()
        self.mock_session.session_handle = "test_session"
        self.operation = FlinkOperation(self.mock_session, "test_operation")

    async def test_async_context_manager(self):
        with patch.object(OperationClose, 'asyncio', new_callable=AsyncMock) as mock_close:
            async with self.operation:
                pass
            mock_close.assert_called_once()

class TestOperationFetch(unittest.TestCase):
    def setUp(self):
        self.mock_operation = Mock()
        self.mock_operation.client = Mock()
        self.mock_operation.session = Mock()
        self.mock_operation.session.session_handle = "test_session"
        self.mock_operation.operation_handle = "test_operation"
        self.fetch = OperationFetch(self.mock_operation, ResultsFetchOpts())

    @patch('resinkit.flink_operation.fetch_results_gen')
    @patch('resinkit.flink_operation.create_dataframe')
    def test_sync_fetch(self, mock_create_df, mock_fetch_gen):
        mock_fetch_gen.return_value = [
            Mock(columns=[{"name": "col1"}], data=[[1], [2]])
        ]
        mock_create_df.return_value = pd.DataFrame([[1], [2]], columns=["col1"])

        result = self.fetch.sync()
        self.assertIsInstance(result, pd.DataFrame)
        mock_create_df.assert_called_once()

class TestOperationFetchAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_operation = Mock()
        self.mock_operation.client = Mock()
        self.mock_operation.session = Mock()
        self.mock_operation.session.session_handle = "test_session"
        self.mock_operation.operation_handle = "test_operation"
        self.fetch = OperationFetch(self.mock_operation, ResultsFetchOpts())

    @patch('resinkit.flink_operation.fetch_results_async_gen')
    @patch('resinkit.flink_operation.create_dataframe')
    async def test_async_fetch(self, mock_create_df, mock_fetch_gen):
        async def mock_gen():
            yield Mock(columns=[{"name": "col1"}], data=[[1], [2]])
        mock_fetch_gen.return_value = mock_gen()
        mock_create_df.return_value = pd.DataFrame([[1], [2]], columns=["col1"])

        result = await self.fetch.asyncio()
        self.assertIsInstance(result, pd.DataFrame)
        mock_create_df.assert_called_once()

class TestFlinkCompositeOperation(unittest.TestCase):
    def setUp(self):
        self.mock_ops = [Mock(spec=FlinkOperation) for _ in range(2)]
        self.composite_op = FlinkCompositeOperation(self.mock_ops)

    def test_fetch_all(self):
        mock_df = pd.DataFrame({'col1': [1, 2]})
        for op in self.mock_ops:
            op.fetch.return_value.sync.return_value = mock_df

        results = self.composite_op.fetch_all(ResultsFetchOpts())
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], pd.DataFrame)

    def test_context_manager(self):
        with self.composite_op:
            pass
        for op in self.mock_ops:
            op.close.return_value.sync.assert_called_once()

class TestFlinkCompositeOperationAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_ops = [Mock(spec=FlinkOperation) for _ in range(2)]
        self.composite_op = FlinkCompositeOperation(self.mock_ops)

    async def test_async_fetch_all(self):
        mock_df = pd.DataFrame({'col1': [1, 2]})
        for op in self.mock_ops:
            op.fetch.return_value.asyncio = AsyncMock(return_value=mock_df)

        results = await self.composite_op.fetch_all_async(ResultsFetchOpts())
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], pd.DataFrame)

    async def test_async_context_manager(self):
        for op in self.mock_ops:
            op.close.return_value.asyncio = AsyncMock()

        async with self.composite_op:
            pass

        for op in self.mock_ops:
            op.close.return_value.asyncio.assert_called_once()

if __name__ == '__main__':
    unittest.main()