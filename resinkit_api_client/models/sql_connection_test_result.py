from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SqlConnectionTestResult")


@_attrs_define
class SqlConnectionTestResult:
    """
    Attributes:
        success (bool): Whether the connection test succeeded
        message (str): Success or error message
        connection_time_ms (Union[None, Unset, float]): Connection time in milliseconds
    """

    success: bool
    message: str
    connection_time_ms: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        message = self.message

        connection_time_ms: Union[None, Unset, float]
        if isinstance(self.connection_time_ms, Unset):
            connection_time_ms = UNSET
        else:
            connection_time_ms = self.connection_time_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "message": message,
            }
        )
        if connection_time_ms is not UNSET:
            field_dict["connection_time_ms"] = connection_time_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        def _parse_connection_time_ms(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        connection_time_ms = _parse_connection_time_ms(
            d.pop("connection_time_ms", UNSET)
        )

        sql_connection_test_result = cls(
            success=success,
            message=message,
            connection_time_ms=connection_time_ms,
        )

        sql_connection_test_result.additional_properties = d
        return sql_connection_test_result

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
