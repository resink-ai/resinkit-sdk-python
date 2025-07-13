from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.column_info import ColumnInfo
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    source_name: str,
    table_name: str,
    *,
    schema_name: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_schema_name: Union[None, Unset, str]
    if isinstance(schema_name, Unset):
        json_schema_name = UNSET
    else:
        json_schema_name = schema_name
    params["schema_name"] = json_schema_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/agent/sql/sources/{source_name}/tables/{table_name}/columns",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["ColumnInfo"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ColumnInfo.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, list["ColumnInfo"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    source_name: str,
    table_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    schema_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["ColumnInfo"]]]:
    """Get Table Columns

     Get columns for a table

    Args:
        source_name (str):
        table_name (str):
        schema_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ColumnInfo']]]
    """

    kwargs = _get_kwargs(
        source_name=source_name,
        table_name=table_name,
        schema_name=schema_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_name: str,
    table_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    schema_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["ColumnInfo"]]]:
    """Get Table Columns

     Get columns for a table

    Args:
        source_name (str):
        table_name (str):
        schema_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ColumnInfo']]
    """

    return sync_detailed(
        source_name=source_name,
        table_name=table_name,
        client=client,
        schema_name=schema_name,
    ).parsed


async def asyncio_detailed(
    source_name: str,
    table_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    schema_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["ColumnInfo"]]]:
    """Get Table Columns

     Get columns for a table

    Args:
        source_name (str):
        table_name (str):
        schema_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ColumnInfo']]]
    """

    kwargs = _get_kwargs(
        source_name=source_name,
        table_name=table_name,
        schema_name=schema_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_name: str,
    table_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    schema_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["ColumnInfo"]]]:
    """Get Table Columns

     Get columns for a table

    Args:
        source_name (str):
        table_name (str):
        schema_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ColumnInfo']]
    """

    return (
        await asyncio_detailed(
            source_name=source_name,
            table_name=table_name,
            client=client,
            schema_name=schema_name,
        )
    ).parsed
