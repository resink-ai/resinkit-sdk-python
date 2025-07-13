from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AnalysisConfig")


@_attrs_define
class AnalysisConfig:
    """Configuration for statistical analysis

    Attributes:
        calculate_null_percentage (Union[Unset, bool]): Calculate null percentage for fields Default: True.
        estimate_cardinality (Union[Unset, bool]): Estimate cardinality of field values Default: True.
    """

    calculate_null_percentage: Union[Unset, bool] = True
    estimate_cardinality: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        calculate_null_percentage = self.calculate_null_percentage

        estimate_cardinality = self.estimate_cardinality

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if calculate_null_percentage is not UNSET:
            field_dict["calculate_null_percentage"] = calculate_null_percentage
        if estimate_cardinality is not UNSET:
            field_dict["estimate_cardinality"] = estimate_cardinality

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        calculate_null_percentage = d.pop("calculate_null_percentage", UNSET)

        estimate_cardinality = d.pop("estimate_cardinality", UNSET)

        analysis_config = cls(
            calculate_null_percentage=calculate_null_percentage,
            estimate_cardinality=estimate_cardinality,
        )

        analysis_config.additional_properties = d
        return analysis_config

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
