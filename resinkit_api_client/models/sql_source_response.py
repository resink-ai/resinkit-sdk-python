from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.database_kind import DatabaseKind

if TYPE_CHECKING:
    from ..models.sql_source_response_extra_params_type_0 import SqlSourceResponseExtraParamsType0


T = TypeVar("T", bound="SqlSourceResponse")


@_attrs_define
class SqlSourceResponse:
    """
    Attributes:
        name (str):
        kind (DatabaseKind):
        host (str):
        port (int):
        database (str):
        user (str):
        query_timeout (str):
        extra_params (Union['SqlSourceResponseExtraParamsType0', None]):
        created_at (str):
        updated_at (str):
        created_by (str):
    """

    name: str
    kind: DatabaseKind
    host: str
    port: int
    database: str
    user: str
    query_timeout: str
    extra_params: Union["SqlSourceResponseExtraParamsType0", None]
    created_at: str
    updated_at: str
    created_by: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.sql_source_response_extra_params_type_0 import SqlSourceResponseExtraParamsType0

        name = self.name

        kind = self.kind.value

        host = self.host

        port = self.port

        database = self.database

        user = self.user

        query_timeout = self.query_timeout

        extra_params: Union[None, dict[str, Any]]
        if isinstance(self.extra_params, SqlSourceResponseExtraParamsType0):
            extra_params = self.extra_params.to_dict()
        else:
            extra_params = self.extra_params

        created_at = self.created_at

        updated_at = self.updated_at

        created_by = self.created_by

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
                "query_timeout": query_timeout,
                "extra_params": extra_params,
                "created_at": created_at,
                "updated_at": updated_at,
                "created_by": created_by,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.sql_source_response_extra_params_type_0 import SqlSourceResponseExtraParamsType0

        d = dict(src_dict)
        name = d.pop("name")

        kind = DatabaseKind(d.pop("kind"))

        host = d.pop("host")

        port = d.pop("port")

        database = d.pop("database")

        user = d.pop("user")

        query_timeout = d.pop("query_timeout")

        def _parse_extra_params(data: object) -> Union["SqlSourceResponseExtraParamsType0", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                extra_params_type_0 = SqlSourceResponseExtraParamsType0.from_dict(data)

                return extra_params_type_0
            except:  # noqa: E722
                pass
            return cast(Union["SqlSourceResponseExtraParamsType0", None], data)

        extra_params = _parse_extra_params(d.pop("extra_params"))

        created_at = d.pop("created_at")

        updated_at = d.pop("updated_at")

        created_by = d.pop("created_by")

        sql_source_response = cls(
            name=name,
            kind=kind,
            host=host,
            port=port,
            database=database,
            user=user,
            query_timeout=query_timeout,
            extra_params=extra_params,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
        )

        sql_source_response.additional_properties = d
        return sql_source_response

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
