from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VariableResponse")


@_attrs_define
class VariableResponse:
    """
    Attributes:
        name (str):
        created_at (str):
        updated_at (str):
        created_by (str):
        description (Union[None, Unset, str]):
    """

    name: str
    created_at: str
    updated_at: str
    created_by: str
    description: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        created_at = self.created_at

        updated_at = self.updated_at

        created_by = self.created_by

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "created_at": created_at,
                "updated_at": updated_at,
                "created_by": created_by,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        created_by = d.pop("created_by")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        variable_response = cls(
            name=name,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            description=description,
        )

        variable_response.additional_properties = d
        return variable_response

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
