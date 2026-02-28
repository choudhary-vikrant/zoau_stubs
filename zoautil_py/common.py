# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2023
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
Functions used in multiple modules.
Doesn't import anything from zoautil_py, unlike utilities.py.
"""

from datetime import datetime
from typing import Union, Tuple
import json
import re


DATASET_EX = r"^(?=.{,44}$)([#@$a-zA-Z]{1}[a-zA-z0-9#@$-]{0,7}\.){1,}([#@$a-zA-Z]{1}[a-zA-z0-9#@$-]{0,7})$"
GDG_REL_EX = r"^(?=.{,54}$)([#@$a-zA-Z]{1}[a-zA-z0-9#@$-]{0,7}\.){1,}([#@$a-zA-Z]{1}[a-zA-z0-9#@$-]{0,7})\(([-+0][0-9]){0,3}\)$"
MEMBER_EX = r"^(?=.{,54}$)([#@$a-zA-Z]{1}[a-zA-z0-9#@$-]{0,7}\.){1,}([#@$a-zA-Z]{1}[a-zA-z0-9#@$-]{0,7})\(([#@$a-zA-Z]{1}[a-zA-z0-9#@$-]{0,7})\)$"

class RelativeList(list):
    """Special list class that can be addressed with GDG logic.

    Arguments
    ---------
        - iterable: Iterable
            Iterable object to base the RelativeList from

        - generator: Callable  *Currently unsupported*
            Function to call to generate a new item
    Notes
    -----
     - RelativeList[0] : Most recent
     - RelativeList[1] : Create next **currently unsupported**

    """
    def __init__(self, iterable):
        super().__init__(item for item in iterable)

    def __getitem__(self, index):
        if index <= 0:
            relative_index = len(self)-1 + index
            if relative_index < 0:
                raise IndexError("list index out of range")
            return super().__getitem__(relative_index)
        if index == 1:
            raise IndexError("GDG cannot be implicitly created by addressing")
        raise IndexError("list index out of range")


def parse_universal_arguments(**kwargs) -> str:
    """
    Builds a command argument string from a dictionary

    Returns
    -------
    str:
        String with all options formatted as "-{option}"

    Parameters
    ----------
    kwargs: dict

    Supported Arguments
    -------------------
    debug: bool
        formatted as "-d " if `True`
    verbose: bool
        formatted as "-v " if `True`
    Options: bool
        Additional preformatted options (appends single space after)

    Notes
    -----
    Preformatted options can be appended with the "options" keyword.
    """
    # Get kwargs parameters

    return_string = ""
    if "debug" in kwargs:
        if isinstance(kwargs['debug'],bool):
            if kwargs['debug']:
                return_string += "-d "
        else:
            raise TypeError("Debug option must be a bool")

    if "verbose" in kwargs :
        if isinstance(kwargs['verbose'],bool):
            if kwargs.get("verbose"):
                return_string += "-v "
        else:
            raise TypeError("Verbose option must be a bool")

    if "options" in kwargs:
        if isinstance(kwargs['options'],str):
            if kwargs.get("options"):
                return_string += f"{kwargs.get('options')} "
        else:
            raise TypeError("additional options must be passed as a string")

    return return_string

def clean_dataset_name(name: str) -> str:
    """
    Returns a string with escaped dollar signs and removes quotes
    Notes
    -----
    The function respects pre-escaped characters.
    """

    if name is None:
        return name

    if name.startswith("'") and name.endswith("'") or \
       name.startswith('"') and name.endswith('"'):
        name = name[1:-1]

    return name.replace(r'\$', '$').replace('$', r'\$')

def clean_shell_input(string: str) -> str:
    """
    Returns a string with escaped dollar signs and double quotes

    Notes
    -----
    The function respects pre-escaped characters.
    """

    if string is None:
        return string

    string = string.replace(r'\$', '$').replace('$', r'\$')
    string = string.replace(r'\"', '"').replace('"', r'\"')
    return string


def escape_block_string(original_string: str) -> str:
    """
    Escapes special chars from a given string.

    Current characters:
    - Double Quotes
    - Dollar Sign
    - Acute Accent
    - New Line
    """

    if original_string is None:
        return original_string

    translations = {'"': r"\"",
                    "$": r"\$",
                    "`": r"\`",
                    "\n": r"\n"}
    translation_table = original_string.maketrans(translations)
    escaped_string = original_string.translate(translation_table)
    # \$ and \` are not escape sequences in python
    # revert the change if they were already initially escaped
    escaped_string = escaped_string.replace(r"\\$", r"\$")
    escaped_string = escaped_string.replace(r"\\`", r"\`")

    return escaped_string


def parse_datetime(date_string: str, time_string: str) -> datetime:
    """
    Given date and time strings, returns a datetime object.

    date_string is in format YYYY/MM/DD

    time_string is in format HH:MM:SS

    Converts month and day 00 to 01.
    """
    date_format = "%Y/%m/%d %H:%M:%S"
    timestamp = f"{date_string} {time_string}"

    if "/00" in date_string:
        timestamp = timestamp.replace("/00", "/01")

    return datetime.strptime(timestamp, date_format)

def parse_unknown(attribute: Union[str, None]) -> Union[str, int, None]:
    """Returns None if value matches the unknown identifiers "??" and "?"

    Parameters
    ----------
    attribute : str
        attribute to evaluate

    Returns
    -------
    str
        Unmodified attribute if it is not the unknown identifier.
    None
        If the attribute is the unknown identifier.

    """
    if attribute in ("??","?"):
        return None

    return attribute

def cast_int_optional(attribute: Union[str, int, None]) -> Union[int, None]:
    """`int` cast wrapper. Returns None if cast is not possible.

    Parameters
    ----------
    attribute : any
        Variable to cast

    Returns
    -------
    int, None
        Returns variable as `int` if possible
        Returns `None` if casting fails.

    Raises
    ------
    TypeError
        _description_
    """
    try:
        return int(attribute)  #type: ignore
    except (TypeError, ValueError):
        return None

def zoau_json_load(json_text: str) -> Tuple[dict, dict]:
    """Get the data and meta objects from a JSON string

    Parameters
    ----------
        json_text : str
            String returned by a core utility

    Returns
    -------
        A dictionary tuple where the first element is the whole 'data' object
        and the second in the meta info in the root level
    """
    try:
        root_json = json.loads(json_text)
    except json.JSONDecodeError as js_ex:
        js_ex.msg += f" {json_text=}"
        raise js_ex

    data_json = root_json.pop('data')
    meta_json = root_json # Everything that isn't "data" is "meta"
    return (data_json, meta_json)

def match_expression(pattern,string:str):
    """Returns boolean value according to a regex match (UTF-8)"""
    return bool(re.match(pattern, string))

def multivar_type_validation(variables: dict , data_types: tuple ):
    """ Type checks against an ordered tuple of types,
    raises a TypeError with a proper message if any of the variables is not of
    the expected type.

    Args:
        variables (dict): dictionary with variable names and their values.
        data_types (tuple): ordered tuple with the types to check against.

    Raises:
        TypeError: If any of the variables is not of the expected type.

    Returns:
        bool : True if every variable is of the expected type.
    """
    for i, (variable,value) in enumerate(variables.items()):
        if not isinstance(value,data_types[i]):
            raise TypeError(
                f"Unexpected {type(value)}. Variable {variable} must be of type {data_types[i]}")

    return True

def slicer(s, n):
    """Produce `n`-character chunks from `s`."""
    for start in range(0, len(s), n):
        yield s[start:start+n]

def identify_dtype(dataset_name:str, expected_type:str) -> bool:
    """_summary_

    Args:
        dataset_name (str): _description_
        expected_type (str): _description_ ("DATASET","RELGDG","MEMBER")

    Raises:
        ValueError: _description_
        ValueError: _description_

    Returns:
        bool: _description_
    """
    if expected_type not in ("DATASET","RELGDG","MEMBER"):
        raise ValueError(f"{expected_type} not supported for identification")

    if expected_type == "DATASET":
        return  match_expression(DATASET_EX,dataset_name)
    if expected_type == "RELGDG":
        return match_expression(GDG_REL_EX, dataset_name)
    if expected_type == "MEMBER":
        return match_expression(MEMBER_EX, dataset_name)

    raise ValueError(f"Unable to identify {dataset_name} as {expected_type}")

