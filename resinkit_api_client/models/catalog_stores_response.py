from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.catalog_store_definition import CatalogStoreDefinition


T = TypeVar("T", bound="CatalogStoresResponse")


@_attrs_define
class CatalogStoresResponse:
    """Response model for listing catalog stores

    Attributes:
        catalog_stores (list['CatalogStoreDefinition']):
    """

    catalog_stores: list["CatalogStoreDefinition"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        catalog_stores = []
        for catalog_stores_item_data in self.catalog_stores:
            catalog_stores_item = catalog_stores_item_data.to_dict()
            catalog_stores.append(catalog_stores_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "catalogStores": catalog_stores,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.catalog_store_definition import CatalogStoreDefinition

        d = dict(src_dict)
        catalog_stores = []
        _catalog_stores = d.pop("catalogStores")
        for catalog_stores_item_data in _catalog_stores:
            catalog_stores_item = CatalogStoreDefinition.from_dict(catalog_stores_item_data)

            catalog_stores.append(catalog_stores_item)

        catalog_stores_response = cls(
            catalog_stores=catalog_stores,
        )

        catalog_stores_response.additional_properties = d
        return catalog_stores_response

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
