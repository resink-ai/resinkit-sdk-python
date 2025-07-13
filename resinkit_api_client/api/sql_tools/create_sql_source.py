from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.sql_source_create import SqlSourceCreate
from ...models.sql_source_response import SqlSourceResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: SqlSourceCreate,
    created_by: Union[Unset, str] = "user",
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["created_by"] = created_by

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/agent/sql/sources",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, SqlSourceResponse]]:
    if response.status_code == 201:
        response_201 = SqlSourceResponse.from_dict(response.json())

        return response_201
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, SqlSourceResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SqlSourceCreate,
    created_by: Union[Unset, str] = "user",
) -> Response[Union[HTTPValidationError, SqlSourceResponse]]:
    """Create Sql Source

     Create a new SQL data source

    Args:
        created_by (Union[Unset, str]):  Default: 'user'.
        body (SqlSourceCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SqlSourceResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        created_by=created_by,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SqlSourceCreate,
    created_by: Union[Unset, str] = "user",
) -> Optional[Union[HTTPValidationError, SqlSourceResponse]]:
    """Create Sql Source

     Create a new SQL data source

    Args:
        created_by (Union[Unset, str]):  Default: 'user'.
        body (SqlSourceCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SqlSourceResponse]
    """

    return sync_detailed(
        client=client,
        body=body,
        created_by=created_by,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SqlSourceCreate,
    created_by: Union[Unset, str] = "user",
) -> Response[Union[HTTPValidationError, SqlSourceResponse]]:
    """Create Sql Source

     Create a new SQL data source

    Args:
        created_by (Union[Unset, str]):  Default: 'user'.
        body (SqlSourceCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SqlSourceResponse]]
    """

    kwargs = _get_kwargs(
        body=body,
        created_by=created_by,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: SqlSourceCreate,
    created_by: Union[Unset, str] = "user",
) -> Optional[Union[HTTPValidationError, SqlSourceResponse]]:
    """Create Sql Source

     Create a new SQL data source

    Args:
        created_by (Union[Unset, str]):  Default: 'user'.
        body (SqlSourceCreate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SqlSourceResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            created_by=created_by,
        )
    ).parsed
