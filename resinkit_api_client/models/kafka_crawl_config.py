from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.default_settings import DefaultSettings
    from ..models.kafka_source import KafkaSource
    from ..models.schema_inference_config import SchemaInferenceConfig
    from ..models.topic_regex_selection import TopicRegexSelection
    from ..models.topic_selection import TopicSelection


T = TypeVar("T", bound="KafkaCrawlConfig")


@_attrs_define
class KafkaCrawlConfig:
    """Main configuration for Kafka message crawling

    Attributes:
        kafka_source (KafkaSource): Kafka cluster connection configuration
        topics (list[Union['TopicRegexSelection', 'TopicSelection']]): List of topic specifications
        defaults (Union[Unset, DefaultSettings]): Global default settings for message sampling
        schema_inference (Union[Unset, SchemaInferenceConfig]): Configuration for schema inference
    """

    kafka_source: "KafkaSource"
    topics: list[Union["TopicRegexSelection", "TopicSelection"]]
    defaults: Union[Unset, "DefaultSettings"] = UNSET
    schema_inference: Union[Unset, "SchemaInferenceConfig"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.topic_selection import TopicSelection

        kafka_source = self.kafka_source.to_dict()

        topics = []
        for topics_item_data in self.topics:
            topics_item: dict[str, Any]
            if isinstance(topics_item_data, TopicSelection):
                topics_item = topics_item_data.to_dict()
            else:
                topics_item = topics_item_data.to_dict()

            topics.append(topics_item)

        defaults: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.defaults, Unset):
            defaults = self.defaults.to_dict()

        schema_inference: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.schema_inference, Unset):
            schema_inference = self.schema_inference.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "kafka_source": kafka_source,
                "topics": topics,
            }
        )
        if defaults is not UNSET:
            field_dict["defaults"] = defaults
        if schema_inference is not UNSET:
            field_dict["schema_inference"] = schema_inference

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.default_settings import DefaultSettings
        from ..models.kafka_source import KafkaSource
        from ..models.schema_inference_config import SchemaInferenceConfig
        from ..models.topic_regex_selection import TopicRegexSelection
        from ..models.topic_selection import TopicSelection

        d = dict(src_dict)
        kafka_source = KafkaSource.from_dict(d.pop("kafka_source"))

        topics = []
        _topics = d.pop("topics")
        for topics_item_data in _topics:

            def _parse_topics_item(data: object) -> Union["TopicRegexSelection", "TopicSelection"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    topics_item_type_0 = TopicSelection.from_dict(data)

                    return topics_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                topics_item_type_1 = TopicRegexSelection.from_dict(data)

                return topics_item_type_1

            topics_item = _parse_topics_item(topics_item_data)

            topics.append(topics_item)

        _defaults = d.pop("defaults", UNSET)
        defaults: Union[Unset, DefaultSettings]
        if isinstance(_defaults, Unset):
            defaults = UNSET
        else:
            defaults = DefaultSettings.from_dict(_defaults)

        _schema_inference = d.pop("schema_inference", UNSET)
        schema_inference: Union[Unset, SchemaInferenceConfig]
        if isinstance(_schema_inference, Unset):
            schema_inference = UNSET
        else:
            schema_inference = SchemaInferenceConfig.from_dict(_schema_inference)

        kafka_crawl_config = cls(
            kafka_source=kafka_source,
            topics=topics,
            defaults=defaults,
            schema_inference=schema_inference,
        )

        kafka_crawl_config.additional_properties = d
        return kafka_crawl_config

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
