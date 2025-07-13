from enum import Enum


class DatabaseKind(str, Enum):
    MSSQL = "mssql"
    MYSQL = "mysql"
    ORACLE = "oracle"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    STARROCKS = "starrocks"

    def __str__(self) -> str:
        return str(self.value)
