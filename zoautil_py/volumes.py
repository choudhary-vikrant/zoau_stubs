import logging
from _typeshed import Incomplete
from zoautil_py.common import clean_shell_input as clean_shell_input, multivar_type_validation as multivar_type_validation, parse_universal_arguments as parse_universal_arguments, zoau_json_load as zoau_json_load
from zoautil_py.core import call_zoau_library as call_zoau_library
from zoautil_py.exceptions import VolumeInfoException as VolumeInfoException, VolumeListException as VolumeListException
from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

logger: logging.Logger
BYTES_PER_TRACK: int
TRACKS_PER_CYLINDER: int
BYTE_UNIT_RATIO: int
BYTES_PER_KIBIBYTE = BYTE_UNIT_RATIO
BYTES_PER_MEBIBYTE: Incomplete
BYTES_PER_GIBIBYTE: Incomplete
BYTES_PER_TEBIBYTE: Incomplete
BYTES_PER_PEBIBYTE: Incomplete

def format_bytes(free_bytes: float) -> str:
    '''Convert a long integer into a "human readable" string using the appropriate SI suffixes.

    Parameters
    ----------
    free_bytes : float
        Number of bytes to be converted

    Returns
    -------
    str
        Formatted with two decimal places and a unit suffix. (e.g. \'18.33G\')
    '''

class Volume:
    """
    Representation of z/OS Volume

    Attributes
    ----------
    volser : str
        Volume serial

    unit : str
        Four character device number.

    free_kilobytes : int
        Available volume space, in kilobytes.

    total_kilobytes : int
        Total volume space, in kilobytes.

    percentage_used : float
        Volume space in use, as a percentage.

    free_tracks : int
        Number of free tracks.

    total_tracks : int
        Total number of tracks.

    is_cylinder_managed : bool
        True for volumes with cylinder-managed space.

    index_vtoc : bool
        Index exists for VTOC.

    vtoc_active : bool
        Index VTOC active.

    status : dict, tuple, list
        Iterable with up to eight entries for the following status flags:
            - ucbonli : bool
                Device is online.
            - ucbchgs : bool
                Device status is to be changed from online to offline,
                and either allocation is enqueued on devices or the device is
                allocated. (Bit 0 is also on.)
            - ucbresv : bool
                The mount status of the volume on this device
                is reserved.
            - ucbunld : bool
                Unload operator command has been addressed to
                this device. The device is not yet unloaded.
            - ucbaloc : bool
                Device is allocated. For auto-switchable devices,
                this bit indicates that the device WAS allocated by some system
                in the SYSPLEX at the time that Allocation last obtained the
                SYSPLEX allocation status.
            - ucbpres : bool
                The mount status of the volume on this device is
                permanently resident.
            - ucbsysr : bool
                System residence device, primary console, or
                active console.
            - ucbdadi : bool
                Standard tape labels have been verified for this
                tape volume or secondary console or console status changing.
        For dict type:
            - Keys are case insensitive.
            - Status can contain only some of the eight flags,
              the rest default to False
        For list and tuple types:
            - Status must contain eight entries in order of highest byte first.
            - Values are cast to bool, so they may be passed as int.
    """
    unit: str
    volser: str
    status: Incomplete
    free_bytes: int
    total_bytes: int
    free_tracks: int
    total_tracks: int
    percentage_used: float
    is_cylinder_managed: bool
    index_vtoc: bool
    vtoc_active: bool
    def __init__(self, unit: str, volser: str, status: dict | tuple | list, is_cylinder_managed: bool, index_vtoc: bool, vtoc_active: bool, free_tracks: int, total_tracks: int, percentage_used: float) -> None: ...
    @classmethod
    def from_core_json(cls, volume_as_json: dict):
        '''Build a `Volume` object from a ZOAU core dictionary.
        Translates the core field names to the pythonic names in the `Volume` class.

        Parameters
        ----------
        volume_as_json : dict
            Dictionary from the "data" object in the ZOAU core JSON response.

        Returns
        -------
        Volume
            Representation of z/OS Volume
        '''
    def free_space(self) -> str: ...
    def total_space(self) -> str: ...
    def formatted_space(self) -> tuple[str, str]: ...

def list_volumes(volume_serial: str = None, **kwargs) -> list[Volume]:
    """List active DASD volumes with status and space information

    Parameters
    ----------
    volume_serial : str, optional
        Serial to retrieve information for a single volume.
        Lists all active volumes when blank or None.

    Returns
    -------
    List[Volume]
        List of Volume objects.
    """
def getIPLVolumeSerial() -> str:
    """Get the IPL Volume Serial name

    Returns
    -------
    str
        Volume serial name
    """
