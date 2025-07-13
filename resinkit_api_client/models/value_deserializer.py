from enum import Enum


class ValueDeserializer(str, Enum):
    AVRO = "avro"
    JSON = "json"
    PROTOBUF = "protobuf"
    STRING = "string"

    def __str__(self) -> str:
        return str(self.value)
