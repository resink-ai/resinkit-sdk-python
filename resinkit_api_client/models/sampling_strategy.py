from enum import Enum


class SamplingStrategy(str, Enum):
    EARLIEST = "earliest"
    LATEST = "latest"

    def __str__(self) -> str:
        return str(self.value)
