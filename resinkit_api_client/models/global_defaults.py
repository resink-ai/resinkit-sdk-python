from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GlobalDefaults")


@_attrs_define
class GlobalDefaults:
    """Global default settings

    Attributes:
        sample_rows (Union[Unset, int]): Default number of sample rows to retrieve Default: 3.
    """

    sample_rows: Union[Unset, int] = 3
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sample_rows = self.sample_rows

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sample_rows is not UNSET:
            field_dict["sample_rows"] = sample_rows

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sample_rows = d.pop("sample_rows", UNSET)

        global_defaults = cls(
            sample_rows=sample_rows,
        )

        global_defaults.additional_properties = d
        return global_defaults

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
