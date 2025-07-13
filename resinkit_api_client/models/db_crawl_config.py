from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dsds_config import DSDSConfig
    from ..models.global_defaults import GlobalDefaults
    from ..models.table_regex_selection import TableRegexSelection
    from ..models.table_selection import TableSelection


T = TypeVar("T", bound="DbCrawlConfig")


@_attrs_define
class DbCrawlConfig:
    """Main configuration for database crawling

    Attributes:
        source (str): SQL source name (configured via /sources endpoints)
        tables (list[Union['TableRegexSelection', 'TableSelection']]): List of table specifications
        defaults (Union[Unset, GlobalDefaults]): Global default settings
        dsds (Union[Unset, DSDSConfig]): Configuration for Descriptive Sample Data Schema generation
    """

    source: str
    tables: list[Union["TableRegexSelection", "TableSelection"]]
    defaults: Union[Unset, "GlobalDefaults"] = UNSET
    dsds: Union[Unset, "DSDSConfig"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.table_selection import TableSelection

        source = self.source

        tables = []
        for tables_item_data in self.tables:
            tables_item: dict[str, Any]
            if isinstance(tables_item_data, TableSelection):
                tables_item = tables_item_data.to_dict()
            else:
                tables_item = tables_item_data.to_dict()

            tables.append(tables_item)

        defaults: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.defaults, Unset):
            defaults = self.defaults.to_dict()

        dsds: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.dsds, Unset):
            dsds = self.dsds.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source": source,
                "tables": tables,
            }
        )
        if defaults is not UNSET:
            field_dict["defaults"] = defaults
        if dsds is not UNSET:
            field_dict["dsds"] = dsds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dsds_config import DSDSConfig
        from ..models.global_defaults import GlobalDefaults
        from ..models.table_regex_selection import TableRegexSelection
        from ..models.table_selection import TableSelection

        d = dict(src_dict)
        source = d.pop("source")

        tables = []
        _tables = d.pop("tables")
        for tables_item_data in _tables:

            def _parse_tables_item(data: object) -> Union["TableRegexSelection", "TableSelection"]:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    tables_item_type_0 = TableSelection.from_dict(data)

                    return tables_item_type_0
                except:  # noqa: E722
                    pass
                if not isinstance(data, dict):
                    raise TypeError()
                tables_item_type_1 = TableRegexSelection.from_dict(data)

                return tables_item_type_1

            tables_item = _parse_tables_item(tables_item_data)

            tables.append(tables_item)

        _defaults = d.pop("defaults", UNSET)
        defaults: Union[Unset, GlobalDefaults]
        if isinstance(_defaults, Unset):
            defaults = UNSET
        else:
            defaults = GlobalDefaults.from_dict(_defaults)

        _dsds = d.pop("dsds", UNSET)
        dsds: Union[Unset, DSDSConfig]
        if isinstance(_dsds, Unset):
            dsds = UNSET
        else:
            dsds = DSDSConfig.from_dict(_dsds)

        db_crawl_config = cls(
            source=source,
            tables=tables,
            defaults=defaults,
            dsds=dsds,
        )

        db_crawl_config.additional_properties = d
        return db_crawl_config

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
