# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2025
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
ZOAU Python functions and objects for z/OS VSAM operations.
"""

import logging
from dataclasses import dataclass, fields
import warnings

from zoautil_py.common import clean_dataset_name, zoau_json_load
from zoautil_py.exceptions import DatasetFetchException, VsamClusterFetchException, VsamClusterNameInvalidPattern
from zoautil_py.ztypes import ZOAUResponse

from zoautil_py.core import call_zoau_library # pylint: disable=import-error, no-name-in-module

logger: logging.Logger
logger = logging.getLogger(__name__)

_VSAM_CLUSTER_CATALOG_TYPE="C"
_VSAM_DATA_COMPONENT_CATALOG_TYPE="D"
_VSAM_INDEX_COMPONENT_CATALOG_TYPE="I"

@dataclass(kw_only=True, frozen=True)
class VsamComponentStatistics():
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
    total_records : int
    deleted_records : int
    inserted_records : int
    updated_records : int
    retrieved_records : int
    control_interval_splits : int
    control_area_splits : int
    free_space_percentage_ci : int
    free_space_percentage_ca : int
    free_space : int

    def __post_init__(self):
        # Verify argument types
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise TypeError(f"{field.name} parameter must be {field.type}")

    @classmethod
    def from_core_json(cls, component_as_dict: dict) -> "VsamComponentStatistics":
        """
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
        """

        return cls(
            total_records=component_as_dict["rec-total"],
            deleted_records=component_as_dict["rec-deleted"],
            inserted_records=component_as_dict["rec-inserted"],
            updated_records=component_as_dict["rec-updated"],
            retrieved_records=component_as_dict["rec-retrieved"],
            control_interval_splits=component_as_dict["splits-ci"],
            control_area_splits=component_as_dict["splits-ca"],
            free_space_percentage_ci=component_as_dict["freespc-%ci"],
            free_space_percentage_ca=component_as_dict["freespc-%ca"],
            free_space=component_as_dict["freespc"]
        )


@dataclass(kw_only=True, frozen=True)
class VsamComponent():
    """
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
    """

    name                        : str
    data_organization           : str | None # Data component field.
    average_record_length       : int
    maximum_record_length       : int
    key_length                  : int | None # KSDS data component field.
    key_position                : int | None # KSDS data component field.
    buffer_space                : int
    control_interval_size       : int
    share_option_region         : int
    share_option_system         : int
    erase                       : bool
    recovery                    : bool
    reuse                       : bool
    spanned                     : bool
    speed                       : bool
    base_cluster_name           : str
    catalog_type                : str

    def __post_init__(self):
        # Verify argument types
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise TypeError(f"{field.name} parameter must be {field.type}")

    @classmethod
    def from_core_json(cls, cluster_as_dict: dict, is_data_component: bool=True):
        """
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
        """

        data_component_dict = cluster_as_dict.get("data")

        # Some types of VSAM datasets do not contain an index component.
        index_component_dict = cluster_as_dict.get("index", None)

        if is_data_component:
            component_as_dict = data_component_dict
        else:
            component_as_dict = index_component_dict

        if not component_as_dict:
            return None

        # We have to adjust some attributes before creation because the instance
        # will be immutable.

        cluster_name = clean_dataset_name(cluster_as_dict.get("name"))
        cluster_type = data_component_dict.get("dsntype")
        data_organization = component_as_dict.get("org")
        key_length = component_as_dict.get("klen")
        key_position = component_as_dict.get("rkp")

        if cluster_type != "KSDS" or not is_data_component:
            key_length = None
            key_position = None

        if not is_data_component:
            data_organization = None

        return cls(
            name=component_as_dict["name"],
            average_record_length=component_as_dict["avglrecl"],
            maximum_record_length=component_as_dict["maxlrecl"],
            buffer_space=component_as_dict["bufspace"],
            control_interval_size=component_as_dict["cisize"],
            share_option_region=component_as_dict["shropt-region"],
            share_option_system=component_as_dict["shropt-system"],
            erase=component_as_dict["erase"],
            recovery=component_as_dict["recovery"],
            reuse=component_as_dict["reuse"],
            spanned=component_as_dict["spanned"],
            speed=component_as_dict["speed"],
            catalog_type=component_as_dict["ctlgtype"],
            base_cluster_name=cluster_name,
            data_organization=data_organization,
            key_length=key_length,
            key_position=key_position
        )

    def fetch_statistics(self, debug: bool = False, verbose: bool = False) -> VsamComponentStatistics:
        """Gets the latest statistics for the VSAM component."""

        options="-tVSAM -Sj "

        if debug:
            options+="-d "
        if verbose:
            options+="-v "

        options+=f' -- "{self.base_cluster_name}"'

        # call shared library
        logger.debug("ZOAU_CORE call: dls %s", options)
        response = ZOAUResponse.from_dict(call_zoau_library("dls", options))

        if response.rc:
            raise DatasetFetchException(response)

        response_json, _ = zoau_json_load(response.stdout_response)

        if self.catalog_type == _VSAM_INDEX_COMPONENT_CATALOG_TYPE:
            component_as_dict = response_json.get("vsams")[0].get("index")
        else:
            component_as_dict = response_json.get("vsams")[0].get("data")

        return VsamComponentStatistics.from_core_json(component_as_dict)


class VsamCluster():
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
    # Immutable properties.
    @property
    def name(self):
        """Name of the VSAM cluster."""
        return self.__name

    @property
    def type(self):
        """Type of VSAM cluster."""
        return self.__type

    @property
    def data(self):
        """VSAM data component representation."""
        return self.__data

    @property
    def index(self):
        """VSAM index component representation."""
        if self.__index is None:
            warnings.warn(
                f"A {self.__type} VSAM type does not contain an index component."
            )

        return self.__index

    # Constructor
    def __init__(
            self,
            name : str,
            type : str,
            data : VsamComponent,
            /,
            index : VsamComponent | None = None,
        ):

        if not isinstance(name, str):
            raise TypeError("name parameter must be a string")

        if not isinstance(type, str):
            raise TypeError("type parameter must be a string")

        if not isinstance(data, VsamComponent):
            raise TypeError("data parameter must be a VsamComponent instance")

        if index is not None and not isinstance(index, VsamComponent):
            raise TypeError("index parameter must be a VsamComponent instance")

        self.__name = name
        self.__type = type
        self.__data = data
        self.__index = index

    @classmethod
    def from_core_json(cls, cluster_as_dict : dict):
        """
        Create a VsamCluster instance from a dls JSON response.

        Returns
        -------
        VsamCluster
            Reprensentation of a VSAM cluster

        Parameters
        ----------
        cluster_as_dict : dict
            An element from the "vsams" array in a dls JSON response.
        """

        cluster_name = cluster_as_dict.get("name")
        vsam_type = cluster_as_dict.get("data").get("dsntype")

        data_component = VsamComponent.from_core_json(cluster_as_dict, True)
        index_component = VsamComponent.from_core_json(cluster_as_dict, False)

        return cls(
            cluster_name,
            vsam_type,
            data_component,
            index = index_component
        )


def fetch_cluster(name : str, *, debug=False, verbose=False) -> VsamCluster:
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
    logger.debug("fetch cluster function call")
    logger.debug("name: %s", name)

    if name.find("*") > 0 or name.find("?") > 0:
        raise VsamClusterNameInvalidPattern

    # Extended VSAM listing options
    options = "-tVSAM -FijlpT "

    if debug:
        options += "-d "
    if verbose:
        options += "-v "

    escaped_name = clean_dataset_name(name)
    options += f" -- {escaped_name}"

    response = call_zoau_library("dls", options)
    response = ZOAUResponse.from_dict(response)

    if response.rc:
        raise VsamClusterFetchException(response)

    response_json, _ = zoau_json_load(response.stdout_response)
    response_dict = response_json.get("vsams")[0]

    return VsamCluster.from_core_json(response_dict)
