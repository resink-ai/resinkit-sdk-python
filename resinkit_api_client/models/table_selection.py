from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TableSelection")


@_attrs_define
class TableSelection:
    """Configuration for selecting a specific table

    Attributes:
        name (str): Table name (fully qualified preferred)
        columns (Union[None, Unset, list[str]]): Specific columns to include (default: all)
        sample_rows (Union[None, Unset, int]): Override default sample rows for this table
        sample_query (Union[None, Unset, str]): Custom SQL query to fetch sample data
    """

    name: str
    columns: Union[None, Unset, list[str]] = UNSET
    sample_rows: Union[None, Unset, int] = UNSET
    sample_query: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        columns: Union[None, Unset, list[str]]
        if isinstance(self.columns, Unset):
            columns = UNSET
        elif isinstance(self.columns, list):
            columns = self.columns

        else:
            columns = self.columns

        sample_rows: Union[None, Unset, int]
        if isinstance(self.sample_rows, Unset):
            sample_rows = UNSET
        else:
            sample_rows = self.sample_rows

        sample_query: Union[None, Unset, str]
        if isinstance(self.sample_query, Unset):
            sample_query = UNSET
        else:
            sample_query = self.sample_query

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if columns is not UNSET:
            field_dict["columns"] = columns
        if sample_rows is not UNSET:
            field_dict["sample_rows"] = sample_rows
        if sample_query is not UNSET:
            field_dict["sample_query"] = sample_query

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        def _parse_columns(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                columns_type_0 = cast(list[str], data)

                return columns_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        columns = _parse_columns(d.pop("columns", UNSET))

        def _parse_sample_rows(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        sample_rows = _parse_sample_rows(d.pop("sample_rows", UNSET))

        def _parse_sample_query(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sample_query = _parse_sample_query(d.pop("sample_query", UNSET))

        table_selection = cls(
            name=name,
            columns=columns,
            sample_rows=sample_rows,
            sample_query=sample_query,
        )

        table_selection.additional_properties = d
        return table_selection

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
