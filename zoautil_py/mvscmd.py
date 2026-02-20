import logging
from zoautil_py.common import clean_shell_input as clean_shell_input, parse_universal_arguments as parse_universal_arguments
from zoautil_py.core import call_zoau_library as call_zoau_library
from zoautil_py.ztypes import DDStatement as DDStatement, ZOAUResponse as ZOAUResponse

logger: logging.Logger

def execute(pgm: str, pgm_args: str | None = None, dds: list[DDStatement] | None = None, json: bool = False, **kwargs) -> ZOAUResponse:
    '''
    Execute an MVS Program

    Returns
    -------
    ZOAUResponse

    Parameters
    ----------
    pgm : str
        Name of the program to run.

    pgm_args : str
        Additional arguments to pass as the PARM parameter

    dds : list[DDStatement]
        List of DD statements to pass with command

    json: bool, optional
        Get JSON output from mvscmd.

        When enabled, the output is a JSON string with this structure:
        {
            "data": {
                "program": <string>,
                "STEPLIB": <string>,
                "DDs": [
                    {
                        "type": <string>,
                        "ddname": <string>,
                        "dsname": <string>,
                        "name": <string>,
                        "path": <string>,
                        "status": <string>,
                        "retained": <boolean>,
                        "list": [
                            {
                                "type": <string>,
                                "ddname": <string>,
                                "dsname": <string>,
                                "path": <string>,
                                "name": <string>,
                                "status": <string>,
                            },
                            ...
                        ],
                    },
                    ...
                ]
            },
            "program": <string>,
            "options": <string>,
            "rc": <string>
        }

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug : bool, optional
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    tmphlq : str
        Use an alternative high-level qualifier (HLQ) for temporary dataset
        names.

    verbose : bool, optional
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    '''
def execute_authorized(pgm: str, pgm_args: str | None = None, dds: list[DDStatement] | None = None, json: bool = False, **kwargs) -> ZOAUResponse:
    '''
    Execute an authorized MVS Program

    Returns
    -------
    ZOAUResponse

    Parameters
    ----------
    pgm : str
        Name of the program to run

    pgm_args : str
        Additional arguments to pass as the PARM parameter

    dds : list[DDStatement], optional
        List of DD statements to pass with command

    json: bool, optional
        Get JSON output from mvscmd.

        When enabled, the output is a JSON string with this structure:
        {
            "data": {
                "program": <string>,
                "STEPLIB": <string>,
                "DDs": [
                    {
                        "type": <string>,
                        "ddname": <string>,
                        "dsname": <string>,
                        "name": <string>,
                        "path": <string>,
                        "status": <string>,
                        "retained": <boolean>,
                        "list": [
                            {
                                "type": <string>,
                                "ddname": <string>,
                                "dsname": <string>,
                                "path": <string>,
                                "name": <string>,
                                "status": <string>,
                            },
                            ...
                        ],
                    },
                    ...
                ]
            },
            "program": <string>,
            "options": <string>,
            "rc": <string>
        }

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug : bool, optional
        Enable debug messages (best used with _function if available and read from ZOAUResponse.stderr_output)

    tmphlq : str
        Use an alternative high-level qualifier (HLQ) for temporary dataset
        names.

    verbose : bool, optional
        Enable verbose messages (best used with _function if available and read from ZOAUResponse.stderr_output)
    '''
