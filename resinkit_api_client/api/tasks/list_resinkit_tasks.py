from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    task_type: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    task_name_contains: Union[None, Unset, str] = UNSET,
    tags_include_any: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, str] = UNSET,
    created_before: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 20,
    page_token: Union[None, Unset, str] = UNSET,
    sort_by: Union[None, Unset, str] = "created_at",
    sort_order: Union[None, Unset, str] = "desc",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_task_type: Union[None, Unset, str]
    if isinstance(task_type, Unset):
        json_task_type = UNSET
    else:
        json_task_type = task_type
    params["task_type"] = json_task_type

    json_status: Union[None, Unset, str]
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_task_name_contains: Union[None, Unset, str]
    if isinstance(task_name_contains, Unset):
        json_task_name_contains = UNSET
    else:
        json_task_name_contains = task_name_contains
    params["task_name_contains"] = json_task_name_contains

    json_tags_include_any: Union[None, Unset, str]
    if isinstance(tags_include_any, Unset):
        json_tags_include_any = UNSET
    else:
        json_tags_include_any = tags_include_any
    params["tags_include_any"] = json_tags_include_any

    json_created_after: Union[None, Unset, str]
    if isinstance(created_after, Unset):
        json_created_after = UNSET
    else:
        json_created_after = created_after
    params["created_after"] = json_created_after

    json_created_before: Union[None, Unset, str]
    if isinstance(created_before, Unset):
        json_created_before = UNSET
    else:
        json_created_before = created_before
    params["created_before"] = json_created_before

    json_limit: Union[None, Unset, int]
    if isinstance(limit, Unset):
        json_limit = UNSET
    else:
        json_limit = limit
    params["limit"] = json_limit

    json_page_token: Union[None, Unset, str]
    if isinstance(page_token, Unset):
        json_page_token = UNSET
    else:
        json_page_token = page_token
    params["page_token"] = json_page_token

    json_sort_by: Union[None, Unset, str]
    if isinstance(sort_by, Unset):
        json_sort_by = UNSET
    else:
        json_sort_by = sort_by
    params["sort_by"] = json_sort_by

    json_sort_order: Union[None, Unset, str]
    if isinstance(sort_order, Unset):
        json_sort_order = UNSET
    else:
        json_sort_order = sort_order
    params["sort_order"] = json_sort_order

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/agent/tasks",
        "params": params,
    }

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
    task_type: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    task_name_contains: Union[None, Unset, str] = UNSET,
    tags_include_any: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, str] = UNSET,
    created_before: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 20,
    page_token: Union[None, Unset, str] = UNSET,
    sort_by: Union[None, Unset, str] = "created_at",
    sort_order: Union[None, Unset, str] = "desc",
) -> Response[Union[Any, HTTPValidationError]]:
    """List Tasks

    Args:
        task_type (Union[None, Unset, str]):
        status (Union[None, Unset, str]):
        task_name_contains (Union[None, Unset, str]):
        tags_include_any (Union[None, Unset, str]):
        created_after (Union[None, Unset, str]):
        created_before (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):  Default: 20.
        page_token (Union[None, Unset, str]):
        sort_by (Union[None, Unset, str]):  Default: 'created_at'.
        sort_order (Union[None, Unset, str]):  Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        task_type=task_type,
        status=status,
        task_name_contains=task_name_contains,
        tags_include_any=tags_include_any,
        created_after=created_after,
        created_before=created_before,
        limit=limit,
        page_token=page_token,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    task_type: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    task_name_contains: Union[None, Unset, str] = UNSET,
    tags_include_any: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, str] = UNSET,
    created_before: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 20,
    page_token: Union[None, Unset, str] = UNSET,
    sort_by: Union[None, Unset, str] = "created_at",
    sort_order: Union[None, Unset, str] = "desc",
) -> Optional[Union[Any, HTTPValidationError]]:
    """List Tasks

    Args:
        task_type (Union[None, Unset, str]):
        status (Union[None, Unset, str]):
        task_name_contains (Union[None, Unset, str]):
        tags_include_any (Union[None, Unset, str]):
        created_after (Union[None, Unset, str]):
        created_before (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):  Default: 20.
        page_token (Union[None, Unset, str]):
        sort_by (Union[None, Unset, str]):  Default: 'created_at'.
        sort_order (Union[None, Unset, str]):  Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        task_type=task_type,
        status=status,
        task_name_contains=task_name_contains,
        tags_include_any=tags_include_any,
        created_after=created_after,
        created_before=created_before,
        limit=limit,
        page_token=page_token,
        sort_by=sort_by,
        sort_order=sort_order,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    task_type: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    task_name_contains: Union[None, Unset, str] = UNSET,
    tags_include_any: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, str] = UNSET,
    created_before: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 20,
    page_token: Union[None, Unset, str] = UNSET,
    sort_by: Union[None, Unset, str] = "created_at",
    sort_order: Union[None, Unset, str] = "desc",
) -> Response[Union[Any, HTTPValidationError]]:
    """List Tasks

    Args:
        task_type (Union[None, Unset, str]):
        status (Union[None, Unset, str]):
        task_name_contains (Union[None, Unset, str]):
        tags_include_any (Union[None, Unset, str]):
        created_after (Union[None, Unset, str]):
        created_before (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):  Default: 20.
        page_token (Union[None, Unset, str]):
        sort_by (Union[None, Unset, str]):  Default: 'created_at'.
        sort_order (Union[None, Unset, str]):  Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        task_type=task_type,
        status=status,
        task_name_contains=task_name_contains,
        tags_include_any=tags_include_any,
        created_after=created_after,
        created_before=created_before,
        limit=limit,
        page_token=page_token,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    task_type: Union[None, Unset, str] = UNSET,
    status: Union[None, Unset, str] = UNSET,
    task_name_contains: Union[None, Unset, str] = UNSET,
    tags_include_any: Union[None, Unset, str] = UNSET,
    created_after: Union[None, Unset, str] = UNSET,
    created_before: Union[None, Unset, str] = UNSET,
    limit: Union[None, Unset, int] = 20,
    page_token: Union[None, Unset, str] = UNSET,
    sort_by: Union[None, Unset, str] = "created_at",
    sort_order: Union[None, Unset, str] = "desc",
) -> Optional[Union[Any, HTTPValidationError]]:
    """List Tasks

    Args:
        task_type (Union[None, Unset, str]):
        status (Union[None, Unset, str]):
        task_name_contains (Union[None, Unset, str]):
        tags_include_any (Union[None, Unset, str]):
        created_after (Union[None, Unset, str]):
        created_before (Union[None, Unset, str]):
        limit (Union[None, Unset, int]):  Default: 20.
        page_token (Union[None, Unset, str]):
        sort_by (Union[None, Unset, str]):  Default: 'created_at'.
        sort_order (Union[None, Unset, str]):  Default: 'desc'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            task_type=task_type,
            status=status,
            task_name_contains=task_name_contains,
            tags_include_any=tags_include_any,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            page_token=page_token,
            sort_by=sort_by,
            sort_order=sort_order,
        )
    ).parsed
