from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="LogEntry")


@_attrs_define
class LogEntry:
    """
    Attributes:
        timestamp (Union[float, int, str]):
        level (str):
        message (str):
    """

    timestamp: Union[float, int, str]
    level: str
    message: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timestamp: Union[float, int, str]
        timestamp = self.timestamp

        level = self.level

        message = self.message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timestamp": timestamp,
                "level": level,
                "message": message,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_timestamp(data: object) -> Union[float, int, str]:
            return cast(Union[float, int, str], data)

        timestamp = _parse_timestamp(d.pop("timestamp"))

        level = d.pop("level")

        message = d.pop("message")

        log_entry = cls(
            timestamp=timestamp,
            level=level,
            message=message,
        )

        log_entry.additional_properties = d
        return log_entry

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
