import logging
from zoautil_py.common import clean_dataset_name as clean_dataset_name, parse_universal_arguments as parse_universal_arguments, zoau_json_load as zoau_json_load
from zoautil_py.core import call_zoau_library as call_zoau_library
from zoautil_py.exceptions import MissingFunctionParameter as MissingFunctionParameter
from zoautil_py.utilities import find_member_in_library as find_member_in_library, list_library as list_library, search_library as search_library
from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

logger: logging.Logger

def read_console(options: str = '-r', json_output: bool = False, **kwargs) -> str:
    '''
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
    '''
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
def apf(*args, **kwargs) -> ZOAUResponse:
    '''
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
            (i.e. { "data": { "format": "DYNAMIC", "header": [\'<1st line>\', ... ],
\t\t\t  datasets: [ { "vol":"G2201D", "ds": "SYS1.LINKLIB" }, ... ] } })

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
        (i.e. [{\'opt\': \'add\', \'dsname\': \'SOME.DATASET.DS1\'},
        {\'opt\': \'del\', \'dsname\': \'SOME.DATASET.DS2\', \'volume\': \'VOL001\'},
        {\'opt\': \'add\', \'dsname\': \'SOME.DATASET.DS3\', \'sms\': True},
        {\'opt\': \'del\', \'dsname\': \'SOME.DATASET.DS4\', \'volume\': \'VOL005\'})

    ignore : bool
        Ignore errors from duplicate add/remove dataset operations.

    debug : bool
        Enable debug messages

    verbose : bool
        Enable verbose messages
    '''
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
