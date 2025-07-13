from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.kafka_field_analysis_analysis import KafkaFieldAnalysisAnalysis


T = TypeVar("T", bound="KafkaFieldAnalysis")


@_attrs_define
class KafkaFieldAnalysis:
    """Analysis results for a specific Kafka message field

    Attributes:
        inferred_type (str): Inferred data type
        examples (list[Any]): Example values
        analysis (KafkaFieldAnalysisAnalysis): Statistical analysis results
    """

    inferred_type: str
    examples: list[Any]
    analysis: "KafkaFieldAnalysisAnalysis"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        inferred_type = self.inferred_type

        examples = self.examples

        analysis = self.analysis.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "inferred_type": inferred_type,
                "examples": examples,
                "analysis": analysis,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.kafka_field_analysis_analysis import KafkaFieldAnalysisAnalysis

        d = dict(src_dict)
        inferred_type = d.pop("inferred_type")

        examples = cast(list[Any], d.pop("examples"))

        analysis = KafkaFieldAnalysisAnalysis.from_dict(d.pop("analysis"))

        kafka_field_analysis = cls(
            inferred_type=inferred_type,
            examples=examples,
            analysis=analysis,
        )

        kafka_field_analysis.additional_properties = d
        return kafka_field_analysis

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
