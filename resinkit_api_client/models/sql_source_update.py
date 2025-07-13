from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sql_source_update_extra_params_type_0 import (
        SqlSourceUpdateExtraParamsType0,
    )


T = TypeVar("T", bound="SqlSourceUpdate")


@_attrs_define
class SqlSourceUpdate:
    """
    Attributes:
        host (Union[None, Unset, str]):
        port (Union[None, Unset, int]):
        database (Union[None, Unset, str]):
        user (Union[None, Unset, str]):
        password (Union[None, Unset, str]):
        query_timeout (Union[None, Unset, str]):
        extra_params (Union['SqlSourceUpdateExtraParamsType0', None, Unset]):
    """

    host: Union[None, Unset, str] = UNSET
    port: Union[None, Unset, int] = UNSET
    database: Union[None, Unset, str] = UNSET
    user: Union[None, Unset, str] = UNSET
    password: Union[None, Unset, str] = UNSET
    query_timeout: Union[None, Unset, str] = UNSET
    extra_params: Union["SqlSourceUpdateExtraParamsType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sql_source_update_extra_params_type_0 import (
            SqlSourceUpdateExtraParamsType0,
        )

        host: Union[None, Unset, str]
        if isinstance(self.host, Unset):
            host = UNSET
        else:
            host = self.host

        port: Union[None, Unset, int]
        if isinstance(self.port, Unset):
            port = UNSET
        else:
            port = self.port

        database: Union[None, Unset, str]
        if isinstance(self.database, Unset):
            database = UNSET
        else:
            database = self.database

        user: Union[None, Unset, str]
        if isinstance(self.user, Unset):
            user = UNSET
        else:
            user = self.user

        password: Union[None, Unset, str]
        if isinstance(self.password, Unset):
            password = UNSET
        else:
            password = self.password

        query_timeout: Union[None, Unset, str]
        if isinstance(self.query_timeout, Unset):
            query_timeout = UNSET
        else:
            query_timeout = self.query_timeout

        extra_params: Union[None, Unset, dict[str, Any]]
        if isinstance(self.extra_params, Unset):
            extra_params = UNSET
        elif isinstance(self.extra_params, SqlSourceUpdateExtraParamsType0):
            extra_params = self.extra_params.to_dict()
        else:
            extra_params = self.extra_params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if host is not UNSET:
            field_dict["host"] = host
        if port is not UNSET:
            field_dict["port"] = port
        if database is not UNSET:
            field_dict["database"] = database
        if user is not UNSET:
            field_dict["user"] = user
        if password is not UNSET:
            field_dict["password"] = password
        if query_timeout is not UNSET:
            field_dict["query_timeout"] = query_timeout
        if extra_params is not UNSET:
            field_dict["extra_params"] = extra_params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sql_source_update_extra_params_type_0 import (
            SqlSourceUpdateExtraParamsType0,
        )

        d = dict(src_dict)

        def _parse_host(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        host = _parse_host(d.pop("host", UNSET))

        def _parse_port(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        port = _parse_port(d.pop("port", UNSET))

        def _parse_database(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        database = _parse_database(d.pop("database", UNSET))

        def _parse_user(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        user = _parse_user(d.pop("user", UNSET))

        def _parse_password(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        password = _parse_password(d.pop("password", UNSET))

        def _parse_query_timeout(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        query_timeout = _parse_query_timeout(d.pop("query_timeout", UNSET))

        def _parse_extra_params(
            data: object,
        ) -> Union["SqlSourceUpdateExtraParamsType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_params_type_0 = SqlSourceUpdateExtraParamsType0.from_dict(data)

                return extra_params_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SqlSourceUpdateExtraParamsType0", None, Unset], data)

        extra_params = _parse_extra_params(d.pop("extra_params", UNSET))

        sql_source_update = cls(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            query_timeout=query_timeout,
            extra_params=extra_params,
        )

        sql_source_update.additional_properties = d
        return sql_source_update

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
