from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.kafka_inferred_schema_properties_type_0 import (
        KafkaInferredSchemaPropertiesType0,
    )


T = TypeVar("T", bound="KafkaInferredSchema")


@_attrs_define
class KafkaInferredSchema:
    """Inferred JSON schema for a Kafka topic

    Attributes:
        type_ (str): Root schema type
        properties (Union['KafkaInferredSchemaPropertiesType0', None, Unset]): Schema properties
        required (Union[None, Unset, list[str]]): Required properties
    """

    type_: str
    properties: Union["KafkaInferredSchemaPropertiesType0", None, Unset] = UNSET
    required: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.kafka_inferred_schema_properties_type_0 import (
            KafkaInferredSchemaPropertiesType0,
        )

        type_ = self.type_

        properties: Union[None, Unset, dict[str, Any]]
        if isinstance(self.properties, Unset):
            properties = UNSET
        elif isinstance(self.properties, KafkaInferredSchemaPropertiesType0):
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
        if properties is not UNSET:
            field_dict["properties"] = properties
        if required is not UNSET:
            field_dict["required"] = required

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.kafka_inferred_schema_properties_type_0 import (
            KafkaInferredSchemaPropertiesType0,
        )

        d = dict(src_dict)
        type_ = d.pop("type")

        def _parse_properties(
            data: object,
        ) -> Union["KafkaInferredSchemaPropertiesType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                properties_type_0 = KafkaInferredSchemaPropertiesType0.from_dict(data)

                return properties_type_0
            except:  # noqa: E722
                pass
            return cast(Union["KafkaInferredSchemaPropertiesType0", None, Unset], data)

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

        kafka_inferred_schema = cls(
            type_=type_,
            properties=properties,
            required=required,
        )

        kafka_inferred_schema.additional_properties = d
        return kafka_inferred_schema

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
