from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.table_crawl_result_dsds_type_0 import TableCrawlResultDsdsType0
    from ..models.table_crawl_result_sample_data_item import TableCrawlResultSampleDataItem


T = TypeVar("T", bound="TableCrawlResult")


@_attrs_define
class TableCrawlResult:
    """Result of crawling a single table

    Attributes:
        table_name (str): Name of the table
        full_path (str): Full path including schema if applicable
        ddl (str): DDL (CREATE TABLE statement) for the table
        sample_data (list['TableCrawlResultSampleDataItem']): Sample data from the table
        dsds (Union['TableCrawlResultDsdsType0', None, Unset]): Descriptive Sample Data Schema
    """

    table_name: str
    full_path: str
    ddl: str
    sample_data: list["TableCrawlResultSampleDataItem"]
    dsds: Union["TableCrawlResultDsdsType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.table_crawl_result_dsds_type_0 import TableCrawlResultDsdsType0

        table_name = self.table_name

        full_path = self.full_path

        ddl = self.ddl

        sample_data = []
        for sample_data_item_data in self.sample_data:
            sample_data_item = sample_data_item_data.to_dict()
            sample_data.append(sample_data_item)

        dsds: Union[None, Unset, dict[str, Any]]
        if isinstance(self.dsds, Unset):
            dsds = UNSET
        elif isinstance(self.dsds, TableCrawlResultDsdsType0):
            dsds = self.dsds.to_dict()
        else:
            dsds = self.dsds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "table_name": table_name,
                "full_path": full_path,
                "ddl": ddl,
                "sample_data": sample_data,
            }
        )
        if dsds is not UNSET:
            field_dict["dsds"] = dsds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.table_crawl_result_dsds_type_0 import TableCrawlResultDsdsType0
        from ..models.table_crawl_result_sample_data_item import TableCrawlResultSampleDataItem

        d = dict(src_dict)
        table_name = d.pop("table_name")

        full_path = d.pop("full_path")

        ddl = d.pop("ddl")

        sample_data = []
        _sample_data = d.pop("sample_data")
        for sample_data_item_data in _sample_data:
            sample_data_item = TableCrawlResultSampleDataItem.from_dict(sample_data_item_data)

            sample_data.append(sample_data_item)

        def _parse_dsds(data: object) -> Union["TableCrawlResultDsdsType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                dsds_type_0 = TableCrawlResultDsdsType0.from_dict(data)

                return dsds_type_0
            except:  # noqa: E722
                pass
            return cast(Union["TableCrawlResultDsdsType0", None, Unset], data)

        dsds = _parse_dsds(d.pop("dsds", UNSET))

        table_crawl_result = cls(
            table_name=table_name,
            full_path=full_path,
            ddl=ddl,
            sample_data=sample_data,
            dsds=dsds,
        )

        table_crawl_result.additional_properties = d
        return table_crawl_result

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
