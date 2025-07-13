from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.schema_info import SchemaInfo
from ...types import UNSET, Response, Unset


def _get_kwargs(
    source_name: str,
    *,
    database_name: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_database_name: Union[None, Unset, str]
    if isinstance(database_name, Unset):
        json_database_name = UNSET
    else:
        json_database_name = database_name
    params["database_name"] = json_database_name

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/agent/sql/sources/{source_name}/schemas",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["SchemaInfo"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = SchemaInfo.from_dict(response_200_item_data)

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
) -> Response[Union[HTTPValidationError, list["SchemaInfo"]]]:
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
    database_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["SchemaInfo"]]]:
    """List Schemas

     List schemas in a database

    Args:
        source_name (str):
        database_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['SchemaInfo']]]
    """

    kwargs = _get_kwargs(
        source_name=source_name,
        database_name=database_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    source_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    database_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["SchemaInfo"]]]:
    """List Schemas

     List schemas in a database

    Args:
        source_name (str):
        database_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['SchemaInfo']]
    """

    return sync_detailed(
        source_name=source_name,
        client=client,
        database_name=database_name,
    ).parsed


async def asyncio_detailed(
    source_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    database_name: Union[None, Unset, str] = UNSET,
) -> Response[Union[HTTPValidationError, list["SchemaInfo"]]]:
    """List Schemas

     List schemas in a database

    Args:
        source_name (str):
        database_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['SchemaInfo']]]
    """

    kwargs = _get_kwargs(
        source_name=source_name,
        database_name=database_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    source_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
    database_name: Union[None, Unset, str] = UNSET,
) -> Optional[Union[HTTPValidationError, list["SchemaInfo"]]]:
    """List Schemas

     List schemas in a database

    Args:
        source_name (str):
        database_name (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['SchemaInfo']]
    """

    return (
        await asyncio_detailed(
            source_name=source_name,
            client=client,
            database_name=database_name,
        )
    ).parsed
