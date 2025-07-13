from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.kafka_retrieval_metadata import KafkaRetrievalMetadata
    from ..models.kafka_topic_crawl_result import KafkaTopicCrawlResult


T = TypeVar("T", bound="KafkaCrawlResult")


@_attrs_define
class KafkaCrawlResult:
    """Complete result of Kafka crawling operation

    Attributes:
        retrieval_metadata (KafkaRetrievalMetadata): Metadata about the Kafka crawl operation
        topics (list['KafkaTopicCrawlResult']): Results for each crawled topic
    """

    retrieval_metadata: "KafkaRetrievalMetadata"
    topics: list["KafkaTopicCrawlResult"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        retrieval_metadata = self.retrieval_metadata.to_dict()

        topics = []
        for topics_item_data in self.topics:
            topics_item = topics_item_data.to_dict()
            topics.append(topics_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "retrieval_metadata": retrieval_metadata,
                "topics": topics,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.kafka_retrieval_metadata import KafkaRetrievalMetadata
        from ..models.kafka_topic_crawl_result import KafkaTopicCrawlResult

        d = dict(src_dict)
        retrieval_metadata = KafkaRetrievalMetadata.from_dict(
            d.pop("retrieval_metadata")
        )

        topics = []
        _topics = d.pop("topics")
        for topics_item_data in _topics:
            topics_item = KafkaTopicCrawlResult.from_dict(topics_item_data)

            topics.append(topics_item)

        kafka_crawl_result = cls(
            retrieval_metadata=retrieval_metadata,
            topics=topics,
        )

        kafka_crawl_result.additional_properties = d
        return kafka_crawl_result

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
