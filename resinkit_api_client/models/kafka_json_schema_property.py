from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.kafka_json_schema_property_items_type_0 import KafkaJsonSchemaPropertyItemsType0
    from ..models.kafka_json_schema_property_properties_type_0 import KafkaJsonSchemaPropertyPropertiesType0


T = TypeVar("T", bound="KafkaJsonSchemaProperty")


@_attrs_define
class KafkaJsonSchemaProperty:
    """JSON Schema property definition for Kafka messages

    Attributes:
        type_ (str): Property type
        format_ (Union[None, Unset, str]): Property format
        items (Union['KafkaJsonSchemaPropertyItemsType0', None, Unset]): Array items schema
        properties (Union['KafkaJsonSchemaPropertyPropertiesType0', None, Unset]): Object properties schema
        required (Union[None, Unset, list[str]]): Required properties for objects
    """

    type_: str
    format_: Union[None, Unset, str] = UNSET
    items: Union["KafkaJsonSchemaPropertyItemsType0", None, Unset] = UNSET
    properties: Union["KafkaJsonSchemaPropertyPropertiesType0", None, Unset] = UNSET
    required: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.kafka_json_schema_property_items_type_0 import KafkaJsonSchemaPropertyItemsType0
        from ..models.kafka_json_schema_property_properties_type_0 import KafkaJsonSchemaPropertyPropertiesType0

        type_ = self.type_

        format_: Union[None, Unset, str]
        if isinstance(self.format_, Unset):
            format_ = UNSET
        else:
            format_ = self.format_

        items: Union[None, Unset, dict[str, Any]]
        if isinstance(self.items, Unset):
            items = UNSET
        elif isinstance(self.items, KafkaJsonSchemaPropertyItemsType0):
            items = self.items.to_dict()
        else:
            items = self.items

        properties: Union[None, Unset, dict[str, Any]]
        if isinstance(self.properties, Unset):
            properties = UNSET
        elif isinstance(self.properties, KafkaJsonSchemaPropertyPropertiesType0):
            properties = self.properties.to_dict()
        else:
            properties = self.properties

        required: Union[None, Unset, list[str]]
        if isinstance(self.required, Unset):
            required = UNSET
        elif isinstance(self.required, list):
            required = self.required

        else:
            required = self.required

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
            }
        )
        if format_ is not UNSET:
            field_dict["format"] = format_
        if items is not UNSET:
            field_dict["items"] = items
        if properties is not UNSET:
            field_dict["properties"] = properties
        if required is not UNSET:
            field_dict["required"] = required

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.kafka_json_schema_property_items_type_0 import KafkaJsonSchemaPropertyItemsType0
        from ..models.kafka_json_schema_property_properties_type_0 import KafkaJsonSchemaPropertyPropertiesType0

        d = dict(src_dict)
        type_ = d.pop("type")

        def _parse_format_(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        format_ = _parse_format_(d.pop("format", UNSET))

        def _parse_items(data: object) -> Union["KafkaJsonSchemaPropertyItemsType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                items_type_0 = KafkaJsonSchemaPropertyItemsType0.from_dict(data)

                return items_type_0
            except:  # noqa: E722
                pass
            return cast(Union["KafkaJsonSchemaPropertyItemsType0", None, Unset], data)

        items = _parse_items(d.pop("items", UNSET))

        def _parse_properties(data: object) -> Union["KafkaJsonSchemaPropertyPropertiesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                properties_type_0 = KafkaJsonSchemaPropertyPropertiesType0.from_dict(data)

                return properties_type_0
            except:  # noqa: E722
                pass
            return cast(Union["KafkaJsonSchemaPropertyPropertiesType0", None, Unset], data)

        properties = _parse_properties(d.pop("properties", UNSET))

        def _parse_required(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                required_type_0 = cast(list[str], data)

                return required_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        required = _parse_required(d.pop("required", UNSET))

        kafka_json_schema_property = cls(
            type_=type_,
            format_=format_,
            items=items,
            properties=properties,
            required=required,
        )

        kafka_json_schema_property.additional_properties = d
        return kafka_json_schema_property

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
