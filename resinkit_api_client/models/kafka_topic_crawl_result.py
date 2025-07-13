from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.kafka_inferred_schema import KafkaInferredSchema
    from ..models.kafka_topic_crawl_result_field_analysis_type_0 import KafkaTopicCrawlResultFieldAnalysisType0


T = TypeVar("T", bound="KafkaTopicCrawlResult")


@_attrs_define
class KafkaTopicCrawlResult:
    """Result of crawling a single Kafka topic

    Attributes:
        topic_name (str): Name of the topic
        partitions (int): Number of partitions
        sample_messages (list[Any]): Sample messages from the topic
        inferred_schema (Union['KafkaInferredSchema', None, Unset]): Inferred JSON schema
        field_analysis (Union['KafkaTopicCrawlResultFieldAnalysisType0', None, Unset]): Field-level analysis
    """

    topic_name: str
    partitions: int
    sample_messages: list[Any]
    inferred_schema: Union["KafkaInferredSchema", None, Unset] = UNSET
    field_analysis: Union["KafkaTopicCrawlResultFieldAnalysisType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.kafka_inferred_schema import KafkaInferredSchema
        from ..models.kafka_topic_crawl_result_field_analysis_type_0 import KafkaTopicCrawlResultFieldAnalysisType0

        topic_name = self.topic_name

        partitions = self.partitions

        sample_messages = self.sample_messages

        inferred_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.inferred_schema, Unset):
            inferred_schema = UNSET
        elif isinstance(self.inferred_schema, KafkaInferredSchema):
            inferred_schema = self.inferred_schema.to_dict()
        else:
            inferred_schema = self.inferred_schema

        field_analysis: Union[None, Unset, dict[str, Any]]
        if isinstance(self.field_analysis, Unset):
            field_analysis = UNSET
        elif isinstance(self.field_analysis, KafkaTopicCrawlResultFieldAnalysisType0):
            field_analysis = self.field_analysis.to_dict()
        else:
            field_analysis = self.field_analysis

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "topic_name": topic_name,
                "partitions": partitions,
                "sample_messages": sample_messages,
            }
        )
        if inferred_schema is not UNSET:
            field_dict["inferred_schema"] = inferred_schema
        if field_analysis is not UNSET:
            field_dict["field_analysis"] = field_analysis

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.kafka_inferred_schema import KafkaInferredSchema
        from ..models.kafka_topic_crawl_result_field_analysis_type_0 import KafkaTopicCrawlResultFieldAnalysisType0

        d = dict(src_dict)
        topic_name = d.pop("topic_name")

        partitions = d.pop("partitions")

        sample_messages = cast(list[Any], d.pop("sample_messages"))

        def _parse_inferred_schema(data: object) -> Union["KafkaInferredSchema", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                inferred_schema_type_0 = KafkaInferredSchema.from_dict(data)

                return inferred_schema_type_0
            except:  # noqa: E722
                pass
            return cast(Union["KafkaInferredSchema", None, Unset], data)

        inferred_schema = _parse_inferred_schema(d.pop("inferred_schema", UNSET))

        def _parse_field_analysis(data: object) -> Union["KafkaTopicCrawlResultFieldAnalysisType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                field_analysis_type_0 = KafkaTopicCrawlResultFieldAnalysisType0.from_dict(data)

                return field_analysis_type_0
            except:  # noqa: E722
                pass
            return cast(Union["KafkaTopicCrawlResultFieldAnalysisType0", None, Unset], data)

        field_analysis = _parse_field_analysis(d.pop("field_analysis", UNSET))

        kafka_topic_crawl_result = cls(
            topic_name=topic_name,
            partitions=partitions,
            sample_messages=sample_messages,
            inferred_schema=inferred_schema,
            field_analysis=field_analysis,
        )

        kafka_topic_crawl_result.additional_properties = d
        return kafka_topic_crawl_result

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
