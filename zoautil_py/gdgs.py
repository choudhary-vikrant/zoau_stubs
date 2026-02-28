# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2024
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------

"""
Module that provides functions and objects for z/OS Generation Data Group (GDG)
operations.
"""

import logging
from typing import Union

from zoautil_py.common import (
    RelativeList,
    clean_dataset_name,
    parse_universal_arguments,
    zoau_json_load,
)

from zoautil_py.core import call_zoau_library # pylint: disable=import-error, no-name-in-module

from zoautil_py.exceptions import (
    DatasetFetchException,
    GenerationDataGroupClearException,
    GenerationDataGroupDeleteException,
    GenerationDataGroupFetchException,
    GenerationDataGroupCreateException,
    GenerationDataGroupViewInvalidName,
    GenerationDataGroupViewInvalidState,
)

from zoautil_py import datasets
from zoautil_py.ztypes import ZOAUResponse

logger: logging.Logger
logger = logging.getLogger(__name__)

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

    def __init__(
        self,
        name : str,
        **kwargs
    ):
        if not isinstance(name, str):
            raise TypeError("The name argument must be a string.")

        if name.find("*") > 0 or name.find("?") > 0:
            raise GenerationDataGroupViewInvalidName(
                "The name argument does not support patterns."
            )

        self.__name_escaped = clean_dataset_name(name)

        response = datasets._dls_call(
            pattern=self.__name_escaped, name_only=False, list_gdg=True, **kwargs
        )

        if response.rc:
            raise GenerationDataGroupFetchException(response)

        response_json, _ = zoau_json_load(response.stdout_response)

        response_dict = response_json.get("gdgs")[0]

        self.__base     = response_dict.get("base")
        self.__limit    = response_dict.get("limit")
        self.__empty    = response_dict.get("empty")
        self.__scratch  = response_dict.get("scratch")
        self.__fifo     = response_dict.get("fifo")
        self.__purge    = response_dict.get("purge")
        self.__extended = response_dict.get("extended")


    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return f"zoautil_py.gdgs.GenerationDataGroupView object with name:{self.__base}"


    @property
    def name(self) -> str:
        """Name of the GDG."""
        return self.__base

    @name.setter
    def name(self, value):
        """Name of the GDG. (Setter)."""
        target = clean_dataset_name(value)
        datasets.move(self.__name_escaped, target)

        self.__name_escaped = target
        self.__base = value


    # Immutable properties.
    # The following properties are meant to be read-only until we provide ALTER
    # capabilities via setters.

    @property
    def limit(self) -> int:
        """Maximum number of active generations in the group."""
        return self.__limit

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
        return self.__scratch

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
        return self.__empty

    @property
    def order(self):
        """
        Determines the allocation order of the generation datasets during GDG
        ALL requests.
        """
        if self.__fifo:
            return "FIFO"
        else:
            return "LIFO"

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
        return self.__purge

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
        return self.__extended

    @property
    def generations(self) -> Union[list[datasets.Dataset],list]:
        """
        Snapshot of the active generation datasets in the GDG.

        Returns
        -------
        list[Dataset]
            Snapshot of the active generation datasets in the GDG.
        """

        if not exists(self.__base):
            # This handles the out of sync possibility between the view object
            # and the underlying GDG.
            raise GenerationDataGroupViewInvalidState(f"The GDG {self.__base} "
                                                       "does not exist.")

        # The type arg will filter out datasets in a rolled-off state.
        response = datasets._dls_call(pattern=f"{self.__name_escaped}.G*",
                                      list_gds=True)

        # Error from dls call
        if response.rc not in (0,1):
            raise DatasetFetchException(response)

        # No dataset match
        if not response.stdout_response:
            return []

        response_json, _ = zoau_json_load(response.stdout_response)

        dict_list: list = []
        try:
            dict_list = response_json.get("datasets") # type: ignore
        except KeyError as exc:
            raise KeyError("Missing dataset key from JSON") from exc

        gds = (datasets.Dataset.from_core_json(ds_dict) for ds_dict in dict_list)

        return RelativeList(gds)


    # Methods
    def __len__(self):
        """
        Returns the number of active generation data sets in the GDG.
        """
        return len(self.generations)


    def _list_rolled_off_generations(
            self, debug: bool = False, verbose: bool = False
        )-> list[str]:
        """
        Lists the rolled-off generations that are still cataloged and named
        after the GDG base.

        Other Parameters
        ----------------
        debug: bool
            Enable debug messages (only for exceptions).

        verbose: bool
            Enable verbose output (only for exceptions).
        """

        response = datasets._dls_call(
            pattern=f"{self.__name_escaped}.G????V??",
            name_only=True,
            list_nvsam=True,
            debug=debug,
            verbose=verbose
        )

        if response.rc not in (0,1):
            raise DatasetFetchException(response)

        if not response.stdout_response:
            return []

        return list(response.stdout_response.rstrip().split("\n"))


    def _delete_rolled_off_generations(
            self, debug: bool = False, verbose: bool = False
        ):
        """
        Deletes the rolled-off generations that are still cataloged and named
        after the GDG base.

        Other parameters
        ----------------
        debug: bool
            Enable debug messages (only for exceptions).

        verbose: bool
            Enable verbose output (only for exceptions).
        """

        undeleted = []

        for dsname in self._list_rolled_off_generations(
            debug=debug,
            verbose=verbose
        ):
            if datasets.delete(dsname) != 0:
                undeleted.append(dsname)

        if undeleted != []:
            raise GenerationDataGroupClearException(
                f"Could not delete the rolled-off generations: {undeleted}"
            )


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

        options = ""
        options += parse_universal_arguments(**kwargs)

        # drm -F forces a GDG deletion when the group is not empty, by deleting
        # first the active GDS and then the base.

        options += f'-F -- "{self.__name_escaped}"'

        logger.debug("ZOAU_CORE call: drm %s", options)

        response = ZOAUResponse.from_dict(
            call_zoau_library("drm", options)
        )

        if response.rc != 0:
            raise GenerationDataGroupDeleteException(response)

        if include_rolled_off:
            self._delete_rolled_off_generations(**kwargs)


    def clear(self):
        """
        Removes all the active generations from the generation data group.
        """

        # Iterate a snapshot instead of calling `drm` with a pattern. This will
        # delete the active GDS and exclude datasets in a rolled-off state.

        undeleted = [] #Unable to delete

        for generation in self.generations:
            if generation.delete() != 0:
                undeleted.append(generation.name)

        if undeleted:
            raise GenerationDataGroupClearException(
                    f"Could not delete the generation datasets: {undeleted}"
                )

    def generate(self, index:int=1, **kwargs) -> datasets.Dataset:
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
        if not isinstance(index,int):
            raise TypeError("index argument must be of type int.")
        if index <= 0:
            raise ValueError("index argument must be a postive integer.")

        new_gen_name = f"{self.name}(+{index})"
        logger.debug("Generating next gdg with index %s",new_gen_name)

        return datasets.create(new_gen_name, **kwargs)


def _create(
    name     : str,
    limit    : int, *,
    empty    : bool = False,
    scratch  : bool = False,
    purge    : bool = False,
    extended : bool = False,
    fifo     : bool = False,
    **kwargs
) -> ZOAUResponse:
    """Builds a command string and calls ZOAU core (dtouch) to create a GDG."""

    options = ""
    options += parse_universal_arguments(**kwargs)

    if empty:
        options += "-E "
    if scratch:
        options += "-S "
    if purge:
        options += "-P "
    if extended:
        options += "-X "
    if fifo:
        options += "-Y "

    options += f' -tGDG -L{limit} -- "{clean_dataset_name(name)}"'

    logger.debug("ZOAU_CORE call: dtouch %s", options)
    response = call_zoau_library("dtouch", options)

    return ZOAUResponse.from_dict(response)


def create(
    name     : str,
    limit    : int, *,
    empty    : bool = False,
    scratch  : bool = False,
    purge    : bool = False,
    extended : bool = False,
    fifo     : bool = False,
    **kwargs
) -> GenerationDataGroupView:
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

    logger.debug("Create GDG function call.")
    logger.debug("name:     %s", name)
    logger.debug("limit:    %s", limit)
    logger.debug("empty:    %s", empty)
    logger.debug("scratch:  %s", scratch)
    logger.debug("purge:    %s", purge)
    logger.debug("extended: %s", extended)
    logger.debug("fifo:     %s", fifo)
    logger.debug("kwargs:   %s", kwargs)

    response = _create(
        name,
        limit,
        empty = empty,
        scratch = scratch,
        purge = purge,
        extended = extended,
        fifo = fifo,
        **kwargs
    )

    if response.rc:
        raise GenerationDataGroupCreateException(response)

    # The constructor escapes the name.
    return GenerationDataGroupView(name)


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

    logger.debug("listing name only GDG function call")
    logger.debug("pattern: %s", pattern)

    response = datasets._dls_call(
        pattern=pattern,
        name_only=True,
        list_gdg=True,
        **kwargs
    )

    if response.rc not in (0,1):
        raise GenerationDataGroupFetchException(response)

    if not response.stdout_response:
        return []

    return list(response.stdout_response.rstrip().split("\n"))


def exists(name : str, **kwargs):
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
    name = clean_dataset_name(name)

    logger.debug("exists GDG function call")
    logger.debug("GDG: %s", name)

    options = ""
    options += parse_universal_arguments(**kwargs)

    # Using dls in quiet mode will return only 0 if a match was found
    options += f'-q -tGDG "{name}"'
    logger.debug("ZOAU_CORE call: dls %s", options)
    response = ZOAUResponse.from_dict(call_zoau_library("dls", options))

    if response.rc not in (1,0):
        raise GenerationDataGroupFetchException(response)

    return response.rc == 0
