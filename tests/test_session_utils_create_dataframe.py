
import unittest
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from pandas.testing import assert_frame_equal

from resinkit.session_utils import create_dataframe


class TestCreateDataFrame(unittest.TestCase):
    def setUp(self):
        # Define some common test data
        self.basic_columns = [
            {
                "name": "age",
                "logicalType": {
                    "type": "INTEGER",
                    "nullable": False
                }
            },
            {
                "name": "name",
                "logicalType": {
                    "type": "CHAR",
                    "nullable": False,
                    "length": 12
                }
            }
        ]

        self.basic_data = [[23, "Alice Liddel"]]

    def test_empty_data(self):
        """Test creating DataFrame with empty data"""
        result = create_dataframe([], self.basic_columns)
        expected = pd.DataFrame({
            "age": pd.Series(dtype="Int64"),
            "name": pd.Series(dtype="string")
        })
        assert_frame_equal(result, expected)

    def test_basic_data(self):
        """Test creating DataFrame with basic data"""
        result = create_dataframe(self.basic_data, self.basic_columns)
        expected = pd.DataFrame({
            "age": pd.Series([23], dtype="Int64"),
            "name": pd.Series(["Alice Liddel"], dtype="string")
        })
        assert_frame_equal(result, expected)

    def test_multiple_rows(self):
        """Test creating DataFrame with multiple rows"""
        data = [
            [23, "Alice Liddel"],
            [25, "Bob Smith"],
            [30, "Charlie Brown"]
        ]
        result = create_dataframe(data, self.basic_columns)
        expected = pd.DataFrame({
            "age": pd.Series([23, 25, 30], dtype="Int64"),
            "name": pd.Series(["Alice Liddel", "Bob Smith", "Charlie Brown"], dtype="string")
        })
        assert_frame_equal(result, expected)

    def test_different_data_types(self):
        """Test creating DataFrame with various data types"""
        columns = [
            {"name": "int_col", "logicalType": {"type": "INTEGER"}},
            {"name": "float_col", "logicalType": {"type": "FLOAT"}},
            {"name": "bool_col", "logicalType": {"type": "BOOLEAN"}},
            {"name": "string_col", "logicalType": {"type": "VARCHAR"}}
        ]
        data = [[1, 1.5, True, "text"]]
        result = create_dataframe(data, columns)
        expected = pd.DataFrame({
            "int_col": pd.Series([1], dtype="Int64"),
            "float_col": pd.Series([1.5], dtype="Float32"),
            "bool_col": pd.Series([True], dtype="boolean"),
            "string_col": pd.Series(["text"], dtype="string")
        })
        assert_frame_equal(result, expected)

    def test_null_values(self):
        """Test handling of null values"""
        data = [[None, "Alice"]]
        result = create_dataframe(data, self.basic_columns)
        expected = pd.DataFrame({
            "age": pd.Series([None], dtype="Int64"),
            "name": pd.Series(["Alice"], dtype="string")
        })
        assert_frame_equal(result, expected)

    def test_invalid_data_type_conversion(self):
        """Test handling of invalid data type conversion"""
        columns = [
            {"name": "age", "logicalType": {"type": "INTEGER"}}
        ]
        data = [["not_a_number"]]

        # Should print warning and keep original data type
        result = create_dataframe(data, columns)
        self.assertEqual(result.shape, (1, 1))
        self.assertEqual(result.iloc[0, 0], "not_a_number")


if __name__ == '__main__':
    unittest.main()