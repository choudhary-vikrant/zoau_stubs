import logging
from _typeshed import Incomplete
from datetime import datetime
from zoautil_py.common import cast_int_optional as cast_int_optional, clean_dataset_name as clean_dataset_name, clean_shell_input as clean_shell_input, escape_block_string as escape_block_string, identify_dtype as identify_dtype, match_expression as match_expression, multivar_type_validation as multivar_type_validation, parse_universal_arguments as parse_universal_arguments, parse_unknown as parse_unknown, slicer as slicer, zoau_json_load as zoau_json_load
from zoautil_py.core import call_zoau_library as call_zoau_library, call_zoau_library_bin as call_zoau_library_bin
from zoautil_py.exceptions import DatasetCreateException as DatasetCreateException, DatasetFetchException as DatasetFetchException, DatasetVerificationError as DatasetVerificationError, DatasetWriteError as DatasetWriteError, DatasetWriteException as DatasetWriteException, MissingFunctionParameter as MissingFunctionParameter, ZOAUException as ZOAUException
from zoautil_py.zoau_io import RecordIO as RecordIO
from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

MULTIBYTE_ENCODINGS: Incomplete
logger: logging.Logger

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

    """
    name: str
    organization: str | None
    record_format: str | None
    volume: str | None
    block_size: int | None
    record_length: int | None
    total_space: int | None
    used_space: int | None
    last_referenced: datetime | None
    type: str | None
    allocated_extents: int | None
    first_extent_size: int | None
    secondary_space: int | None
    encoding: str | None
    serialize: bool | None
    next_record_char: str | None
    def __init__(self, name: str, organization: str | None = None, record_format: str | None = None, volume: str | None = None, block_size: str | int | None = None, record_length: str | int | None = None, total_space: str | int | None = None, used_space: str | int | None = None, last_referenced: str | datetime | None = None, type: str | None = None, allocated_extents: int | None = None, first_extent_size: int | None = None, secondary_space: int | None = None, encoding: str | None = None, serialize: str | None = None, next_record_char: str | None = None) -> None: ...
    def to_dict(self) -> dict[str, str | int | datetime]:
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
            encoding: str
                Encoding of text content if available. (Python only)
                `None` if unknown.
            serialize: str
                Serialization method of the dataset. (Python only)
                `None` if unknown.
            next_record_char: str
                New record character of the dataset. (Python only)
                `None` if unknown.

        Notes
        -----
        Provides the same result as calling <Dataset>.__dict__, kept for legacy support
        """
    @classmethod
    def from_dict(cls, ds_as_dict: dict) -> Dataset:
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
    @classmethod
    def from_core_json(cls, ds_as_json: dict[str, str]):
        '''Create a Dataset instance from a dls or dinfo JSON response

        Returns
        -------
        Dataset
            Representation of z/OS Dataset

        Parameters
        ----------
        ds_as_json : dict
            Dictionary from the "datasets" array in the "data" object of a
            JSON dls response
        '''
    def write(self, content: str, member_name: str = '', append: bool = False, encoding: str | None = None, serialize: str | None = None, next_record_char: str | None = None, max_record_length: int | None = None, fill_char: str = ' ', validate_record_length: bool = True):
        '''Writes encoded text content to a z/OS dataset.

        Arguments
        ---------
        content : str
            Content to write.

        member_name: str, optional
            Member to write to.

        encoding : str, optional
            The encoding character scheme used to represent the dataset\'s content.
            Defaults to \'cp1047\'.

        serialize : str, optional
            If set to record, the content will be serialized and written with a 
            1:1 mapping of lines to records.

            If set to \'byte\', the content will be serialized and sliced according 
            to the maximum byte record length of the dataset.
            Required for multi-byte encoding schemes such as UTF-8. 
            
            Byte serialization may not be interpretable until the whole dataset 
            content is read and serialized.

            If the encoding is on the supported multi-byte encoding list, 
            serialize is set to \'byte\' automatically. See notes.

        next_record_char : str, optional
            The new line character used for writing records in a 1:1 relationship
            with lines. The actual character is not written to the dataset.
            The default value is "
".
            Ignored if serialize is enabled.

        max_record_length : int, optional
            Overrides auto-discovery of maximum record length. Value 0 enables
            auto-discovery.

        fill_char : str, optional
            Character to fill the trailing free space of each record with.
            Supported with fixed record_length datasets only.
            Defaults to the selected encoding\'s whitespace character.

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
        '''
    def delete(self) -> int:
        """Delete this dataset.

        Returns
        -------
        int
            Return code from z/OS. Zero if successful. Non-zero otherwise.
        """
    def read_as_bytes(self, number_of_records: int = 0, offset: int = 0, tail: bool = False) -> list[bytes]:
        """
        Reads records as bytes from a dataset.

    Arguments
    ---------
    filename : str 
        The name of the dataset to read from.
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
    def read(self, member_name: str = '', encoding: str | None = None, lines: int = 0, offset: int = 0, tail: bool = False, serialize: str = 'record', next_record_char: str = '\n') -> str:
        '''
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
            Defaults to \'record\'. Automatically set to \'byte\' if encoding is on the 
            supported multi-byte encoding list. See notes.
        next_record_char : str, optional
            The character that indicates a new record.
            If not provided, uses the stored one.
            If no new record character is stored, defaults to "
".

        Returns
        -------
        str: The content read from the dataset as a python string.

        Notes
        -----
            Multi-byte ncoding schemes currently supported:
                - UTF-8. 
        '''

def read_as_bytes(dataset_name: str, records: int = 0, offset: int = 0, tail: bool = False) -> list[bytes]:
    """Returns a dataset's content as a list of bytes (by record).

    Parameters
    ----------
        dataset_name : str
            Name of the dataset to read.
        number_of_records : int, optional
            Maximum number of records to read. Defaults to 0.
            If set to 0, all possible records will be read.
        offset : int, optional
            Offsets the starting index for reading. Defaults to 0.
        tail : bool, optional
            If True, the last n records will be returned. n is defined by
            limited to number_of_records. Defaults to False.

    Returns:
        list[bytes]
            A list of byte objects split by record.
    """
def read(dataset_name: str, encoding: str = 'cp1047', lines: int = 0, offset: int = 0, tail: bool = False, serialize: str = 'record', next_record_char: str = '\n') -> str:
    '''
    Read encoded text content from a non-VSAM dataset.

    Returns
    -------
    str
        Contents of the dataset

    Parameters
    ----------
    dataset_name : str
        The dataset\'s name to read. Generation dataset relative name notation
        is supported.

    encoding : str, optional
            The encoding character scheme used to represent the dataset\'s content.
            Defaults to \'cp1047\'.

    serialize : str, optional
        The serialization method to use. 
        Defaults to \'record\'.
        If the encoding is on the supported multi-byte encoding list, 
        serialize is set to \'byte\' automatically. See notes.

    next_record_char : str, optional
        The new line character used for reading records in a 1:1 relationship
        with lines. The actual character is not present in the content of the dataset.
        The default value is "
".
        Ignored if serialize is not set to  \'record\'.

    Notes
    -----
        Multi-byte ncoding schemes currently supported:
            - UTF-8.
    '''
def read_head(dataset: str, lines: int = 10, encoding: str = 'cp1047', serialize: str = 'record') -> str:
    """
    Get the head content of a non-VSAM dataset, defaults to 10 lines.

    Returns
    -------
    str : Contents of the dataset.

    Parameters
    ----------
    dataset : str
        The dataset to read. Generation dataset relative name notation is
        supported.

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
def write(dataset_name: str, content: str, append: bool = False, encoding: str = 'cp1047', serialize: str = 'record', next_record_char: str = '\n', max_record_length: int = 0, fill_char: str = ' ', validate_record_length: bool = True) -> None:
    '''Writes encoded text content to a z/OS dataset.

    Arguments
    ---------
        dataset_name : str
            Target dataset name.

        content : str
            Content to write.

        append : bool, optional
            Appends content trailing any previous content. Defaults to False.

        encoding : str, optional
            The encoding character scheme used to represent the dataset\'s content.
            Defaults to \'cp1047\'.

        serialize : str, optional
            If set to record, the content will be serialized and written with a 
            1:1 mapping of lines to records.

            If set to \'byte\', the content will be serialized and sliced according 
            to the maximum byte record length of the dataset.
            Required for multi-byte encoding schemes such as UTF-8. 
            
            Byte serialization may not be interpretable until the whole dataset 
            content is read and serialized.

            If the encoding is on the supported multi-byte encoding list, 
            serialize is set to \'byte\' automatically. See notes.

        next_record_char : str, optional
            The new line character used for writing records in a 1:1 relationship
            with lines. The actual character is not written to the dataset.
            The default value is "
".

            Ignored if serialize is enabled.

        max_record_length : int, optional
            Overrides auto-discovery of maximum record length. Value 0 enables
            auto-discovery.

        fill_char : str, optional
            Character to fill the trailing free space of each record with.
            Supported with fixed record_length datasets only.
            Defaults to the selected encoding\'s whitespace character.

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

    '''
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
        Examples: 1M, 2MB, 1G, 2GB

    secondary_space : str, optional
        Secondary (extent) space to allocate for the dataset. Defaults to 1/10 of primary space.
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

    Raises
    ------
    ZOAUException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls

    DatasetVerificationError
        Failed to verify the creation of the dataset after ZOAU call
    """
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
    """
def copy(source: str, target: str, **kwargs) -> int:
    '''
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
        See message for details.'''
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
def compare(source: str, target: str, **kwargs) -> str | None:
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
def search(dataset: str, value: str, **kwargs) -> str | None:
    '''
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
    '''
def search_dictionary(dataset: str, value: str, **kwargs) -> dict | None:
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
def list_datasets(pattern: str, volume: str | None = None, **kwargs) -> list[Dataset]:
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
def list_dataset_names(pattern: str, volume: str | None = None, migrated: bool = False, **kwargs) -> list[str]:
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
def find_member(member: str, concatenation: str, **kwargs) -> str | None:
    '''
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
    '''
def get_hlq(**kwargs) -> str:
    """
    Returns the active TSO high-level qualifier

    Returns
    -------
    str
        The active TSO high-level qualifier
    """
def tmp_name(high_level_qualifier: str | None = None, **kwargs) -> str:
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
def dzip(file: str, target: str, **kwargs) -> int:
    '''
    Dump and terse datasets into a z/OS UNIX file or dataset.

    Returns
    -------
    int
        Return code from z/OS

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

    dataset : str
        Dataset name or pattern to archive.

    dataset-type : str
        Specifies the type of dataset used for both the temporary and output
        datasets. This may be one of the following: LARGE, SEQ.
        Defaults to SEQ.

    dest_volume : str
        Specifies a particular volume should be used when creating
        temporary and target datasets.

    dataset_type: str
        Specifies the dataset type to be used when creating temporary and target
        datasets. Valid values are `SEQ` or `LARGE`.

    exclude : str
        Exclude particular dataset patterns when dumping the source datasets.
        This option is ignored if dumping a volume.

    force : bool
        Specifies potentially recoverable errors should be tolerated.

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
        This requires READ access to the STGADMIN.ADR.DUMP.PROCESS.SYS profile
        in the FACILITY class. Equivalent to the PROCESS(SYS1) command keyword.

    size : int
        Specify how large to allocate datasets. Valid units are:
        CYL, TRK, K, M, G. Defaults to bytes if no unit provided.

    src_volume : str
        Dump a volume instead of datasets.

    storage_class_name : str
        Specifies the user-desired storage class is to be used when
        creating temporary and target datasets.

   terse : bool
        Uses AMATERSE to compress and pack the dump generated by ADRDSSU.
        Defaults to True. Must be True if `dataset` is False

    tmphlq : str
        Use an alternative high-level qualifier (HLQ) for temporary dataset
        names.

    volume : str
        Dump a volume instead of datasets.
    '''
def dunzip(file: str, high_level_qualifier: str | None = None, **kwargs) -> int:
    '''
    Unzips a dzip archive and restores the datasets to either the original or a new location.

    Returns
    -------
    int
        Return code from z/OS

    Parameters
    ----------
    file : str
        zFS path or dataset name of the dzip archive.

    high_level_qualifier : str, optional
        Single segment HLQ that is used to unpack the archive.
        Default is `None`,  which unpacks to the user\'s HLQ.
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
        not to be invoked to determine the target dataset\'s storage class or
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
        None by default, which unpacks to the user\'s HLQ

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
        rather than the source dataset\'s management class. Corresponds with
        NULLMGMTCLAS command keyword.

    null_storage_class : bool
        Specifies that the input to the ACS routines is to be a null storage
        class rather than the source dataset\'s storage class. Corresponds with
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

    rename : bool
        Specifies that, if a dataset with the old name exists on the
        output DASD volume, DFSMSdss is to allocate a new dataset with the new
        name and restore the dataset. If the dataset with the old name does
        not exist on the volume, the dataset is restored with the old name.
        For a VSAM dataset that already exists on another DASD volume and is
        cataloged, the VSAM dataset is restored with the new name unless the
        new name also exists and is cataloged. Corresponds with RENAME command
        keyword.

    share : bool
        Specifies that DFSMSdss is to share, for read access with other
        programs, the data sets that are to be restored. The resetting of the
        dataset change indicator is bypassed if share is specified on a data
        set restore operation. Corresponds with the SHARE command keyword.

    sms_for_tmp : bool
        Specifies the SMS classes specified with -S and/or -m should be used
        when creating temporary datasets.

    sphere
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

    '''
def lineinfile(dataset: str, line: str, state: bool = True, regex: str | None = None, insert_after: str | None = None, insert_before: str | None = None, **kwargs) -> ZOAUResponse:
    '''
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
    '''
def blockinfile(dataset: str, state: bool = True, **kwargs) -> ZOAUResponse:
    '''
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
        The line(s) to insert inside the marker lines separated by \'\\n\'. (e.g. "line 1\\nline 2\\nline 3")

    marker : str, optional
        The marker line template in this format <marker_begin>\\n<marker_end>\\n< {mark} marker>
        The template should be 3 sections separated by \'\\n\'. (e.g "OPEN\\nCLOSE\\n# {mark} IBM BLOCK")
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
    '''
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
