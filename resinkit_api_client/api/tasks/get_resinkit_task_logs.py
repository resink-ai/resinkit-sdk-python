from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.log_entry import LogEntry
from ...types import UNSET, Response, Unset


def _get_kwargs(
    task_id: str,
    *,
    level: Union[Unset, str] = "INFO",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["level"] = level

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/api/v1/agent/tasks/{task_id}/logs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["LogEntry"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = LogEntry.from_dict(response_200_item_data)

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
) -> Response[Union[HTTPValidationError, list["LogEntry"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    task_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    level: Union[Unset, str] = "INFO",
) -> Response[Union[HTTPValidationError, list["LogEntry"]]]:
    """Get Task Logs

    Args:
        task_id (str):
        level (Union[Unset, str]): Log level filter (INFO, WARN, ERROR, DEBUG) Default: 'INFO'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['LogEntry']]]
    """

    kwargs = _get_kwargs(
        task_id=task_id,
        level=level,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    task_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    level: Union[Unset, str] = "INFO",
) -> Optional[Union[HTTPValidationError, list["LogEntry"]]]:
    """Get Task Logs

    Args:
        task_id (str):
        level (Union[Unset, str]): Log level filter (INFO, WARN, ERROR, DEBUG) Default: 'INFO'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['LogEntry']]
    """

    return sync_detailed(
        task_id=task_id,
        client=client,
        level=level,
    ).parsed


async def asyncio_detailed(
    task_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    level: Union[Unset, str] = "INFO",
) -> Response[Union[HTTPValidationError, list["LogEntry"]]]:
    """Get Task Logs

    Args:
        task_id (str):
        level (Union[Unset, str]): Log level filter (INFO, WARN, ERROR, DEBUG) Default: 'INFO'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['LogEntry']]]
    """

    kwargs = _get_kwargs(
        task_id=task_id,
        level=level,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    task_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    level: Union[Unset, str] = "INFO",
) -> Optional[Union[HTTPValidationError, list["LogEntry"]]]:
    """Get Task Logs

    Args:
        task_id (str):
        level (Union[Unset, str]): Log level filter (INFO, WARN, ERROR, DEBUG) Default: 'INFO'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['LogEntry']]
    """

    return (
        await asyncio_detailed(
            task_id=task_id,
            client=client,
            level=level,
        )
    ).parsed
