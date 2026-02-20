import logging
from zoautil_py import datasets as datasets
from zoautil_py.common import RelativeList as RelativeList, clean_dataset_name as clean_dataset_name, parse_universal_arguments as parse_universal_arguments, zoau_json_load as zoau_json_load
from zoautil_py.core import call_zoau_library as call_zoau_library
from zoautil_py.exceptions import DatasetFetchException as DatasetFetchException, GenerationDataGroupClearException as GenerationDataGroupClearException, GenerationDataGroupCreateException as GenerationDataGroupCreateException, GenerationDataGroupDeleteException as GenerationDataGroupDeleteException, GenerationDataGroupFetchException as GenerationDataGroupFetchException, GenerationDataGroupViewInvalidName as GenerationDataGroupViewInvalidName, GenerationDataGroupViewInvalidState as GenerationDataGroupViewInvalidState
from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

logger: logging.Logger

class GenerationDataGroupView:
    """
    Class that provides an interface to a z/OS generation data group (GDG).

    Parameters
    ----------
    name : str
        Name of the GDG to fetch.

    kwargs: dict, optional
        Additional parameters (see other parameters).

    Other parameters
    ----------------
    debug: bool
        Enable debug messages (only for constructor exceptions).

    verbose: bool
        Enable verbose output (only for constructor exceptions).

    Notes
    -----
    The class supports the iterator protocol by yielding the active generation
    datasets in a GDG snapshot. The GDG base is not protected while iterating.
    Use a batch job if you need to serialize the group.
    """
    def __init__(self, name: str, **kwargs) -> None: ...
    @property
    def name(self) -> str:
        """Name of the GDG."""
    @name.setter
    def name(self, value) -> None:
        """Name of the GDG. (Setter)."""
    @property
    def limit(self) -> int:
        """Maximum number of active generations in the group."""
    @property
    def scratch(self) -> bool:
        """
        True if the GDG has the SCRATCH attribute.
        False if the GDG has the NOSCRATCH attribute.

        Notes
        -----
        This attribute has no effect on generation datasets located on tape.

        SCRATCH
            * Generation datasets located on disk volumes are to be scratched.
              This means that a dataset is removed from disk when it is unlinked
              from the GDG base.

        NOSCRATCH
            * Generation datasets are not scratched when unlinked from the GDG.
                * non-SMS managed datasets are not removed from the volume they
                  occupy.
                * SMS-managed datasets are recataloged as non-VSAM datasets in
                  a rolled-off status.
        """
    @property
    def empty(self) -> bool:
        """
        True if the GDG has the EMPTY attribute.
        False if the GDG has the NOEMPTY attribute.

        Notes
        -----
        EMPTY
            * When the maximum number of generation datasets in the GDG is
            reached (given under limit), and one more dataset is added to the
            group, then all generation datasets are uncataloged.

        NOEMPTY
            * When the maximum number of generation datasets in the GDG is
            reached (given under limit), and one more dataset is added to the
            group, then the oldest generation dataset in the GDG is uncataloged.
        """
    @property
    def order(self):
        """
        Determines the allocation order of the generation datasets during GDG
        ALL requests.
        """
    @property
    def purge(self) -> bool:
        """
        True if the GDG has the PURGE attribute.
        False if the GDG has the NOPURGE attribute.

        Notes
        -----
        PURGE
            * Overrides the expiration date when scratching a generation dataset.

        NOPURGE
            * Does not override the expiration date when scratching a generation
            dataset.
        """
    @property
    def extended(self) -> bool:
        """
        True if the GDG has the EXTENDED attribute.
        False if the GDG has the NOEXTENDED attribute.

        Notes
        -----
        EXTENDED
            * The maximum LIMIT of generation datasets is 999.

        NOEXTENDED
            * The maximum LIMIT of generation datasets is 255.
        """
    @property
    def generations(self) -> list[datasets.Dataset] | list:
        """
        Snapshot of the active generation datasets in the GDG.

        Returns
        -------
        list[Dataset]
            Snapshot of the active generation datasets in the GDG.
        """
    def __len__(self) -> int:
        """
        Returns the number of active generation data sets in the GDG.
        """
    def delete(self, include_rolled_off: bool = False, **kwargs):
        """
        Deletes the generation data group and all its active generations.

        Parameters
        ----------
        include_rolled_off: bool, optional
            When set to `True`, also deletes the rolled-off generations that are
            still cataloged and named after the GDG base. Defaults to `False`.

        kwargs: dict, optional
            Additional parameters (see other parameters).

        Other parameters
        ----------------
        debug: bool
            Enable debug messages (only for exceptions).

        verbose: bool
            Enable verbose output (only for exceptions).
        """
    def clear(self) -> None:
        """
        Removes all the active generations from the generation data group.
        """
    def generate(self, index: int = 1, **kwargs) -> datasets.Dataset:
        """Creates new GDG generation

        Arguments:
            index (int, optional): GDG incremental generation index. 
            Defaults to 1.
        
        Other Arguments
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
            F/FB/FBS=80, FBA=133, VB/VBA/VBS=137, U=0. For variable datasets, 
            the length must include the 4-byte prefix area.

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
        """

def create(name: str, limit: int, *, empty: bool = False, scratch: bool = False, purge: bool = False, extended: bool = False, fifo: bool = False, **kwargs) -> GenerationDataGroupView:
    """
    Creates a GDG base with the following default attributes:

    NOEMPTY, NOSCRATCH, NOPURGE, NOEXTENDED, LIFO.

    Returns
    -------
    GenerationDataGroupView object.

    Parameters
    ----------
    name : str
        Name of the GDG base being defined.

    limit : int
        Maximum number of generation datasets that can be associated with the
        GDG.
        - Must be between 1 and 255 for a NOEXTENDED GDG.
        - Must be between 1 and 999 for an EXTENDED GDG.

    empty : bool, optional
        If True creates a GDG with the EMPTY attribute. NOEMPTY when False.

    scratch : bool, optional
        If True creates a GDG with the SCRATCH attribute. NOSCRATCH when False.

    purge : bool, optional
        If True creates a GDG with the PURGE attribute. NOPURGE when False.
        The PURGE attribute requires the SCRATCH attribute to be set.

    extended : bool, optional
        If True creates a GDG with the EXTENDED attribute. NOEXTENDED when False.

    fifo : bool, optional
        If True creates a GDG with the FIFO attribute. LIFO when False.

    kwargs: dict, optional
        Additional parameters (see other parameters).

    Other parameters
    ----------------
    debug: bool
        Enable debug messages (only for exceptions).

    verbose: bool
        Enable verbose output (only for exceptions).

    Notes
    -----
    See the class `GenerationDataGroupView` members for a description of the GDG
    attributes.
    """
def list_gdg_names(pattern: str, **kwargs) -> list[str]:
    """
    Returns a list of GDG names matching the supplied pattern.

    Returns
    -------
    list[str]
        List of GDG names matching the pattern.

    Parameters
    ----------
    pattern : str
        The GDG pattern to search.

    kwargs: dict, optional
        Additional parameters (see other parameters).

    Other Parameters
    ----------------
    debug: bool
        Enable debug messages (only for exceptions).

    verbose: bool
        Enable verbose output (only for exceptions).
    """
def exists(name: str, **kwargs):
    """
    Check if a GDG exists.

    Returns
    -------
    bool
        True if the GDG was found; False otherwise.

    Parameters
    ----------
    name : str
        The GDG base name to check for.

    kwargs: dict, optional
        Additional parameters (see other parameters).

    Other Parameters
    ----------------
    debug: bool
        Enable debug messages (only for exceptions).

    verbose: bool
        Enable verbose output (only for exceptions).
    """
