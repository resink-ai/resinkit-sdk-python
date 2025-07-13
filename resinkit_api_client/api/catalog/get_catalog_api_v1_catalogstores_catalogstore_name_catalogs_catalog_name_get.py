from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.catalog_response import CatalogResponse
from ...models.error_response import ErrorResponse
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    catalogstore_name: str,
    catalog_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/catalogstores/{catalogstore_name}/catalogs/{catalog_name}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[CatalogResponse, ErrorResponse, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = CatalogResponse.from_dict(response.json())

        return response_200
    if response.status_code == 404:
        response_404 = ErrorResponse.from_dict(response.json())

        return response_404
    if response.status_code == 500:
        response_500 = ErrorResponse.from_dict(response.json())

        return response_500
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[CatalogResponse, ErrorResponse, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    catalogstore_name: str,
    catalog_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[CatalogResponse, ErrorResponse, HTTPValidationError]]:
    """Get Catalog

     Retrieves the configuration details of a specific catalog.

    Args:
        catalogstore_name (str): The name of the catalog store
        catalog_name (str): The name of the catalog to retrieve

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CatalogResponse, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        catalogstore_name=catalogstore_name,
        catalog_name=catalog_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    catalogstore_name: str,
    catalog_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[CatalogResponse, ErrorResponse, HTTPValidationError]]:
    """Get Catalog

     Retrieves the configuration details of a specific catalog.

    Args:
        catalogstore_name (str): The name of the catalog store
        catalog_name (str): The name of the catalog to retrieve

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CatalogResponse, ErrorResponse, HTTPValidationError]
    """

    return sync_detailed(
        catalogstore_name=catalogstore_name,
        catalog_name=catalog_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    catalogstore_name: str,
    catalog_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[CatalogResponse, ErrorResponse, HTTPValidationError]]:
    """Get Catalog

     Retrieves the configuration details of a specific catalog.

    Args:
        catalogstore_name (str): The name of the catalog store
        catalog_name (str): The name of the catalog to retrieve

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[CatalogResponse, ErrorResponse, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        catalogstore_name=catalogstore_name,
        catalog_name=catalog_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    catalogstore_name: str,
    catalog_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[CatalogResponse, ErrorResponse, HTTPValidationError]]:
    """Get Catalog

     Retrieves the configuration details of a specific catalog.

    Args:
        catalogstore_name (str): The name of the catalog store
        catalog_name (str): The name of the catalog to retrieve

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[CatalogResponse, ErrorResponse, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            catalogstore_name=catalogstore_name,
            catalog_name=catalog_name,
            client=client,
        )
    ).parsed
