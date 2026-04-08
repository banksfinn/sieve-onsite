from enum import Enum

DEFAULT_LIMIT = 100
DEFAULT_OFFSET = 0


class SortOrder(Enum):
    asc = "asc"
    desc = "desc"
