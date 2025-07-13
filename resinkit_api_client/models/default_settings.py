from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.sampling_strategy import SamplingStrategy
from ..types import UNSET, Unset

T = TypeVar("T", bound="DefaultSettings")


@_attrs_define
class DefaultSettings:
    """Global default settings for message sampling

    Attributes:
        sample_messages (Union[Unset, int]): Default number of messages to sample Default: 10.
        sampling_strategy (Union[Unset, SamplingStrategy]): Message sampling strategies
        consumer_timeout_ms (Union[Unset, int]): Consumer timeout in milliseconds Default: 5000.
    """

    sample_messages: Union[Unset, int] = 10
    sampling_strategy: Union[Unset, SamplingStrategy] = UNSET
    consumer_timeout_ms: Union[Unset, int] = 5000
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sample_messages = self.sample_messages

        sampling_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.sampling_strategy, Unset):
            sampling_strategy = self.sampling_strategy.value

        consumer_timeout_ms = self.consumer_timeout_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sample_messages is not UNSET:
            field_dict["sample_messages"] = sample_messages
        if sampling_strategy is not UNSET:
            field_dict["sampling_strategy"] = sampling_strategy
        if consumer_timeout_ms is not UNSET:
            field_dict["consumer_timeout_ms"] = consumer_timeout_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sample_messages = d.pop("sample_messages", UNSET)

        _sampling_strategy = d.pop("sampling_strategy", UNSET)
        sampling_strategy: Union[Unset, SamplingStrategy]
        if isinstance(_sampling_strategy, Unset):
            sampling_strategy = UNSET
        else:
            sampling_strategy = SamplingStrategy(_sampling_strategy)

        consumer_timeout_ms = d.pop("consumer_timeout_ms", UNSET)

        default_settings = cls(
            sample_messages=sample_messages,
            sampling_strategy=sampling_strategy,
            consumer_timeout_ms=consumer_timeout_ms,
        )

        default_settings.additional_properties = d
        return default_settings

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
