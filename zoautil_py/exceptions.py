from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

class _ZOAUExtendableException(Exception):
    """Custom exception supporting a string message and ZOAUResponse object

    Attributes
    ----------
    message: str
        ZOAUResponse as string (Printed as output by `raise`)
    response : ZOAUResponse
        Addressable ZOAUResponse object

    Notes
    -----
    `ZOAUResponse` attributes
        - rc: str
            Return code
        - stdout_response: str
            Stdout
        - stderr_response: str
            Stderr
        - command: str
            Command performed during a ZOAU core call
        - response_format: str
            Response encoding
    """
    message: str
    response: ZOAUResponse
    def __init__(self, response_obj: ZOAUResponse) -> None: ...

class ZOAUException(_ZOAUExtendableException):
    """Errors happening during ZOAU core calls, see message for details"""
class DatasetCreateException(_ZOAUExtendableException):
    """Errors while trying to create the dataset, see message for details"""
class DatasetFetchException(_ZOAUExtendableException):
    """Errors during dataset queries, see message for details"""
class DatasetFormatException(_ZOAUExtendableException):
    """Dataset content does not match expected formats, see message for details"""
class DatasetWriteException(_ZOAUExtendableException):
    """Errors while trying to write into a Dataset, see message for details"""
class DatasetVerificationError(Exception):
    """Errors while verifiyng dataset creation"""
class DatasetWriteError(Exception):
    """Dataset specific writing Errors"""
class GenerationDataGroupDeleteException(_ZOAUExtendableException):
    """Errors while deleting the GDG, see message for details"""
class GenerationDataGroupClearException(_ZOAUExtendableException):
    """Errors while clearing the GDG, see message for details"""
class GenerationDataGroupFetchException(_ZOAUExtendableException):
    """Errors during GDG queries, see message for details"""
class GenerationDataGroupViewInvalidName(Exception):
    """Can not construct a GDG view instance, an invalid name was provided,
       see error message for details"""
class GenerationDataGroupViewInvalidState(Exception):
    """The GDG view state is invalid, see message for details"""
class GenerationDataGroupCreateException(_ZOAUExtendableException):
    """Errors while creating the GDG, see message for details"""
class JobFetchException(_ZOAUExtendableException):
    """Errors during job fetch, see message for details"""
class JobSubmitException(_ZOAUExtendableException):
    """Job submission errors, see message for details"""
class JobCancelException(_ZOAUExtendableException):
    """Job cancelling errors, see message for details"""
class JobPurgeException(_ZOAUExtendableException):
    """Job purging errors, see message for details"""
class DDQueryException(_ZOAUExtendableException):
    """Errors during a Job's DD Querying, see message for details"""
class VolumeListException(_ZOAUExtendableException):
    """Failed to list volumes"""
class VolumeInfoException(_ZOAUExtendableException):
    """Failed to get volume information"""
class JobCancelConfirmException(Exception):
    """Cannot confirm job cancellation, see message for details"""
class JobPurgeConfirmException(Exception):
    """Cannot confirm purge of given job, see message for details"""
class MissingEnvironmentVariable(Exception): ...
class MissingFunctionParameter(Exception): ...
class MemberFetchException(_ZOAUExtendableException):
    """Errors during member queries, see message for details"""
class MemberFetchInvalidParameter(Exception):
    """An invalid parameter was provided, see message for details."""
class SmdeExtendedAttributesUnavailable(Exception):
    """No SMDE extended attributes are registered for this member."""
class IspfMemberStatisticsUnavailable(Exception):
    """No ISPF member statistics are registered for this member"""
class VsamClusterNameInvalidPattern(Exception):
    """Wildcards '*' or '?' are not supported when fetching a VSAM cluster."""
class VsamClusterFetchException(_ZOAUExtendableException):
    """Errors during VSAM queries, see message for details"""
