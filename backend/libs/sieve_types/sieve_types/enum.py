from enum import Enum


class SerializableEnum(str, Enum):
    def __str__(self) -> str:
        return self._value_

    def __repr__(self) -> str:
        return self._value_.__repr__()
