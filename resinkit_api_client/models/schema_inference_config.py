from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.analysis_config import AnalysisConfig


T = TypeVar("T", bound="SchemaInferenceConfig")


@_attrs_define
class SchemaInferenceConfig:
    """Configuration for schema inference

    Attributes:
        generate (Union[Unset, bool]): Whether to generate inferred schemas Default: True.
        include_examples (Union[Unset, bool]): Include example values in field analysis Default: True.
        max_examples_per_field (Union[Unset, int]): Maximum number of examples per field Default: 3.
        analysis (Union[Unset, AnalysisConfig]): Configuration for statistical analysis
    """

    generate: Union[Unset, bool] = True
    include_examples: Union[Unset, bool] = True
    max_examples_per_field: Union[Unset, int] = 3
    analysis: Union[Unset, "AnalysisConfig"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generate = self.generate

        include_examples = self.include_examples

        max_examples_per_field = self.max_examples_per_field

        analysis: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.analysis, Unset):
            analysis = self.analysis.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if generate is not UNSET:
            field_dict["generate"] = generate
        if include_examples is not UNSET:
            field_dict["include_examples"] = include_examples
        if max_examples_per_field is not UNSET:
            field_dict["max_examples_per_field"] = max_examples_per_field
        if analysis is not UNSET:
            field_dict["analysis"] = analysis

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.analysis_config import AnalysisConfig

        d = dict(src_dict)
        generate = d.pop("generate", UNSET)

        include_examples = d.pop("include_examples", UNSET)

        max_examples_per_field = d.pop("max_examples_per_field", UNSET)

        _analysis = d.pop("analysis", UNSET)
        analysis: Union[Unset, AnalysisConfig]
        if isinstance(_analysis, Unset):
            analysis = UNSET
        else:
            analysis = AnalysisConfig.from_dict(_analysis)

        schema_inference_config = cls(
            generate=generate,
            include_examples=include_examples,
            max_examples_per_field=max_examples_per_field,
            analysis=analysis,
        )

        schema_inference_config.additional_properties = d
        return schema_inference_config

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
