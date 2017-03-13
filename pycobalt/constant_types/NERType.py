from enum import Enum


class NERType(Enum):
    NONE = 0
    PERSON = 1
    OTHER = 2
    THING = 3
    DATE = 4
    NUMBER = 5
    SET = 6
    MONEY = 7
    PERCENT = 8
    DURATION = 9
    MISC = 10
    ORDINAL = 11
