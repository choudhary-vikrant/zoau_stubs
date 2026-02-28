# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2023
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
Internal methods to invoke ZOAU core tools.
"""
from zoautil_py.common import (clean_dataset_name, clean_shell_input,
                               parse_universal_arguments)
from zoautil_py.core import call_zoau_library  # pylint: disable=import-error, no-name-in-module
from zoautil_py.ztypes import ZOAUResponse


def search_library(command: str, find: str, *args, **kwargs) -> ZOAUResponse:
    """
    Search library for a specific command with a call to the ZOAU_CORE library

    Returns
    -------
    ZOAUResponse

    Parameters
    ----------
    command : str
        The command to submit

    find : str
        Command parameters

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    ignore_case : bool, optional

    display_lines : bool, optional

    """
    options = ""
    options += parse_universal_arguments(**kwargs)

    if "ignore_case" in kwargs and kwargs.get("ignore_case"):
        options += "-i "

    if "display_lines" in kwargs and kwargs.get("display_lines"):
        options += "-n "

    options += clean_shell_input(find)

    response = call_zoau_library(command, options)
    return ZOAUResponse.from_dict(response)


def list_library(command: str, *args, **kwargs) -> ZOAUResponse:
    """A simple call to the ZOAU_CORE library"""
    options = ""
    options += parse_universal_arguments(**kwargs)
    response = call_zoau_library(command, options)
    return ZOAUResponse.from_dict(response)


def find_member_in_library(command: str, member: str, *args, **kwargs) -> ZOAUResponse:
    """Find member within the ZOAU_CORE library"""
    options = ""
    options += parse_universal_arguments(**kwargs)
    member = clean_dataset_name(member)
    options += f'"{member}"'

    response = call_zoau_library(command, options)
    return ZOAUResponse.from_dict(response)
