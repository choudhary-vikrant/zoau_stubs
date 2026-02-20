import logging
from _typeshed import Incomplete
from datetime import datetime
from zoautil_py.common import cast_int_optional as cast_int_optional, clean_dataset_name as clean_dataset_name, clean_shell_input as clean_shell_input, parse_universal_arguments as parse_universal_arguments, parse_unknown as parse_unknown, zoau_json_load as zoau_json_load
from zoautil_py.core import call_zoau_library as call_zoau_library
from zoautil_py.core_return_codes import DDLSReturnCodes as DDLSReturnCodes
from zoautil_py.exceptions import DDQueryException as DDQueryException, JobCancelConfirmException as JobCancelConfirmException, JobCancelException as JobCancelException, JobFetchException as JobFetchException, JobPurgeConfirmException as JobPurgeConfirmException, JobPurgeException as JobPurgeException, JobSubmitException as JobSubmitException
from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

logger: logging.Logger
BASIC_JOB_FIELDS: Incomplete
DEFAULT_JOB_FIELDS: Incomplete
EXTENDED_JOB_FIELDS: Incomplete

class Job:
    '''
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
        Program name for the job\'s last completed step

    return_code : str, None
        Last known return code of job

    status : str, None
        Last known status of job

    service_class : str, None
        WLM service class

    creation_datetime: datetime, None
        Datetime object with the job\'s input start date and time

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
    '''
    job_id: str
    name: str
    job_class: str
    asid: int
    priority: int
    queue_position: int
    owner: str | None
    program_name: str | None
    return_code: str | None
    status: str | None
    service_class: str | None
    creation_datetime: datetime | None
    job_type: str | None
    execution_time: str | None
    execution_seconds: int | None
    system: str | None
    subsystem: str | None
    origin_node: str | None
    execution_node: str | None
    member_name: str | None
    cpu_time: int
    srb_time: int
    purged: bool
    def __init__(self, job_id: str, name: str, job_class: str, asid: str | int, priority: str | int, queue_position: str | int, owner: str | None = None, program_name: str | None = None, return_code: str | None = None, status: str | None = None, service_class: str | None = None, creation_datetime: str | datetime | None = None, job_type: str | None = None, execution_time: str | None = None, execution_seconds: str | None = None, system: str | None = None, subsystem: str | None = None, origin_node: str | None = None, execution_node: str | None = None, member_name: str | None = None, cpu_time: str | int | None = None, srb_time: str | int | None = None, purged: bool = False) -> None: ...
    @classmethod
    def from_core_json(cls, job_as_json: dict):
        '''Build a `Job` object from a ZOAU core dictionary.
        Translates the core field names to the pythonic names in the `Job` class.

        Parameters
        ----------
        job_as_json : dict
            Dictionary from the "data" object in the ZOAU core JSON response.

        Returns
        -------
        Job
            Representation of z/OS Job
        '''
    def cancel(self, purge_job: bool = False, confirm_timeout: int = 0):
        """Queue job for cancellation"""
    def purge(self, confirm_timeout: int = 0):
        """Queue job for purge"""
    def refresh(self) -> None:
        """Refresh job information"""
    def wait(self, seconds_per_loop: float = 1.0, max_loops: int | None = None):
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
    def fetch_extended_fields(self) -> None:
        """Fetch the extended attributes"""

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
def cancel(job_id: str, purge_job: bool = False, confirm_timeout: int = 0, **kwargs) -> None:
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
def list_dds(job_id: str, **kwargs) -> list[dict]:
    '''List DDs of a z/OS Job

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
    '''
def read_output(job_id: str, stepname: str = "'*'", dd_name: str = '', **kwargs) -> str:
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
def fetch_multiple_as_json(job_id: str | None = None, job_owner: str | None = None, job_name: str | None = None, included_fields: list[str] | None = None, **kwargs) -> dict:
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
def fetch_multiple(job_id: str | None = None, job_owner: str | None = None, job_name: str | None = None, include_extended: bool = False, **kwargs) -> list[Job]:
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
def fetch(job_id: str | None = None, include_extended: bool = False, **kwargs) -> Job:
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
def refresh(job: Job, **kwargs) -> None:
    """Updates a job's status.
    Job must have been generated from a previous fetch or fetch_multiple call.

    Parameters
    ----------
    job : Job
        Job object to update.
        Must have been generated from a previous fetch() or fetch_multiple() call.
    """
