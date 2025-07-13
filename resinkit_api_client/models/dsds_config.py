from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.attribute_detection_config import AttributeDetectionConfig
    from ..models.type_inference_config import TypeInferenceConfig


T = TypeVar("T", bound="DSDSConfig")


@_attrs_define
class DSDSConfig:
    """Configuration for Descriptive Sample Data Schema generation

    Attributes:
        generate (Union[Unset, bool]): Whether to generate DSDS Default: True.
        include_examples (Union[Unset, bool]): Include example values in DSDS Default: True.
        max_examples_per_column (Union[Unset, int]): Maximum number of examples per column Default: 3.
        include_comments (Union[Unset, bool]): Include column comments if available Default: True.
        type_inference (Union[Unset, TypeInferenceConfig]): Configuration for custom column type inference
        attribute_detection (Union[Unset, AttributeDetectionConfig]): Configuration for attribute detection
    """

    generate: Union[Unset, bool] = True
    include_examples: Union[Unset, bool] = True
    max_examples_per_column: Union[Unset, int] = 3
    include_comments: Union[Unset, bool] = True
    type_inference: Union[Unset, "TypeInferenceConfig"] = UNSET
    attribute_detection: Union[Unset, "AttributeDetectionConfig"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        generate = self.generate

        include_examples = self.include_examples

        max_examples_per_column = self.max_examples_per_column

        include_comments = self.include_comments

        type_inference: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.type_inference, Unset):
            type_inference = self.type_inference.to_dict()

        attribute_detection: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.attribute_detection, Unset):
            attribute_detection = self.attribute_detection.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if generate is not UNSET:
            field_dict["generate"] = generate
        if include_examples is not UNSET:
            field_dict["include_examples"] = include_examples
        if max_examples_per_column is not UNSET:
            field_dict["max_examples_per_column"] = max_examples_per_column
        if include_comments is not UNSET:
            field_dict["include_comments"] = include_comments
        if type_inference is not UNSET:
            field_dict["type_inference"] = type_inference
        if attribute_detection is not UNSET:
            field_dict["attribute_detection"] = attribute_detection

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.attribute_detection_config import AttributeDetectionConfig
        from ..models.type_inference_config import TypeInferenceConfig

        d = dict(src_dict)
        generate = d.pop("generate", UNSET)

        include_examples = d.pop("include_examples", UNSET)

        max_examples_per_column = d.pop("max_examples_per_column", UNSET)

        include_comments = d.pop("include_comments", UNSET)

        _type_inference = d.pop("type_inference", UNSET)
        type_inference: Union[Unset, TypeInferenceConfig]
        if isinstance(_type_inference, Unset):
            type_inference = UNSET
        else:
            type_inference = TypeInferenceConfig.from_dict(_type_inference)

        _attribute_detection = d.pop("attribute_detection", UNSET)
        attribute_detection: Union[Unset, AttributeDetectionConfig]
        if isinstance(_attribute_detection, Unset):
            attribute_detection = UNSET
        else:
            attribute_detection = AttributeDetectionConfig.from_dict(
                _attribute_detection
            )

        dsds_config = cls(
            generate=generate,
            include_examples=include_examples,
            max_examples_per_column=max_examples_per_column,
            include_comments=include_comments,
            type_inference=type_inference,
            attribute_detection=attribute_detection,
        )

        dsds_config.additional_properties = d
        return dsds_config

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
