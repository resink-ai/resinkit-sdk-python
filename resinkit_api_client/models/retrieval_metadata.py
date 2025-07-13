from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="RetrievalMetadata")


@_attrs_define
class RetrievalMetadata:
    """Metadata about the crawl operation

    Attributes:
        timestamp_utc (str): UTC timestamp when crawl was performed
        source_database (str): Source database name
        config_hash (str): Hash of the configuration used
    """

    timestamp_utc: str
    source_database: str
    config_hash: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timestamp_utc = self.timestamp_utc

        source_database = self.source_database

        config_hash = self.config_hash

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timestamp_utc": timestamp_utc,
                "source_database": source_database,
                "config_hash": config_hash,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        timestamp_utc = d.pop("timestamp_utc")

        source_database = d.pop("source_database")

        config_hash = d.pop("config_hash")

        retrieval_metadata = cls(
            timestamp_utc=timestamp_utc,
            source_database=source_database,
            config_hash=config_hash,
        )

        retrieval_metadata.additional_properties = d
        return retrieval_metadata

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
