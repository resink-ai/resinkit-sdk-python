from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.catalog_store_definition_options import CatalogStoreDefinitionOptions


T = TypeVar("T", bound="CatalogStoreDefinition")


@_attrs_define
class CatalogStoreDefinition:
    """Data model representing a catalog store configuration

    Attributes:
        name (str): Unique identifier for the catalog store
        kind (str): Type of the catalog store
        options (Union[Unset, CatalogStoreDefinitionOptions]): Key-value pairs for specific catalog store configurations
    """

    name: str
    kind: str
    options: Union[Unset, "CatalogStoreDefinitionOptions"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        kind = self.kind

        options: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.options, Unset):
            options = self.options.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "kind": kind,
            }
        )
        if options is not UNSET:
            field_dict["options"] = options

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.catalog_store_definition_options import (
            CatalogStoreDefinitionOptions,
        )

        d = dict(src_dict)
        name = d.pop("name")

        kind = d.pop("kind")

        _options = d.pop("options", UNSET)
        options: Union[Unset, CatalogStoreDefinitionOptions]
        if isinstance(_options, Unset):
            options = UNSET
        else:
            options = CatalogStoreDefinitionOptions.from_dict(_options)

        catalog_store_definition = cls(
            name=name,
            kind=kind,
            options=options,
        )

        catalog_store_definition.additional_properties = d
        return catalog_store_definition

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
