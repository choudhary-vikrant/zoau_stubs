# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2023
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------

import logging
from typing import Optional

from zoautil_py.common import parse_universal_arguments, clean_shell_input
from zoautil_py.core import (  # pylint: disable=import-error, no-name-in-module
    call_zoau_library,
)
from zoautil_py.ztypes import ZOAUResponse, DDStatement

logger: logging.Logger
logger = logging.getLogger(__name__)


def execute(
    pgm: str,
    pgm_args: Optional[str] = None,
    dds: Optional[list[DDStatement]] = None,
    json: bool = False,
    **kwargs,
) -> ZOAUResponse:
    """
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
    """
    options = ""
    options += parse_universal_arguments(**kwargs)

    if json:
        options += "-j "

    if "tmphlq" in kwargs:
        options += f"-Q=\"{kwargs.get('tmphlq')}\" "

    options += f"--pgm={pgm} "

    if pgm_args:
        pgm_args = clean_shell_input(pgm_args)
        options += f'--args="{pgm_args}" '

    if dds is not None:
        dds_string = ""
        for dd in dds:
            dds_string += " " + dd.get_mvscmd_string()
        options += dds_string

    logger.debug("ZOAU_CORE call: mvscmd %s", options)
    response = call_zoau_library("mvscmd", options)
    return ZOAUResponse.from_dict(response)


def execute_authorized(
    pgm: str,
    pgm_args: Optional[str] = None,
    dds: Optional[list[DDStatement]] = None,
    json: bool = False,
    **kwargs,
) -> ZOAUResponse:
    """
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
    """
    options = ""
    options += parse_universal_arguments(**kwargs)

    if json:
        options += "-j "

    if "tmphlq" in kwargs:
        options += f"-Q=\"{kwargs.get('tmphlq')}\" "

    options += f"--pgm={pgm} "

    if pgm_args:
        pgm_args = clean_shell_input(pgm_args)
        options += f'--args="{pgm_args}" '

    if dds is not None:
        dds_string = ""
        for dd in dds:
            dds_string += " " + dd.get_mvscmd_string()
        options += dds_string

    logger.debug("ZOAU_CORE call: mvscmdauth %s", options)
    response = call_zoau_library("mvscmdauth", options)

    return ZOAUResponse.from_dict(response)
