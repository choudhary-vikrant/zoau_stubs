# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2025
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
ZOAU Python functions and objects for z/OS Dataset operations.
"""
import codecs
import logging
import warnings
from datetime import datetime
from typing import Any, Optional, Union

from zoautil_py.common import (
    cast_int_optional,
    clean_dataset_name,
    clean_shell_input,
    escape_block_string,
    parse_universal_arguments,
    parse_unknown,
    slicer,
    zoau_json_load,
    match_expression,
    multivar_type_validation,
    identify_dtype,
)
from zoautil_py.core import (  # pylint: disable=import-error, no-name-in-module
    call_zoau_library,
    call_zoau_library_bin,
)
from zoautil_py.exceptions import (
    DatasetCreateException,
    DatasetFetchException,
    DatasetVerificationError,
    DatasetWriteException,
    MissingFunctionParameter,
    ZOAUException,
    DatasetWriteError,
)

from zoautil_py.zoau_io import RecordIO
from zoautil_py.ztypes import ZOAUResponse

MULTIBYTE_ENCODINGS = ("utf_8",)


logger: logging.Logger
logger = logging.getLogger(__name__)


class Dataset:
    """
    Class that represents the z/OS dataset.

    Attributes
    ----------
    name: str
        Name of the dataset.

    organization: str, None
        Dataset organization of the dataset. `None` if unknown.

    record_format: str, None
        Record format of the dataset. `None` if unknown.

    volume: str, None
        Volume the dataset resides on. `None` if unknown.

    block_size: int, None
        Block size of the dataset. `None` if unknown.

    record_length: int, None
        Record length of the dataset. `None` if unknown.

    total_space: int, None
        Estimated total space of the dataset. `None` if unknown.

    used_space: int, None
        Estimated used space of the dataset. `None` if unknown.

    last_referenced: datetime, None
        Date when the dataset was last referenced. `None` if unknown.

    type: str, None
        Type of the dataset. `None` if unknown.

    encoding: str, None
        Encoding of text content if available. (Python only)

    allocated_extents: int
        Extents that the dataset occupies in the volume. `None` if unknown.

    first_extent_size: int
        Estimated size (in bytes) of the first extent of the dataset. `None` if
        unknown.

    secondary_space: int
        Estimated amount of secondary space (in bytes) of the dataset.
        `None` if unknown.

    used_directory_blocks: int
        Number of used directory blocks in a partitioned dataset.
        `None` if unknown.

    maximum_directory_blocks: int
        Maximum number of directory blocks in a partitioned dataset.
        `None` if unknown.

    encoding: str, None
        Encoding of text content if available. (Python only)

    allocated_extents: int
        Extents that the dataset occupies in the volume. `None` if unknown.

    first_extent_size: int
        Estimated size (in bytes) of the first extent of the dataset. `None` if
        unknown.

    secondary_space: int
        Estimated amount of secondary space (in bytes) of the dataset.
        `None` if unknown.

    alias_of: str
        The name of the dataset that the alias is related to. `None` if the
        dataset is not an alias.
    """

    name: str
    organization: Union[str, None]
    record_format: Union[str, None]
    volume: Union[str, None]
    block_size: Union[int, None]
    record_length: Union[int, None]
    total_space: Union[int, None]
    used_space: Union[int, None]
    last_referenced: Union[datetime, None]
    type: Union[str, None]
    allocated_extents: Union[int, None]
    first_extent_size: Union[int, None]
    secondary_space: Union[int, None]
    used_directory_blocks: Union[str, None]
    maximum_directory_blocks: Union[str, None]
    encoding: Union[str, None]
    serialize: Union[bool, None]
    next_record_char: Union[str, None]
    alias_of: Union[str, None]

    def __init__(
        self,
        name: str,
        organization: Union[str, None] = None,
        record_format: Union[str, None] = None,
        volume: Union[str, None] = None,
        block_size: Union[str, int, None] = None,
        record_length: Union[str, int, None] = None,
        total_space: Union[str, int, None] = None,
        used_space: Union[str, int, None] = None,
        last_referenced: Union[str, datetime, None] = None,
        type: Union[str, None] = None,
        allocated_extents: Union[int, None] = None,
        first_extent_size: Union[int, None] = None,
        secondary_space: Union[int, None] = None,
        used_directory_blocks: Union[int, None] = None,
        maximum_directory_blocks: Union[int, None] = None,
        encoding: Union[str, None] = None,
        serialize: Union[str, None] = None,
        next_record_char: Union[str, None] = None,
        alias_of: Union[str, None] = None
    ):
        # Parameter sanitization
        # str
        if not isinstance(name, str):
            raise TypeError("name parameter must be a string")
        if organization is not None and not isinstance(organization, str):
            raise TypeError("organization parameter must be a string")
        if record_format is not None and not isinstance(record_format, str):
            raise TypeError("record_format parameter must be a string")
        if volume is not None and not isinstance(volume, str):
            raise TypeError("volume parameter must be a string")
        if type is not None and not isinstance(type, str):
            raise TypeError("type parameter must be a string")
        if encoding is not None and not isinstance(encoding, str):
            raise TypeError("encoding parameter must be a string")
        if serialize is not None and not isinstance(serialize, str):
            raise TypeError("serialize parameter must be a string")
        if next_record_char is not None and not isinstance(next_record_char, str):
            raise TypeError("next_record_char parameter must be a string")
        if alias_of is not None and not isinstance(alias_of, str):
            raise TypeError("alias_of parameter must be a string")
        # int
        if block_size is not None and not isinstance(block_size, (str, int)):
            raise TypeError("block_size parameter must be a string or int")
        if record_length is not None and not isinstance(record_length, (str, int)):
            raise TypeError("record_length parameter must be a string or int")
        if total_space is not None and not isinstance(total_space, (str, int)):
            raise TypeError("total_space parameter must be a string or int")
        if used_space is not None and not isinstance(used_space, (str, int)):
            raise TypeError("used_space parameter must be a string or int")
        if allocated_extents is not None and not isinstance(
            allocated_extents, (str, int)
        ):
            raise TypeError("allocated_extents parameter must be a string or int")
        if first_extent_size is not None and not isinstance(
            first_extent_size, (str, int)
        ):
            raise TypeError("first_extent_size parameter must be a string or int")
        if secondary_space is not None and not isinstance(secondary_space, (str, int)):
            raise TypeError("secondary_space parameter must be a string or int")
        if used_directory_blocks is not None and not isinstance(used_directory_blocks, (str, int)):
            raise TypeError("used_directory_blocks parameter must be a string or int")
        if maximum_directory_blocks is not None and not isinstance(maximum_directory_blocks, (str, int)):
            raise TypeError("maximum_directory_blocks parameter must be a string or int")

        # datetime

        if last_referenced is not None and not isinstance(
            last_referenced, (str, datetime)
        ):
            raise TypeError("last_referenced parameter must be a string or datetime")

        # Missing Values
        # Attribute declaration
        # str
        self.name = name
        self.organization = parse_unknown(organization)
        self.record_format = parse_unknown(record_format)
        self.volume = parse_unknown(volume)
        self.type = parse_unknown(type)
        self.encoding = encoding
        self.serialize = serialize
        self.next_record_char = next_record_char
        self.alias_of = alias_of
        # int
        self.block_size = cast_int_optional(parse_unknown(block_size))
        self.record_length = cast_int_optional(parse_unknown(record_length))
        self.total_space = cast_int_optional(parse_unknown(total_space))
        self.used_space = cast_int_optional(parse_unknown(used_space))
        self.allocated_extents = cast_int_optional(parse_unknown(allocated_extents))
        self.first_extent_size = cast_int_optional(parse_unknown(first_extent_size))
        self.secondary_space = cast_int_optional(parse_unknown(secondary_space))
        self.used_directory_blocks = cast_int_optional(parse_unknown(used_directory_blocks))
        self.maximum_directory_blocks = cast_int_optional(parse_unknown(maximum_directory_blocks))

        # datetime
        if last_referenced is None:
            self.last_referenced = last_referenced
        if isinstance(last_referenced, datetime):
            self.last_referenced = last_referenced
        elif isinstance(last_referenced, str):
            try:
                self.last_referenced = datetime.strptime(last_referenced, "%Y/%m/%d")
            except ValueError:
                logger.debug(
                    "last_referenced of dataset: %s : %s is invalid. "
                    + "Defaulting to None",
                    name,
                    last_referenced,
                )
                self.last_referenced = None

    def to_dict(self) -> dict[str, Union[str, int, datetime]]:
        """Returns dataset information as a dictionary

        Returns
        -------
        dict[str, any]
            name: str
                Name of the dataset.
            organization: str
                Dataset organization of the dataset. `None` if unknown.
            record_format: str
                Record format of the dataset. `None` if unknown.
            volume: str
                Volume the dataset resides on. `None` if unknown.
            block_size: int
                Block size of the dataset. `None` if unknown.
            record_length: int
                Record length of the dataset. `None` if unknown.
            total_space: int
                Estimated total space of the dataset. `None` if unknown.
            used_space: int
                Estimated used space of the dataset. `None` if unknown.
            last_referenced: datetime
                Date when the dataset was last referenced. `None` if unknown.
            type: str
                Type of the dataset. `None` if unknown.
            allocated_extents: int
                Extents that the dataset occupies in the volume. `None` if
                unknown.
            first_extent_size: int
                Estimated size (in bytes) of the first extent of the dataset.
                `None` if unknown.
            secondary_space: int
                Amount of secondary space (in bytes) of the dataset. `None`
                if unknown.
            used_directory_blocks: int
                Number of used directory blocks.
                `None` if unknown.
            maximum_directory_blocks: int
                Maximum number of directory blocks.
                `None` if unknown.
            encoding: str
                Encoding of text content if available. (Python only)
                `None` if unknown.
            serialize: str
                Serialization method of the dataset. (Python only)
                `None` if unknown.
            next_record_char: str
                New record character of the dataset. (Python only)
                `None` if unknown.
            alias_of: str
                The name of the dataset that the alias is related to. `None`
                if unknown or if the dataset is not an alias.

        Notes
        -----
        Provides the same result as calling <Dataset>.__dict__, kept for legacy support
        """
        warnings.warn(
            "to_dict() is deprecated, use vars(<dataset>) instead",
            DeprecationWarning,
        )
        return self.__dict__

    @classmethod
    def from_dict(cls, ds_as_dict: dict) -> "Dataset":
        """Builds a Dataset object from a dictionary

        Parameters
        ----------
        ds_as_dict : dict
            Dictionary containing:
                name, recfm, record_length, volume, block_size,
                last_referenced, used_space, total_space, type

        Returns
        -------
        Dataset
            Representation of z/OS Dataset
        """
        return cls(
            name=ds_as_dict["name"],
            record_format=ds_as_dict["recfm"],
            record_length=ds_as_dict["record_length"],
            volume=ds_as_dict["volume"],
            block_size=ds_as_dict["block_size"],
            last_referenced=ds_as_dict["last_referenced"],
            used_space=ds_as_dict["used_space"],
            total_space=ds_as_dict["total_space"],
            type=ds_as_dict["dsntype"],
            allocated_extents=ds_as_dict["allocated_extents"],
            first_extent_size=ds_as_dict["first_extent_size"],
            secondary_space=ds_as_dict["secondary_space"],
            used_directory_blocks=ds_as_dict["used_directory_blocks"],
            maximum_directory_blocks=ds_as_dict["maximum_directory_blocks"],
            alias_of=ds_as_dict["relation"]
        )

    @classmethod
    def from_core_json(cls, ds_as_json: dict[str, str]):
        """Create a Dataset instance from a dls or dinfo JSON response

        Returns
        -------
        Dataset
            Representation of z/OS Dataset

        Parameters
        ----------
        ds_as_json : dict
            Dictionary from the "datasets" array in the "data" object of a
            JSON dls response
        """

        max_dir_blocks = ds_as_json.get("maxdirblks", None)

        # PDSE datasets do not have a limit.
        if max_dir_blocks == "NOLIMIT":
            max_dir_blocks = None

        return cls(
            name=ds_as_json.get("name"),  # type: ignore
            record_format=ds_as_json.get("recfm", None),
            record_length=ds_as_json.get("lrecl", None),
            volume=ds_as_json.get("volume", None),
            block_size=ds_as_json.get("blksize", None),
            last_referenced=ds_as_json.get("ref", None),
            used_space=ds_as_json.get("used", None),
            total_space=ds_as_json.get("alloc", None),
            organization=ds_as_json.get("dsorg", None),
            type=ds_as_json.get("dsntype", None),
            allocated_extents=ds_as_json.get("extents", None),
            first_extent_size=ds_as_json.get("firstext", None),
            secondary_space=ds_as_json.get("secondary", None),
            used_directory_blocks=ds_as_json.get("useddirblks", None),
            maximum_directory_blocks=max_dir_blocks,
            alias_of=ds_as_json.get("relation", None)
        )

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return f"zoautil_py.datasets.Dataset object with name:{self.name}"

    def write(
        self,
        content: str,
        member_name: str = "",
        append: bool = False,
        encoding: Union[str, None] = None,
        serialize: Union[str, None] = None,
        next_record_char: Union[str, None] = None,
        max_record_length: Union[int, None] = None,
        fill_char: str = " ",
        validate_record_length: bool = True,
    ):
        """Writes encoded text content to a z/OS dataset.

        Arguments
        ---------
        content : str
            Content to write.

        member_name: str, optional
            Member to write to.

        encoding : str, optional
            The encoding character scheme used to represent the dataset's content.
            Defaults to 'cp1047'.

        serialize : str, optional
            If set to 'record', the content will be serialized and written with a
            1:1 mapping of lines to records.

            If set to 'byte', the content will be serialized and sliced according
            to the maximum byte record length of the dataset.
            Required for multi-byte encoding schemes such as UTF-8.

            Byte serialization may not be interpretable until the whole dataset
            content is read and serialized.

            If the encoding is on the supported multi-byte encoding list,
            serialize is set to 'byte' automatically. See notes.

        next_record_char : str, optional
            The new line character used for writing records in a 1:1 relationship
            with lines. The actual character is not written to the dataset.
            The default value is "\n".
            Ignored if serialize is enabled.

        max_record_length : int, optional
            Overrides auto-discovery of maximum record length. Value 0 enables
            auto-discovery.

        fill_char : str, optional
            Character to fill the trailing free space of each record with.
            Supported with fixed record_length datasets only.
            Defaults to the selected encoding's whitespace character.

        validate_record_length: bool, optional
            Validates the record lengths of the data prior to writing when True.
            Validation is skipped when False.
            Defaults to False.

        Returns
        -------
            None

        Notes
        -----
            Multi-byte ncoding schemes currently supported:
                - UTF-8.
            The following parameters are stored in the object after each operation:
                - encoding, serialize, next_record_char
            If set, function calls can be made without passing the parameters.
        """
        logger.debug("Dataset.write method call")
        # logger.debug("attributes: %s", locals())
        payload_dict: dict[str, Any]
        payload_dict = {}

        if self.type in ("PDS", "PDSE") and not member_name:
            raise ValueError("Cannot write to PDS/PDSE dataset without member name.")

        if member_name:
            logger.debug("Appending member (%s) to dataset name", member_name)
            payload_name = f"{self.name}({member_name})"
            logger.debug("New dataset name: %s", payload_name)
        else:
            payload_name = self.name
        if encoding is not None:
            logger.debug("Overriding encoding parameter to: %s", encoding)
            payload_dict["encoding"] = encoding
        elif self.encoding is not None:
            logger.debug("Using object's stored parameter: %s", self.encoding)
            payload_dict["encoding"] = self.encoding
        if serialize is not None:
            payload_dict["serialize"] = serialize
        elif self.serialize is not None:
            payload_dict["serialize"] = self.serialize
        if next_record_char is not None:
            payload_dict["next_record_char"] = next_record_char
        elif self.next_record_char is not None:
            payload_dict["next_record_char"] = self.next_record_char
        if max_record_length is not None:
            payload_dict["max_record_length"] = max_record_length
        else:
            payload_dict["max_record_length"] = self.record_length

        logger.debug("attributes in payload: %s", payload_dict)
        write(
            dataset_name=payload_name,
            content=content,
            append=append,
            fill_char=fill_char,
            validate_record_length=validate_record_length,
            **payload_dict,
        )

        if "encoding" in payload_dict:
            self.encoding = payload_dict["encoding"]
        if "serialize" in payload_dict:
            self.serialize = payload_dict["serialize"]
        if "next_record_char" in payload_dict:
            self.next_record_char = payload_dict["next_record_char"]
        # TODO: store fill_char too.

    def delete(self) -> int:
        """Delete this dataset.

        Returns
        -------
        int
            Return code from z/OS. Zero if successful. Non-zero otherwise.
        """
        return delete(self.name)

    def read_as_bytes(
        self,
        member_name: str = "",
        number_of_records: int = 0,
        offset: int = 0,
        tail: bool = False
    ) -> list[bytes]:
        """
        Reads records as bytes from a dataset.

    Arguments
    ---------
    member_name : str
        The name of the member to read from, if any.
    records : int, optional
        The number of records to read. Default is 0 (read all).
    offset : int, optional
        The offset from the beginning of the dataset to start reading. Default is 0.
    tail : bool, optional
        If True, read from the end of the dataset instead of the beginning. Default is False.

    Returns
    -------
        list[bytes]: A list of bytes read from the dataset.
        """
        if member_name:
            logger.debug("Appending member (%s) to dataset name", member_name)
            payload_name = f"{self.name}({member_name})"
            logger.debug("New dataset name: %s", payload_name)
        else:
            payload_name = self.name

        return read_as_bytes(
            payload_name, records=number_of_records, offset=offset, tail=tail
        )

    def read(
        self,
        member_name: str = "",
        encoding: Union[str, None] = None,
        lines: int = 0,
        offset: int = 0,
        tail: bool = False,
        serialize: str = "record",
        next_record_char: str = "\n",
    ) -> str:
        """
        Read encoded text content from a non-VSAM dataset.

        Arguments
        ---------
        member_name : str, optional
            The name of the member to read. If empty, reads the entire dataset.
        encoding: str, optional
            The encoding used when the dataset is read.
            If not provided, uses the stored encoding.
            If no encoding is stored, defaults to "cp1047".
        lines : int, optional
            The number of lines to read. If 0, reads until the end of the dataset.
            Defaults to 0.
        offset : int, optional
            The offset from the beginning to start reading.
            Defaults to 0.
        tail : bool, optional
            If True, reads the dataset in reverse order.
            Defaults to False.
        serialize : str, optional
            The serialization method to use.
            Defaults to 'record'. Automatically set to 'byte' if encoding is on the
            supported multi-byte encoding list. See notes.
        next_record_char : str, optional
            The character that indicates a new record.
            If not provided, uses the stored one.
            If no new record character is stored, defaults to "\n".

        Returns
        -------
        str: The content read from the dataset as a python string.

        Notes
        -----
            Multi-byte ncoding schemes currently supported:
                - UTF-8.
        """
        logger.debug("Dataset.read method call")
        logger.debug("attributes: %s", locals())

        payload_dict: dict[str, Any]
        payload_dict = {}

        if member_name:
            logger.debug("Appending member (%s) to dataset name", member_name)
            payload_name = f"{self.name}({member_name})"
            logger.debug("New dataset name: %s", payload_name)
        else:
            payload_name = self.name
        if encoding is not None:
            logger.debug("Overriding encoding parameter to: %s", encoding)
            payload_dict["encoding"] = encoding
        elif self.encoding is not None:
            logger.debug("Using object's stored encoding parameter: %s", self.encoding)
            payload_dict["encoding"] = self.encoding
        if serialize is not None:
            logger.debug("Overriding serialize parameter to: %s", serialize)
            payload_dict["serialize"] = serialize
        elif self.serialize is not None:
            logger.debug(
                "Using object's stored serialize parameter: %s", self.serialize
            )
            payload_dict["serialize"] = self.serialize
        if next_record_char is not None:
            logger.debug("Overriding next_record_char parameter to: %s", next_record_char)
            payload_dict["next_record_char"] = next_record_char
        elif self.next_record_char is not None:
            logger.debug(
                "Using object's stored next_record_char parameter: %s",
                self.next_record_char,
            )
            payload_dict["next_record_char"] = self.next_record_char

        logger.debug("attributes in payload: %s", payload_dict)
        dataset_content = read(
            payload_name, lines=lines, offset=offset, tail=tail, **payload_dict
        )

        if "encoding" in payload_dict:
            self.encoding = payload_dict["encoding"]
        if "serialize" in payload_dict:
            self.serialize = payload_dict["serialize"]
        if "next_record_char" in payload_dict:
            self.next_record_char = payload_dict["next_record_char"]

        return dataset_content

def read_as_bytes(
    dataset_name: str | None = None,
    *,
    data_definition_name: str | None = None,
    records: int = 0,
    offset: int = 0,
    tail: bool = False,
) -> list[bytes]:
    """
    Returns the contents of a non-VSAM dataset as a list of bytes (one item per
    record).

    The dataset can be identified by either its dataset name or data definition
    name.

    Parameters
    ----------
    dataset_name : str, optional
        Name of the dataset to read.
        Cannot be used together with the `data_definition_name` argument.

    data_definition_name: str, optional
        Name of the data definition (DD) to read.
        Cannot be used together with the `dataset_name` argument.
        A DD must exist before it can be read.
        A DD can be created in one of the following ways:
            * Under MVS batch, defined with a DD statement in JCL.
            * Dynamically allocated, via `DYNALLOC` or equivalent z/OS services.

    number_of_records : int, optional
        Maximum number of records to read. Defaults to 0.
        If set to 0, all possible records will be read.

    offset : int, optional
        Offsets the starting index for reading. Defaults to 0.

    tail : bool, optional
        If True, the last n records will be returned. n must be specified in
        the `number_of_records` parameter. Defaults to False.

    Returns:
        list[bytes]
            A list of byte objects split by record.
    """
    logger.debug("datasets.read_as_bytes function call")
    logger.debug("arguments: %s", locals())

    if (dataset_name is None) == (data_definition_name is None):
        raise ValueError("Exactly one of `dataset_name` or `data_definition_name` must be provided")

    if dataset_name:
        file_name = dataset_name
        if not match_expression(r"^\/\/'.*\'$", dataset_name):
            file_name = f"//'{dataset_name}'"
            logging.debug("Formatted name %s", file_name)

    if data_definition_name:
        file_name = data_definition_name
        if not match_expression(r"^[Dd]{2}:.*$", data_definition_name):
            file_name = f"DD:{data_definition_name}"
            logging.debug("Formatted name %s", file_name)

    if not isinstance(records, int):
        raise TypeError("number_of_records must be an int")
    if not isinstance(offset, int):
        raise TypeError("offset must be an int")
    if not isinstance(tail, bool):
        raise TypeError("reverse must be a bool")

    dataset_stream = RecordIO(file_name, "r")
    if "F" in dataset_stream.recfm:
        Warning(
            "Strings read from datasets with fixed record formats may content trailing NULL bytes not printed by print()"
        )
    if tail:
        if records == 0:
            records = 1
        compound_offset = -(offset + records)
        dataset_stream.seek(compound_offset, 2)  # seek mode 2 "from end"
        dataset_content = dataset_stream.readrecords()
    else:
        dataset_stream.seek(offset, 0)  # seek mode 0 "from the start"
        dataset_content = dataset_stream.readrecords(records)

    dataset_stream.close()
    return dataset_content


def read(
    dataset_name: str | None = None,
    *,
    data_definition_name: str | None = None,
    encoding: str = "cp1047",
    lines: int = 0,
    offset: int = 0,
    tail: bool = False,
    serialize: str = "record",
    next_record_char: str = "\n",
) -> str:
    """
    Read encoded text content from a non-VSAM dataset identified by either
    its dataset name or data definition (DD) name.

    Exactly one of `dataset_name` or `data_definition_name` must be provided.

    Returns
    -------
    str
        Contents of the dataset

    Parameters
    ----------
    dataset_name : str, optional
        Name of the dataset to read.
        Cannot be used together with the `data_definition_name` argument.

    data_definition_name: str, optional
        Name of the data definition (DD) to read.
        Cannot be used together with the `dataset_name` argument.
        A DD must exist before it can be read.
        A DD can be created in one of the following ways:
            * Under MVS batch, defined with a DD statement in JCL.
            * Dynamically allocated, via `DYNALLOC` or equivalent z/OS services.

    encoding : str, optional
        The encoding character scheme used to represent the dataset's content.
        Defaults to 'cp1047'.

    serialize : str, optional
        The serialization method to use.
        Defaults to 'record'.
        If the encoding is on the supported multi-byte encoding list,
        serialize is set to 'byte' automatically. See notes.

    next_record_char : str, optional
        The new line character used for reading records in a 1:1 relationship
        with lines. The actual character is not present in the content of the dataset.
        The default value is "\n".
        Ignored if serialize is not set to  'record'.

    Notes
    -----
        Multi-byte ncoding schemes currently supported:
            - UTF-8.
    """
    logger.debug("read dataset function call")
    logger.debug("arguments: %s", locals())

    # argument type validation
    arg_dict = locals()
    arg_dict.pop("dataset_name")
    arg_dict.pop("data_definition_name")

    if dataset_name is not None and not isinstance(dataset_name, str):
        raise TypeError("dataset_name parameter must be a string")

    if data_definition_name is not None and not isinstance(data_definition_name, str):
        raise TypeError("data_definition_name parameter must be a string")

    multivar_type_validation(arg_dict, (str, int, int, bool, str, str))

    binary_records = read_as_bytes(
        dataset_name,
        data_definition_name=data_definition_name,
        records=lines,
        offset=offset,
        tail=tail
    )
    logger.debug("Dataset read as a binary object")

    # special serialization built-in cases
    if encoding in MULTIBYTE_ENCODINGS and serialize not in ("byte"):
        warnings.warn(
            f"{encoding} encoded content written through ZOAU must be deserialized."
            f"Automatically setting argument serialize to byte"
        )
        serialize = "byte"

    if serialize == "record":
        encoded_char = next_record_char.encode(encoding)
        logger.debug("Concatenating record with %s", encoded_char)
        dataset_content = encoded_char.join(binary_records)
    else:  # byte
        logger.debug("Concatenating without break characters")
        dataset_content = b"".join(binary_records)

    logger.debug("Encoding binary object as %s", encoding)
    encoded_buffer = codecs.decode(
        dataset_content,
        encoding,
        # type: ignore[arg-type, call-overload]
        errors="strict",
    )
    logger.debug("Finished encoding")

    return encoded_buffer


def read_head(
    dataset: str | None = None,
    *,
    data_definition_name: str | None = None,
    lines: int = 10,
    encoding: str = "cp1047",
    serialize: str = "record"
) -> str:
    """
    Get the head content of a non-VSAM dataset, defaults to 10 lines.

    Returns
    -------
    str : Contents of the dataset.

    Parameters
    ----------
    dataset: str, optional
        Name of the dataset to read.
        Cannot be used together with the `data_definition_name` argument.

    data_definition_name: str, optional
        Name of the data definition (DD) to read.
        Cannot be used together with the `dataset_name` argument.
        A DD must exist before it can be read.
        A DD can be created in one of the following ways:
            * Under MVS batch, defined with a DD statement in JCL.
            * Dynamically allocated, via `DYNALLOC` or equivalent z/OS services.

    lines : int, optional
        Read the first n lines from the dataset; defaults to 10.

    encoding: str, optional
        Expected encoding of the dataset

    serialize : str, optional
        The serialization method to use.
        Defaults to 'record'.
        If the encoding is on the supported multi-byte encoding list,
        serialize is set to 'byte' automatically. See notes.

    Notes
    -----
        Multi-byte ncoding schemes currently supported:
            - UTF-8.
    """
    logger.debug("read_head dataset function call")
    logger.debug("arguments: %s", locals())

    return read(dataset, data_definition_name=data_definition_name, lines=lines, encoding=encoding, serialize=serialize)


def write(
    dataset_name: str,
    content: str,
    append: bool = False,
    encoding: str = "cp1047",
    serialize: str = "record",  # Record, character(future), byte
    next_record_char: str = "\n",  # only for record serialization.
    max_record_length: int = 0,
    fill_char: str = " ",  # only for non-serialized, fixed record length.
    validate_record_length: bool = True,  # only for non-serialized
) -> None:
    """Writes encoded text content to a z/OS dataset.

    Arguments
    ---------
        dataset_name : str
            Target dataset name.

        content : str
            Content to write.

        append : bool, optional
            Appends content trailing any previous content. Defaults to False.

        encoding : str, optional
            The encoding character scheme used to represent the dataset's content.
            Defaults to 'cp1047'.

        serialize : str, optional
            If set to record, the content will be serialized and written with a
            1:1 mapping of lines to records.

            If set to 'byte', the content will be serialized and sliced according
            to the maximum byte record length of the dataset.
            Required for multi-byte encoding schemes such as UTF-8.

            Byte serialization may not be interpretable until the whole dataset
            content is read and serialized.

            If the encoding is on the supported multi-byte encoding list,
            serialize is set to 'byte' automatically. See notes.

        next_record_char : str, optional
            The new line character used for writing records in a 1:1 relationship
            with lines. The actual character is not written to the dataset.
            The default value is "\n".

            Ignored if serialize is enabled.

        max_record_length : int, optional
            Overrides auto-discovery of maximum record length. Value 0 enables
            auto-discovery.

        fill_char : str, optional
            Character to fill the trailing free space of each record with.
            Supported with fixed record_length datasets only.
            Defaults to the selected encoding's whitespace character.

        validate_record_length: bool, optional
            Validates the record lengths of the data prior to writing when True.
            Validation is skipped when False.
            Defaults to False.

    Returns
    -------
        None

    Notes
    -----
        Multi-byte ncoding schemes currently supported:
            - UTF-8.

    """
    logger.debug("dataset write call")
    # logger.debug("arguments: %s", locals())

    # argument type validation
    multivar_type_validation(locals(), (str, str, bool, str, str, str, int, str, bool))

    # fill_char must be a single character or less.
    if len(fill_char) > 1:
        raise ValueError("fill_char must be a single character")

    if serialize not in ("record", "byte"):
        raise ValueError("serialize must be one of: (record, byte)")

    # Exit if format includes backslashes (cannot be parsed for id)
    if match_expression(r"^\/\/'.*\'$", dataset_name):
        raise ValueError("Explicit backslash format is not supported")

    # Writing case identification
    # fopen() can't resolve relative GDG names.
    if identify_dtype(dataset_name, "RELGDG"):
        raise ValueError(
            "datasets.write() is unable to resolve relative GDS names. "
            "Alternatively use a GenerationDataGroupView relative addressing, "
            "for example: GenerationDataGroupView.generations[i].write(content)"
        )

    # Members can't be appended
    is_member: bool = False
    if identify_dtype(dataset_name, "MEMBER"):
        is_member = True  # kept to allow member creation
        if append:
            raise ValueError("Direct append to member is not supported")

    # Serialize by byte for multi-byte encodings.
    if encoding in MULTIBYTE_ENCODINGS and serialize not in ("byte"):
        warnings.warn(
            f"mutli-byte {encoding} content must be serialized by  in dataset;"
            f"auto-setting serialize to byte.\n"
            f"Content will be sliced based on record length."
        )
        serialize = "byte"

    # formats dataset_name with backslashes format.
    dataset_name = rf"//'{dataset_name}'"
    logging.debug("Dataset name reformatted to %s", dataset_name)

    # No implicit creation, except for new members
    try:
        stream = RecordIO(dataset_name, "r")
    except OSError as os_error:
        if os_error.errno == 67:
            if is_member:
                stream = RecordIO(dataset_name, "w")
            else:
                raise FileExistsError(f"Unable to locate {dataset_name}") from os_error
        else:
            raise FileExistsError(f"Unable to locate {dataset_name}") from os_error

    # Metadata auto discovery from open stream
    # max_record_length
    if max_record_length == 0:  # if max_record_length is unknown
        logger.debug("Fetching max record length")
        max_record_length = stream.maxreclen
        # TODO: Error if overridden record_length is longer than the actual one.
    # record_format
    record_format = stream.recfm
    # Variable record length
    if "V" in record_format:
        logger.debug("Adjusting for '%s' variable record format.", record_format)
        max_record_length = max_record_length - 4
        logger.debug("max_record_length: %i", max_record_length)

    stream.close()

    # SERIALIZATION

    if serialize == "record":
        lines_to_write = content.split(next_record_char)
        logger.debug("Lines to write with RECORD serialization: %i", len(lines_to_write))

        # Accidental deletion protection.
        # A bit expensive, but protects the dataset content if there's a line exceeding the limit.
        # If the record format is variable, max_record_length is reduced to allow space
        # for the leading record length bytes.
        if validate_record_length:
            logger.debug("validating record length")
            for i, byte_line in enumerate(lines_to_write):
                if len(byte_line) > max_record_length:
                    raise ValueError(
                        f"Line {i} of length {len(byte_line)} exceeds max_record_length: "
                        f"{max_record_length}.\n"
                        f"{dataset_name} content preserved"
                    )

        # Can be removed if a perfomance boost is needed.
        lines_to_write = list(
            map(
                lambda line: line.encode(encoding=encoding, errors="strict"),
                lines_to_write,
            )
        )
    elif serialize == "byte":  # left intentionally as elif for future implemetations
        binary_content = content.encode(encoding=encoding, errors="strict")
        lines_to_write = list(slicer(binary_content, max_record_length))
        logger.debug(
            "Lines to write with RECORD serialization: %i * %i bytes",
            len(lines_to_write),
            len(lines_to_write[0]),
        )

    # Open to write
    mode = "a" if append else "w"
    try:
        stream = RecordIO(dataset_name, mode, recfm="*")
    except OSError as os_error:
        error_message = ""
        if os_error.errno == 47:
            error_message = (
                "Unable to open dataset for writing.\n"
                "Possible cause: Cannot write to partitioned dataset without member name."
            )
        raise DatasetWriteError(error_message) from os_error
    logger.debug("opened stream %s in %s mode, recfm='*'", dataset_name, mode)

    # fill char setup
    if "F" in record_format:
        logger.debug("Filling character: %s", fill_char)
    logger.debug("writing lines\n")

    # Writing
    for i, byte_line in enumerate(lines_to_write):
        if "F" in record_format:
            fill_byte = fill_char.encode(encoding=encoding, errors="strict")
            byte_line = byte_line.ljust(max_record_length, fill_byte)
        try:
            stream.write(byte_line)
        except Exception as ex:
            # A general exception seems to be the only one working to catch this OSError.
            error_message = (
                f"Unable to open record {i+1} for writing. "
                f"Make sure there is space available on the dataset."
                f"{i} records have been written."
            )
            raise RuntimeError(error_message) from ex
        logger.debug("wrote line %d", i)
    stream.close()
    logger.debug("Wrote %i lines", len(lines_to_write))


def _create(name: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dtouch)"""
    # build options
    options = "-j "
    options += parse_universal_arguments(**kwargs)

    if "dataset_type" in kwargs:
        options += f"-t{kwargs.get('dataset_type')} "

    if "primary_space" in kwargs:
        options += f"-s{kwargs.get('primary_space')} "

    if "secondary_space" in kwargs:
        options += f"-e{kwargs.get('secondary_space')} "

    if "block_size" in kwargs:
        options += f"-B{kwargs.get('block_size')} "

    if "record_format" in kwargs:
        options += f"-r{kwargs.get('record_format')} "

    if "storage_class_name" in kwargs:
        options += f"-c{kwargs.get('storage_class_name')} "

    if "data_class_name" in kwargs:
        options += f"-D{kwargs.get('data_class_name')} "

    if "management_class_name" in kwargs:
        options += f"-m{kwargs.get('management_class_name')} "

    if "record_length" in kwargs:
        options += f"-l{kwargs.get('record_length')} "

    if "key_length" in kwargs and "key_offset" in kwargs:
        options += f"-k{kwargs.get('key_length')}:{kwargs.get('key_offset')} "

    if "directory_blocks" in kwargs:
        options += f"-b{kwargs.get('directory_blocks')} "

    if "volumes" in kwargs:
        options += f"-V{kwargs.get('volumes')} "

    if "device_unit" in kwargs:
        options += f"-u{kwargs.get('device_unit')} "

    if "average_block_length" in kwargs:
        options += f"-C{kwargs.get('average_block_length')} "

    options += f' -- "{clean_dataset_name(name)}"'

    logger.debug("ZOAU_CORE call: dtouch %s", options)
    response = call_zoau_library("dtouch", options)

    return ZOAUResponse.from_dict(response)


def create(name: str, **kwargs) -> Dataset:
    """Create a z/OS dataset.

    NOTE: This function does not create dataset members. An attempt to do so
    will result in an error.

    Returns
    -------
    Dataset object.

    Parameters
    ----------
    name : str
        Name of the dataset.

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------

    dataset_type : str, optional
        Type of dataset. Uses system's default if not provided.
        Options: KSDS, ESDS, RRDS, LDS, SEQ, LARGE, PDS, PDSE, LIBRARY.

    primary_space : str, optional
        Space to allocate for the dataset. Defaults to 5M.
        Use the following suffixes to specify the space allocation unit:
            - K or KB (kilobytes)
            - M or MB (megabytes)
            - G or GB (gigabytes)
            - C or CYL (cylinders)
            - T or TRK (tracks)
            - BLK (blocks)
        If no suffix is specified, the size is calculated as bytes.
        When using bytes, KB, MB, or GB units the number of tracks to allocate
        is rounded up.
        The following constants are used to convert between different unit
        types:
            - 1 KB = 1024 bytes
            - 1 MB = 1024 KB
            - 1 GB = 1024 MB
            - 1 track = 56664 bytes
            - 1 cylinder = 15 tracks
        When using block units the `average_block_length` argument must be
        specified to compute the amount of space to allocate.
        Examples: 1M, 2MB, 1G, 2GB

    secondary_space : str, optional
        Secondary (extent) space to allocate for the dataset.
        Defaults to 1/10 of primary space.
        Use the following suffixes to specify the space allocation unit:
            - K or KB (kilobytes)
            - M or MB (megabytes)
            - G or GB (gigabytes)
            - C or CYL (cylinders)
            - T or TRK (tracks)
            - BLK (blocks)
        If no suffix is specified, the size is calculated as bytes.
        When using bytes, KB, MB, or GB units the number of tracks to allocate
        is rounded up.
        The following constants are used to convert between different unit
        types:
            - 1 KB = 1024 bytes
            - 1 MB = 1024 KB
            - 1 GB = 1024 MB
            - 1 track = 56664 bytes
            - 1 cylinder = 15 tracks
        When using block units the `average_block_length` argument must be
        specified to compute the amount of space to allocate.
        Examples: 1M, 2MB, 1G, 2GB

    block_size : int, optional
        Block size of dataset. Default varies on record format: F=80, FB/FBS=32720, FBA=32718,
         VB/VBS=32760, VBA=32743.

    record_format : str, optional
        Record format of dataset. Options: FB (default), F, FBA, FBS, U, VB, VBA, VBS.

    storage_class_name : str, optional
        The storage class for an SMS-managed dataset.
        Required for SMS-managed datasets that do not match an SMS-rule.
        Not valid for datasets that are not SMS-managed.
        Note that all non-linear VSAM datasets are SMS-managed.

    data_class_name : str, optional
        Data class name for dataset.

    management_class_name : str, optional
        The management class for an SMS-managed dataset.
        Optional for SMS-managed datasets that do not match an SMS-rule.
        Not valid for datasets that are not SMS-managed.
        Note that all non-linear VSAM datasets are SMS-managed.

    record_length : int, optional
        Logical record length, expressed in bytes. Defaults vary on format.
        F/FB/FBS=80, FBA=133, VB/VBA/VBS=137, U=0. For variable datasets, the length must include the
        4-byte prefix area.

    key_length : int, optional
        Mutually inclusive with key_offset. Required for KSDS datasets.

    key_offset : int, optional
        Mutually inclusive with key_length. Required for KSDS datasets.

    volumes : str, optional
        Comma separated list of volume serials. Offline volumes are not considered.

    directory_blocks : int, optional
        Directory blocks for PDS-type datasets. Default 5.

    device_unit : str, optional
        Unit name of the device that the dataset will reside on.
        To target a specific device number, you must precede the address with
        a slash (/) character.

    average_block_length: int, optional
        Average data block length, in bytes, the system will use when computing
        the amount of space to allocate. When using this argument you must
        specify the primary and secondary space in block units.

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls

    DatasetVerificationError
        Failed to verify the creation of the dataset after ZOAU call
    """
    logger.debug("create dataset function call")
    logger.debug("name: %s", name)
    logger.debug("kwargs: %s", kwargs)

    name = name.replace('"', "")
    response = _create(name, **kwargs)

    if response.rc != 0:
        raise DatasetCreateException(response)

    # dtouch may have assigned a different name, retrieve this name from the response.
    # e,g. Generation dataset relative name -> Generation dataset absolute name.

    response_json, _ = zoau_json_load(response.stdout_response)
    logger.debug("response_json: %s", response_json)

    try:
        assigned_name = str(response_json.get("dsname"))
    except KeyError as exc:
        raise KeyError("Missing dsname key from JSON") from exc

    try:
        dataset_type = kwargs.get("dataset_type", "")
        if dataset_type.upper() in ["KSDS", "ESDS", "RRDS", "LDS"]:
            dataset = list_vsam_datasets(assigned_name)[0]
        else:
            dataset = list_datasets(assigned_name)[0]
    except:
        raise DatasetVerificationError(name)

    return dataset


def _delete(dataset: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (drm)"""
    # clean input
    dataset = clean_dataset_name(dataset)

    # build options
    options = ""
    options += parse_universal_arguments(**kwargs)

    no_scratch = kwargs.get("no_scratch", False)
    if not isinstance(no_scratch, bool):
        raise TypeError("no_scratch should be True or False")

    purge = kwargs.get("purge", False)
    if not isinstance(purge, bool):
        raise TypeError("purge should be True or False")

    if no_scratch:
        options += "-n "

    if purge:
        options += "-p "

    options += f' -- "{dataset}"'

    # call shared library
    logger.debug("ZOAU_CORE call: drm %s", options)
    response = call_zoau_library("drm", options)

    return ZOAUResponse.from_dict(response)


def delete(dataset: str, **kwargs) -> int:
    """
    Delete a z/OS non-VSAM dataset, VSAM cluster, generation dataset, or an
    empty generation data group.

    Returns
    -------
    int
        Return code from z/OS

    Parameters
    ----------
    dataset : str
        Dataset to delete

    Other Parameters
    ----------------
    no_scratch : bool, optional
        When set to True, non-VSAM datasets are uncataloged but are not scratched
        from the VTOC of the volumes on which they reside.
        The default value is False.

    purge : bool, optional
        When set to True, deletes non-VSAM datasets even if their retention
        periods have not expired.
    """
    logger.debug("delete dataset function call")
    logger.debug("dataset: %s", dataset)
    logger.debug("kwargs: %s", kwargs)

    response = _delete(dataset, **kwargs)
    return response.rc


def _copy(source: str, target: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dcp)"""
    # clean input
    source = clean_dataset_name(source)
    target = clean_dataset_name(target)

    # build options
    options = ""
    options += parse_universal_arguments(**kwargs)

    alias_arg = "alias"
    executable_arg = "executable"
    force_arg = "force"

    force_flag = kwargs.get(force_arg, False)
    if isinstance(force_flag, bool):
        if force_flag:
            options += "-f "
    else:
        raise TypeError(f"{force_arg} should be a boolean variable")

    alias_flag = kwargs.get(alias_arg, False)
    if not isinstance(alias_flag, bool):
        raise TypeError(f"{alias_arg} should be a boolean variable")

    executable_flag = kwargs.get(executable_arg, False)
    if not isinstance(executable_flag, bool):
        raise TypeError(f"{executable_arg} should be a boolean variable")

    if executable_flag:
        options += "-X "
        if alias_flag:
            options += "-I "
    else:
        if alias_flag:
            options += "-i "

    # The "--" disables further argument processing
    options += f'-- "{source}" "{target}"'

    # call shared library
    logger.debug("ZOAU_CORE call: dcp %s", options)
    response = call_zoau_library("dcp", options)
    return ZOAUResponse.from_dict(response)


def copy(source: str, target: str, **kwargs) -> int:
    """
    Copy a z/OS source (dataset, zFS file) to a z/OS target.

    Returns
    -------
    int
        RC from z/OS.

    Parameters

    ----------
    source : str
        Absolute path of z/OS dataset or zFS file to copy from.

    target : str
        Absolute path of z/OS dataset or zFS file to copy to.

    kwargs: dict, optional
        Additional parameters (see other parameters).

    Other Parameters
    ----------------
    alias : bool
        If the source dataset has aliases, they will be recreated in the target.
        dataset.

    executable : bool
        This should be set if the source dataset is an executable.

    force : bool
        Forces the copy.
        WARNING: Use of this option could lead to permanent loss of the original target information.

        NOTE: If a dataset member has aliases, and is NOT a program
        object, copying that member to a dataset that is in use will result in
        the aliases not being preserved in the target dataset. When this scenario
        occurs an exception will be raised, along with an error message and a non-zero return code.

    Notes
    -----
    Generation data sets (GDS) are supported with the following considerations:
        * The generation data group (GDG) is not locked when referencing a GDS.
        * Relative names have their scope in the function call. This means that two
          consecutive datasets.copy calls that target a new generation, i.e. "GDG(+1)",
          result in the creation of two consecutive new generations.

    Generation data groups (GDG) are supported as `source`, and can be copied to a new
    GDG as `target`. The source GDG attributes and all its active generations are copied
    to the target. The source GDG base will not be locked, so prefer a job to ensure the
    GDG order is protected from concurrent operations.

    Raises
    ------
    ZOAUException
        See message for details."""

    logger.debug("copy dataset dataset function call")
    logger.debug("source: %s", source)
    logger.debug("target: %s", target)
    logger.debug("kwargs: %s", kwargs)

    response = _copy(source, target, **kwargs)
    if response.rc > 0:
        raise ZOAUException(response)

    return response.rc


def exists(dataset: str, **kwargs) -> bool:
    """
    Check whether or not a dataset exists.
    The function checks the catalog for the following entries:
        * Dataset aliases.
        * Generation datasets (specified by absolute name).
        * Non-VSAM datasets.
        * VSAM alternate indexes.
        * VSAM clusters.
        * VSAM paths.

    Returns
    -------
    bool
        Whether or not the dataset was found

    Parameters
    ----------
    dataset : str
        The dataset to check for

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls
    """
    logger.debug("exists dataset function call")
    logger.debug("dataset: %s", dataset)

    dataset = clean_dataset_name(dataset)
    options = "-t AIX -t ALIAS -t CLUSTER -t GDS -t NONVSAM -t PATH "
    options += f'"{dataset}"'
    logger.debug("ZOAU_CORE call: dls %s", options)
    response = ZOAUResponse.from_dict(call_zoau_library("dls", options))

    if response.rc not in (1, 0):
        raise ZOAUException(response)

    return response.rc == 0


def _move(source: str, target: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dmv)"""
    # clean input
    source = clean_dataset_name(source)
    target = clean_dataset_name(target)

    # build options
    options = ""
    options += parse_universal_arguments(**kwargs)
    options += f'"{source}" "{target}"'

    # call shared library
    logger.debug("ZOAU_CORE call: dmv %s", options)
    response = call_zoau_library("dmv", options)

    return ZOAUResponse.from_dict(response)


def move(source: str, target: str, **kwargs) -> bool:
    """
    Move (rename) a non-VSAM dataset or generation data group (GDG).

    Returns
    -------
    int
        Return code from z/OS

    Parameters
    ----------
    source : str
        The source dataset name or GDG base name.

    target : str
        The target dataset name or GDG base name.

    Notes
    -----
    The generation dataset relative name syntax is supported.
    move() can only rename generation data groups and generation data sets
    located on disk.

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls
    """
    logger.debug("move dataset function call")
    logger.debug("source: %s", source)
    logger.debug("target: %s", target)
    logger.debug("kwargs: %s", kwargs)

    response = _move(source, target, **kwargs)

    if response.rc > 0:
        raise ZOAUException(response)

    return response.rc


def _compare(source: str, target: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (ddiff)"""
    # clean inputs
    source = clean_dataset_name(source)
    target = clean_dataset_name(target)

    # build options
    options = ""
    options += parse_universal_arguments(**kwargs)

    if "lines" in kwargs:
        options += f"-C{kwargs.get('lines')} "

    if "columns" in kwargs:
        options += f"-c{kwargs.get('columns')} "

    if "ignore_case" in kwargs and kwargs.get("ignore_case"):
        options += "-i "

    if "tmphlq" in kwargs:
        options += f"-Q\"{kwargs.get('tmphlq')}\" "

    options += f'"{source}" "{target}"'

    logger.debug("ZOAU_CORE call: ddiff %s", options)
    response = call_zoau_library("ddiff", options)

    return ZOAUResponse.from_dict(response)


def compare(source: str, target: str, **kwargs) -> Union[str, None]:
    """
    Compare two datasets, output the ISRSUPC output.

    Returns
    -------
    str : ISRSUPC output
        The output from ISRSUPC

    None
        Datasets are the same

    Parameters
    ----------
    source : str
        First dataset to compare

    target : str
        Second dataset to compare

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    lines : str, int
        Display n lines of context around a displayed line

    columns : str, int
        Specify column comparison specifiers to pass to SUPERCE

    ignore_case : bool
        Ignore case in comparison

    tmphlq : str
        Use an alternative high-level qualifier (HLQ) for temporary dataset
        names.

    Notes
    -----
    The arguments support the generation dataset (GDS) relative name notation.
    """
    logger.debug("compare dataset function call")
    logger.debug("source: %s", source)
    logger.debug("target: %s", target)
    logger.debug("kwargs: %s", kwargs)

    response = _compare(source, target, **kwargs)

    if response.rc > 1:
        # ddiff rc = 0 for equality, rc = 1 inequality, rc > 1 error
        raise ZOAUException(response)

    if not response.stdout_response:
        return None

    return response.stdout_response


def _search(dataset: str, value: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dgrep)"""
    # clean inputs
    source = clean_dataset_name(dataset)
    value = clean_shell_input(value)

    # build options
    options = ""
    options += parse_universal_arguments(**kwargs)

    if "lines" in kwargs:
        options += f"-C{kwargs.get('lines')} "

    if "ignore_case" in kwargs and kwargs.get("ignore_case"):
        options += "-i "

    if "display_lines" in kwargs and kwargs.get("display_lines"):
        options += "-n "

    if "print_datasets" in kwargs and kwargs.get("print_datasets"):
        options += "-v "

    if "count_lines" in kwargs and kwargs.get("count_lines"):
        options += "-c "

    if "json" in kwargs and kwargs.get("json"):
        options += "-j "

    # The double hyphen terminates argument processing so that "value"
    # isn't treated as an argument.
    options += f'-- "{value}" "{source}"'

    # call shared library
    logger.debug("ZOAU_CORE call: dgrep %s", options)
    response = call_zoau_library("dgrep", options)

    return ZOAUResponse.from_dict(response)


def search(dataset: str, value: str, **kwargs) -> Union[str, None]:
    """
    Search a dataset using ISRSUPC.

    Returns
    -------
    str
        The ISRSUPC output from the search command

    None
        Content was not found in dataset

    Parameters
    ----------
    dataset : str
        The dataset to search

    value : str
        The string to search for in dataset

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    count_lines : bool, optional
        Print only a count of matched lines in the dataset

    display_lines : bool, optional
        Display the line number for each match

    lines : int, optional
        Number of lines to be shown before and after each match

    ignore_case : bool, optional
        Ignore case for search

    json : bool, optional
        Get the results in JSON format. Default is False.

        When enabled, the output is a JSON string with this structure:
        {
            "data": {
                <sequential DS name>: <string>,
                <partitioned DS name>: {
                    <member name>: <string>,
                    ...
                },
                ...
            },
            "program": <string>,
            "options": <string>,
            "rc": <string>,
        }

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls
    """
    logger.debug("search dataset function call")
    logger.debug("dataset: %s", dataset)
    logger.debug("value: %s", value)
    logger.debug("kwargs: %s", kwargs)

    response = _search(dataset, value, **kwargs)

    if response.rc > 1:
        raise ZOAUException(response)

    if not response.stdout_response:
        return None

    return response.stdout_response


def search_dictionary(dataset: str, value: str, **kwargs) -> Union[dict, None]:
    """
    Search a dataset using ISRSUPC.

    Returns
    -------
    dict
        The records found.

    Parameters
    ----------
    dataset : str
        The dataset to search

    value : str
        The string to search for in dataset

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    count_lines : bool, optional
        Print only a count of matched lines in the dataset

    display_lines : bool, optional
        Display the line number for each match

    lines : int, optional
        Number of lines to be shown before and after each match

    ignore_case : bool, optional
        Ignore case for search

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls
    """
    logger.debug("search dataset function call")
    logger.debug("dataset: %s", dataset)
    logger.debug("value: %s", value)
    logger.debug("kwargs: %s", kwargs)

    response = _search(dataset, value, json=True, **kwargs)
    data, meta = zoau_json_load(response.stdout_response)
    logger.debug("json data: %s", data)

    if not data:
        return None

    if int(meta["rc"]) > 1:
        raise ZOAUException(response)

    return data


def _dls_call(
    pattern: str,
    volume: Union[str, None] = None,
    name_only=False,
    migrated=False,
    fetch_directory_blocks=False,
    list_alias: bool = False,
    list_nvsam: bool = False,
    list_gdg: bool = False,
    list_gds: bool = False,
    **kwargs,
) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dls)"""
    # clean input
    pattern = clean_dataset_name(pattern)
    if not isinstance(name_only, bool):
        raise TypeError("name_only parameter must be a bool")
    if not isinstance(migrated, bool):
        raise TypeError("migrated parameter must be a bool")
    if not isinstance(fetch_directory_blocks, bool):
        raise TypeError("fetch_directory_blocks parameter must be a bool")
    if migrated and not name_only:
        raise MissingFunctionParameter(
            "Listing migrated datasets require the parameter name_only to be True"
        )
    if volume is not None:
        if not isinstance(volume, str):
            raise TypeError("volume parameter must be a string")

    # build options
    options = ""
    options += parse_universal_arguments(**kwargs)

    if migrated and name_only:
        options += "-m "

    if not name_only:
        options += "-b -j -l -s -T -u "

        # Directory blocks are expensive to fetch, requires to open the PDS/E
        # datasets for read. This may also cause dataset contention problems,
        # so it is better to have them optional.
        if fetch_directory_blocks:
            options += "-B "

    if volume is not None:
        options += f"-V {volume} "

    if list_alias:
         options += f"-t ALIAS "

    if list_nvsam:
         options += f"-t NONVSAM "

    if list_gdg:
         options += f"-t GDG "

    if list_gds:
         options += f"-t GDS "

    options += " -- "
    options += f'"{pattern}"'

    # call shared library
    logger.debug("ZOAU_CORE call: dls %s", options)
    response = call_zoau_library("dls", options)

    return ZOAUResponse.from_dict(response)


def list_datasets(
    pattern: str,
    volume: Union[str, None] = None,
    include_aliases : bool = False,
    fetch_directory_blocks : bool = False,
    **kwargs
) -> list[Dataset]:
    """
    Returns a list of Dataset objects matching the supplied pattern.

    Returns
    -------
    list[Dataset]
        List of Dataset objects

    list[]
        Empty list if no dataset is found

    Parameters
    ----------
    pattern : str
        Pattern to match. e.g IBMUSER.*

    volume : str, optional
        Filter dataset list by volume name.

    include_aliases : bool, optional
        Include dataset aliases.

    fetch_directory_blocks: bool, optional
        When true, gets the total and used directory blocks for partitioned
        datasets.

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------

    debug: bool
        Enable debug messages (only for exceptions)

    verbose: bool
        Enable verbose output (only for exceptions)

    Notes
    -----
    A multi-volume dataset will return a Dataset object for each utilized volume.

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls. See message for details
    """
    logger.debug("listing dataset function call")
    logger.debug("pattern: %s", pattern)
    logger.debug("volume: %s", pattern)
    logger.debug("kwargs: %s", kwargs)

    response = _dls_call(
        pattern=pattern,
        volume=volume,
        fetch_directory_blocks=fetch_directory_blocks,
        list_nvsam=True,
        list_gds=True,
        list_alias=include_aliases,
        **kwargs
    )

    # Error from dls call
    if response.rc not in (0, 1):
        raise DatasetFetchException(response)

    # No dataset match
    if not response.stdout_response:
        return []

    response_json, _ = zoau_json_load(response.stdout_response)
    logger.debug("json data: %s", response_json)

    dict_list: list = []
    try:
        dict_list = response_json.get("datasets")  # type: ignore
    except KeyError as exc:
        raise KeyError("Missing dataset key from JSON") from exc

    return [Dataset.from_core_json(ds_dict) for ds_dict in dict_list]


def list_dataset_names(
    pattern: str, volume: Union[str, None] = None, migrated: bool = False, **kwargs
) -> list[str]:
    """Returns a list of dataset names matching the supplied pattern.

    Returns
    -------
    list[str]
        List of dataset names matching the pattern.

    list[]
        Empty list if no dataset is found

    Parameters
    ----------
    pattern : str
        Dataset search pattern.

    migrated : bool, optional
        Enables fetching information from migrated datasets, by default False

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    debug: bool
        Enable debug messages (only for exceptions)

    verbose: bool
        Enable verbose output (only for exceptions)
    """
    logger.debug("listing name only dataset function call")
    logger.debug("pattern: %s", pattern)
    logger.debug("volume: %s", volume)
    logger.debug("migrated: %s", pattern)

    response = _dls_call(
        pattern=pattern,
        volume=volume,
        name_only=True,
        list_nvsam=True,
        list_gds=True,
        migrated=migrated,
        **kwargs
    )

    if response.rc not in (0, 1):
        raise DatasetFetchException(response)

    if not response.stdout_response:
        return []

    return list(response.stdout_response.rstrip().split("\n"))


def _list_members(pattern: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (mls)"""
    # clean input
    pattern = clean_dataset_name(pattern)

    alias_arg = "alias"
    alias_flag = kwargs.get(alias_arg, True)

    if not isinstance(alias_flag, bool):
        raise TypeError(f"{alias_arg} should be a boolean variable")

    # build options
    options = ""
    options += parse_universal_arguments(**kwargs)

    if not alias_flag:
        options += "-H "

    options += f'"{pattern}"'

    # call shared library
    logger.debug("ZOAU_CORE call: mls %s", options)
    response = call_zoau_library("mls", options)

    return ZOAUResponse.from_dict(response)


def list_members(pattern: str, **kwargs) -> list[str]:
    """
    Get a list of members from a dataset.

    Returns
    -------
    list[str]
        Members contained within dataset

    list[]
        Empty list if no members were found

    Parameters
    ----------
    pattern : str
        The dataset pattern to search

    Other Parameters
    ----------------
    alias : bool
        Include member aliases. True by default.

    """
    logger.debug("list_members dataset function call")
    logger.debug("pattern: %s", pattern)
    logger.debug("kwargs: %s", kwargs)

    response = _list_members(pattern, **kwargs)

    # mls RC - 0 ok, RC - 2 no members match patten
    if response.rc != 0 and response.rc != 2:
        raise ZOAUException(response)

    if not response.stdout_response:
        return []

    return response.stdout_response.split()


def _delete_members(pattern: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (MRM)"""
    # clean input
    pattern = clean_dataset_name(pattern)

    # build options
    options = ""
    options += parse_universal_arguments(**kwargs)

    force = kwargs.get("force") or False
    if not isinstance(force, bool):
        raise TypeError("'force' should be True or False")

    if force:
        options += "-f "

    options += f' "{pattern}"'

    # call shared library
    logger.debug("ZOAU_CORE call: mrm %s", options)
    response = call_zoau_library("mrm", options)

    return ZOAUResponse.from_dict(response)


def delete_members(pattern: str, **kwargs) -> int:
    """
    Delete members contained in a dataset.

    Returns
    -------
    int
        Return code from z/OS

    Parameters
    ----------
    pattern : str
        Dataset pattern to match

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    force : bool, optional
        Force the deletion of a member that is in use.

    """
    logger.debug("delete_members dataset function call")
    logger.debug("pattern: %s", pattern)
    logger.debug("kwargs: %s", kwargs)

    response = _delete_members(pattern, **kwargs)
    return response.rc


def _move_member(dataset: str, source: str, target: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (mmv)"""
    # clean input
    dataset = clean_dataset_name(dataset)
    source = clean_shell_input(source)
    target = clean_shell_input(target)

    # build options
    options = ""
    options += parse_universal_arguments(**kwargs)
    options += f'"{dataset}" "{source}" "{target}"'

    # call shared library
    logger.debug("ZOAU_CORE call: mmv %s", options)
    response = call_zoau_library("mmv", options)
    return ZOAUResponse.from_dict(response)


def move_member(dataset: str, source: str, target: str, **kwargs) -> int:
    """
    Move (rename) a member.

    Returns
    -------
    int
        Return code from z/OS

    Parameters
    ----------
    dataset : str
        The dataset that contains the member

    source : str
        The current member name

    target : str
        The desired member name
    """
    logger.debug("move_member dataset function call")
    logger.debug("dataset: %s", dataset)
    logger.debug("source: %s", source)
    logger.debug("target: %s", target)
    logger.debug("kwargs: %s", kwargs)

    response = _move_member(dataset, source, target, **kwargs)
    return response.rc


def _find_member(member: str, concatenation: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dwhence)"""
    # clean input
    member = clean_shell_input(member)
    concatenation = clean_dataset_name(concatenation)

    # build options
    options = "-j "
    options += parse_universal_arguments(**kwargs)
    options += f'-- "{member}" "{concatenation}"'

    # call shared library
    logger.debug("ZOAU_CORE call: dwhence %s", options)
    response = call_zoau_library("dwhence", options)

    return ZOAUResponse.from_dict(response)


def find_member(member: str, concatenation: str, **kwargs) -> Union[str, None]:
    """
    Find dataset that contains member within a concatenation.
    Returns the first dataset that contains member.

    Returns
    -------
    str
        The dataset name containing the member

    None
        If no member was found

    Parameters
    ----------
    member : str
        The member to find

    concatenation : str
        The concatenation of dataset names, separated by colons
        (e.g "IBMUSER.A:IBMUSER.B")

    Examples
    --------
    datasets.find_member("PGM", ":".join("IBMUSER.A", "IBMUSER.B"))

    Notes
    -----
    find_member() supports operations over generation datasets (GDS).
    """
    logger.debug("find_member dataset function call")
    logger.debug("member: %s", member)
    logger.debug("concatenation: %s", concatenation)
    logger.debug("kwargs: %s", kwargs)

    response = _find_member(member, concatenation, **kwargs)
    if response.rc:
        return None

    json_data, _ = zoau_json_load(response.stdout_response)
    logger.debug("json_data: %s", json_data)
    return json_data.get("result", None)


def _get_hlq(**kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (hlq)"""
    options = ""
    options += parse_universal_arguments(**kwargs)

    logger.debug("ZOAU_CORE call: hlq %s", options)
    response = call_zoau_library("hlq", options)

    return ZOAUResponse.from_dict(response)


def get_hlq(**kwargs) -> str:
    """
    Returns the active TSO high-level qualifier

    Returns
    -------
    str
        The active TSO high-level qualifier
    """
    logger.debug("hlq dataset function call")
    logger.debug("kwargs: %s", kwargs)

    response = _get_hlq(**kwargs)
    return response.stdout_response.rstrip("\n")


def _tmp_name(high_level_qualifier: Optional[str] = None, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (mvstmp)"""
    options = ""
    options += parse_universal_arguments(**kwargs)

    if high_level_qualifier:
        options += clean_dataset_name(high_level_qualifier)

    logger.debug("ZOAU_CORE call: mvstmp %s", options)
    response = call_zoau_library("mvstmp", options)

    return ZOAUResponse.from_dict(response)


def tmp_name(high_level_qualifier: Optional[str] = None, **kwargs) -> str:
    """
    Creates a temporary dataset name.

    Returns
    -------
    str

    Parameters
    ----------
    high_level_qualifier: str
        The HLQ of the temporary dataset name.
        Maximum of 17 characters long

        Ex: `HLQ.NAME`.

    """
    logger.debug("tmp_name dataset function call")
    logger.debug("HLQ: %s", high_level_qualifier)
    logger.debug("kwargs: %s", kwargs)

    response = _tmp_name(high_level_qualifier, **kwargs)
    return response.stdout_response.rstrip("\n")


def _find_replace(dataset: str, find: str, replace: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dsed)"""
    options = ""
    options += parse_universal_arguments(**kwargs)
    dataset = clean_dataset_name(dataset)
    options += f's/{find}/{replace}/g "{dataset}"'

    logger.debug("ZOAU_CORE call: dsed %s", options)
    response = call_zoau_library("dsed", options)
    return ZOAUResponse.from_dict(response)


def find_replace(dataset: str, find: str, replace: str, **kwargs) -> int:
    """
    Replace text within a dataset.

    Returns
    -------
    int
        Return code from z/OS

    Parameters
    ----------
    dataset : str
        Dataset to act on

    find : str
        String to find

    replace : str
        String to replace find with

    Notes
    -----
    find_replace() supports operations over generation datasets (GDS).
    GDS relative name notation is supported, but the GDG base is not protected
    during execution. Use a batch job if you need to serialize the group.
    """
    logger.debug("find_replace dataset function call")
    logger.debug("dataset: %s", dataset)
    logger.debug("find: %s", find)
    logger.debug("replace: %s", replace)
    logger.debug("kwargs: %s", kwargs)

    response = _find_replace(dataset, find, replace, **kwargs)

    return response.rc


def _dzip(file: str, target: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dzip)"""
    target = clean_shell_input(target)
    file = clean_shell_input(file)

    options = ""
    options += parse_universal_arguments(**kwargs)

    # Boolean args

    if kwargs.get("compress", False) is True:
        options += "--compress "

    if kwargs.get("dataset", False) is True:
        options += "-D "

    if kwargs.get("force", False) is True:
        options += "-f "

    if kwargs.get("overwrite", False) is True:
        options += "-o "

    if kwargs.get("process_sys1", False) is True:
        options += "--process-sys1 "

    if kwargs.get("terse", True) is False:
        options += "--no-terse "

    if kwargs.get("volume", False) is True:
        options += "-V "

    # Keyword-value args

    if "dataset_type" in kwargs:
        options += f"-T\"{kwargs.get('dataset_type')}\" "

    if "dest_volume" in kwargs:
        options += f"-t\"{kwargs.get('dest_volume')}\" "

    if "exclude" in kwargs:
        options += f"-e\"{kwargs.get('exclude')}\" "

    if "management_class_name" in kwargs:
        options += f"-m\"{kwargs.get('management_class_name')}\" "

    if "size" in kwargs:
        options += f"-s{kwargs.get('size')} "

    if "storage_class_name" in kwargs:
        options += f"-S\"{kwargs.get('storage_class_name')}\" "

    if "tmphlq" in kwargs:
        options += f"-Q\"{kwargs.get('tmphlq')}\" "

    # Raw ADRDSSU keyword arguments
    if "keywords" in kwargs:
        keywords_dict = kwargs.get('keywords')
        if not isinstance(keywords_dict, dict):
            raise TypeError("keywords should be a dictionary")

        for key, value in keywords_dict.items():
            if value is None:
                options += f"--keyword={key} "
            else:
                options += f"--keyword=\"{key}({value})\" "

    # Argument processing complete.
    options += f'"{file}" "{target}" '

    if "src_volume" in kwargs:
        options += f"\"{kwargs.get('src_volume')}\" "

    logger.debug("ZOAU_CORE call: dzip %s", options)
    response = call_zoau_library("dzip", options)

    return ZOAUResponse.from_dict(response)


def dzip(file: str, target: str, **kwargs) -> int:
    """
    Dump and terse datasets into a z/OS UNIX file or dataset.

    Returns
    -------
    int
        Return code from z/OS.

    Parameters
    ----------
    file : str
        Fully qualified zFS file path or dataset name.

    target : str
        Dataset name or dataset pattern.

    Other Parameters
    ----------------
    compress : bool
        Compress the dataset or file produced by ADRDSSU DUMP. This option can
        reduce the size of the temporary dataset produced before it is passed
        to AMATERSE for tersing. It can also reduce the overall time it takes
        to run the dzip command. Enabling this option with --terse may increase
        the size of the dzip file or dataset. Equivalent to the
        ZCOMPRESS(PREF) COMPRESS command keywords.

    dataset : bool
        Dump to a z/OS dataset instead of a z/OS UNIX file.

    dataset_type : str
        Specifies the type of dataset used for both the temporary and output
        datasets. This may be one of the following: `LARGE`, `SEQ`.
        Defaults to `SEQ`.

    dest_volume : str
        Specifies a particular volume should be used when creating
        temporary and target datasets.

    exclude : str
        Exclude particular dataset patterns when dumping the source datasets.
        This option is ignored if dumping a volume. Equivalent to the EXCLUDE
        command keyword.

    force : bool
        Specifies that target datasets are to be processed even though shared
        or exclusive access fails. Also specifies that processing continues
        if I/O errors occur during read operations.
        Equivalent to the `TOL(ENQF, IOER)` command keyword.

    keywords : dict
        This argument is used to specify ADRDSSU keywords that will be passed
        directly to the dunzip utility. It is a Python dictionary where the
        key is the ADRDSSU command keyword, and the value (if any) is the
        keyword argument.  If the keyword does not have an argument, then the
        value should be None.

        For example:

        keywords_dict = {"purge" : None,
                         "container" : "container_name",
                         "rsa" : "keylabel" }

    management_class_name : str
        Specifies the user-desired management class that is to be used
        when creating temporary and target datasets.

    overwrite : bool
        Overwrite file or dataset destination if it already exists.

    process_sys1 : bool
        Allows ADRDSSU to dump datasets with a high-level qualifier of SYS1.
        This requires READ access to the `STGADMIN.ADR.DUMP.PROCESS.SYS` profile
        in the `FACILITY` class. Equivalent to the `PROCESS(SYS1)` command keyword.

    size : int
        Specify how large to allocate datasets. Valid units are:
        `CYL`, `TRK`, `K`, `M`, and `G`. Defaults to bytes if no unit provided.

    storage_class_name : str
        Specifies the user-desired storage class is to be used when
        creating temporary and target datasets.

   terse : bool
        Uses AMATERSE to compress and pack the dump generated by ADRDSSU.
        Defaults to True. Must be True if `dataset` is False

    tmphlq : str
        Use an alternative high-level qualifier (HLQ) for temporary dataset
        names.

    src_volume : str
    volume : str
        Dump a volume instead of datasets. Equivalent to the `FULL` command
        keyword.
    """
    logger.debug("zip dataset function call")
    logger.debug("file: %s", file)
    logger.debug("target: %s", target)
    logger.debug("kwargs: %s", kwargs)

    response = _dzip(file, target, **kwargs)
    if response.rc > 0:
        raise ZOAUException(response)

    return response.rc


def _dunzip(
    file: str, high_level_qualifier: Optional[str] = None, **kwargs
) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dunzip)"""
    file = clean_shell_input(file)
    high_level_qualifier = clean_shell_input(high_level_qualifier)

    options = ""
    options += parse_universal_arguments(**kwargs)

    # Boolean arguments
    if kwargs.get("admin", False) is True:
        options += "--admin "

    if kwargs.get("dataset", False) is True:
        options += "-D "

    if kwargs.get("import_dataset", False) is True:
        options += "--import "

    if kwargs.get("keep_original_hlq", False) is True:
        options += "-N "

    if kwargs.get("keep_temporary_dataset", False) is True:
        options += "--keep-temporary-dataset "

    if kwargs.get("no_rename", False) is True:
        options += "--no-rename "

    if kwargs.get("null_management_class", False) is True:
        options += "--null-management-class "

    if kwargs.get("null_storage_class", False) is True:
        options += "--null-storage-class "

    if kwargs.get("overwrite", False) is True:
        options += "-o "

    if kwargs.get("share", False) is True:
        options += "--share "

    if kwargs.get("sms_for_tmp", False) is True:
        options += "-u "

    if kwargs.get("sphere", False) is True:
        options += "--sphere "

    if kwargs.get("tolerate", False) is True:
        options += "--tolerate "

    if kwargs.get("volume", False) is True:
        options += "-V "

    # Key-value arguments
    if "bypass_acs" in kwargs:
        options += f"--bypass-acs=\"{kwargs.get('bypass-acs')}\" "

    if "dataset_type" in kwargs:
        options += f"-T\"{kwargs.get('dataset_type')}\" "

    if "dest_volume" in kwargs:
        options += f"-t\"{kwargs.get('dest_volume')}\" "

    if "exclude" in kwargs:
        options += f"-i\"{kwargs.get('exclude')}\" "

    if "include" in kwargs:
        options += f"-i\"{kwargs.get('include')}\" "

    if "management_class_name" in kwargs:
        options += f"-m{kwargs.get('management_class_name')} "

    if "recatalog" in kwargs:
        options += f"--recatalog=\"{kwargs.get('recatalog')}\" "

    if "size" in kwargs:
        options += f"-s{kwargs.get('size')} "

    if "storage_class_name" in kwargs:
        options += f"-S{kwargs.get('storage_class_name')} "

    if "target_gds" in kwargs:
        options += f"--target-gds={kwargs.get('target_gds')} "

    if "tmphlq" in kwargs:
        options += f"-Q\"{kwargs.get('tmphlq')}\" "

    if high_level_qualifier:
        options += f"-H{high_level_qualifier} "

    # Rename arguments
    if "rename" in kwargs:
        rename_arg = kwargs.get("rename")
        if not isinstance(rename_arg, dict):
            raise TypeError("rename should be a dictionary")

        for key, value in rename_arg.items():
            options += f"--rename=\"{key},{value}\" "

    # Raw ADRDSSU keyword arguments
    if "keywords" in kwargs:
        keywords_dict = kwargs.get("keywords")
        if not isinstance(keywords_dict, dict):
            raise TypeError("keywords should be a dictionary")

        for key, value in keywords_dict.items():
            if value is None:
                options += f"--keyword={key} "
            else:
                options += f'--keyword="{key}({value})" '

    # Argument processing complete.
    options += f'-- "{file}" '

    if "volume" in kwargs:
        options += f"\"{kwargs.get('volume')}\" "
    elif "src_volume" in kwargs:
        options += f"\"{kwargs.get('src_volume')}\" "

    logger.debug("ZOAU_CORE call: dunzip %s", options)
    response = call_zoau_library("dunzip", options)

    return ZOAUResponse.from_dict(response)


def dunzip(file: str, high_level_qualifier: Optional[str] = None, **kwargs) -> int:
    """
    Unzips a dzip archive and restores the datasets to either the original or a new location.

    Returns
    -------
    int
        Return code from z/OS.

    Parameters
    ----------
    file : str
        zFS path or dataset name of the dzip archive.

    high_level_qualifier : str, optional
        Single segment HLQ that is used to unpack the archive.
        Default is `None`,  which unpacks to the user's HLQ.
        You can use either `keep_original_hlq` or `high_level_qualifier`,
        but not both.

    Other Parameters
    ----------------
    admin : bool
        Sets the ADMINISTRATOR keyword for the ADRDSSU RESTORE command. Acts as
        a DFSMSdss storage administrator.  For administrators, DFSMSdss
        bypasses access checking for data sets and catalogs.

    bypass_acs : str
        Specifies that Automatic Class Selection (ACS) routines are
        not to be invoked to determine the target dataset's storage class or
        management class names. Corresponds with BYPASSACS command keyword.

    dataset : bool
        Source is a dataset.

    dataset_type: str
        Specifies the type of dataset used for both the temporary and output
        datasets. This may be one of the following: LARGE, SEQ.
        Defaults to SEQ.

    dest_volume : str
        Specifies a particular volume should be used when creating temporary
        datasets.

    exclude : str
        Exclude particular dataset patterns when restoring the datasets
        from the dzip archive.

    import_dataset : bool
        Specifies that the data sets that are being restored were dumped from a
        different system and they should be considered new data sets.
        Corresponds with IMPORT command keyword.

    include : str
        Include particular dataset patterns from the dzip binary file
        in the unzipped contents.

    high_level_qualifier : str, optional
        Single segment HLQ to unpack to
        None by default, which unpacks to the user's HLQ

    keep_original_hlq : bool, optional
        Restores the datasets to their original high-level-qualifier.
        Mutually exclusive with high_level_qualifier.

    keep_temporary_dataset : bool
        Do not delete the temporary dataset produced by untersing the input
        archive file or dataset. This can reduce processing time if the
        dataset needs to be used for multiple dunzip invocations.
        Note that the dataset will need to be manually deleted when no longer
        needed.

    keywords : dict
        This argument is used to specify ADRDSSU keywords that will be passed
        directly to the dunzip utility. It is a Python dictionary where the
        key is the ADRDSSU command keyword, and the value (if any) is the
        keyword argument.  If the keyword does not have an argument, then the
        value should be None.

        For example:

        keywords_dict = {"purge" : None,
                         "container" : "container_name",
                         "rsa" : "keylabel" }

    management_class_name : str
        Specifies the user-desired management class that is to replace the
        source management class as input to the ACS routines.

    no_rename : bool
        Restore datasets to their original HLQ from when they were archived.
        This overrides any value specified by the keep_original_hlq argument,
        if any. Corresponds with RENUNC command keyword.

    null_management_class : bool
        Specifies that the input to the ACS routines is a null management class
        rather than the source dataset's management class. Corresponds with
        NULLMGMTCLAS command keyword.

    null_storage_class : bool
        Specifies that the input to the ACS routines is to be a null storage
        class rather than the source dataset's storage class. Corresponds with
        NULLSTORCLAS command keyword.

    overwrite : bool
        Overwrite existing datasets with the same name on target device.
        Corresponds with REPUNC command keyword.

    recatalog : str
        Equivalent to RECATALOG command keyword. If this argument is not
        specified, then the CATALOG keyword is used instead. The argument
        value can either be the new catalog name, or `*` to catalog the
        target dataset in the same catalog that points to the
        source dataset. If the source dataset was not cataloged, the new
        dataset is not cataloged either.

    rename : dict
        Specifies that, if a dataset with the old name exists on the
        output DASD volume, DFSMSdss is to allocate a new dataset with the new
        name and restore the dataset. If the dataset with the old name does
        not exist on the volume, the dataset is restored with the old name.
        For a VSAM dataset that already exists on another DASD volume and is
        cataloged, the VSAM dataset is restored with the new name unless the
        new name also exists and is cataloged. Corresponds with RENAME command
        keyword.

        This argument is a Python dictionary where the key is the old name
        of the dataset to be renamed, and the value is the new name.
        Multiple dataset patterns are supported for the rename operation.

        For example:

        rename_dict = {"ZOAU.TEST.DS" : "RENAME.DS",
                       "ZOAU.LISTING" : "ZOAU.LIST"}

    share : bool
        Specifies that DFSMSdss is to share, for read access with other
        programs, the data sets that are to be restored. The resetting of the
        dataset change indicator is bypassed if share is specified on a data
        set restore operation. Corresponds with the SHARE command keyword.

    sms_for_tmp : bool
        Specifies the SMS classes specified with -S and/or -m should be used
        when creating temporary datasets.

    sphere : bool
        Specifies that for any VSAM cluster dumped with the SPHERE keyword,
        DFSMSdss must also restore all associated AIX clusters and paths.
        Individual sphere component names need not be specified; only the base
        cluster name is required. Corresponds with the SPHERE keyword.

    src_volume : str
        Name of volume to unzip.

    storage_class_name : str
        Specifies the user-desired storage class that is to replace the source
        storage class as input to the ACS routines.

    target_gds : str
        Specifies the status in which SMS-managed generation datasets are to
        be restored. Status may be one of the following:
            - active
            - deferred
            - rolledoff
            - source
        The target GDG base must exist for a successful restore.

    tmphlq : str
        Use an alternative high-level qualifier (HLQ) for the temporary dataset
        name.

    tolerate : bool
        Tolerate failure for exclusive access to target datasets.

    volume : str
        Unzip volume (default is dataset).

    """
    logger.debug("unzip dataset function call")
    logger.debug("file: %s", file)
    logger.debug("high_level_qualifier: %s", high_level_qualifier)
    logger.debug("kwargs: %s", kwargs)

    if high_level_qualifier and kwargs.get("keep_original_hlq", False):
        raise ValueError(
            "high_level_qualifier and keep_original_hlq are mutually exclusive."
        )

    response = _dunzip(file, high_level_qualifier, **kwargs)
    if response.rc > 0:
        raise ZOAUException(response)

    return response.rc


def lineinfile(
    dataset: str,
    line: str,
    state: bool = True,
    regex: Optional[str] = None,
    insert_after: Optional[str] = None,
    insert_before: Optional[str] = None,
    **kwargs,
) -> ZOAUResponse:
    """
    ZOAU dsed function to be used by zos_lineinfile Ansible module

    Returns
    -------
    ZOAUResponse
        Response object from dsed call.

    Parameters
    ----------
    dataset : str
        The target dataset or zFS file to modify to (e.g "IBMUSER.TEST.MOD")

    state : boolean
        state=True -> Insert or replace line
        state=False -> Remove line
        Defaults to True.

    line : str, optional
        The line to insert/replace.

    regex : str, optional
        The regular expression to look for in every line of the dataset or zFS file.
        For state=True, the pattern to replace if found. Only the last line found will be replaced.
        For state=False, the pattern of the line(s) to remove.
        If the regular expression is not matched, the line will be added to the dataset or zFS file
        in keeping with insert_after or insert_before settings.

    insert_after : str, optional
        Insert line after matching regex pattern
        The special value "EOF" will insert the line at the end of the target dataset or zFS file.
        If regex is provided, insert_after is only honored if no match for regex is found.
        insert_before will be ignored if provided.

    insert_before : str, optional
        Insert line before matching regex pattern
        The special value "BOF" will insert the line at the beginning of the target dataset or zFS file.
        If regex is provided, insert_before is only honored if no match for regex is found.
        insert_before will be ignored if insert_after is provided.

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    first_match : bool, optional
        If set, insert_after and insert_before will work with the first line that matches the given regular expression.

    encoding : str, optional
        Encoding of the dataset

    lock : bool, optional
        Obtain exclusive lock for the dataset

    force : bool, optional
        Force open. Open dataset member in DISP=SHR mode. Default is DISP=OLD mode when False.

    backref : bool, optional
        Use back references in regular expressions. Default is False.

    Notes
    -----
    Use debug=True parameter for debug information in JSON format

    lineinfile() supports operations over generation datasets (GDS).
    GDS relative name notation is supported, but the GDG base is not protected
    during execution. Use a batch job if you need to serialize the group.
    """
    logger.debug("lineinfile dataset function call")
    logger.debug("dataset: %s", dataset)
    logger.debug("line: %s", line)
    logger.debug("state: %s", state)
    logger.debug("regex: %s", regex)
    logger.debug("insert_after: %s", insert_after)
    logger.debug("insert_before: %s", insert_before)
    logger.debug("kwargs: %s", kwargs)

    dataset = clean_dataset_name(dataset)
    options = ""
    options += parse_universal_arguments(**kwargs)

    if "lock" in kwargs:
        if not isinstance(kwargs.get("lock"), bool):
            raise TypeError("lock should be True or False")
        if kwargs.get("lock"):
            options += "-l  "

    if "force" in kwargs:
        if not isinstance(kwargs.get("force"), bool):
            raise TypeError("force should be True or False")
        if kwargs.get("force"):
            options += "-f  "

    if "encoding" in kwargs:
        options += f"-c {kwargs.get('encoding')} "

    if "backref" in kwargs:
        if not isinstance(kwargs.get("backref"), bool):
            raise TypeError("backref should be True or False")
        if kwargs.get("backref"):
            options += "-r  "

    if kwargs.get("first_match", None):
        match_character = "1"
    else:
        match_character = "$"

    if state:
        if regex:
            if insert_after:
                if insert_after == "EOF":
                    options += f' -s -e "/{regex}/c\\{line}/{match_character}" -e "$ a\\{line}" "{dataset}" '
                else:
                    options += f' -s -e "/{regex}/c\\{line}/{match_character}" -e "/{insert_after}/a\\{line}/{match_character}" -e "$ a\\{line}" "{dataset}" '

            elif insert_before:
                if insert_before == "BOF":
                    options += f' -s -e "/{regex}/c\\{line}/{match_character}" -e "1 i\\{line}" "{dataset}" '
                else:
                    options += f' -s -e "/{regex}/c\\{line}/{match_character}" -e "/{insert_before}/i\\{line}/{match_character}" -e "$ a\\{line}" "{dataset}" '
            else:
                options += f' "/{regex}/c\\{line}/{match_character}" "{dataset}" '
        else:
            if insert_after:
                if insert_after == "EOF":
                    opts = options + f'"/{line}/c\\{line}/$"  "{dataset}"'
                    resp = call_zoau_library("dsed", opts)

                    if int(resp["rc"]) > 0:
                        # Insert at the end
                        options += f' "$ a\\{line}" "{dataset}" '
                    else:
                        logger.debug("ZOAU_CORE call: dsed %s", opts)
                        return ZOAUResponse.from_dict(resp)
                else:
                    options += f' -s -e "/{insert_after}/a\\{line}/{match_character}" -e "$ a\\{line}" "{dataset}" '
            elif insert_before:
                if insert_before == "BOF":
                    options += f' "1 i\\{line}" "{dataset}" '
                else:
                    options += f' -s -e "/{insert_before}/i\\{line}/{match_character}" -e "$ a\\{line}" "{dataset}" '
            else:
                raise ValueError("Incorrect parameters")
    else:
        if regex:
            if line:
                options += f'-s -e "/{regex}/d" -e "/{line}/d" "{dataset}" '
            else:
                options += f'"/{regex}/d" "{dataset}" '
        else:
            options += f'"/{line}/d" "{dataset}" '

    logger.debug("ZOAU_CORE call: dsed %s", options)
    response = call_zoau_library("dsed", options)
    return ZOAUResponse.from_dict(response)


def blockinfile(dataset: str, state: bool = True, **kwargs) -> ZOAUResponse:
    """
    ZOAU dmod function to be used by zos_blockinfile Ansible module

    Returns
    -------
    ZOAUResponse
        Response object from dsed call.

    Parameters
    ----------
    dataset : str
        The target dataset or z/OS UNIX file to modify to (e.g "IBMUSER.TEST.MOD")

    state : boolean
        state=True -> Insert or replace block
        state=False -> Remove block
        Defaults to True.

    kwargs: dict, optional
        Additional parameters (see other parameters)

    Other Parameters
    ----------------
    block : str, optional
        The line(s) to insert inside the marker lines separated by '\\n'. (e.g. "line 1\\nline 2\\nline 3")

    marker : str, optional
        The marker line template in this format <marker_begin>\\n<marker_end>\\n< {mark} marker>
        The template should be 3 sections separated by '\\n'. (e.g "OPEN\\nCLOSE\\n# {mark} IBM BLOCK")
        "{mark}" should be included in the < {mark} marker> (default="# {mark} MANAGED BLOCK") section
        and will be replaced with <marker_begin> (default="BEGIN") and <marker_end> (default="END").
        The two marker lines will be surrounding the lines that are going to be inserted.
        Marker lines can only be used once. If marker lines already exist in the target dataset or zFS file,
        they will be removed with the surrounded lines before new block get inserted.

    insert_after : str, optional
        Insert block after matching regex pattern
        The special value "EOF" will insert the block at the end of the target dataset or zFS file.

    insert_before : str, optional
        Insert block before matching regex pattern
        The special value "BOF" will insert the block at the beginning of the target dataset or zFS file.

    encoding : str, optional
        Encoding of the dataset

    lock : bool, optional
        Obtain exclusive lock for the dataset

    force : bool, optional
        Force open. Open dataset member in DISP=SHR mode. Default is DISP=OLD mode when False.

    as_json : bool, optional
        Display output in JSON format.

        When enabled, the output is a JSON string with this structure:
        {
            "data": {
                "changed": <boolean>,
                "found": <number>,
                "commands": [
                    <string>,
                    ...
                ]
            },
            "program": <string>,
            "options": <string>,
            "rc": <string>,
            "encoding": <string>
        }

    Notes
    -----
    blockinfile() supports operations over generation datasets (GDS).
    GDS relative name notation is supported, but the GDG base is not protected
    during execution. Use a batch job if you need to serialize the group.
    """
    logger.debug("blockinfile dataset function call")
    logger.debug("dataset: %s", dataset)
    logger.debug("state: %s", state)
    logger.debug("kwargs: %s", kwargs)

    dataset = clean_dataset_name(dataset)
    options = "-b "
    options += parse_universal_arguments(**kwargs)

    if "force" in kwargs:
        if not isinstance(kwargs.get("force"), bool):
            raise TypeError("force should be True or False")
        if kwargs.get("force"):
            options += "-f  "

    if "lock" in kwargs:
        if not isinstance(kwargs.get("lock"), bool):
            raise TypeError("lock should be True or False")
        if kwargs.get("lock"):
            options += "-l  "

    if "encoding" in kwargs:
        options += f"-c \"{kwargs.get('encoding')}\" "
    if "marker" in kwargs:
        options += f"-m \"{kwargs.get('marker')}\" "
    if "as_json" in kwargs:
        if not isinstance(kwargs.get("as_json"), bool):
            raise TypeError("as_json should be True or False")
        options += "-j "

    block = kwargs.get("block", None)
    if block:
        block = escape_block_string(block)
    insert_after = kwargs.get("insert_after", None)
    insert_before = kwargs.get("insert_before", None)

    if state:
        if not block:
            raise MissingFunctionParameter("block is required when state=True")

        if insert_after:
            if insert_after == "EOF":
                options += f' "$ a\\{block}" "{dataset}" '
            else:
                options += f' -s -e "/{insert_after}/a\\{block}/$" -e "$ a\\{block}" "{dataset}" '
        elif insert_before:
            if insert_before == "BOF":
                options += f' "1 i\\{block}" "{dataset}" '
            else:
                options += f' -s -e "/{insert_before}/i\\{block}/$" -e "$ a\\{block}" "{dataset}" '
        else:
            raise MissingFunctionParameter(
                "insert_after or insert_before is required when state=True"
            )
    else:
        options += f'"//d" "{dataset}" '

    logger.debug("ZOAU_CORE call: dmod %s", options)
    response = call_zoau_library("dmod", options)

    return ZOAUResponse.from_dict(response)


def _list_vsam_datasets(pattern: str, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls zoau core (vls)"""
    pattern = clean_dataset_name(pattern)

    options = ""
    options += parse_universal_arguments(**kwargs)

    if "migrated" in kwargs and kwargs.get("migrated"):
        options += "-m "

    options += pattern

    logger.debug("ZOAU_CORE call: vls %s", options)
    response = call_zoau_library("vls", options)
    return ZOAUResponse.from_dict(response)


def list_vsam_datasets(pattern: str, **kwargs) -> list[Dataset]:
    """
    Get a list of VSAM datasets and their volumes.

    Returns
    -------
    list[Dataset]
        List of Dataset objects found.
        These objects will have only the `name` attribute set.

    list[]
        Empty list if no datasets match the pattern.

    Parameters
    ----------
    pattern : str
        Pattern to match.

    kwargs: dict
        Additional parameters (see other parameters).

    Other Parameters
    ----------------
    migrated : bool, optional
        Display migrated datasets.
    """
    logger.debug("list_vsam_datasets function call")
    logger.debug("pattern: %s", pattern)
    logger.debug("kwargs: %s", kwargs)

    response = _list_vsam_datasets(pattern, **kwargs)
    datasets = []
    if response.rc == 1:
        # No match found.
        return datasets

    for line in response.stdout_response.rstrip("\n").split("\n"):
        dataset_row = list(filter(None, line.split()))
        datasets.append(Dataset(name=dataset_row[0]))
    return datasets


def _list_datasets_by_volume(volume: str, *args, **kwargs) -> ZOAUResponse:
    """Builds a command string and calls zoau core (vtocls)"""
    options = ""
    options += parse_universal_arguments(**kwargs)
    options += volume
    options += " "
    for arg in args:
        options += arg
        options += " "

    logger.debug("ZOAU_CORE call: vtocls %s", options)
    response = call_zoau_library("vtocls", options)
    return ZOAUResponse.from_dict(response)


def list_datasets_by_volume(volume: str, *args, **kwargs) -> list[Dataset]:
    """
    List the contents of a given volume.

    Returns
    -------
    list[Dataset]
        List of Dataset objects with only these attributes set:
        name, organization, record_format, record_length, volume

    Parameters
    ----------
    volume : str
        Volume to list

    *args : str
        Additional dataset names to filter by

    kwargs: dict
        Additional parameters
    """
    logger.debug("list_datasets_by_volume function call")
    logger.debug("volume: %s", volume)
    logger.debug("kwargs: %s", kwargs)

    response = _list_datasets_by_volume(volume, *args, **kwargs)
    datasets = []
    for line in response.stdout_response.rstrip("\n").split("\n"):
        dataset_row = list(filter(None, line.split()))

        if len(dataset_row) != 5:
            logger.warning("Unexpected row: %s", dataset_row)
            continue

        datasets.append(
            Dataset(
                name=dataset_row[0],
                organization=dataset_row[1],
                record_format=dataset_row[2],
                record_length=dataset_row[3],
                volume=dataset_row[4],
            )
        )

    return datasets
