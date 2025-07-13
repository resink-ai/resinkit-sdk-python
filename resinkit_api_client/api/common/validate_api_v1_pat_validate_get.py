from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    x_resinkit_pat: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    if not isinstance(x_resinkit_pat, Unset):
        headers["x-resinkit-pat"] = x_resinkit_pat

    if not isinstance(authorization, Unset):
        headers["authorization"] = authorization

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/pat/validate",
    }

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, HTTPValidationError]]:
    if response.status_code == 200:
        response_200 = response.json()
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
) -> Response[Union[Any, HTTPValidationError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    x_resinkit_pat: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Validate

    Args:
        x_resinkit_pat (Union[None, Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        x_resinkit_pat=x_resinkit_pat,
        authorization=authorization,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    x_resinkit_pat: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Validate

    Args:
        x_resinkit_pat (Union[None, Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        x_resinkit_pat=x_resinkit_pat,
        authorization=authorization,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    x_resinkit_pat: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Response[Union[Any, HTTPValidationError]]:
    """Validate

    Args:
        x_resinkit_pat (Union[None, Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        x_resinkit_pat=x_resinkit_pat,
        authorization=authorization,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    x_resinkit_pat: Union[None, Unset, str] = UNSET,
    authorization: Union[None, Unset, str] = UNSET,
) -> Optional[Union[Any, HTTPValidationError]]:
    """Validate

    Args:
        x_resinkit_pat (Union[None, Unset, str]):
        authorization (Union[None, Unset, str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            x_resinkit_pat=x_resinkit_pat,
            authorization=authorization,
        )
    ).parsed
