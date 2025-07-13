from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.catalog_response_properties import CatalogResponseProperties


T = TypeVar("T", bound="CatalogResponse")


@_attrs_define
class CatalogResponse:
    """
    Example:
        {'name': 'my_catalog', 'properties': {'default-database': 'mydb', 'username': 'user', 'base-url':
            'jdbc:postgresql://localhost:5432'}, 'type': 'jdbc'}

    Attributes:
        name (str):
        type_ (str):
        properties (CatalogResponseProperties):
    """

    name: str
    type_: str
    properties: "CatalogResponseProperties"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        type_ = self.type_

        properties = self.properties.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "type": type_,
                "properties": properties,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.catalog_response_properties import CatalogResponseProperties

        d = dict(src_dict)
        name = d.pop("name")

        type_ = d.pop("type")

        properties = CatalogResponseProperties.from_dict(d.pop("properties"))

        catalog_response = cls(
            name=name,
            type_=type_,
            properties=properties,
        )

        catalog_response.additional_properties = d
        return catalog_response

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
