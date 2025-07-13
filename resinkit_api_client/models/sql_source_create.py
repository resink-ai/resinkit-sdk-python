from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.database_kind import DatabaseKind
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sql_source_create_extra_params_type_0 import SqlSourceCreateExtraParamsType0


T = TypeVar("T", bound="SqlSourceCreate")


@_attrs_define
class SqlSourceCreate:
    """
    Attributes:
        name (str): Unique name for the SQL source
        kind (DatabaseKind):
        host (str): Database host
        port (int): Database port
        database (str): Database name
        user (str): Username (can reference variables)
        password (str): Password (can reference variables)
        query_timeout (Union[None, Unset, str]): Query timeout duration Default: '30s'.
        extra_params (Union['SqlSourceCreateExtraParamsType0', None, Unset]): Additional connection parameters
    """

    name: str
    kind: DatabaseKind
    host: str
    port: int
    database: str
    user: str
    password: str
    query_timeout: Union[None, Unset, str] = "30s"
    extra_params: Union["SqlSourceCreateExtraParamsType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sql_source_create_extra_params_type_0 import SqlSourceCreateExtraParamsType0

        name = self.name

        kind = self.kind.value

        host = self.host

        port = self.port

        database = self.database

        user = self.user

        password = self.password

        query_timeout: Union[None, Unset, str]
        if isinstance(self.query_timeout, Unset):
            query_timeout = UNSET
        else:
            query_timeout = self.query_timeout

        extra_params: Union[None, Unset, dict[str, Any]]
        if isinstance(self.extra_params, Unset):
            extra_params = UNSET
        elif isinstance(self.extra_params, SqlSourceCreateExtraParamsType0):
            extra_params = self.extra_params.to_dict()
        else:
            extra_params = self.extra_params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "kind": kind,
                "host": host,
                "port": port,
                "database": database,
                "user": user,
                "password": password,
            }
        )
        if query_timeout is not UNSET:
            field_dict["query_timeout"] = query_timeout
        if extra_params is not UNSET:
            field_dict["extra_params"] = extra_params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sql_source_create_extra_params_type_0 import SqlSourceCreateExtraParamsType0

        d = dict(src_dict)
        name = d.pop("name")

        kind = DatabaseKind(d.pop("kind"))

        host = d.pop("host")

        port = d.pop("port")

        database = d.pop("database")

        user = d.pop("user")

        password = d.pop("password")

        def _parse_query_timeout(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        query_timeout = _parse_query_timeout(d.pop("query_timeout", UNSET))

        def _parse_extra_params(data: object) -> Union["SqlSourceCreateExtraParamsType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_params_type_0 = SqlSourceCreateExtraParamsType0.from_dict(data)

                return extra_params_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SqlSourceCreateExtraParamsType0", None, Unset], data)

        extra_params = _parse_extra_params(d.pop("extra_params", UNSET))

        sql_source_create = cls(
            name=name,
            kind=kind,
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            query_timeout=query_timeout,
            extra_params=extra_params,
        )

        sql_source_create.additional_properties = d
        return sql_source_create

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
