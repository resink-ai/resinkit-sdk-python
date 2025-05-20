import unittest
from unittest.mock import Mock, patch, AsyncMock

from flink_gateway_api import Client
from resinkit.flink_session import FlinkSession, SessionCompleteStatement


class TestFlinkSession(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock(spec=Client)
        self.session = FlinkSession(self.mock_client)

    def test_init(self):
        session = FlinkSession(self.mock_client, {"k": "v"}, "test_session")
        self.assertEqual(session.properties, {"k": "v"})
        self.assertEqual(session.session_name, "test_session")
        self.assertIsNone(session.session_handle)

    @patch("resinkit.flink_session.open_session")
    @patch("resinkit.flink_session.close_session")
    def test_sync_context_manager(self, mock_close, mock_open):
        mock_open.sync.return_value.session_handle = "test_handle"

        with self.session as session:
            self.assertEqual(session.session_handle, "test_handle")
            mock_open.sync.assert_called_once()

        mock_close.sync.assert_called_once_with("test_handle", client=self.mock_client)

    @patch("resinkit.flink_session.execute_statement")
    @patch("resinkit.flink_session.FlinkOperation")
    def test_execute_sync(self, mock_operation_cls, mock_execute):
        mock_execute.sync.return_value.operation_handle = "op_handle"
        mock_operation = Mock()
        mock_operation_cls.return_value = mock_operation

        with self.session.execute("SELECT 1").sync() as operation:
            self.assertEqual(operation, mock_operation)
            mock_execute.sync.assert_called_once()

        mock_operation.close.return_value.sync.assert_called_once()

    @patch("resinkit.flink_session.execute_statement")
    @patch("resinkit.flink_session.FlinkOperation")
    @patch("resinkit.flink_session.FlinkCompositeOperation")
    def test_execute_all_sync(
        self, mock_composite_cls, mock_operation_cls, mock_execute
    ):
        mock_execute.sync.return_value.operation_handle = "op_handle"
        mock_operations = [Mock() for _ in range(2)]
        mock_operation_cls.side_effect = mock_operations
        mock_composite = Mock()
        mock_composite_cls.return_value = mock_composite

        with self.session.execute_all(["SELECT 1", "SELECT 2"]).sync() as composite:
            self.assertEqual(composite, mock_composite)
            self.assertEqual(mock_execute.sync.call_count, 2)

        for op in mock_operations:
            op.close.return_value.sync.assert_called_once()


class TestFlinkSessionAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_client = Mock(spec=Client)
        self.session = FlinkSession(self.mock_client)

    @patch("resinkit.flink_session.open_session")
    @patch("resinkit.flink_session.close_session")
    async def test_async_context_manager(self, mock_close, mock_open):
        mock_open.asyncio = AsyncMock(return_value=Mock(session_handle="test_handle"))
        mock_close.asyncio = AsyncMock()

        async with self.session as session:
            self.assertEqual(session.session_handle, "test_handle")
            mock_open.asyncio.assert_called_once()

        mock_close.asyncio.assert_called_once_with(
            "test_handle", client=self.mock_client
        )

    @patch("resinkit.flink_session.execute_statement")
    @patch("resinkit.flink_session.FlinkOperation")
    async def test_execute_async(self, mock_operation_cls, mock_execute):
        mock_execute.asyncio = AsyncMock(
            return_value=Mock(operation_handle="op_handle")
        )
        mock_operation = Mock()
        mock_operation.close.return_value.asyncio = AsyncMock()
        mock_operation_cls.return_value = mock_operation

        async with self.session.execute("SELECT 1").asyncio() as operation:
            self.assertEqual(operation, mock_operation)
            mock_execute.asyncio.assert_called_once()

        mock_operation.close.return_value.asyncio.assert_called_once()

    @patch("resinkit.flink_session.execute_statement")
    @patch("resinkit.flink_session.FlinkOperation")
    @patch("resinkit.flink_session.FlinkCompositeOperation")
    async def test_execute_all_async(
        self, mock_composite_cls, mock_operation_cls, mock_execute
    ):
        mock_execute.asyncio = AsyncMock(
            return_value=Mock(operation_handle="op_handle")
        )
        mock_operations = [Mock() for _ in range(2)]
        for op in mock_operations:
            op.close.return_value.asyncio = AsyncMock()
        mock_operation_cls.side_effect = mock_operations
        mock_composite = Mock()
        mock_composite_cls.return_value = mock_composite

        async with self.session.execute_all(
            ["SELECT 1", "SELECT 2"]
        ).asyncio() as composite:
            self.assertEqual(composite, mock_composite)
            self.assertEqual(mock_execute.asyncio.call_count, 2)

        for op in mock_operations:
            op.close.return_value.asyncio.assert_called_once()


class TestSessionCompleteStatement(unittest.TestCase):
    def setUp(self):
        self.mock_session = Mock()
        self.mock_session.client = Mock(spec=Client)
        self.mock_session.session_handle = "test_handle"
        self.complete_statement = SessionCompleteStatement(self.mock_session)

    @patch("resinkit.flink_session.complete_statement")
    def test_sync_complete(self, mock_complete):
        self.complete_statement.sync(0, "SELECT")
        mock_complete.sync.assert_called_once()

    @patch("resinkit.flink_session.complete_statement")
    async def test_async_complete(self, mock_complete):
        mock_complete.asyncio = AsyncMock()
        await self.complete_statement.asyncio(0, "SELECT")
        mock_complete.asyncio.assert_called_once()


if __name__ == "__main__":
    unittest.main()
