from dataclasses import dataclass
import logging
from typing import Any, Dict, List, Optional

import pandas as pd
from flink_gateway_api.models import FetchResultsResponseBody, ResultType, RowKind
from flink_gateway_api.types import UNSET

logger = logging.getLogger(__name__)


def map_flink_to_pandas_dtype(flink_type: str) -> str:
    """
    Map Flink SQL types to pandas dtypes
    """
    # see https://pandas.pydata.org/docs/user_guide/basics.html#basics-dtypes
    type_mapping = {
        'INTEGER': 'Int64',
        'BIGINT': 'Int64',
        'SMALLINT': 'Int16',
        'TINYINT': 'Int8',
        'FLOAT': 'Float32',
        'DOUBLE': 'Float64',
        'DECIMAL': 'Float64',
        'BOOLEAN': 'boolean',
        'CHAR': 'string',
        'VARCHAR': 'string',
        'STRING': 'string',
        'DATE': 'datetime64[ns]',
        'TIME': 'datetime64[ns]',
        'TIMESTAMP': 'datetime64[ns]'
    }
    return type_mapping.get(flink_type, 'object')


def create_dataframe(data: List[List[Any]], columns: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create a pandas DataFrame with proper data types based on Flink column definitions

    Args:
        data: List of data rows
        columns: List of column definitions from Flink

    Returns:
        pandas.DataFrame: DataFrame with proper data types
    """
    if not columns and not data:
        return pd.DataFrame()
    if not columns and data:
        return pd.DataFrame(data)
    if not data:
        # Create empty DataFrame with proper columns if no data
        df = pd.DataFrame(columns=[col['name'] for col in columns])
    else:
        # Create DataFrame from data
        df = pd.DataFrame(data, columns=[col['name'] for col in columns])

    # Set proper data types
    for column in columns:
        col_name = column['name']
        flink_type = column['logicalType']['type']
        pandas_dtype = map_flink_to_pandas_dtype(flink_type)

        try:
            df[col_name] = df[col_name].astype(pandas_dtype)
        except Exception as e:
            print(
                f"Warning: Could not convert column {col_name} to {pandas_dtype}: {str(e)}")

    return df


@dataclass
class FetchResultData:
    columns: List[Dict[str, Any]]
    data: List[List[Any]]
    eos: bool
    next_url: str | None = None

    @staticmethod
    def result_ok():
        return FetchResultData(columns=[{
            'name': 'result',
            'logicalType': {
                'type': 'VARCHAR',
                'nullable': True,
                'length': 2147483647,
            },
            'comment': None,
        }], data=[['OK']], eos=True, next_url=None)


def get_fetch_result_data(response: FetchResultsResponseBody | None) -> FetchResultData:
    """
    Extract columns and data from the result
    Args:
        response: FetchResultsResponseBody object
    Returns: FetchResultData object
    """
    if not response:
        return FetchResultData(columns=[], data=[], eos=True, next_url=None)
    eos = response.result_type == ResultType.EOS
    next_url = None
    if response.next_result_uri is not UNSET:
        next_url = response.next_result_uri

    if response.results is UNSET:
        return FetchResultData(columns=[], data=[], eos=eos, next_url=next_url)
    res_results = response.results.to_dict()
    cols = res_results.get('columns') or res_results.get('columnInfos', [])
    data = []
    for row in res_results.get('data', []):
        if row['kind'] == RowKind.INSERT:
            data.append(row.get('fields', []))
    return FetchResultData(columns=cols, data=data, eos=eos, next_url=next_url)


def get_execute_statement_request(
        sql: str,
        query_props: Optional[Dict[str, Any]] = None,
        execute_timeout: Optional[int] = None,
):
    request_dict = {
        "statement": sql,
    }

    if query_props:
        request_dict["properties"] = query_props

    if execute_timeout:
        request_dict["execution_timeout"] = execute_timeout
    return request_dict
