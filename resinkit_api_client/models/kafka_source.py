from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="KafkaSource")


@_attrs_define
class KafkaSource:
    """Kafka cluster connection configuration

    Attributes:
        bootstrap_servers (str): Comma-separated list of Kafka brokers
        security_protocol (Union[None, Unset, str]): Security protocol (e.g., SASL_SSL)
        sasl_mechanism (Union[None, Unset, str]): SASL mechanism (e.g., PLAIN)
        schema_registry_url (Union[None, Unset, str]): Schema Registry URL for Avro/Protobuf
        sasl_username (Union[None, Unset, str]): SASL username
        sasl_password (Union[None, Unset, str]): SASL password
    """

    bootstrap_servers: str
    security_protocol: Union[None, Unset, str] = UNSET
    sasl_mechanism: Union[None, Unset, str] = UNSET
    schema_registry_url: Union[None, Unset, str] = UNSET
    sasl_username: Union[None, Unset, str] = UNSET
    sasl_password: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        bootstrap_servers = self.bootstrap_servers

        security_protocol: Union[None, Unset, str]
        if isinstance(self.security_protocol, Unset):
            security_protocol = UNSET
        else:
            security_protocol = self.security_protocol

        sasl_mechanism: Union[None, Unset, str]
        if isinstance(self.sasl_mechanism, Unset):
            sasl_mechanism = UNSET
        else:
            sasl_mechanism = self.sasl_mechanism

        schema_registry_url: Union[None, Unset, str]
        if isinstance(self.schema_registry_url, Unset):
            schema_registry_url = UNSET
        else:
            schema_registry_url = self.schema_registry_url

        sasl_username: Union[None, Unset, str]
        if isinstance(self.sasl_username, Unset):
            sasl_username = UNSET
        else:
            sasl_username = self.sasl_username

        sasl_password: Union[None, Unset, str]
        if isinstance(self.sasl_password, Unset):
            sasl_password = UNSET
        else:
            sasl_password = self.sasl_password

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bootstrap_servers": bootstrap_servers,
            }
        )
        if security_protocol is not UNSET:
            field_dict["security_protocol"] = security_protocol
        if sasl_mechanism is not UNSET:
            field_dict["sasl_mechanism"] = sasl_mechanism
        if schema_registry_url is not UNSET:
            field_dict["schema_registry_url"] = schema_registry_url
        if sasl_username is not UNSET:
            field_dict["sasl_username"] = sasl_username
        if sasl_password is not UNSET:
            field_dict["sasl_password"] = sasl_password

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        bootstrap_servers = d.pop("bootstrap_servers")

        def _parse_security_protocol(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        security_protocol = _parse_security_protocol(d.pop("security_protocol", UNSET))

        def _parse_sasl_mechanism(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sasl_mechanism = _parse_sasl_mechanism(d.pop("sasl_mechanism", UNSET))

        def _parse_schema_registry_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        schema_registry_url = _parse_schema_registry_url(d.pop("schema_registry_url", UNSET))

        def _parse_sasl_username(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sasl_username = _parse_sasl_username(d.pop("sasl_username", UNSET))

        def _parse_sasl_password(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        sasl_password = _parse_sasl_password(d.pop("sasl_password", UNSET))

        kafka_source = cls(
            bootstrap_servers=bootstrap_servers,
            security_protocol=security_protocol,
            sasl_mechanism=sasl_mechanism,
            schema_registry_url=schema_registry_url,
            sasl_username=sasl_username,
            sasl_password=sasl_password,
        )

        kafka_source.additional_properties = d
        return kafka_source

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
