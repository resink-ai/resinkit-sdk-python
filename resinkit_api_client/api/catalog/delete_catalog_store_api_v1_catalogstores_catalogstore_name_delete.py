from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import Response


def _get_kwargs(
    catalogstore_name: str,
) -> dict[str, Any]:
    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": f"/api/v1/catalogstores/{catalogstore_name}",
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 204:
        response_204 = cast(Any, None)
        return response_204
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    catalogstore_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, HTTPValidationError]]:
    """Delete Catalog Store

     Deletes a specific catalog store identified by its name.

    Args:
        catalogstore_name: The unique name of the catalog store to delete.

    Returns:
        204 No Content on successful deletion.

    Raises:
        HTTPException: 404 Not Found if no catalog store with the specified name exists.
        HTTPException: 500 Internal Server Error if there's an issue deleting the store.

    Args:
        catalogstore_name (str): The unique name of the catalog store to delete

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        catalogstore_name=catalogstore_name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    catalogstore_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, HTTPValidationError]]:
    """Delete Catalog Store

     Deletes a specific catalog store identified by its name.

    Args:
        catalogstore_name: The unique name of the catalog store to delete.

    Returns:
        204 No Content on successful deletion.

    Raises:
        HTTPException: 404 Not Found if no catalog store with the specified name exists.
        HTTPException: 500 Internal Server Error if there's an issue deleting the store.

    Args:
        catalogstore_name (str): The unique name of the catalog store to delete

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        catalogstore_name=catalogstore_name,
        client=client,
    ).parsed


async def asyncio_detailed(
    catalogstore_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[Union[Any, HTTPValidationError]]:
    """Delete Catalog Store

     Deletes a specific catalog store identified by its name.

    Args:
        catalogstore_name: The unique name of the catalog store to delete.

    Returns:
        204 No Content on successful deletion.

    Raises:
        HTTPException: 404 Not Found if no catalog store with the specified name exists.
        HTTPException: 500 Internal Server Error if there's an issue deleting the store.

    Args:
        catalogstore_name (str): The unique name of the catalog store to delete

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        catalogstore_name=catalogstore_name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    catalogstore_name: str,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Optional[Union[Any, HTTPValidationError]]:
    """Delete Catalog Store

     Deletes a specific catalog store identified by its name.

    Args:
        catalogstore_name: The unique name of the catalog store to delete.

    Returns:
        204 No Content on successful deletion.

    Raises:
        HTTPException: 404 Not Found if no catalog store with the specified name exists.
        HTTPException: 500 Internal Server Error if there's an issue deleting the store.

    Args:
        catalogstore_name (str): The unique name of the catalog store to delete

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            catalogstore_name=catalogstore_name,
            client=client,
        )
    ).parsed
