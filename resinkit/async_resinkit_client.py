import asyncio
import json
import logging
import uuid
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional, Tuple

import pandas as pd
from flink_gateway_api import Client, errors
from flink_gateway_api.api.default import (
    open_session,
    execute_statement,
    fetch_results,
)
from flink_gateway_api.models import (
    OpenSessionRequestBody,
    ExecuteStatementResponseBody,
    RowFormat, FetchResultsResponseBody,
)

from resinkit.session_utils import (
    create_dataframe,
    get_execute_statement_request,
    get_fetch_result_data,
    FetchResultData,
)

logger = logging.getLogger(__name__)


async def fetch_results_async_gen(
        client: 'Client',
        session_handle: str,
        operation_handle: str,
        row_format: RowFormat = RowFormat.JSON,
        poll_interval_secs: float = 0.1,
        max_poll_secs: Optional[float] = None,
        n_row_limit: Optional[int] = None,
) -> AsyncGenerator[FetchResultData, None]:
    """
    Fetch all results from Flink SQL Gateway until EOS is reached using async client
    
    Args:
        client: Async client instance
        session_handle: Session handle string
        operation_handle: Operation handle string
        row_format: Format for the returned rows (JSON or CSV)
        poll_interval_secs: Time to wait between polling
        max_poll_secs: Maximum time to poll
        n_row_limit: Maximum number of rows to fetch
    
    YieldType:
        tuple: (list of all data rows, list of column definitions)
    SendType: None
    ReturnType: None
    """
    next_url = None
    n_rows = 0
    tic = asyncio.get_event_loop().time()
    while True:
        result: FetchResultsResponseBody | None = None
        if next_url is not None:
            raw_response = await client.get_async_httpx_client().request(
                method='GET',
                url=str(next_url),
                params={'rowFormat': row_format},
            )
            if raw_response.status_code == 200:
                result = FetchResultsResponseBody.from_dict(raw_response.json())
            elif client.raise_on_unexpected_status:
                raise errors.UnexpectedStatus(raw_response.status_code, raw_response.content)
        else:
            result = await fetch_results.asyncio(
                session_handle,
                operation_handle,
                0,
                client=client,
                row_format=row_format
            )
        logger.debug(f"Fetch result: {json.dumps(result.to_dict(), indent=2) if result else None}")
        res_data = get_fetch_result_data(result)
        if res_data.data:
            n_rows += len(res_data.data)
            yield res_data
        if res_data.eos or res_data.next_url is None:
            break
        if n_row_limit is not None and n_rows >= n_row_limit:
            break
        if max_poll_secs is not None and (asyncio.get_event_loop().time() - tic) >= max_poll_secs:
            break
        # break if the result is not a query result
        next_url = res_data.next_url
        await asyncio.sleep(poll_interval_secs)


class AsyncResinkitClient(object):
    def __init__(self, flink_gateway_url: str):
        self.fg_client: Client = Client(flink_gateway_url, raise_on_unexpected_status=True)

    async def query(
            self,
            sql: str,
            query_props: Optional[Dict[str, Any]] = None,
            execute_timeout: Optional[int] = None,
            session_name: Optional[str] = None,
            poll_interval_secs: float = 0.1,
            max_poll_secs: Optional[float] = None,
            n_row_limit: Optional[int] = 500,
    ) -> pd.DataFrame:
        """_summary_

        Args:
            execute_timeout:
            session_name:
            sql (str): Statement to execute
            query_props (Dict[str, Any]): Properties for current session that will override the default properties of gateway.
            poll_interval_secs (float): Time to wait between polling (default: 0.1)
            max_poll_secs (float): Maximum time to poll
            n_row_limit (int): Maximum number of rows to fetch (default: 500)
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

        return await self.fetch_all_result(
            responses.session_handle,
            select_result.operation_handle,
            poll_interval_secs=poll_interval_secs,
            max_poll_secs=max_poll_secs,
            n_row_limit=n_row_limit,
        )

    async def fetch_all_result(
            self,
            session_handle: str,
            operation_handle: str,
            poll_interval_secs: float = 0.1,
            max_poll_secs: Optional[float] = None,
            n_row_limit: int = 500,
    ) -> pd.DataFrame:
        """
        Fetch all results from Flink SQL Gateway until EOS is reached
        
        Args:
            session_handle: Session handle string
            operation_handle: Operation handle string
            poll_interval_secs: Time to wait between polling (default: 0.1)
            max_poll_secs: Maximum time to poll
            n_row_limit: Maximum number of rows to fetch
        
        Returns:
            Generator[tuple]: (list of all data rows, list of column definitions)
        """
        if n_row_limit < 0:
            raise ValueError("n_row_limit must be greater than or equal to 0")
        columns, all_rows = None, []
        async for res_data in fetch_results_async_gen(
                self.fg_client,
                session_handle,
                operation_handle,
                poll_interval_secs=poll_interval_secs,
                max_poll_secs=max_poll_secs,
                n_row_limit=n_row_limit
        ):
            res_data: FetchResultData
            if columns is None and res_data.columns is not None:
                columns = res_data.columns
            all_rows.extend(res_data.data)
        return create_dataframe(all_rows[:n_row_limit], columns)

    async def query_multiple(
            self,
            sqls: List[str],
            query_props: Optional[Dict[str, Any]] = None,
            execute_timeout: Optional[int] = None,
            session_name: Optional[str] = None,
            poll_interval_secs: float = 0.1,
            max_poll_secs: Optional[float] = None,
            n_row_limit: int = 500,
    ) -> List[pd.DataFrame]:
        """
        Execute multiple SQL statements in a single session

        Args:
            sqls (List[str]): List of SQL statements to execute
            query_props (Dict[str, Any]): Properties for current session that will override the default properties of gateway.
            execute_timeout (int): Timeout for the query execution
            session_name (str): Name of the session
            poll_interval_secs (float): Time to wait between polling (default: 0.1)
            max_poll_secs (float): Maximum time to poll
            n_row_limit (int): Maximum number of rows to fetch (default: 500)
        Returns:
            List[pd.DataFrame]: List of DataFrames for each query

        """
        properties = query_props or {}
        responses = await open_session.asyncio(client=self.fg_client, body=OpenSessionRequestBody.from_dict({
            "properties": properties,
            "sessionName": session_name or str(uuid.uuid4())
        }))
        logger.debug(f"Opened session for multiple queries: {responses.session_handle}")

        results = []
        for sql in sqls:

            request_dict = get_execute_statement_request(sql, query_props, execute_timeout)
            logger.debug(f"Running query: request: {json.dumps(request_dict, indent=2)}")
            select_result = await execute_statement.asyncio(
                responses.session_handle,
                client=self.fg_client,
                body=ExecuteStatementResponseBody.from_dict(request_dict),
            )
            logger.debug(f"Query result: {select_result.to_dict()}")

            results.append(await self.fetch_all_result(
                responses.session_handle,
                select_result.operation_handle,
                poll_interval_secs=poll_interval_secs,
                max_poll_secs=max_poll_secs,
                n_row_limit=n_row_limit,
            ))

        return results
