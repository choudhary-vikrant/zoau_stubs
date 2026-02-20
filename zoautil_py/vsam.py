import logging
from dataclasses import dataclass
from zoautil_py.common import clean_dataset_name as clean_dataset_name, zoau_json_load as zoau_json_load
from zoautil_py.core import call_zoau_library as call_zoau_library
from zoautil_py.exceptions import DatasetFetchException as DatasetFetchException, VsamClusterFetchException as VsamClusterFetchException, VsamClusterNameInvalidPattern as VsamClusterNameInvalidPattern
from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

logger: logging.Logger

@dataclass(kw_only=True, frozen=True)
class VsamComponentStatistics:
    """
    Class that represents the statistics of a VSAM component.

    Attributes
    ----------
    total_records : int
        The total number of records in the component.

    deleted_records : int
        Number of records that are deleted from the component.

    inserted_records : int
        For KSDS datasets, it represents the number of records that are inserted
        into the data component before the last record.
        For RRDS datasets is the number of records inserted into available slots.

    updated_records : int
        Number of records that are retrieved for update and rewritten.

    retrieved_records : int
        Number of records that are retrieved from the component, whether it is
        used for update or not.

    control_interval_splits : int
        Control interval splits.

    control_area_splits : int
        Control area splits.

    free_space_percentage_ci : int
        Percentage of space allocated that is kept free in a control interval,
        which will be used for subsequent processing.

    free_space_percentage_ca : int
        Percentage of space allocated that is kept free in a control area,
        which will be used for subsequent processing.

    free_space : int
        Actual number of bytes of free space that are allocated to the component.

    Notes
    -----
    See https://www.ibm.com/docs/en/zos/latest?topic=fields-sta-statistics-group
    for additional details.
    """
    total_records: int
    deleted_records: int
    inserted_records: int
    updated_records: int
    retrieved_records: int
    control_interval_splits: int
    control_area_splits: int
    free_space_percentage_ci: int
    free_space_percentage_ca: int
    free_space: int
    def __post_init__(self) -> None: ...
    @classmethod
    def from_core_json(cls, component_as_dict: dict) -> VsamComponentStatistics:
        '''
        Creates a VsamComponentStatistics object from a dls JSON response.

        Parameters
        ----------
        component_as_dict : dict
            "data" or "index" dictionary from an element of the "vsams" array
            in a dls JSON response.

        Returns
        -------
        VsamComponentStatistics
            Representation of the statistics for a VSAM component.
        '''

@dataclass(kw_only=True, frozen=True)
class VsamComponent:
    '''
    Class that represents a VSAM component.

    Attributes
    ----------
    name : str
        Name of the VSAM component.

    data_organization : str
        Dataset data organization

    average_record_length : int
        Average record length in bytes.

    maximum_record_length : int
        Maximum record length in bytes.

    key_length : int | None
        Length of the key field in a data record.
        This field applies to KSDS data components.

    key_position : int | None
        Relative key position.
        This field applies to KSDS data components.

    buffer_space : int
        The minimum buffer space, in bytes, in virtual storage that is provided
        by a processing program.

    control_interval_size : int
        Size of a control interval in bytes.

    share_option_region : int
        Cross region share option

    share_option_system : int
        Cross system share option.

    erase : bool
        True if the dataset has the `ERASE` attribute.
        False if the dataset has the `NOERASE` attribute.

    recovery : bool
        True if the dataset has the `RECOVERY` attributes. False otherwise.

    reuse : bool
        True if the dataset has the `REUSE` attribute.
        False if the dataset has the `NOREUSE` attribute.

    spanned : bool
        True if the dataset has the `SPANNED` attribute.
        False if the dataset has the `NOSPANNED` attribute.

    speed : bool
        True if the dataset has the `SPEED` attribute. False otherwise.

    base_cluster : str
        The name of the cluster base this component belongs to.

    catalog_type : str
        The catalog type identifier for this entry. May be one of the following:
            "D" for data components.
            "I" for index components.

    @see https://www.ibm.com/docs/en/zos/latest?topic=dcp-optional-parameters
    for detailed descriptions of the VSAM attributes.
    '''
    name: str
    data_organization: str | None
    average_record_length: int
    maximum_record_length: int
    key_length: int | None
    key_position: int | None
    buffer_space: int
    control_interval_size: int
    share_option_region: int
    share_option_system: int
    erase: bool
    recovery: bool
    reuse: bool
    spanned: bool
    speed: bool
    base_cluster_name: str
    catalog_type: str
    def __post_init__(self) -> None: ...
    @classmethod
    def from_core_json(cls, cluster_as_dict: dict, is_data_component: bool = True):
        '''
        Create a VsamComponent instance from a dls VSAM cluster JSON object.

        Parameters
        ----------
        cluster_as_dict : dict
            An element from the "vsams" array in a dls JSON response.

        is_data_component : bool
            True to extract the information from the data component.
            False to extract the information from the index component.

        Returns
        -------
        VsamComponent | None
            Reprensentation of a VSAM component.
            None if the cluster does not contain the requested component.
        '''
    def fetch_statistics(self, debug: bool = False, verbose: bool = False) -> VsamComponentStatistics:
        """Gets the latest statistics for the VSAM component."""

class VsamCluster:
    """
    Class that represents a z/OS VSAM cluster.

    Attributes
    ----------
    name : str
        Name of the VSAM cluster.

    type : str
        Type of VSAM cluster.

    data : VsamComponent
        VSAM data component representation.

    index : VsamComponent | None
        Representation of the index component for a KSDS VSAM.
        `None` for other types of VSAM clusters.
    """
    @property
    def name(self):
        """Name of the VSAM cluster."""
    @property
    def type(self):
        """Type of VSAM cluster."""
    @property
    def data(self):
        """VSAM data component representation."""
    @property
    def index(self):
        """VSAM index component representation."""
    def __init__(self, name: str, type: str, data: VsamComponent, /, index: VsamComponent | None = None) -> None: ...
    @classmethod
    def from_core_json(cls, cluster_as_dict: dict):
        '''
        Create a VsamCluster instance from a dls JSON response.

        Returns
        -------
        VsamCluster
            Reprensentation of a VSAM cluster

        Parameters
        ----------
        cluster_as_dict : dict
            An element from the "vsams" array in a dls JSON response.
        '''

def fetch_cluster(name: str, *, debug: bool = False, verbose: bool = False) -> VsamCluster:
    """
    Fetches the metadata of a cataloged VSAM cluster.

    Parameters
    ----------
    name : str
        Fully qualified VSAM cluster name.

    Other Parameters
    ----------------
    debug: bool
        Enable debug messages (only for exceptions)

    verbose: bool
        Enable verbose output (only for exceptions)

    Returns
    -------
    VsamCluster
        Representation of the VSAM cluster.

    Raises
    ------
    VsamClusterFetchException : (message:str, response:ZOAUResponse)
        Errors during the ZOAU Core library calls. See message for details
    """
