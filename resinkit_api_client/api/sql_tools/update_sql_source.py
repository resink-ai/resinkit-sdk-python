from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.sql_source_response import SqlSourceResponse
from ...models.sql_source_update import SqlSourceUpdate
from ...types import Response


def _get_kwargs(
    source_name: str,
    *,
    body: SqlSourceUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": f"/api/v1/agent/sql/sources/{source_name}",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, SqlSourceResponse]]:
    if response.status_code == 200:
        response_200 = SqlSourceResponse.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, SqlSourceResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    source_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SqlSourceUpdate,
) -> Response[Union[HTTPValidationError, SqlSourceResponse]]:
    """Update Sql Source

     Update a SQL data source

    Args:
        source_name (str):
        body (SqlSourceUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SqlSourceResponse]]
    """

    kwargs = _get_kwargs(
        source_name=source_name,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SqlSourceUpdate,
) -> Optional[Union[HTTPValidationError, SqlSourceResponse]]:
    """Update Sql Source

     Update a SQL data source

    Args:
        source_name (str):
        body (SqlSourceUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SqlSourceResponse]
    """

    return sync_detailed(
        source_name=source_name,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    source_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SqlSourceUpdate,
) -> Response[Union[HTTPValidationError, SqlSourceResponse]]:
    """Update Sql Source

     Update a SQL data source

    Args:
        source_name (str):
        body (SqlSourceUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, SqlSourceResponse]]
    """

    kwargs = _get_kwargs(
        source_name=source_name,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SqlSourceUpdate,
) -> Optional[Union[HTTPValidationError, SqlSourceResponse]]:
    """Update Sql Source

     Update a SQL data source

    Args:
        source_name (str):
        body (SqlSourceUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, SqlSourceResponse]
    """

    return (
        await asyncio_detailed(
            source_name=source_name,
            client=client,
            body=body,
        )
    ).parsed
