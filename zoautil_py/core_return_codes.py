from enum import Enum

class DDLSReturnCodes(Enum):
    OK = 0
    SYNTAX_ERROR = 2
    INVALID_ARGUMENT = 4
    JOB_NOT_READY = 5
    JOB_IN_TRANSMISSION = 6
    ERROR = 8
