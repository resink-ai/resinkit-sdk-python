from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.catalog_store_definition import CatalogStoreDefinition
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    *,
    body: CatalogStoreDefinition,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/catalogstores",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CatalogStoreDefinition, HTTPValidationError]]:
    if response.status_code == 201:
        response_201 = CatalogStoreDefinition.from_dict(response.json())

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
) -> Response[Union[CatalogStoreDefinition, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CatalogStoreDefinition,
) -> Response[Union[CatalogStoreDefinition, HTTPValidationError]]:
    """Create Catalog Store

     Creates a new catalog store configuration.

    Args:
        catalog_store: The Catalog Store Definition for the store to be created.

    Returns:
        The complete Catalog Store Definition of the newly created store.

    Raises:
        HTTPException: 400 Bad Request if the request body is malformed or missing required fields.
        HTTPException: 409 Conflict if a catalog store with the provided name already exists.
        HTTPException: 500 Internal Server Error if there's an issue persisting the configuration.

    Args:
        body (CatalogStoreDefinition): Data model representing a catalog store configuration

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CatalogStoreDefinition, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CatalogStoreDefinition,
) -> Optional[Union[CatalogStoreDefinition, HTTPValidationError]]:
    """Create Catalog Store

     Creates a new catalog store configuration.

    Args:
        catalog_store: The Catalog Store Definition for the store to be created.

    Returns:
        The complete Catalog Store Definition of the newly created store.

    Raises:
        HTTPException: 400 Bad Request if the request body is malformed or missing required fields.
        HTTPException: 409 Conflict if a catalog store with the provided name already exists.
        HTTPException: 500 Internal Server Error if there's an issue persisting the configuration.

    Args:
        body (CatalogStoreDefinition): Data model representing a catalog store configuration

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CatalogStoreDefinition, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CatalogStoreDefinition,
) -> Response[Union[CatalogStoreDefinition, HTTPValidationError]]:
    """Create Catalog Store

     Creates a new catalog store configuration.

    Args:
        catalog_store: The Catalog Store Definition for the store to be created.

    Returns:
        The complete Catalog Store Definition of the newly created store.

    Raises:
        HTTPException: 400 Bad Request if the request body is malformed or missing required fields.
        HTTPException: 409 Conflict if a catalog store with the provided name already exists.
        HTTPException: 500 Internal Server Error if there's an issue persisting the configuration.

    Args:
        body (CatalogStoreDefinition): Data model representing a catalog store configuration

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CatalogStoreDefinition, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: CatalogStoreDefinition,
) -> Optional[Union[CatalogStoreDefinition, HTTPValidationError]]:
    """Create Catalog Store

     Creates a new catalog store configuration.

    Args:
        catalog_store: The Catalog Store Definition for the store to be created.

    Returns:
        The complete Catalog Store Definition of the newly created store.

    Raises:
        HTTPException: 400 Bad Request if the request body is malformed or missing required fields.
        HTTPException: 409 Conflict if a catalog store with the provided name already exists.
        HTTPException: 500 Internal Server Error if there's an issue persisting the configuration.

    Args:
        body (CatalogStoreDefinition): Data model representing a catalog store configuration

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CatalogStoreDefinition, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
