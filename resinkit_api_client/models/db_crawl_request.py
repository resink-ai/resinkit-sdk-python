from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.db_crawl_config import DbCrawlConfig


T = TypeVar("T", bound="DbCrawlRequest")


@_attrs_define
class DbCrawlRequest:
    """Request model for database crawl API

    Attributes:
        config (DbCrawlConfig): Main configuration for database crawling
    """

    config: "DbCrawlConfig"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config = self.config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "config": config,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.db_crawl_config import DbCrawlConfig

        d = dict(src_dict)
        config = DbCrawlConfig.from_dict(d.pop("config"))

        db_crawl_request = cls(
            config=config,
        )

        db_crawl_request.additional_properties = d
        return db_crawl_request

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
