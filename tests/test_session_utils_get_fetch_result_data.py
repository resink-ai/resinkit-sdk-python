import json

from flink_gateway_api.models import FetchResultsResponseBody

from resinkit.session_utils import get_fetch_result_data
from .sample_responses import FETCH_RESULT_1_NOT_READY, FETCH_RESULT_1_PAYLOAD, FETCH_RESULT_1_EOS


def test_get_fetch_result_data_with_data():
    response = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_1_PAYLOAD))
    result = get_fetch_result_data(response)
    assert len(result.columns) == 2
    assert result.data == [23, "Alice Liddel"]
    assert result.eos is False
    assert result.next_url is not None


def test_get_fetch_result_data_eos():
    response = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_1_EOS))
    result = get_fetch_result_data(response)
    assert result.columns is None
    assert result.data is None
    assert result.eos is True
    assert result.next_url is None


def test_get_fetch_result_data_not_ready():
    response = FetchResultsResponseBody.from_dict(json.loads(FETCH_RESULT_1_NOT_READY))
    result = get_fetch_result_data(response)
    assert result.columns is None
    assert result.data is None
    assert result.eos is False
    assert result.next_url is not None
