from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.kafka_crawl_request import KafkaCrawlRequest
from ...models.kafka_crawl_result import KafkaCrawlResult
from ...types import Response


def _get_kwargs(
    *,
    body: KafkaCrawlRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/agent/kafka-crawl/crawl",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, KafkaCrawlResult]]:
    if response.status_code == 200:
        response_200 = KafkaCrawlResult.from_dict(response.json())

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
) -> Response[Union[HTTPValidationError, KafkaCrawlResult]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: KafkaCrawlRequest,
) -> Response[Union[HTTPValidationError, KafkaCrawlResult]]:
    """Crawl Kafka topics

     Crawl specified Kafka topics and return structured knowledge including schemas, sample messages, and
    field analysis

    Args:
        body (KafkaCrawlRequest): Request model for Kafka crawl API

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, KafkaCrawlResult]]
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
    body: KafkaCrawlRequest,
) -> Optional[Union[HTTPValidationError, KafkaCrawlResult]]:
    """Crawl Kafka topics

     Crawl specified Kafka topics and return structured knowledge including schemas, sample messages, and
    field analysis

    Args:
        body (KafkaCrawlRequest): Request model for Kafka crawl API

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, KafkaCrawlResult]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: KafkaCrawlRequest,
) -> Response[Union[HTTPValidationError, KafkaCrawlResult]]:
    """Crawl Kafka topics

     Crawl specified Kafka topics and return structured knowledge including schemas, sample messages, and
    field analysis

    Args:
        body (KafkaCrawlRequest): Request model for Kafka crawl API

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, KafkaCrawlResult]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: KafkaCrawlRequest,
) -> Optional[Union[HTTPValidationError, KafkaCrawlResult]]:
    """Crawl Kafka topics

     Crawl specified Kafka topics and return structured knowledge including schemas, sample messages, and
    field analysis

    Args:
        body (KafkaCrawlRequest): Request model for Kafka crawl API

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, KafkaCrawlResult]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
