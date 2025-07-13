from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sampling_strategy import SamplingStrategy
from ..models.value_deserializer import ValueDeserializer
from ..types import UNSET, Unset

T = TypeVar("T", bound="TopicSelection")


@_attrs_define
class TopicSelection:
    """Configuration for selecting a specific topic

    Attributes:
        name (str): Topic name
        value_deserializer (Union[Unset, ValueDeserializer]): Supported message value deserializers
        sample_messages (Union[None, Unset, int]): Override default sample message count
        sampling_strategy (Union[None, SamplingStrategy, Unset]): Override default sampling strategy
        fields (Union[None, Unset, list[str]]): Specific fields to analyze (default: all)
    """

    name: str
    value_deserializer: Union[Unset, ValueDeserializer] = UNSET
    sample_messages: Union[None, Unset, int] = UNSET
    sampling_strategy: Union[None, SamplingStrategy, Unset] = UNSET
    fields: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        value_deserializer: Union[Unset, str] = UNSET
        if not isinstance(self.value_deserializer, Unset):
            value_deserializer = self.value_deserializer.value

        sample_messages: Union[None, Unset, int]
        if isinstance(self.sample_messages, Unset):
            sample_messages = UNSET
        else:
            sample_messages = self.sample_messages

        sampling_strategy: Union[None, Unset, str]
        if isinstance(self.sampling_strategy, Unset):
            sampling_strategy = UNSET
        elif isinstance(self.sampling_strategy, SamplingStrategy):
            sampling_strategy = self.sampling_strategy.value
        else:
            sampling_strategy = self.sampling_strategy

        fields: Union[None, Unset, list[str]]
        if isinstance(self.fields, Unset):
            fields = UNSET
        elif isinstance(self.fields, list):
            fields = self.fields

        else:
            fields = self.fields

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if value_deserializer is not UNSET:
            field_dict["value_deserializer"] = value_deserializer
        if sample_messages is not UNSET:
            field_dict["sample_messages"] = sample_messages
        if sampling_strategy is not UNSET:
            field_dict["sampling_strategy"] = sampling_strategy
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        _value_deserializer = d.pop("value_deserializer", UNSET)
        value_deserializer: Union[Unset, ValueDeserializer]
        if isinstance(_value_deserializer, Unset):
            value_deserializer = UNSET
        else:
            value_deserializer = ValueDeserializer(_value_deserializer)

        def _parse_sample_messages(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        sample_messages = _parse_sample_messages(d.pop("sample_messages", UNSET))

        def _parse_sampling_strategy(
            data: object,
        ) -> Union[None, SamplingStrategy, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                sampling_strategy_type_0 = SamplingStrategy(data)

                return sampling_strategy_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, SamplingStrategy, Unset], data)

        sampling_strategy = _parse_sampling_strategy(d.pop("sampling_strategy", UNSET))

        def _parse_fields(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                fields_type_0 = cast(list[str], data)

                return fields_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        fields = _parse_fields(d.pop("fields", UNSET))

        topic_selection = cls(
            name=name,
            value_deserializer=value_deserializer,
            sample_messages=sample_messages,
            sampling_strategy=sampling_strategy,
            fields=fields,
        )

        topic_selection.additional_properties = d
        return topic_selection

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
