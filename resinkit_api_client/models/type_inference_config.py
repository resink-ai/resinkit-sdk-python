from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="TypeInferenceConfig")


@_attrs_define
class TypeInferenceConfig:
    """Configuration for custom column type inference

    Attributes:
        enable (Union[Unset, bool]): Enable custom type inference Default: True.
        string_length_threshold (Union[Unset, int]): Strings longer than this are classified as 'text' Default: 50.
    """

    enable: Union[Unset, bool] = True
    string_length_threshold: Union[Unset, int] = 50
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enable = self.enable

        string_length_threshold = self.string_length_threshold

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enable is not UNSET:
            field_dict["enable"] = enable
        if string_length_threshold is not UNSET:
            field_dict["string_length_threshold"] = string_length_threshold

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        enable = d.pop("enable", UNSET)

        string_length_threshold = d.pop("string_length_threshold", UNSET)

        type_inference_config = cls(
            enable=enable,
            string_length_threshold=string_length_threshold,
        )

        type_inference_config.additional_properties = d
        return type_inference_config

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
