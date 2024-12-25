import logging
import uuid
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional, Tuple

import pandas as pd
from flink_gateway_api import Client
from flink_gateway_api.api.default import (
    open_session,
    execute_statement,
    fetch_results,
)
from flink_gateway_api.models import (
    OpenSessionRequestBody,
    ExecuteStatementResponseBody,
    RowFormat,
)

from resinkit.session_utils import create_dataframe, get_execute_statement_request, get_fetch_result_data, \
    FetchResultData

logger = logging.getLogger(__name__)


async def fetch_results_async_gen(
    client: 'Client',
    session_handle: str,
    operation_handle: str,
    row_format: RowFormat = RowFormat.JSON
) -> AsyncGenerator[FetchResultData, None, None]:
    """
    Fetch all results from Flink SQL Gateway until EOS is reached using async client
    
    Args:
        client: Async client instance
        session_handle: Session handle string
        operation_handle: Operation handle string
        row_format: Format for the returned rows (JSON or CSV)
    
    YieldType:
        tuple: (list of all data rows, list of column definitions)
    SendType: None
    ReturnType: None
    """
    token = 0  # Start with token 0
    while True:
        # Use the fetch_results function from the client
        result = await fetch_results.asyncio(
            session_handle,
            operation_handle,
            token,
            client=client,
            row_format=row_format
        )
        res_data = get_fetch_result_data(result)
        if res_data.data:
            yield res_data
        if res_data.eos:
            break
        # Increment token for next batch
        token += 1


class AsyncResinkitClient(object):
    def __init__(self, flink_gateway_url: str):
        self.fg_client: Client = Client(flink_gateway_url)

    async def query(
        self,
        sql: str,
        query_props: Optional[Dict[str, Any]] = None,
        execute_timeout: Optional[int] = None,
        session_name: Optional[str] = None,
    ) -> pd.DataFrame:
        """_summary_

        Args:
            execute_timeout:
            session_name:
            sql (str): Statement to execute
            query_props (Dict[str, Any]): Properties for current session that will override the default properties of gateway.
        Returns:
            pd.DataFrame: _description_
        """
        properties = query_props or {}
        responses = await open_session.asyncio(client=self.fg_client, body=OpenSessionRequestBody.from_dict({
            "properties": properties,
            "sessionName": session_name or str(uuid.uuid4())
        }))
        logger.debug(f"Opened session: {responses.session_handle}")

        request_dict = get_execute_statement_request(sql, query_props, execute_timeout)
        
        select_result = await execute_statement.asyncio(
            responses.session_handle,
            client=self.fg_client,
            body=ExecuteStatementResponseBody.from_dict(request_dict),
        )
        logger.debug(f"Select result: {select_result.to_dict()}")
        
        return await self.fetch_all_result(responses.session_handle, select_result.operation_handle)
    
    async def fetch_all_result(self, session_handle: str, operation_handle: str) -> pd.DataFrame:
        """
        Fetch all results from Flink SQL Gateway until EOS is reached
        
        Args:
            session_handle: Session handle string
            operation_handle: Operation handle string
        
        Returns:
            Generator[tuple]: (list of all data rows, list of column definitions)
        """
        columns, all_rows = None, []
        async for res_data in fetch_results_async_gen(self.fg_client, session_handle, operation_handle):
            res_data: FetchResultData
            if columns is None and not res_data.columns:
                columns = res_data.columns
            all_rows.append(res_data.data)
        return create_dataframe(all_rows, columns)
