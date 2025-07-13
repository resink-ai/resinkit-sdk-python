from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.retrieval_metadata import RetrievalMetadata
    from ..models.table_crawl_result import TableCrawlResult


T = TypeVar("T", bound="DbCrawlResult")


@_attrs_define
class DbCrawlResult:
    """Complete result of database crawling operation

    Attributes:
        retrieval_metadata (RetrievalMetadata): Metadata about the crawl operation
        tables (list['TableCrawlResult']): Results for each crawled table
    """

    retrieval_metadata: "RetrievalMetadata"
    tables: list["TableCrawlResult"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        retrieval_metadata = self.retrieval_metadata.to_dict()

        tables = []
        for tables_item_data in self.tables:
            tables_item = tables_item_data.to_dict()
            tables.append(tables_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "retrieval_metadata": retrieval_metadata,
                "tables": tables,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.retrieval_metadata import RetrievalMetadata
        from ..models.table_crawl_result import TableCrawlResult

        d = dict(src_dict)
        retrieval_metadata = RetrievalMetadata.from_dict(d.pop("retrieval_metadata"))

        tables = []
        _tables = d.pop("tables")
        for tables_item_data in _tables:
            tables_item = TableCrawlResult.from_dict(tables_item_data)

            tables.append(tables_item)

        db_crawl_result = cls(
            retrieval_metadata=retrieval_metadata,
            tables=tables,
        )

        db_crawl_result.additional_properties = d
        return db_crawl_result

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
