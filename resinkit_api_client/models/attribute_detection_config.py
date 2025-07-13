from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AttributeDetectionConfig")


@_attrs_define
class AttributeDetectionConfig:
    """Configuration for attribute detection

    Attributes:
        primary_key (Union[Unset, bool]): Detect primary key attributes Default: True.
        foreign_key (Union[Unset, bool]): Detect foreign key attributes Default: True.
        unique_constraint (Union[Unset, bool]): Detect unique constraint attributes Default: True.
        not_null (Union[Unset, bool]): Detect not null attributes Default: True.
        default_value (Union[Unset, bool]): Detect default value attributes Default: True.
    """

    primary_key: Union[Unset, bool] = True
    foreign_key: Union[Unset, bool] = True
    unique_constraint: Union[Unset, bool] = True
    not_null: Union[Unset, bool] = True
    default_value: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        primary_key = self.primary_key

        foreign_key = self.foreign_key

        unique_constraint = self.unique_constraint

        not_null = self.not_null

        default_value = self.default_value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if primary_key is not UNSET:
            field_dict["primary_key"] = primary_key
        if foreign_key is not UNSET:
            field_dict["foreign_key"] = foreign_key
        if unique_constraint is not UNSET:
            field_dict["unique_constraint"] = unique_constraint
        if not_null is not UNSET:
            field_dict["not_null"] = not_null
        if default_value is not UNSET:
            field_dict["default_value"] = default_value

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        primary_key = d.pop("primary_key", UNSET)

        foreign_key = d.pop("foreign_key", UNSET)

        unique_constraint = d.pop("unique_constraint", UNSET)

        not_null = d.pop("not_null", UNSET)

        default_value = d.pop("default_value", UNSET)

        attribute_detection_config = cls(
            primary_key=primary_key,
            foreign_key=foreign_key,
            unique_constraint=unique_constraint,
            not_null=not_null,
            default_value=default_value,
        )

        attribute_detection_config.additional_properties = d
        return attribute_detection_config

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
