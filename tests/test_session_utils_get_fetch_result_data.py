import json

from flink_gateway_api.models import FetchResultsResponseBody

from resinkit.session_utils import get_fetch_result_data
from .sample_responses import (
    FETCH_RESULT_1_NOT_READY,
    FETCH_RESULT_1_PAYLOAD,
    FETCH_RESULT_1_EOS,
    FETCH_RESULT_2_EMPTY_PAYLOAD,
    FETCH_RESULT_3_MULTIPLE_ROWS,
)


def test_get_fetch_result_data_with_data():
    response = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_1_PAYLOAD))
    result = get_fetch_result_data(response)
    assert len(result.columns) == 2
    assert result.data == [[23, "Alice Liddel"]]
    assert result.eos is False
    assert result.next_url is not None


def test_get_fetch_result_data_eos():
    response = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_1_EOS))
    result = get_fetch_result_data(response)
    assert len(result.columns) == 2
    assert result.data == []
    assert result.eos is True
    assert result.next_url is None


def test_get_fetch_result_data_not_ready():
    response = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_1_NOT_READY))
    result = get_fetch_result_data(response)
    assert result.columns == []
    assert result.data == []
    assert result.eos is False
    assert result.next_url is not None

def test_get_fetch_result_empty_data():
    response = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_2_EMPTY_PAYLOAD))
    result = get_fetch_result_data(response)
    assert len(result.columns) == 1
    assert result.data == []
    assert result.eos is True
    assert result.next_url is None

def test_get_fetch_result_multiple_rows():
    response = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_3_MULTIPLE_ROWS))
    result = get_fetch_result_data(response)
    assert len(result.columns) == 2
    assert result.data[0] == [23, "Alice Liddel"]
    assert result.data[1] == [19, "Bob Smith"]
    assert result.eos is False
    assert result.next_url is not None
