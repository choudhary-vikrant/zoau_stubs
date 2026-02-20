import logging
from zoautil_py.common import clean_shell_input as clean_shell_input, parse_universal_arguments as parse_universal_arguments
from zoautil_py.core import call_zoau_library as call_zoau_library
from zoautil_py.exceptions import ZOAUException as ZOAUException
from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

logger: logging.Logger

def execute(command: str, timeout: int = 0, json: bool = False, **kwargs) -> ZOAUResponse:
    '''
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
    '''
