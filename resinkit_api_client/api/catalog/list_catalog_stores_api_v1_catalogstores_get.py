from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.catalog_stores_response import CatalogStoresResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/catalogstores",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[CatalogStoresResponse]:
    if response.status_code == 200:
        response_200 = CatalogStoresResponse.from_dict(response.json())

        return response_200
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[CatalogStoresResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[CatalogStoresResponse]:
    """List Catalog Stores

     Retrieves a list of all configured catalog stores.

    Returns:
        A JSON object containing a list of catalog store definitions.

    Raises:
        HTTPException: 500 Internal Server Error if there's an issue retrieving the list.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CatalogStoresResponse]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[CatalogStoresResponse]:
    """List Catalog Stores

     Retrieves a list of all configured catalog stores.

    Returns:
        A JSON object containing a list of catalog store definitions.

    Raises:
        HTTPException: 500 Internal Server Error if there's an issue retrieving the list.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CatalogStoresResponse
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[CatalogStoresResponse]:
    """List Catalog Stores

     Retrieves a list of all configured catalog stores.

    Returns:
        A JSON object containing a list of catalog store definitions.

    Raises:
        HTTPException: 500 Internal Server Error if there's an issue retrieving the list.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[CatalogStoresResponse]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[CatalogStoresResponse]:
    """List Catalog Stores

     Retrieves a list of all configured catalog stores.

    Returns:
        A JSON object containing a list of catalog store definitions.

    Raises:
        HTTPException: 500 Internal Server Error if there's an issue retrieving the list.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        CatalogStoresResponse
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
