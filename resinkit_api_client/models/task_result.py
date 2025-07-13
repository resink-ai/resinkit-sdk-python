from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.task_result_data import TaskResultData


T = TypeVar("T", bound="TaskResult")


@_attrs_define
class TaskResult:
    """
    Attributes:
        task_id (str):
        result_type (str):
        data (TaskResultData):
        summary (str):
    """

    task_id: str
    result_type: str
    data: "TaskResultData"
    summary: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        task_id = self.task_id

        result_type = self.result_type

        data = self.data.to_dict()

        summary = self.summary

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "task_id": task_id,
                "result_type": result_type,
                "data": data,
                "summary": summary,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.task_result_data import TaskResultData

        d = dict(src_dict)
        task_id = d.pop("task_id")

        result_type = d.pop("result_type")

        data = TaskResultData.from_dict(d.pop("data"))

        summary = d.pop("summary")

        task_result = cls(
            task_id=task_id,
            result_type=result_type,
            data=data,
            summary=summary,
        )

        task_result.additional_properties = d
        return task_result

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
