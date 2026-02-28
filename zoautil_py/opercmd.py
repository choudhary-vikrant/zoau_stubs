# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2022
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
ZOAU Python functions for z/OS operator commands.
"""
import logging

from zoautil_py.common import clean_shell_input, parse_universal_arguments
from zoautil_py.core import call_zoau_library  # pylint: disable=import-error, no-name-in-module
from zoautil_py.exceptions import ZOAUException
from zoautil_py.ztypes import ZOAUResponse

logger: logging.Logger
logger = logging.getLogger(__name__)


def execute(command: str, timeout: int = 0, json: bool = False, **kwargs) -> ZOAUResponse:
    """
    Submit a z/OS operator command.

    Returns
    -------
    ZOAUResponse

    Parameters
    ----------
    command : str
        The z/OS operator command to submit.

    timeout : int, optional
        The maximum amount of time, in centiseconds (0.01s), to wait for a
        response after submitting the console command.

        A value of 0 means to wait the default amount of time
        supported by the `opercmd` utility. The timeout must be
        between 0 and 2147483600 centiseconds, inclusive.
        This value should be increased if the command response output is unexpectedly truncated.

    json : bool, optional
        Invoke JSON output from opercmd. False by default.

        When enabled, the output is a JSON string with this structure:
        {
            "data": {
                "output": <string>
            },
            "timestamp": <string>,
            "timeout": <number>,
            "command": <string>,
            "console": <string>,
            "program": <string>,
            "options": <string>,
            "rc": <string>
        }

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------

    debug : bool, optional
        Enable debug messages (best used with _function if available and read from
        ZOAUResponse.stderr_output)

    console : str, optional
        Suffix to be used for generating the console name used to submit the command.
        It must be a positive integer between 0-9999. This is combined with the
        first four characters of the submitting user ID to create a specific console name.
        If omitted, the default value is 0.

    parameters : str, optional
        Additional operator command parameters.

    preserve : bool, optional
        Preserve the case of the `command` argument. The command is
        converted to uppercase by default. This is useful for operator commands
        that specify a case-sensitive z/OS UNIX path.

    terse : bool, optional
        Provide terse output. Only the command response is returned.

    verbose : bool, optional
        Enable verbose messages (best used with _function if available and read
        from ZOAUResponse.stderr_output)

    wait : bool, optional
        If true, the `opercmd` utility waits the full amount of time specified by
        the `timeout` argument.  If false, the utility returns as soon as
        a command response is received.

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls.
    """
    console_arg = "console"
    preserve_arg = "preserve"
    terse_arg = "terse"
    wait_arg = "wait"

    timeout_max = 2147483600
    timeout_min = 0

    cons_suffix_min = 0
    cons_suffix_max = 9999

    if not isinstance(timeout, int):
        raise TypeError("timeout must be an integer.")
    if timeout < timeout_min:
        raise ValueError("timeout must be a positive number.")
    if timeout > timeout_max:
        raise ValueError(f"timeout must be no more than {timeout_max}.")

    command = clean_shell_input(command)

    options = f"-T {timeout} "

    options += parse_universal_arguments(**kwargs)
    if terse_arg in kwargs:
        if not isinstance(kwargs.get(terse_arg), bool):
            raise TypeError(f"'{terse_arg}' must be True or False.")
        if kwargs.get(terse_arg):
            options += "-t "

    if preserve_arg in kwargs:
        if not isinstance(kwargs.get(preserve_arg), bool):
            raise TypeError(f"'{preserve_arg}' must be True or False.")
        if kwargs.get(preserve_arg):
            options += "-p "

    if wait_arg in kwargs:
        if not isinstance(kwargs.get(wait_arg), bool):
            raise TypeError(f"{wait_arg} must be True or False.")
        if kwargs.get(wait_arg):
            options += "-w "

    if console_arg in kwargs:
        if not isinstance(kwargs.get(console_arg), int):
            raise TypeError("'console' must be an integer.")

        console_suffix = kwargs.get(console_arg, 0)
        if console_suffix < cons_suffix_min or console_suffix > cons_suffix_max:
            raise ValueError(
                f"'console' must be between {cons_suffix_min} and {cons_suffix_max}.")

        options += f"-c {console_suffix}  "

    if json:
        options += "-j "

    # Options processing is finished.
    options += "-- "

    if 'parameters' in kwargs:
        parameters = kwargs.get('parameters')
    else:
        parameters = ""

    options += f"\"{command} {parameters}\""

    logger.debug("ZOAU_CORE Call: opercmd %s", options)
    response = call_zoau_library("opercmd", options)

    zoau_response = ZOAUResponse.from_dict(response)

    if zoau_response.rc != 0:
        raise ZOAUException(zoau_response)

    return ZOAUResponse.from_dict(response)
