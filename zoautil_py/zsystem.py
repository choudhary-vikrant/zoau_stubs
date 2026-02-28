# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2021
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
ZOAU Python functions for z/OS system operations.
"""
import json
import logging

from zoautil_py.common import (clean_dataset_name, parse_universal_arguments,
                               zoau_json_load)
from zoautil_py.core import call_zoau_library  # pylint: disable=import-error, no-name-in-module
from zoautil_py.exceptions import MissingFunctionParameter
from zoautil_py.utilities import (find_member_in_library, list_library,
                                  search_library)
from zoautil_py.ztypes import ZOAUResponse

logger: logging.Logger
logger = logging.getLogger(__name__)


def _read_console(json_output: bool = False, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (pcon)"""

    option_str = ''
    # pcon uses -v for both debug and verbose, so we can't use parse_universal_arguments() here
    if ('debug' in kwargs and kwargs.get('debug')) or \
       ('verbose' in kwargs and kwargs.get('verbose')):
        option_str += "-v "

    if json_output:
        option_str += "-j "

    if 'options' in kwargs:
        option_str += kwargs.get('options', '')
    else:
        option_str += '-r'

    logger.debug("ZOAU_CORE call: pcon %s", option_str)
    response = call_zoau_library("pcon", option_str)
    return ZOAUResponse.from_dict(response)


def read_console(options: str = "-r", json_output: bool = False, **kwargs) -> str:
    """
    Fetch contents of the system console within a given period.

    Returns
    -------
    str
        Console output from z/OS system

    Parameters
    ----------
    options : str
        Command line option to select time frame. May be one of the following:
            -r      (recent) last ten minutes of data written to the log
            -l      last hour of data written to the log
            -d      last day of data written to the log
            -w      last week of data written to the log
            -m      last month of data written to the log
            -y      last year of data written to the log
            -a      the entire log

    Other Parameters
    ----------------
    debug : bool
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    json_output : bool
        Enable JSON output. The returned string is a serialized JSON string with this structure:
            {
                "data": {
                    "content": ".....",
                    "content_length": 800,
                    "records": 10,
                    "seconds": 600
                },
                "program": "pcon",
                "options": "-J -r",
                "rc": "0"
            }

    verbose : bool
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    """
    logger.debug("read_console zsystem function call")
    logger.debug("options: %s", options)
    logger.debug("kwargs: %s", kwargs)

    response = _read_console(json_output, options=options, **kwargs)
    return response.stdout_response.rstrip("\n")

def list_data_classes(*args, **kwargs) -> list[str]:
    """
    Return a list of the SMS data classes on the system.

    Returns
    =======
    list[str]

    Other Parameters
    ================
    `debug` : bool
        Enable debug messages (best used with _function if available and read
        from ZOAUResponse.stderr_output)

    `verbose` : bool
        Enable verbose messages (best used with _function if available and read
        from ZOAUResponse.stderr_output)
    """
    logger.debug("list_data_classes zsystem function call")
    logger.debug("args: %s",args)
    logger.debug("kwargs: %s",kwargs)

    response = list_library("pdc", *args, **kwargs)
    if not response.stdout_response:
        return []
    return response.stdout_response.rstrip("\n").split("\n")

def list_linklist(*args, **kwargs) -> list[str]:
    """
    Return linklist representation on system

    Returns
    -------
    list[str]
        List of the dataset names in the link list

    list[]
        Empty list if no datasets were found in the link list

    Parameters
    ----------
    kwargs: dict
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug : bool
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    verbose : bool
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    """
    logger.debug("list_linklist zsystem function call")
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    response = list_library("pll", *args, **kwargs)
    if not response.stdout_response:
        return []
    return response.stdout_response.rstrip("\n").split("\n")


def list_parmlib(*args, **kwargs) -> list[str]:
    """
    Return parmlib representation on system

    Returns
    -------
    list[str]
        List of the dataset names in the parmlib

    list[]
        Empty list if no datasets were found in the parmlib

    Parameters
    ----------
    kwargs: dict
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug : bool
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    verbose : bool
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    """
    logger.debug("list_parmlib zsystem function call")
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    response = list_library("pparm", *args, **kwargs)
    if not response.stdout_response:
        return []
    return response.stdout_response.rstrip("\n").split("\n")


def list_proclib(*args, **kwargs) -> list[str]:
    """
    Return proclib representation on system

    Returns
    -------
    list[str]
        List of the dataset names in the proclib

    list[]
        Empty list if no datasets were found in the proclib

    Parameters
    ----------

    kwargs: dict
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug : bool
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    verbose : bool
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    """
    logger.debug("list_proclib zsystem function call")
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    response = list_library("pproc", *args, **kwargs)
    if not response.stdout_response:
        return []
    return response.stdout_response.rstrip("\n").split("\n")


def find_linklist(member: str, *args, **kwargs) -> str:
    """
    Find member in linklist

    Returns
    -------
    str
        Library that contains the member

    Parameters
    ----------
    member : str
        The member to search for

    kwargs: dict
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug : bool
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    verbose : bool
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    """
    logger.debug("find_linklist zsystem function call")
    logger.debug("member: %s", member)
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    response = find_member_in_library("llwhence", member, *args, **kwargs)
    return response.stdout_response.rstrip("\n")


def find_parmlib(member: str, *args, **kwargs) -> str:
    """
    Find member in parmlib

    Returns
    -------
    str
        Library that contains the member

    Parameters
    ----------
    member : str
        The member to search for

    kwargs: dict
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug : bool
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    verbose : bool
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    """
    logger.debug("find_parmlib zsystem function call")
    logger.debug("member: %s", member)
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    member = clean_dataset_name(member)

    response = find_member_in_library("parmwhence", member, *args, **kwargs)
    return response.stdout_response.rstrip("\n")


def find_proclib(member: str, *args, **kwargs) -> str:
    """
    Find member in proclib

    Returns
    -------
    str
        Library that contains the member

    Parameters
    ----------
    member : str
        The member to search for

    kwargs: dict
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug : bool
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    verbose : bool
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    """
    logger.debug("find_proclib zsystem function call")
    logger.debug("member: %s", member)
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    member = clean_dataset_name(member)

    response = find_member_in_library("procwhence", member, *args, **kwargs)
    return response.stdout_response.rstrip("\n")


def search_parmlib(find: str, *args, **kwargs) -> str:
    """
    Search parmlib for string

    Returns
    -------
    str
        Output of search (grep-like response)

    Parameters
    ----------
    find : str
        The string to search for

    kwargs: dict
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    ignore_case : bool
        Ignore case in search

    display_lines : bool
        Display the lines that contain found string

    debug : bool
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    verbose : bool
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    """
    logger.debug("search_parmlib zsystem function call")
    logger.debug("find: %s", find)
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    response = search_library("parmgrep", find=find, *args, **kwargs)
    if not response.stdout_response:
        return None
    return response.stdout_response.rstrip("\n")


def search_proclib(find: str, *args, **kwargs) -> str:
    """
    Search proclib for string

    Returns
    -------
    str
        Output of search (grep-like response)

    Parameters
    ----------
    find : str
        The string to search for

    kwargs: dict
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    ignore_case : bool
        Ignore case in search

    display_lines : bool
        Display the lines that contain found string

    debug : bool
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    verbose : bool
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    """
    logger.debug("search_proclib zsystem function call")
    logger.debug("find: %s", find)
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    response = search_library("procgrep", find=find, *args, **kwargs)
    if not response.stdout_response:
        return None
    return response.stdout_response.rstrip("\n")


def apf(*args, **kwargs) -> ZOAUResponse:
    """
    Authorized Program Facility (APF) operations
    ZOAU apfadm utility python API

    Returns
    -------
    ZOAUResponse
        stdout_response, stderr_response, rc

    Parameters
    ----------

    kwargs: dict
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    opt : str
        APF operation. May be one of:
            add          : Add dataset
            del          : Remove dataset
            set_dynamic  : Set APF list format to DYNAMIC
            set_static   : Set APF list format to STATIC
            check_format : Check APF list current format
            list         : Return APF list in JSON format.
            (i.e. { "data": { "format": "DYNAMIC", "header": ['<1st line>', ... ],
			  datasets: [ { "vol":"G2201D", "ds": "SYS1.LINKLIB" }, ... ] } })

    dsname : str
        Dataset name (library) to be added or removed to or from APF list.
        This is required if opt is add or del

    volume: str
        The volume serial number that dsname resides on.
        If not provided, dsname has to be cataloged.

    sms: bool
        Indicates that the library specified on the dsname parameter is managed by the Storage Management Subsystem (SMS)
        If true, volume value will be ignored.

    forceDynamic: bool
        Ensure APF list format is "DYNAMIC" before adding or removing libraries

    persistent: dict
        Add or remove a persistent entry to a dataset. Choices:
            addDataset : The dataset be used to Persist the APF entry
            delDataset : The dataset be used to Remove the APF entry
            marker     : Custom marker in "\\/\\*.\\*{mark}.\\*\\*\\/" format, default: "/\\* {mark} MANAGED BLOCK <timestamp> \\*/"
            <timestamp> will be replaced with current time, format: "+%Y%m%d-%H%M%S"

    batch: list[dict]
        A list of dictionaries for adding/removing libraries. This is mutually exclusive with opt, dsname, volume, sms
        Can be used with persistent. the options are opt, dsname, volume and sms. the description of the options are
        the same as above except opt options are add and del.
        (i.e. [{'opt': 'add', 'dsname': 'SOME.DATASET.DS1'},
        {'opt': 'del', 'dsname': 'SOME.DATASET.DS2', 'volume': 'VOL001'},
        {'opt': 'add', 'dsname': 'SOME.DATASET.DS3', 'sms': True},
        {'opt': 'del', 'dsname': 'SOME.DATASET.DS4', 'volume': 'VOL005'})

    ignore : bool
        Ignore errors from duplicate add/remove dataset operations.

    debug : bool
        Enable debug messages

    verbose : bool
        Enable verbose messages
    """
    logger.debug("apf zsystem function call")
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    options = " "
    options += parse_universal_arguments(**kwargs)

    ignore = kwargs.get("ignore", False)
    opt = kwargs.get("opt", None)
    dsname = clean_dataset_name(kwargs.get("dsname"))
    volume = kwargs.get("volume", None)
    sms = kwargs.get("sms", False)
    force_dynamic = kwargs.get("forceDynamic", False)
    persistent = kwargs.get("persistent", None)
    batch = kwargs.get("batch", None)

    if ignore:
        options += "-i "

    if persistent:
        if not isinstance(persistent, dict):
            raise TypeError("Invalid persistent format ")
        persistent_option = " "
        add_ds = clean_dataset_name(persistent.get("addDataset"))
        del_ds = clean_dataset_name(persistent.get("delDataset"))
        marker = persistent.get("marker", None)
        if add_ds is None and del_ds is None:
            raise ValueError(
                "addDataset and/or delDataset is required with persistent option"
            )
        if marker:
            persistent_option += f'-M "{marker}" '
        if add_ds:
            persistent_option += f'-P "{add_ds}" '
        if del_ds:
            persistent_option += f'-R "{del_ds}" '
    if opt:
        if opt in ["add", "del"]:
            if dsname is None:
                raise ValueError(f"dsname is required with {opt} operation")
            if force_dynamic:
                options += "-f "
            if opt == "add":
                options += "-A "
            else:
                options += "-D "
            options += f'"{dsname}'
            if sms:
                options += ",sms"
            elif volume:
                options += f",{volume}"
            options += '" '
            if persistent:
                options += persistent_option
        elif opt in ["set_dynamic", "set_static", "check_format"]:
            options += "-F "
            if opt == "set_dynamic":
                options += "DYNAMIC"
            elif opt == "set_static":
                options += "STATIC"
        elif opt == "list":
            options += "-lj"
        else:
            raise ValueError("Invalid operation: " + opt)
    elif batch:
        if not isinstance(batch, list):
            raise TypeError("Invalid batch format ")
        if force_dynamic:
            options += "-f "
        for b in batch:
            if not isinstance(b, dict):
                raise TypeError("Invalid batch member format ")
            opt = b.get("opt", None)
            dsname =  clean_dataset_name(b.get("dsname"))
            volume = b.get("volume", None)
            sms = b.get("sms", False)
            if opt in ["add", "del"]:
                if dsname is None:
                    raise MissingFunctionParameter(
                        f"dsname is required with {opt} operation"
                    )
                if opt == "add":
                    options += "-A "
                else:
                    options += "-D "
                options += f'"{dsname}'
                if sms:
                    options += ",sms"
                elif volume:
                    options += f",{volume}"
                options += '" '
            else:
                raise ValueError("Invalid operation: " + opt)
        if persistent:
            options += persistent_option
    else:
        raise ValueError("Incorrect parameters")

    response = call_zoau_library("apfadm", options)
    return ZOAUResponse.from_dict(response)


def _zinfo(*args, **kwargs) -> ZOAUResponse:
    # these are flags for verbose, debug and options
    # options = parse_universal_arguments(**kwargs)

    # call to zinfo() --> -a, get everything
    # change options -> facts
    facts_str = "-aj"

    if "facts_str" in kwargs and kwargs.get("facts_str"):
        facts_str = kwargs.get("facts_str")

    # TODO - sanitize input string

    response = call_zoau_library("zinfo", facts_str)
    return ZOAUResponse.from_dict(response)


def zinfo(*args, **kwargs) -> str:
    """
    z/OS Fact Gathering (zinfo) operations

    Returns
    -------
    str
        z/OS fact string gathered from system

    dict
        The information retrieved, in JSON format

    Other Parameters
    ----------------
    facts : list of str
        List of subsets to include in the payload. The following is a list of
        currently available subsets followed by options to specify them.

            'ipl' subset    :  ipl, iplinfo, ipl_info
            'cpu' subset    :  cpu, cpuinfo, cpu_info
            'sys' subset    :  sys, sysinfo, sys_info
            'iodf' subset   :  iodf, iodfinfo, iodf_info

            To include all subsets in the payload, use: a or all.

    json : bool
        When True, the output is a dictionary
        When False, the output is a string

    """
    logger.debug("zinfo zsystem function call")
    logger.debug("args: %s", args)
    logger.debug("kwargs: %s", kwargs)

    all_arg = "-aj"
    ipl_arg = "-jt ipl"
    cpu_arg = "-jt cpu"
    sys_arg = "-jt sys"
    iodf_arg = "-jt iodf"

    opts_dict = {
        "a": all_arg,
        "all": all_arg,
        "ipl": ipl_arg,
        "iplinfo": ipl_arg,
        "ipl_info": ipl_arg,
        "cpu": cpu_arg,
        "cpuinfo": cpu_arg,
        "cpu_info": cpu_arg,
        "sys": sys_arg,
        "sysinfo": sys_arg,
        "sys_info": sys_arg,
        "iodf": iodf_arg,
        "iodfinfo": iodf_arg,
        "iodf_info": iodf_arg,
    }

    facts_str = ""
    facts = []
    json_output = False

    # Grab facts selections passed in from kwargs.
    if "facts" in kwargs and kwargs.get("facts"):
        facts += kwargs.get("facts")  # append to default (empty) facts list

    if 'json' in kwargs and kwargs.get('json'):
        json_output = kwargs.get('json')

    # Options parsing and validating.
    for fact in facts:
        if fact.lower() not in opts_dict:
            raise ValueError(f"Invalid zinfo option '{fact}'")

        # At this point we know that opt is in opts_dict.

        # If it's '-a' then facts_str = '-a' and end the loop
        # zinfohelper.c logic already catches this use case...
        if opts_dict[fact.lower()] == opts_dict["a"]:
            facts_str = (
                opts_dict[fact.lower()] + " "
            )  # add space char in case of additional flags
            break

        facts_str += opts_dict[fact.lower()] + ' ' # add space char in case of additional flags

    # print(facts_str)
    response =_zinfo(*args, facts_str=facts_str, **kwargs)
    response_json, _ = zoau_json_load(response.stdout_response)
    logger.debug("json data: %s", response_json)

    if json_output:
        return response_json

    return json.dumps(response_json)
