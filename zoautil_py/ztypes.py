#----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2024
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
ZOAU general class library.
"""
import warnings
from typing import Optional, Union

from zoautil_py.common import clean_dataset_name


class ZOAUResponse:
    """
    Representation of payload between the Python API and the C or Shell libraries.

    Attributes
    ----------
    rc : int
        Return code of the command executed by the vector.

    stdout_response : str
        Standard out buffer of the executed command.

    stderr_response : str
        Standard error buffer of the executed command.

    command : str
        Full command string, including options and arguments.

    response_format : str
        Encoding label of the payload contents. For example `utf-8`.
    """
    rc: int
    stdout_response: Union[str,bytes]
    stderr_response: str
    command: str
    response_format: str

    def __init__(
        self,
        rc: Union[str,int],
        stdout_response: Union[str,bytes],
        stderr_response: str,
        command: str,
        response_format: str,
    ):
        self.rc = int(rc)
        self.response_format = response_format
        self.stdout_response = stdout_response
        self.stderr_response = stderr_response
        self.command = command

    def __str__(self):
        return (
            f"[ZOAUResponse]\n"
            f"\trc: {self.rc}\n"
            f"\tresponse_format: {self.response_format}\n"
            f"\tstdout_response: {self.stdout_response}\n"
            f"\tstderr_response: {self.stderr_response}\n"
            f"\tcommand: {self.command}"
        )

    def to_dict(self) -> dict[str, Union[str, int]]:
        """ Returns job represented as a dictionary"""
        warnings.warn(
            "to_dict() will be deprecated, use vars(<dataset>) instead",
            DeprecationWarning,
        )
        return self.__dict__

    @classmethod
    def from_dict(cls, response_as_dict) -> "ZOAUResponse":
        """Builds ZOAUResponse object from a given dictionary"""
        return cls(
            rc=int(response_as_dict["rc"]),
            response_format=response_as_dict["response_format"],
            stdout_response=response_as_dict["stdout_response"],
            stderr_response=response_as_dict["stderr_response"],
            command=response_as_dict["command"],
        )


class DDStatement:
    """
    DDStatement for use with zoautil_py.mvscmd.execute and similar functions

    Parameters
    ----------
    name : str
        DD name

    definition : DatasetDefinition, FileDefinition, VolumeDefinition, str, list[DatasetDefinition]
        Additional arguments and options for DDStatement. For specifying a concatenation
        of datasets, use list[DataDefinition].
    """

    name: str
    definition: Union[
        str, "DatasetDefinition", "FileDefinition", "VolumeDefinition", list["DatasetDefinition"]
    ]

    def __init__(
        self,
        name: str,
        definition: Union[
            str, "DatasetDefinition", "FileDefinition", "VolumeDefinition", list["DatasetDefinition"]
        ],
    ):
        self.name = clean_dataset_name(name)
        if isinstance(definition, str):
            self.definition = clean_dataset_name(definition)
        else:
            self.definition = definition

    def __str__(self):
        return (
            f"[DDStatement]\n"
            f"\tname: {self.name}\n"
            f"\tdefinition: {self.definition}"
        )

    def get_mvscmd_string(self) -> str:
        """Format and return the string to be used as an mvscmd DD option

        Examples
        --------
        - "--ddname=data.set.name"
        - "--ddname=data.set.name,new,type=seq,primary=10,secondary=2"

        Returns
        -------
        str
            DD option string.
        """
        mvscmd_string = f'--{self.name}="'

        if isinstance(self.definition, list):
            dd_strings = [x.build_arg_string() for x in self.definition]
            mvscmd_string += ":".join(dd_strings)
        elif isinstance(self.definition, str):
            mvscmd_string += self.definition
        else:
            mvscmd_string += self.definition.build_arg_string()

        mvscmd_string += '"'
        return mvscmd_string


class DataDefinition:
    """
    Base definition of a DD to use with mvscmd

    Parameters
    ----------
    name : str
        Name of a dataset or path to a zFS file
    """
    name: str

    def __init__(self, name: str):
        self.name = clean_dataset_name(name)

    def __str__(self):
        return f"[DataDefinition]\n\tname: {self.name}"

    def _build_arg_string(self):
        """Seems like its getting overloaded by core"""
        pass

    def build_arg_string(self) -> str:
        return self.name + self._build_arg_string()

    def _append_mvscmd_string(self, string, variable_name, variable):
        if (
            variable is None
            or variable_name is None
            or (isinstance(variable, list) and len(variable) == 0)
        ):
            return string
        string += f",{variable_name}="
        if isinstance(variable, list):
            string += ",".join(variable)
        else:
            string += str(variable)
        return string


class FileDefinition(DataDefinition):
    """
    Definition of a zFS file.

    Parameters
    ----------
    path_name: str
        Full path to the zFS file. This is case-sensitive,
        between 1 and 255 characters long, and must be an absolute path.

    Supported Arguments
    -------------------
    normal_disposition: str, optional
        What to do with the UNIX file after normal termination of the program.
        May be one of KEEP, DELETE.

    abnormal_disposition: str, optional
        What to do with the UNIX file after abnormal termination of the program.
        May be one of KEEP, DELETE.

    path_mode: str, optional
        The file access attributes for the UNIX file being allocated.
        Provide in chmod-like number format. (e.g. 0644, 1777)

    status_group: str, optional
        The file access attributes for zFS file being allocated.
        Specify up to 6 of:
            OCREAT, OEXCL, OAPPEND, ORDWR, ORDONLY, OWRONLY, ONOCTTY, ONONBLOCK, OSYNC, OTRUNC.
        Provide multiple attributes as a comma-separated list.

    file_data: str, optional
        The type of data that is (or will be) stored in the zFS file.
        May be one of BINARY, TEXT, RECORD.

    record_length: str, optional
        Use the specified logical record length for the zFS file being allocated.
        This is required in situations where the data will be processed as
        records and therefore, the record length, block size and record format
        need to be supplied since a zFS file would normally be treated as
        a stream of bytes.

    block_size: str, optional
        Use the specified block size for the zFS file being allocated since a
        zFS file would normally be treated as a stream of bytes.

    record_format: str, optional
        Use the specified record format for the zFS file being allocated since
        a zFS file would normally be treated as a stream of bytes.
    """

    path_name: str
    normal_disposition: Union[str, None]
    abnormal_disposition: Union[str, None]
    path_mode: Union[str, None]
    status_group: Union[str, None]
    file_data: Union[str, None]
    record_length: Union[str, None]
    block_size: Union[str, None]
    record_format: Union[str, None]

    def __init__(
        self,
        path_name: str,
        normal_disposition: Optional[str] = None,
        abnormal_disposition: Optional[str] = None,
        path_mode: Optional[str] = None,
        status_group: Optional[str] = None,
        file_data: Optional[str] = None,
        record_length: Optional[str] = None,
        block_size: Optional[str] = None,
        record_format: Optional[str] = None,
    ):
        super().__init__(path_name)
        self.normal_disposition = normal_disposition
        self.abnormal_disposition = abnormal_disposition
        self.path_mode = path_mode
        self.status_group = status_group
        self.file_data = file_data
        self.record_length = record_length
        self.block_size = block_size
        self.record_format = record_format

    def __str__(self):
        return (
            f"[FileDefinition]\n"
            f"\tnormal_disposition: {self.normal_disposition}\n"
            f"\tabnormal_disposition: {self.abnormal_disposition}"
            f"\n\tpath_mode: {self.path_mode}\n"
            f"\tstatus_group: {self.status_group}\n"
            f"\tfile_data: {self.file_data}\n"
            f"\trecord_length: {self.record_length}"
            f"\n\tblock_size: {self.block_size}\n"
            f"\trecord_format: {self.record_format}"
        )

    def _build_arg_string(self):
        mvscmd_string = ""
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "normdisp", self.normal_disposition
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "conddisp", self.abnormal_disposition
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "pathmode", self.path_mode
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "statusgroup", self.status_group
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "filedata", self.file_data
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "lrecl", self.record_length
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "blksize", self.block_size
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "recfm", self.record_format
        )
        return mvscmd_string


class VolumeDefinition(DataDefinition):
    """
    Definition of a z/OS Volume for allocation

    Parameters
    ----------
    volume_serial : str
        Unique serial number for the volume. 1 to 6 characters.

    disposition : str
        The status for the volume allocation.
        May be one of OLD/EXCL.
        Default is OLD.

    device_unit : str, optional
        Device type or group of devices
    """

    volume_serial: str
    disposition: str
    device_unit: Union[str, None]

    def __init__(
        self,
        volume_serial: str,
        disposition: str = "OLD",
        device_unit: Optional[str] = None,
    ):
        # Parameter sanitization
        if not isinstance(volume_serial, str):
            raise TypeError("volume_serial parameter must be a string")
        if not isinstance(disposition, str):
            raise TypeError("disposition parameter must be a string")
        if device_unit is not None and not isinstance(device_unit, str):
            raise TypeError("device_unit parameter must be a string")

        super().__init__(volume_serial)
        self.disposition = disposition
        self.device_unit = device_unit

    def __str__(self):
        return (
            f"[VolumeDefinition]\n"
            f"\tvolume_serial: {self.volume_serial}\n"
            f"\tdisposition: {self.disposition}\n"
            f"\tdevice_unit: {self.device_unit}"
        )

    def _build_arg_string(self):
        mvscmd_string = ",volume"
        mvscmd_string += f",{self.disposition}"
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "unit", self.device_unit
        )
        return mvscmd_string

class DatasetDefinition(DataDefinition):
    """
    Definition of z/OS dataset

    Parameters
    ----------
    dataset_name: str
        Name of the dataset.

    disposition: str
        The status of a dataset. Default is `SHR`.
        May be one of:

        - `EXCL,OLD`
            Allocate this dataset exclusively.

        - `MOD`
            Allocates the dataset for update (modification).

        - `NEW`
            Create dataset. Use the keyword arguments to tailor the dataset
            attributes. See `Supported Arguments` for the default values.

        - `SHR`
            Allocates an existing dataset that can be shared by other jobs.

        - `RAW`
            Create the dataset without the default values. Use this option to
            let the called MVS program set its own defaults.

    Supported Arguments
    -------------------
    type: str
        May be one of: KSDS, ESDS, RRDS, LDS, SEQ/BASIC, LARGE, PDS, PDSE/LIBRARY, HFS.
        Default is PDSE.

    primary: str
        Amount of primary space to allocate for the dataset.
        Default is 5 units of primary_unit.

    primary_unit: str
        May be K or KB (kilobytes), M or MB (megabytes),
        G or GB (gigabytes), C or CYL (cylinders), T or TRK (tracks)
        Default is M.

    secondary: str
        Amount of secondary space to allocate for the dataset.
        Defaults to 1/10 of primary space.

    secondary_unit: str
        May be K or KB (kilobytes), M or MB (megabytes),
        G or GB (gigabytes), C or CYL (cylinders), T or TRK (tracks)

    normal_disposition: str
        What to do with the dataset after normal termination of the program.
        May be one of DELETE, PASS, CATALOG, UNCATALOG.

    abnormal_disposition: str
        What to do with the dataset after normal termination of the program.
        May be one of DELETE, CATALOG, UNCATALOG.

    block_size: str
        Block size of the dataset.
        Default is one of:
            32718 for record format FBA,
            32720 for FB,
            32743 for VBA,
            32760 for VB and U.

    record_format: str
        Record format for the dataset.
        May be one of F, FB, VB, FBA, VBA, U.
        Default is FB.

    record_length: str
        Record length specified in bytes.
        Default is one of:
            80 for fixed datasets (FB, FBA)
            137 for variable datasets (VB, VBA)
            0 for unformatted datasets (U)
        For variable datasets, the length must include the 4-byte
        prefix area.

    storage_class: str
        The storage class for an SMS-managed dataset.
        Required for SMS-managed datasets that do not match an SMS-rule.
        Not valid for datasets that are not SMS-managed.

    data_class: str
        The data class for an SMS-managed dataset.
        Optional for SMS-managed datasets that do not match an SMS-rule.
        Not valid for datasets that are not SMS-managed.

    management_class: str
        The management class for an SMS-managed dataset.
        Optional for SMS-managed datasets that do not match an SMS-rule.
        Not valid for datasets that are not SMS-managed.

    key_length: str
        Length of the key for Key Sequenced Datasets (KSDS).

    key_offset: str
        Offset of the key for Key Sequenced Datasets (KSDS).

    volumes: str
        A list of comma separated volume serials.
        When providing multiple volumes, processing will begin with
        the first volume in the provided list. Offline volumes are not considered.
        Volumes can always be provided when not using SMS.

    dataset_key_label: str
        The label for the encryption key used by the system to encrypt
        the dataset. Only applicable when using encrypted datasets.

    key_label1: str
        The label for the key encrypting key used by the
        Encryption Key Manager. Only applicable when using encrypted datasets.

    key_encoding1: str
        How the label for the key encrypting key (key_label1) is encoded by
        the Encryption Key Manager.
        May be one of: L, H
        Only applicable when using encrypted datasets.

    key_label2: str
        The label for the key encrypting key used by the Encryption Key Manager.
        Only applicable when using encrypted datasets.

    key_encoding2: str
        How the label for the key encrypting key (key_label2) is encoded by
        the Encryption Key Manager.
        May be one of: L, H
        Only applicable when using encrypted datasets.

    device_unit: str
        Unit name of the device that the dataset will reside on.
        To target a specific device number, you must precede the address with
        a slash (/) character.
    """

    dataset_name: str
    disposition: str
    type: Union[str, None]
    primary: Union[str, None]
    primary_unit: Union[str, None]
    secondary: Union[str, None]
    secondary_unit: Union[str, None]
    normal_disposition: Union[str, None]
    abnormal_disposition: Union[str, None]
    conditional_disposition: Union[str, None]
    block_size: Union[str, None]
    record_format: Union[str, None]
    record_length: Union[str, None]
    storage_class: Union[str, None]
    data_class: Union[str, None]
    management_class: Union[str, None]
    key_length: Union[str, None]
    key_offset: Union[str, None]
    volumes: Union[str, None]
    dataset_key_label: Union[str, None]
    key_label1: Union[str, None]
    key_encoding1: Union[str, None]
    key_label2: Union[str, None]
    key_encoding2: Union[str, None]
    device_unit: Union[str, None]

    def __init__(
        self,
        dataset_name: str,
        disposition: str = "SHR",
        type: Optional[str] = None,
        primary: Optional[str] = None,
        primary_unit: Optional[str] = None,
        secondary: Optional[str] = None,
        secondary_unit: Optional[str] = None,
        normal_disposition: Optional[str] = None,
        abnormal_disposition: Optional[str] = None,
        conditional_disposition: Optional[str] = None,
        block_size: Optional[str] = None,
        record_format: Optional[str] = None,
        record_length: Optional[str] = None,
        storage_class: Optional[str] = None,
        data_class: Optional[str] = None,
        management_class: Optional[str] = None,
        key_length: Optional[str] = None,
        key_offset: Optional[str] = None,
        volumes: Optional[str] = None,
        dataset_key_label: Optional[str] = None,
        key_label1: Optional[str] = None,
        key_encoding1: Optional[str] = None,
        key_label2: Optional[str] = None,
        key_encoding2: Optional[str] = None,
        device_unit: Optional[str] = None,
    ):
        super().__init__(dataset_name)
        self.disposition = disposition
        self.type = type
        self.primary = primary
        self.primary_unit = primary_unit
        self.secondary = secondary
        self.secondary_unit = secondary_unit
        self.normal_disposition = normal_disposition
        self.abnormal_disposition = abnormal_disposition
        self.conditional_disposition = conditional_disposition
        self.block_size = block_size
        self.record_format = record_format
        self.record_length = record_length
        self.storage_class = storage_class
        self.data_class = data_class
        self.management_class = management_class
        self.key_length = key_length
        self.key_offset = key_offset
        self.volumes = volumes
        self.dataset_key_label = dataset_key_label
        self.key_label1 = key_label1
        self.key_encoding1 = key_encoding1
        self.key_label2 = key_label2
        self.key_encoding2 = key_encoding2
        self.device_unit = device_unit

    def __str__(self):
        return (
            f"[DatasetDefinition]\n"
            f"\tdisposition: {self.disposition}\n"
            f"\ttype: {self.type}\n"
            f"\tprimary: {self.primary}\n"
            f"\tprimary_unit: {self.primary_unit}\n"
            f"\tsecondary: {self.secondary}\n"
            f"\tsecondary_unit: {self.secondary_unit}\n"
            f"\tnormal_disposition: {self.normal_disposition}\n"
            f"\tabnormal_disposition: {self.abnormal_disposition}\n"
            f"\tconditional_disposition: {self.conditional_disposition}\n"
            f"\tblock_size: {self.block_size}\n"
            f"\trecord_format: {self.record_format}\n"
            f"\trecord_length: {self.record_length}\n"
            f"\tstorage_class: {self.storage_class}\n"
            f"\tdata_class: {self.data_class}\n"
            f"\tmanagement_class: {self.management_class}\n"
            f"\tkey_length: {self.key_length}\n"
            f"\tkey_offset: {self.key_offset}\n"
            f"\tvolumes: {self.volumes}\n"
            f"\tdataset_key_label: {self.dataset_key_label}\n"
            f"\tkey_label1: {self.key_label1}\n"
            f"\tkey_encoding1: {self.key_encoding1}\n"
            f"\tkey_label2: {self.key_label2}\n"
            f"\tkey_encoding2: {self.key_encoding2}\n"
            f"\tdevice_unit: {self.device_unit}"
        )

    def _build_arg_string(self):
        mvscmd_string = f",{self.disposition}" if self.disposition else ""
        mvscmd_string = self._append_mvscmd_string(mvscmd_string, "type", self.type)
        if self.primary:
            mvscmd_string += f",primary={self.primary}"
            if self.primary_unit:
                mvscmd_string += self.primary_unit

        if self.secondary:
            mvscmd_string += f",secondary={self.secondary}"
            if self.secondary_unit:
                mvscmd_string += self.secondary_unit

        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "normdisp", self.normal_disposition
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "conddisp", self.abnormal_disposition
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "blksize", self.block_size
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "recfm", self.record_format
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "lrecl", self.record_length
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "storclas", self.storage_class
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "dataclas", self.data_class
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "mgmtclas", self.management_class
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "keylen", self.key_length
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "keyoffset", self.key_offset
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "volumes", self.volumes
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "dskeylbl", self.dataset_key_label
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "keylab1", self.key_label1
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "keylab2", self.key_label2
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "keycd1", self.key_encoding1
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "keycd2", self.key_encoding2
        )
        mvscmd_string = self._append_mvscmd_string(
            mvscmd_string, "unit", self.device_unit
        )
        return mvscmd_string
