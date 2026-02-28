# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2023
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
Enum classes listing the possible return codes for each callable ZOAU Core utility
"""
from enum import Enum

class DDLSReturnCodes(Enum):
    """
    Defined to match return codes on `ddlshelper.c`
    """
    OK = 0
    SYNTAX_ERROR = 2
    INVALID_ARGUMENT = 4
    JOB_NOT_READY = 5
    JOB_IN_TRANSMISSION = 6
    ERROR = 8
