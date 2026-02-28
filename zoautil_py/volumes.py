# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2025
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
Functions to work with z/OS system volumes.
"""

import logging
from typing import List
import subprocess

from zoautil_py.common import parse_universal_arguments, zoau_json_load, clean_shell_input, multivar_type_validation
from zoautil_py.core import call_zoau_library # pylint: disable=import-error, no-name-in-module
from zoautil_py.ztypes import ZOAUResponse
from zoautil_py.exceptions import VolumeInfoException, VolumeListException

logger: logging.Logger
logger = logging.getLogger(__name__)

# Constants for a 3390 device
BYTES_PER_TRACK = 56664
TRACKS_PER_CYLINDER = 15

BYTE_UNIT_RATIO = 1024
BYTES_PER_KIBIBYTE = BYTE_UNIT_RATIO
BYTES_PER_MEBIBYTE = BYTES_PER_KIBIBYTE * BYTE_UNIT_RATIO
BYTES_PER_GIBIBYTE = BYTES_PER_MEBIBYTE * BYTE_UNIT_RATIO
BYTES_PER_TEBIBYTE = BYTES_PER_GIBIBYTE * BYTE_UNIT_RATIO
BYTES_PER_PEBIBYTE = BYTES_PER_TEBIBYTE * BYTE_UNIT_RATIO

def format_bytes(free_bytes: float) -> str:
    """Convert a long integer into a "human readable" string using the appropriate SI suffixes.

    Parameters
    ----------
    free_bytes : float
        Number of bytes to be converted

    Returns
    -------
    str
        Formatted with two decimal places and a unit suffix. (e.g. '18.33G')
    """
    if free_bytes < BYTES_PER_KIBIBYTE:
        return '{0:.0f}'.format(free_bytes)
    elif BYTES_PER_KIBIBYTE <= free_bytes < BYTES_PER_MEBIBYTE:
        return '{0:.2f}K'.format(free_bytes / BYTES_PER_KIBIBYTE)
    elif BYTES_PER_MEBIBYTE <= free_bytes < BYTES_PER_GIBIBYTE:
        return '{0:.2f}M'.format(free_bytes / BYTES_PER_MEBIBYTE)
    elif BYTES_PER_GIBIBYTE <= free_bytes < BYTES_PER_TEBIBYTE:
        return '{0:.2f}G'.format(free_bytes / BYTES_PER_GIBIBYTE)
    elif BYTES_PER_TEBIBYTE <= free_bytes < BYTES_PER_PEBIBYTE:
        return '{0:.2f}T'.format(free_bytes / BYTES_PER_TEBIBYTE)
    elif BYTES_PER_PEBIBYTE <= free_bytes:
        return '{0:.2f}P'.format(free_bytes / BYTES_PER_PEBIBYTE)
    else:
        raise RuntimeError("Unable to format bytes")

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
    status = {
        "ucbonli": False,
        "ucbchgs": False,
        "ucbresv": False,
        "ucbunld": False,
        "ucbaloc": False,
        "ucbpres": False,
        "ucbsysr": False,
        "ucbdadi": False,
    }
    free_bytes: int
    total_bytes: int
    free_tracks: int
    total_tracks: int
    percentage_used: float
    is_cylinder_managed : bool
    index_vtoc : bool
    vtoc_active : bool

    def __init__(
        self,
        unit: str,
        volser: str,
        status: dict | tuple | list,
        is_cylinder_managed : bool,
        index_vtoc : bool,
        vtoc_active : bool,
        free_tracks: int,
        total_tracks: int,
        percentage_used: float,
    ):
        # Parameter sanitization
        multivar_type_validation(locals(), (Volume, str, str, (dict, tuple, list), bool, bool, bool, int, int, float))

        # Attribute assignment
        ## str
        self.volser = volser
        self.unit = unit
        ## bool
        self.is_cylinder_managed = is_cylinder_managed
        self.index_vtoc = index_vtoc
        self.vtoc_active = vtoc_active
        ## int
        self.free_tracks = int(free_tracks)
        self.total_tracks = int(total_tracks)
        self.free_bytes = self.free_tracks * BYTES_PER_TRACK
        self.total_bytes = self.total_tracks * BYTES_PER_TRACK
        ## float
        self.percentage_used = float(percentage_used)
        ## dict
        status_tmp = {}
        if not len(status):
            raise ValueError("status must not be empty")
        if isinstance(status, (tuple, list)):
            bool_list = [bool(x) for x in status]
            if len(bool_list) != len(self.status.keys()):
                raise ValueError("Incorrect number of status values")
            status_tmp = dict(zip(self.status.keys(), bool_list))
        elif isinstance(status, dict):
            for key, val in status.items():
                key_lower = key.lower()
                if key_lower in self.status.keys():
                    status_tmp[key_lower] = val
        self.status = status_tmp

    @classmethod
    def from_core_json(cls, volume_as_json: dict):
        """Build a `Volume` object from a ZOAU core dictionary.
        Translates the core field names to the pythonic names in the `Volume` class.

        Parameters
        ----------
        volume_as_json : dict
            Dictionary from the "data" object in the ZOAU core JSON response.

        Returns
        -------
        Volume
            Representation of z/OS Volume
        """
        # Job Creation
        try:
            volume_as_json.pop("free_space")
            volume_as_json.pop("total_space")
            volume_as_json.pop("free_kilobytes")
            volume_as_json.pop("total_kilobytes")
            new_volume = cls(**volume_as_json)
        except KeyError as key_error:
            raise KeyError(
                f"Error while trying to parse the following volume JSON: {volume_as_json}"
            ) from key_error
        return new_volume

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return f"zoautil_py.volumes.Volume object with serial:{self.volser}"

    def free_space(self) -> str:
        free_bytes = float(self.free_bytes)
        return format_bytes(free_bytes)

    def total_space(self) -> str:
        total_bytes = float(self.total_bytes)
        return format_bytes(total_bytes)

    def formatted_space(self) -> tuple[str, str]:
        return (self.free_space(), self.total_space())


def _vf_call(
    volume_serial: str | None = None,
    json_output=True,
    **kwargs,
) -> ZOAUResponse:
    """Builds a command string and calls zoau core (vf)"""

    command_opts = ""
    if json_output:
        command_opts += "-j "

    command_opts += parse_universal_arguments(**kwargs)

    command_opts += " -- "

    if volume_serial:
        volume_serial = clean_shell_input(volume_serial)
        command_opts += volume_serial

    logger.debug("ZOAU_CORE call: vf %s", command_opts)

    zoau_response = ZOAUResponse.from_dict(call_zoau_library("vf", command_opts))
    return zoau_response


def list_volumes(volume_serial: str = None, **kwargs) -> List[Volume]:
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
    logger.debug("vf zsystem function call")
    logger.debug("volume_serial: '%s'", volume_serial)
    logger.debug("kwargs: '%s'", kwargs)

    response = _vf_call(volume_serial, json_output=True, **kwargs)
    response_json, meta_json = zoau_json_load(response.stdout_response)

    volume_json_list: List[dict] = response_json.get("volumes", [])
    error_list: List[dict] = response_json.get("errors", [])

    logger.debug("Listed %d volumes", meta_json.get("volumes_reported", 0))
    logger.debug("Encountered %d errors", meta_json.get("errors_encountered", 0))

    if meta_json.get("errors_encountered", 0):
        # Raise an exception only for single volume requests
        if volume_serial:
            raise VolumeInfoException(response)

        # For multiple volume requests, just log the debug info
        for vol_error in error_list:
            logger.debug("Failed to get information for volume '%s'", vol_error.get("volser", "ERROR"))
            logger.debug("LSPACE diagnostics: %s", vol_error)

    volume_list = []
    if not meta_json.get("volumes_reported", None):
        return volume_list

    for volume_as_json in volume_json_list:
        volume_list.append(Volume.from_core_json(volume_as_json))

    return volume_list

def getIPLVolumeSerial() -> str:
    """Get the IPL Volume Serial name

    Returns
    -------
    str
        Volume serial name
    """
    command = "sysvar SYSR1"
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    response_out, response_err = proc.communicate()
    response_str = response_out.decode('utf-8')[:-1] # Decode the response and remove the trailing newline
    return response_str
