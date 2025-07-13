from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.kafka_crawl_config import KafkaCrawlConfig


T = TypeVar("T", bound="KafkaCrawlRequest")


@_attrs_define
class KafkaCrawlRequest:
    """Request model for Kafka crawl API

    Attributes:
        config (KafkaCrawlConfig): Main configuration for Kafka message crawling
    """

    config: "KafkaCrawlConfig"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config = self.config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.kafka_crawl_config import KafkaCrawlConfig

        d = dict(src_dict)
        config = KafkaCrawlConfig.from_dict(d.pop("config"))

        kafka_crawl_request = cls(
            config=config,
        )

        kafka_crawl_request.additional_properties = d
        return kafka_crawl_request

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
