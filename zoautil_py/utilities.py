from zoautil_py.common import clean_dataset_name as clean_dataset_name, clean_shell_input as clean_shell_input, parse_universal_arguments as parse_universal_arguments
from zoautil_py.core import call_zoau_library as call_zoau_library
from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

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
def list_library(command: str, *args, **kwargs) -> ZOAUResponse:
    """A simple call to the ZOAU_CORE library"""
def find_member_in_library(command: str, member: str, *args, **kwargs) -> ZOAUResponse:
    """Find member within the ZOAU_CORE library"""
