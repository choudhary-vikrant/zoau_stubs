# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2023
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
ZOAU Python functions to manage z/OS Jobs.
"""
import logging
import time
import warnings
from datetime import datetime
from typing import List, Union

from zoautil_py.common import (cast_int_optional, clean_dataset_name,
                               clean_shell_input, parse_universal_arguments,
                               parse_unknown, zoau_json_load)
from zoautil_py.core import call_zoau_library  # pylint: disable=import-error, no-name-in-module #type: ignore
from zoautil_py.core_return_codes import DDLSReturnCodes
from zoautil_py.exceptions import (DDQueryException, JobCancelConfirmException,
                                   JobCancelException, JobFetchException,
                                   JobPurgeConfirmException, JobPurgeException,
                                   JobSubmitException)
from zoautil_py.ztypes import ZOAUResponse

logger: logging.Logger
logger = logging.getLogger(__name__)

# Keep owner, name, id, status, and ccode in the first 5, because they match the jls output
BASIC_JOB_FIELDS = [
    "owner",
    "name",
    "id",
    "status",
    "ccode",
    "jobclass",
    "serviceclass",
    "priority",
    "asid",
    "creationdate",
    "creationtime",
    "queueposition",
    "jobtype",
    "executiontime",
    "executionseconds",
    "system",
    "subsystem",
    "onode",
    "xnode",
    "membname",
]
DEFAULT_JOB_FIELDS = BASIC_JOB_FIELDS[0:5]
EXTENDED_JOB_FIELDS = [
    "programname",
    "cputime",
    "srbtime",
]


class Job:
    """
    Representation of z/OS Job

    Attributes
    ----------
    job_id : str
        Job ID

    name : str
        Job Name

    job_class : str
        Job class

    asid : int
        The Address Space Identifier (ASID) is a unique descriptor for the job address space

    priority : int
        Priority of job

    queue_position: int
        Position of job on class queue or phase queue

    owner : str, None
        Job Owner

    program_name: str, None
        Program name for the job's last completed step

    return_code : str, None
        Last known return code of job

    status : str, None
        Last known status of job

    service_class : str, None
        WLM service class

    creation_datetime: datetime, None
        Datetime object with the job's input start date and time

    job_type : str, None
        Type of address space.

    execution_time : str, None
        Elapsed execution time in format "[ddd-]HH:MM:SS".
        If the job did not execute the value is None

    execution_seconds : int, None
        Total elapsed execution time in seconds.
        If the job did not execute the value is None

    system: str, None
        MVS execution system.

    subsystem: str, None
        Subsystem that executed the job.

    origin_node: str, None
        Origin node (node of submittal).

    execution_node: str, None
        Execution node.

    member_name: str, None
        Execution JES member name.

    cpu_time: int
        Sum of the CPU time used by each job step, in microseconds.

    srb_time: int
        Sum of the service request block (SRB) time for each job step, in microseconds.

    purged: bool
        Tracks if job was purged. Exclusive to the ZOAU API.
    """

    job_id: str  # TODO: underscore disclaimer
    name: str
    job_class: str
    asid: int
    priority: int
    queue_position: int
    owner: Union[str, None]
    program_name: Union[str, None]
    return_code: Union[str, None]
    status: Union[str, None]
    service_class: Union[str, None]
    creation_datetime: Union[datetime, None]
    job_type: Union[str, None]
    execution_time: Union[str, None]
    execution_seconds: Union[int, None]
    system: Union[str, None]
    subsystem: Union[str, None]
    origin_node: Union[str, None]
    execution_node: Union[str, None]
    member_name: Union[str, None]
    cpu_time: int
    srb_time: int
    purged: bool

    def __init__(
        self,
        job_id: str,
        name: str,
        job_class: str,
        asid: Union[str, int],
        priority: Union[str, int],
        queue_position: Union[str, int],
        owner: Union[str, None] = None,
        program_name: Union[str, None] = None,
        return_code: Union[str, None] = None,
        status: Union[str, None] = None,
        service_class: Union[str, None] = None,
        creation_datetime: Union[str, datetime, None] = None,
        job_type: Union[str, None] = None,
        execution_time: Union[str, None] = None,
        execution_seconds: Union[str, None] = None,
        system: Union[str, None] = None,
        subsystem: Union[str, None] = None,
        origin_node: Union[str, None] = None,
        execution_node: Union[str, None] = None,
        member_name: Union[str, None] = None,
        cpu_time: Union[str, int, None] = None,
        srb_time: Union[str, int, None] = None,
        purged: bool = False,
    ):
        # Parameter sanitization
        ## str
        if not isinstance(job_id, str):
            raise TypeError("job_id parameter must be a string")
        if not isinstance(name, str):
            raise TypeError("name parameter must be a string")
        if not isinstance(job_class, str):
            raise TypeError("job_class parameter must be a string")
        ## int
        if not isinstance(asid, (str, int)):
            raise TypeError("asid parameter must be a int")
        if not isinstance(priority, (str, int)):
            raise TypeError("priority parameter must be a int")
        if not isinstance(queue_position, (str, int)):
            raise TypeError("queue_position parameter must be a int")
        if cpu_time is not None and not isinstance(cpu_time, (str, int)):
            raise TypeError("cpu_time parameter must be a int or str")
        if srb_time is not None and not isinstance(srb_time, (str, int)):
            raise TypeError("srb_time parameter must be a int or str")
        ## Optional str
        if owner is not None and not isinstance(owner, str):
            raise TypeError("queue_position parameter must be a str or None")
        if program_name is not None and not isinstance(program_name, str):
            raise TypeError("program_name parameter must be a str or None")
        if return_code is not None and not isinstance(return_code, str):
            raise TypeError("return_code parameter must be a str or None")
        if status is not None and not isinstance(status, str):
            raise TypeError("status parameter must be a str or None")
        if service_class is not None and not isinstance(service_class, str):
            raise TypeError("service_class parameter must be a str or None")
        if job_type is not None and not isinstance(job_type, str):
            raise TypeError("job_type parameter must be a str or None")
        if execution_time is not None and not isinstance(execution_time, str):
            raise TypeError("execution_time parameter must be a str or None")
        if execution_seconds is not None and not isinstance(execution_seconds, str):
            raise TypeError("execution_seconds parameter must be a str or None")
        if system is not None and not isinstance(system, str):
            raise TypeError("system parameter must be a str or None")
        if subsystem is not None and not isinstance(subsystem, str):
            raise TypeError("subsystem parameter must be a str or None")
        if origin_node is not None and not isinstance(origin_node, str):
            raise TypeError("origin_node parameter must be a str or None")
        if execution_node is not None and not isinstance(execution_node, str):
            raise TypeError("execution_node parameter must be a str or None")
        if member_name is not None and not isinstance(member_name, str):
            raise TypeError("member_name parameter must be a str or None")
        ## bool
        if not isinstance(purged, bool):
            raise TypeError("purged parameter must be a boolean")
        ## Datetime
        if creation_datetime is not None and not isinstance(
            creation_datetime, (str, datetime)
        ):
            raise TypeError("creation_date must be a string or datetime")

        # Attribute declaration
        ## str
        self.job_id = job_id
        self.name = name
        self.job_class = job_class
        ## int
        self.asid = int(asid)
        self.priority = int(priority)
        self.queue_position = int(queue_position)
        ## optional int
        # cputime and srbtime can have unknown value '?' that must be turned into a 0
        casted_value = cast_int_optional(cpu_time)
        self.cpu_time = casted_value if casted_value is not None else 0
        casted_value = cast_int_optional(srb_time)
        self.srb_time = casted_value if casted_value is not None else 0
        self.execution_seconds = cast_int_optional(execution_seconds)
        ## optional str
        self.owner = parse_unknown(owner)
        self.program_name = parse_unknown(program_name)
        self.return_code = parse_unknown(return_code)
        self.status = parse_unknown(status)
        self.service_class = parse_unknown(service_class)
        self.job_type = parse_unknown(job_type)
        self.execution_time = parse_unknown(execution_time)
        self.system = parse_unknown(system)
        self.subsystem = parse_unknown(subsystem)
        self.origin_node = parse_unknown(origin_node)
        self.execution_node = parse_unknown(execution_node)
        self.member_name = parse_unknown(member_name)
        ## bool
        self.purged = purged
        ##datetime
        if creation_datetime is None:
            self.creation_datetime = creation_datetime
        if isinstance(creation_datetime, datetime):
            self.creation_datetime = creation_datetime
        elif isinstance(creation_datetime, str):
            try:
                self.creation_datetime = datetime.strptime(
                    creation_datetime, "%Y/%m/%d %H:%M:%S"
                )
            except ValueError:
                logger.debug(
                    "creation_datetime of job: %s : %s is invalid. Defaulting the attribute to None",
                    job_id,
                    creation_datetime,
                )
                self.creation_datetime = None

    @classmethod
    def from_core_json(cls, job_as_json: dict):
        """Build a `Job` object from a ZOAU core dictionary.
        Translates the core field names to the pythonic names in the `Job` class.

        Parameters
        ----------
        job_as_json : dict
            Dictionary from the "data" object in the ZOAU core JSON response.

        Returns
        -------
        Job
            Representation of z/OS Job
        """
        # Parameter translation
        job_as_json["job_id"] = job_as_json.pop("id")
        job_as_json["return_code"] = job_as_json.pop("ccode")
        job_as_json["service_class"] = job_as_json.pop("serviceclass", None)
        job_as_json["program_name"] = job_as_json.pop("programname", None)
        job_as_json["job_class"] = job_as_json.pop("jobclass", None)
        job_as_json["queue_position"] = job_as_json.pop("queueposition", None)
        job_as_json["job_type"] = job_as_json.pop("jobtype", None)
        job_as_json["execution_time"] = job_as_json.pop("executiontime", None)
        job_as_json["execution_seconds"] = job_as_json.pop("executionseconds", None)
        job_as_json["system"] = job_as_json.pop("system", None)
        job_as_json["subsystem"] = job_as_json.pop("subsystem", None)
        job_as_json["origin_node"] = job_as_json.pop("onode", None)
        job_as_json["execution_node"] = job_as_json.pop("xnode", None)
        job_as_json["member_name"] = job_as_json.pop("membname", None)
        job_as_json["cpu_time"] = job_as_json.pop("cputime", None)
        job_as_json["srb_time"] = job_as_json.pop("srbtime", None)

        # creationdate and creationtime to creation_datetime
        if (
            not job_as_json.get("creationdate") is None
            and not job_as_json.get("creationtime") is None
        ):
            job_as_json["creation_datetime"] = (
                f"{job_as_json.pop('creationdate')} {job_as_json.pop('creationtime')}"
            )
        else:
            job_as_json["creation_datetime"] = None

        # Job Creation
        try:
            populated_job = cls(**job_as_json)
        except KeyError as key_error:
            raise KeyError(
                f"Error while trying to parse the following job JSON: {job_as_json}"
            ) from key_error
        return populated_job

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return f"zoautil_py.jobs.Job object with ID:{self.job_id}"

    def cancel(self, purge_job: bool = False, confirm_timeout: int = 0):
        """Queue job for cancellation"""
        if self.purged:
            warnings.warn(
                f"Job {self.job_id} is already labeled as purged. Current attributes are preserved.",
                RuntimeWarning,
            )
            return None

        cancel(job_id=self.job_id, purge_job=purge_job, confirm_timeout=confirm_timeout)
        self.refresh()

    def purge(self, confirm_timeout: int = 0):
        """Queue job for purge"""
        if self.purged:
            warnings.warn(
                f"Job {self.job_id} has been purged already. Current attributes are preserved.",
                RuntimeWarning,
            )
            return
        purge(self.job_id, confirm_timeout=confirm_timeout)
        self.purged = True  # Safe because failing to purge raises exceptions.

    def refresh(self):
        """Refresh job information"""
        refresh(self)

    def wait(self, seconds_per_loop: float = 1.0, max_loops: Union[int,None] = None):
        """Wait until job stops running.

        Parameters
        ----------
        seconds_per_loop : float, optional
            The number of seconds to wait between each check. Defaults to 1.0.

        max_loops : int, optional:
            The maximum number of loops to wait before raising a TimeoutError. Defaults to None.

        Raises
        ------
        TypeError:
            If seconds_per_loop is not a float or timeout is not an integer.

        ValueError:
            If seconds_per_loop is not a positive float or timeout is not a positive integer.

        TimeoutError:
            If the timeout is reached before the job is no longer running."""
        # Type Validation
        if not isinstance(seconds_per_loop, float):
            raise TypeError("seconds_per_loop must be a float")
        if max_loops and not isinstance(max_loops, int):
            raise TypeError("max_loops must be an integer")
        # Value Validation
        if seconds_per_loop <= 0:
            raise ValueError("seconds_per_loop must be a positive float")
        if max_loops and max_loops <= 0:
            raise ValueError("max_loops must be a positive integer")
        # Purge Validation
        if self.purged:
            warnings.warn(
                f"Can't wait for purged Job {self.job_id}. Current attributes are preserved.",
                RuntimeWarning,
            )
            return
        # Synchronous wait
        timeout = max_loops is not None
        while self.status in ('AC', 'HOLD'):
            time.sleep(seconds_per_loop)
            self.refresh()
            if timeout:
                if max_loops < 1:
                    raise TimeoutError(f"{self.job_id} wait() timeout reached")
                max_loops = max_loops - 1

    def fetch_extended_fields(self):
        """Fetch the extended attributes"""
        fetch_extended_fields(self)


def _jls_call(
    job_id: Union[str, None] = None,
    job_owner: Union[str, None] = None,
    job_name: Union[str, None] = None,
    fetch_max_retries: int = 2,
    include_extended=False,
    manual_field_select=False,
    **kwargs,
) -> ZOAUResponse:
    """Builds a command string and calls zoau core (jls)"""
    # Manual expects -o in options, from kwargs

    if job_id:
        job_id = clean_shell_input(job_id)
    elif job_owner:
        job_owner = clean_shell_input(job_owner)

    command = ""
    command += parse_universal_arguments(**kwargs)
    command += "-j "

    if not manual_field_select:
        command += "-o "
        included_fields = ",".join(BASIC_JOB_FIELDS)
        if include_extended:
            included_fields += ","
            included_fields += ",".join(EXTENDED_JOB_FIELDS)
        command += included_fields

    command += " -- "

    job_owner = "" if job_owner is None else job_owner
    job_name = "" if job_name is None else job_name

    # If job_id exists, or if it's the * (any) wildcard,
    # use the other two arguments to search.
    if job_id and job_id != "*":
        command += f"'{job_id}'"
    elif job_owner or job_name:
        command += f"'/{job_owner}/{job_name}'"

    logger.debug("ZOAU_CORE call: jls %s", command)

    retry_counter = 0
    while retry_counter < fetch_max_retries:
        zoau_response = ZOAUResponse.from_dict(call_zoau_library("jls", command))
        if zoau_response.rc == 0:
            return zoau_response
        time.sleep(1)
        retry_counter += 1

    raise JobFetchException(zoau_response)


def _submit(source: str, is_unix: bool, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls zoau core (jsub)"""
    source = clean_dataset_name(source)
    options = ""
    if is_unix:
        options += "-f "
    options += parse_universal_arguments(**kwargs)
    options += "-- "
    options += f'"{source}"'

    logger.debug("ZOAU_CORE call: jsub %s", options)
    response = call_zoau_library("jsub", options)
    return ZOAUResponse.from_dict(response)


def submit_return_job_id(source: str, is_unix: bool = False, **kwargs) -> str:
    """
    Submit a z/OS JCL Job from a z/OS UNIX file or dataset, returns the submitted job's id

    Returns
    -------
    str
        Submitted job's ID.

    Parameters
    ----------
    source : str
        Fully qualified dataset name or path to the z/OS UNIX file to submit.

    is_unix : bool
        `True` if source refers to a z/OS UNIX file.
        `False` if it refers to a dataset.

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug: bool
        Enable debug messages (only for exceptions)

    verbose: bool
        Enable verbose output (only for exceptions)

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls

    JobSubmitException : (message:str, response:ZOAUResponse)
        Errors while trying to submit a job
    """
    logger.debug("submit_async function call")
    logger.debug("file name: %s", source)
    logger.debug("is_unix: %s", is_unix)
    logger.debug("kwargs: %s", kwargs)

    # Parameter sanitization
    if not isinstance(source, str):
        raise TypeError("file_name parameter must be a string")
    if not isinstance(is_unix, bool):
        raise TypeError("is_unix parameter must be a bool")

    # job submit command
    zoau_response = _submit(source, is_unix, **kwargs)

    if zoau_response.rc != 0:
        raise JobSubmitException(zoau_response)

    return zoau_response.stdout_response.strip()


def submit(source: str, is_unix: bool = False, **kwargs) -> Job:
    """
    Submit a z/OS JCL Job from a z/OS UNIX file or dataset, returns Job object.

    Note
    ----
    Locks I/O until a job object can be constructed.

    Returns
    -------
    Job
        Job object representing the submitted dataset/unix file.

    Parameters
    ----------
    source : str
        Fully qualified dataset name or path to the z/OS UNIX file to submit.

    is_unix : bool
        `True` if source refers to a UNIX file.
        `False` if it refers to a dataset.

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    fetch_max_retries: int
        Maximum number of times to query the job for information. (1 second delay per retry)

    debug: bool
        Enable debug messages (only for exceptions)

    verbose: bool
        Enable verbose output (only for exceptions)

    Raises
    ------
    JobFetchException : (message:str, response:ZOAUResponse)
        An error occurred when trying to fetch the job.

    JobSubmitException : (message:str, response:ZOAUResponse)
        Errors during job submission
    """
    logger.debug("submit job function call")
    logger.debug("file name: %s", source)
    logger.debug("is_unix: %s", is_unix)
    logger.debug("kwargs: %s", kwargs)

    # Additional sanitization on submit_id().

    job_id = submit_return_job_id(source, is_unix, **kwargs)
    logger.debug("Job Submitted. ID: %s", job_id)

    return fetch(job_id, **kwargs)


def _jcan_call(job_id: str, purge_job: bool, **kwargs) -> ZOAUResponse:
    """
    Builds a command string and calls zoau core (jcan)

    Notes
    -----
    If no job_id is provided, a wildcard of "*" will be used.
    """
    options = ""
    options += parse_universal_arguments(**kwargs)

    if purge_job:
        options += "P "
    else:
        options += "C "

    job_name = kwargs.get("job_name", "*")

    options += f'"{job_name}" "{job_id}"'

    logger.debug("ZOAU_CORE call: jcan %s", options)
    response = call_zoau_library("jcan", options)

    return ZOAUResponse.from_dict(response)


def cancel(
    job_id: str, purge_job: bool = False, confirm_timeout: int = 0, **kwargs
) -> None:
    """
    Cancel (or purge) a z/OS Job.
    Purge will attempt to verify the job is properly removed based on a timeout.
    Disabled by default.

    Returns
    -------
    None

    Parameters
    ----------
    job_id : str
        The Job ID to target.

    confirm_timeout: int
        Maximum time (in seconds) to wait for the job to be cancelled or purged.

    kwargs: dict, optional
        Additional parameters (see other parameters).

    Other Parameters
    ----------------
    job_name : str, optional
        Job name to specify (needed for some systems).

    debug: bool
        Enable debug messages (only for exceptions)

    verbose: bool
        Enable verbose output (only for exceptions)

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls.
    JobCancelException: (message:str, response:ZOAUResponse)
        Job cancelling errors, see message for details
    """
    logger.debug("cancel job function call")
    logger.debug("job_id: %s", job_id)
    logger.debug("purge_job: %s", purge_job)
    logger.debug("max_timeout: %s", confirm_timeout)
    logger.debug("kwargs: %s", kwargs)

    if not isinstance(job_id, str):
        raise TypeError("job_id parameter must be a string")
    if not isinstance(confirm_timeout, int):
        raise TypeError("max_timeout parameter must be a int")
    if not isinstance(purge_job, bool):
        raise TypeError("purge parameter must be a boolean")

    fetched_job = fetch(job_id=job_id)
    if fetched_job.status == "CANCELED":
        warnings.warn(f"Cannot cancel job {job_id}, job is already cancelled.")
        return None
    if fetched_job.status != "AC":
        warnings.warn(
            f"Cannot cancel job {job_id}, job is not running. Current status {fetched_job.status}"
        )
        return None

    response = _jcan_call(job_id, purge_job, **kwargs)

    if response.rc != 0:
        raise JobCancelException(response)
    # Raise specific exception due to authorization

    if confirm_timeout == 0:
        return None

    if purge_job:
        for _ in range(confirm_timeout):
            if not exists(job_id):
                return None
            time.sleep(1)
        raise JobPurgeConfirmException(
            f"Couldn't confirm purging of job {job_id} within the timeout limits."
        )

    fetched_job = fetch(job_id)
    for _ in range(confirm_timeout):
        if fetched_job.status == "CANCELED":
            return None
        if fetched_job.status == "CC":
            warnings.warn(
                f"Cannot cancel job {job_id}, job reached a finished state before cancelling. Current status {fetched_job.status}"
            )
            return None
        time.sleep(1)
        fetched_job = fetch(job_id=job_id)
    raise JobCancelConfirmException(
        f"Could not confirm cancellation of job {job_id} within the timeout limits. Current status: {fetched_job.status}"
    )


def purge(job_id: str, confirm_timeout: int = 0, **kwargs) -> None:
    """
    Purge a z/OS Job.
    Purge will attempt to verify the job is properly removed based on a timeout. Disabled by default.

    Returns
    -------
    None

    Parameters
    ----------
    job_id : str
        The Job ID to target.

    max_timeout: int
        Max time (in seconds) to wait for the job to be cancelled.

    kwargs: dict, optional
        Additional parameters (see other parameters).

    Other Parameters
    ----------------
    job_name : str, optional
        Job name to specify (needed for some systems).

    debug: bool
        Enable debug messages (only for exceptions)

    verbose: bool
        Enable verbose output (only for exceptions)

    Raises
    ------
    JobPurgeException: (message:str, response:ZOAUResponse)
        Job purging errors, see message for details
    """
    logger.debug("Purge job function call")
    logger.debug("job_id: %s", job_id)
    logger.debug("max_timeout: %s", confirm_timeout)
    logger.debug("kwargs: %s", kwargs)

    if not isinstance(job_id, str):
        raise TypeError("job_id parameter must be a string")
    if not isinstance(confirm_timeout, int):
        raise TypeError("max_timeout parameter must be a int")

    response = _jcan_call(job_id, purge_job=True, **kwargs)

    if response.rc != 0:
        raise JobPurgeException(response)
    # Special exception for authorization

    if confirm_timeout == 0:
        return None

    for _ in range(confirm_timeout):
        if not exists(job_id):
            return None
        time.sleep(1)
    raise JobPurgeConfirmException(
        f"Couldn't confirm purging of job {job_id} within the timeout limits."
    )


def _list_dds(job_id: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls zoau core (ddls)"""

    options = ""
    options += parse_universal_arguments(**kwargs)

    owner = kwargs.get("owner", "")
    prefix = kwargs.get("prefix", "")

    if "sysin" in kwargs and kwargs.get("sysin"):
        options += "-i "

    job_id = clean_shell_input(job_id)
    owner = clean_shell_input(owner)
    prefix = clean_shell_input(prefix)

    options += "-j "
    options += f"{job_id} '/{owner}/{prefix}'"

    logger.debug("ZOAU_CORE call: ddls %s", options)
    response = call_zoau_library("ddls", options)

    return ZOAUResponse.from_dict(response)


def list_dds(job_id: str, **kwargs) -> list[dict]:
    """List DDs of a z/OS Job

    Returns
    -------
    list[dict]
        List of Data Definitions (DD) as dictionaries

        - "dd_name" : str
        - "step_name : str
        - "procstep : str
        - "record_format" : str
        - "record_length" : int
        - "records" : int
        - "dsid" : int

    list[]
        Empty list if no DDs are present

    Parameters
    ----------
    job_id : str
        Job ID to pull DDs from

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    owner : str, optional
        ISFOWNER parameter (needed for some systems)

    prefix : str, optional
        ISFPREFIX parameter (needed for some systems)

    sysin : bool, optional
        When True, the list will include SYSIN DDs
        Default is False

    Raises
    ------
    DDQueryException
        - BGYSC3505E : If the job is not ready for DD querying yet
        - BGYSC3506E : If the job is at a transmission phase
    """
    logger.debug("list_dds job function call")
    logger.debug("job_id: %s", job_id)
    logger.debug("kwargs: %s", kwargs)

    response = _list_dds(job_id, **kwargs)

    if (
        response.rc
        in (DDLSReturnCodes.JOB_NOT_READY, DDLSReturnCodes.JOB_IN_TRANSMISSION)
        or not response.stdout_response
    ):
        raise DDQueryException(response)

    data_json, meta_json = zoau_json_load(response.stdout_response)
    logger.debug("Full JSON Response: %s \n %s", data_json, meta_json)

    if meta_json["dds_found"] == 0:
        return []

    return data_json["dd_list"]


def _read_output(job_id: str, stepname: str, dd_name: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls zoau core (pjdd)"""
    job_id = clean_shell_input(job_id)
    stepname = clean_shell_input(stepname)
    dd_name = clean_shell_input(dd_name)

    procstep = clean_shell_input(kwargs.get("procstep", ""))

    # TODO: Review these unused variables.
    # if 'owner' in kwargs:
    #     owner = escape_quotes(kwargs.get('owner'))
    # else:
    #     owner = ""

    # if 'prefix' in kwargs:
    #     prefix = escape_quotes(kwargs.get('prefix'))
    # else:
    #     prefix = ""

    if "dataset_id" in kwargs:
        dataset_id = clean_shell_input(kwargs["dataset_id"])
        stepname = ""
        procstep = ""
        dd_name = ""
    else:
        dataset_id = ""

    options = ""
    options += parse_universal_arguments(**kwargs)
    options += f"-j {job_id} {stepname} {procstep} {dd_name} {dataset_id}"

    logger.debug("ZOAU_CORE call: pjdd %s", options)
    response = call_zoau_library("pjdd", options)

    return ZOAUResponse.from_dict(response)


def read_output(job_id: str, stepname: str = "'*'", dd_name: str = "", **kwargs) -> str:
    """
    Read output from a z/OS Job DD

    Returns
    -------
    str
       Records read from the DDs

    Parameters
    ----------
    job_id : str
        Job ID to pull DDs from

    stepname : str
        Step name to filter DDs

    dd_name : str
        Name of the DD to read

    kwargs : dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    dataset_id : str, int, optional
        ID for the DD to read.
        If provided, any other filters will be ignored

    owner : str, optional
        ISFOWNER parameter (needed for some systems)

    prefix : str, optional
        ISFPREFIX parameter (needed for some systems)

    procstep : str, optional
        For jobs with multiple steps per DD
    """
    logger.debug("read_output job function call")
    logger.debug("job_id: %s", job_id)
    logger.debug("stepname: %s", stepname)
    logger.debug("dataset: %s", dd_name)
    logger.debug("kwargs: %s", kwargs)

    zoau_response = _read_output(job_id, stepname, dd_name, **kwargs)

    if zoau_response.rc != 0:
        raise JobFetchException(zoau_response)

    data_json, meta_json = zoau_json_load(zoau_response.stdout_response)
    logger.debug("Full JSON Response: %s \n %s", data_json, meta_json)

    if meta_json["content_length"] == 0:
        return ""

    content = data_json["content"].rstrip("\\n").replace("\\n", "\n")

    return content


def fetch_multiple_as_json(
    job_id: Union[str, None] = None,
    job_owner: Union[str, None] = None,
    job_name: Union[str, None] = None,
    included_fields: Union[List[str], None] = None,
    **kwargs,
) -> dict:
    """Fetch jobs as a JSON object. Allows fetching only specific job attributes.
    The job ID is always added to the included fields.

    Returns
    -------
    dict
        Loaded JSON response as an addressable JSON

    Parameters
    ----------
    job_id: str
        ID of the job to list. Should be used with wildcards.
    job_owner: str
        Owner of the jobs to list.
    job_name: str
        Name of the jobs to list.
    included_fields : [str], optional, defaults to: ['owner', 'name', 'id', 'status', 'ccode']
        List of field names to retrieve. Uses the core field names.

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    fetch_max_retries: int, defaults to 2
        Maximum number of times to query the job for information. (1 second delay per retry)

    Available Fields
    ----------------
    - owner
    - name
    - id
    - status
    - ccode
    - jobclass
    - serviceclass
    - priority
    - asid
    - creationdate
    - creationtime
    - queueposition
    - programname
    - jobtype
    - executiontime
    - executionseconds
    - system
    - subsystem
    - onode
    - xnode
    - membname
    - cputime
    - srbtime

    Notes
    -----
    Filter names do NOT match up with Job class attribute names.
    """
    logger.debug("fetch_multiple_as_string function call")
    logger.debug("job_id: %s", job_id)
    logger.debug("job_owner: %s", job_owner)
    logger.debug("job_name: %s", job_name)
    logger.debug("included_fields: %s", included_fields)

    if included_fields is None:
        included_fields = DEFAULT_JOB_FIELDS
        zoau_response = _jls_call(
            job_id=job_id,
            job_owner=job_owner,
            job_name=job_name,
            manual_field_select=True,
            **kwargs,
        )
        if zoau_response.rc != 0:
            raise JobFetchException(zoau_response)
        json_data, json_metadata = zoau_json_load(zoau_response.stdout_response)
        logger.debug("Full JSON Response: %s \n %s", json_data, json_metadata)

        return json_data

    if not all(isinstance(field, str) for field in included_fields):
        raise TypeError(
            f"Every field in included_fields: {included_fields} must be of type str."
        )

    if "id" not in included_fields:
        included_fields.append("id")

    fields_string = "-o" + ",".join(included_fields)
    zoau_response = _jls_call(
        job_id=job_id,
        job_owner=job_owner,
        job_name=job_name,
        options=fields_string,
        manual_field_select=True,
        **kwargs,
    )

    if zoau_response.rc != 0:
        raise JobFetchException(zoau_response)

    json_data, json_metadata = zoau_json_load(zoau_response.stdout_response)
    logger.debug("Full JSON Response: %s \n %s", json_data, json_metadata)

    return json_data


def fetch_multiple(
    job_id: Union[str, None] = None,
    job_owner: Union[str, None] = None,
    job_name: Union[str, None] = None,
    include_extended: bool = False,
    **kwargs,
) -> list[Job]:
    """
    Lists Jobs on the system

    Returns
    -------
    list[Job]
        List of jobs obtained from listing (varies based on permissions, parameters)

    list[]
        Empty list if no jobs were found.

    Parameters
    ----------
    job_id: str
        ID of the jobs to list. Use with wildcards.

    job_owner: str
        Owner of the jobs to list.

    job_name: str
        Name of the job to list.

    include_extended: bool
        Includes expensive fields in Job fetch, this includes:
            - program_name

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    fetch_max_retries: int, defaults to 2
        Maximum number of times to query the job for information. (1 second delay per retry)

    debug: bool
        Enable debug messages (only for exceptions)

    verbose: bool
        Enable verbose output (only for exceptions)

    Notes
    -----
    For more control over the fields retrieved, use `fetch_multiple_as_json()`
    """
    logger.debug("listing job function call")
    logger.debug("job_id: %s", job_id)
    logger.debug("job_owner: %s", job_owner)
    logger.debug("job_name: %s", job_name)
    logger.debug("kwargs: %s", kwargs)

    zoau_response = _jls_call(
        job_id=job_id,
        job_owner=job_owner,
        job_name=job_name,
        include_extended=include_extended,
        **kwargs,
    )

    if zoau_response.rc != 0:
        raise JobFetchException(zoau_response)

    if not zoau_response.stdout_response:
        return []

    job_list = []

    response_json, json_metadata = zoau_json_load(zoau_response.stdout_response)
    logger.debug("Full JSON Response: %s \n %s", response_json, json_metadata)

    job_json_list = list(response_json.values())

    for job_as_json in job_json_list:
        job_list.append(Job.from_core_json(job_as_json))

    return job_list


def exists(job_id: str, **kwargs) -> bool:
    """Returns True if job exists

    Parameters
    ----------
    job_id : str
        ID of the job to search for

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    fetch_max_retries: int, defaults to 2
        Maximum number of times to query the job for information. (1 second delay per retry)

    Returns
    -------
    bool
        `True`if job exists, `False` if not
    """
    try:
        fetch(job_id, **kwargs)
    except JobFetchException:
        return False
    return True


def fetch(
    job_id: Union[str, None] = None, include_extended: bool = False, **kwargs
) -> Job:
    """
    Returns single Job object from Job ID.

    Returns
    -------
    job : Job
        Job object matching job_id

    Parameters
    ----------
    job_id : str
        Particular job ID to search for

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    fetch_max_retries: int, defaults to 2
        Maximum number of times to query the job for information. (1 second delay per retry)

    debug: bool
        Enable debug messages (only for exceptions)

    verbose: bool
        Enable verbose output (only for exceptions)

    Raises
    ------
    JobFetchException : (message:str, response:ZOAUResponse)
        An error occurred when trying to fetch the job.

    Notes
    -----
        `fetch_max_retries` can be set to `0` to disable any wait time;
        if so, a try-except block for `JobFetchException` is recommended.

        The job_id parameter can not be an empty string.

        Wildcards are not supported.
    """
    logger.debug("get job function call")
    logger.debug("job_id: %s", job_id)

    # Get kwargs parameters
    fetch_max_retries = kwargs.get("fetch_max_retries", 2)

    # Parameter sanitization
    if job_id is None or not isinstance(job_id, str):
        raise TypeError("job_id parameter should be a string")

    if not isinstance(fetch_max_retries, int):
        raise TypeError("fetch_max_retries parameter must be a int")

    # Invalid queries filtering
    if job_id == "" or job_id.isspace():
        raise ValueError("job_id can't be an empty string")

    if "*" in job_id:
        raise ValueError(
            "Invalid query: '*' wildcard unsupported in a single job fetch"
        )

    # jls call
    zoau_response = _jls_call(
        job_id=job_id, include_extended=include_extended, **kwargs
    )

    if zoau_response.rc != 0:
        raise JobFetchException(zoau_response)

    response_json, meta_json = zoau_json_load(zoau_response.stdout_response)
    logger.debug("Full JSON Response: %s \n %s", response_json, meta_json)

    if int(meta_json["jobs_found"]) != 1:
        raise JobFetchException(zoau_response)

    # Hardcoded indexes to match json schema
    job_json = list(response_json.values())[0]

    return Job.from_core_json(job_json)


def fetch_extended_fields(job: Job) -> None:
    """Get the extended attributes for a Job object, in place.

    Parameters
    ----------
    job : Job
        Job object to update

    Returns
    -------
    None
    """
    refresh(job, include_extended=True)


def refresh(job: Job, **kwargs) -> None:
    """Updates a job's status.
    Job must have been generated from a previous fetch or fetch_multiple call.

    Parameters
    ----------
    job : Job
        Job object to update.
        Must have been generated from a previous fetch() or fetch_multiple() call.
    """
    if job.purged:
        warnings.warn(
            f"Job {job.job_id} has been purged and cannot be refreshed. Current attributes preserved.",
            RuntimeWarning,
        )
        return None

    try:
        refreshed_job = fetch(job.job_id, **kwargs)
        job.status = refreshed_job.status
        job.return_code = refreshed_job.return_code
        job.service_class = refreshed_job.service_class
        job.queue_position = refreshed_job.queue_position
        job.program_name = refreshed_job.program_name
        job.execution_time = refreshed_job.execution_time
        job.execution_seconds = refreshed_job.execution_seconds
        job.system = refreshed_job.system
        job.subsystem = refreshed_job.subsystem
        job.member_name = refreshed_job.member_name
        job.cpu_time = refreshed_job.cpu_time
        job.srb_time = refreshed_job.srb_time
    except JobFetchException:
        job.purged = True
        logger.debug(
            "Unable to refresh attributes for %s. Job is in a purged state.",
            job.job_id,
        )
