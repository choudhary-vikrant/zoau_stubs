# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2019, 2025
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
"""
ZOAU Python functions and objects for z/OS partitioned dataset member operations.
"""

import logging
import warnings

from dataclasses import dataclass, fields
from datetime import datetime

from zoautil_py.core import call_zoau_library
from zoautil_py.common import clean_dataset_name, zoau_json_load
from zoautil_py.exceptions import (MemberFetchInvalidParameter,
                                   SmdeExtendedAttributesUnavailable,
                                   MemberFetchException,
                                   IspfMemberStatisticsUnavailable)
from zoautil_py.ztypes import ZOAUResponse

logger: logging.Logger
logger = logging.getLogger(__name__)


@dataclass(kw_only=True, frozen=True)
class IspfMemberStatistics:
    """
    Class that represents a snapshot of the ISPF statistics for a z/OS
    partitioned dataset member.

    Attributes
    ----------
    version: int
        ISPF version number.

    modification_level: int
        ISPF modification level.
        Number of times this version has been modified.

    current_lines: int
        Current number of lines.

    initial_lines: int
        Initial number of lines.

    modified_lines: int
        Number of lines that have been added or changed. If the data is
        unnumbered this equals zero.

    date_created: datetime
        Date this version was created.

    time_changed: datetime
        Date and time this version was last modified.

    modified_by_user: str
        User ID that created or last updated this version.
    """

    version : int
    modification_level : int
    current_lines : int
    initial_lines : int
    modified_lines : int
    date_created : datetime
    time_changed : datetime
    modified_user : str

    def __post_init__(self):
        # Verify argument types
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise TypeError(f"{field.name} parameter must be {field.type}")

    @classmethod
    def from_core_json(cls, stats_as_dict: dict):

        created = stats_as_dict["created"]
        changed = stats_as_dict["changed"]

        date_created = datetime.strptime(created, "%Y/%m/%d")
        time_changed = datetime.strptime(changed, "%Y/%m/%d %H:%M:%S")

        return cls(
            version=stats_as_dict["version"],
            modification_level=stats_as_dict["modlvl"],
            current_lines=stats_as_dict["current"],
            initial_lines=stats_as_dict["initial"],
            modified_lines=stats_as_dict["modified"],
            modified_user=stats_as_dict["user"],
            date_created=date_created,
            time_changed=time_changed
        )


@dataclass(kw_only=True, frozen=True)
class SmdeExtendedAttributes:
    """
    Class that represents a snapshot of the system managed directory entry (SMDE)
    extended attributes for a z/OS partitioned dataset member.

    Attributes
    ----------
    ccsid: int | None
        Coded character set identifier.

    time_modified: datetime | None
        Last time the member was modified.

    user_modified: str | None
        Last uset that modified the member.
    """

    ccsid : int | None
    time_modified : datetime | None
    user_modified : str | None

    def __post_init__(self):
        # Verify argument types
        for field in fields(self):
            value = getattr(self, field.name)
            if not isinstance(value, field.type):
                raise TypeError(f"{field.name} parameter must be {field.type}")

    @classmethod
    def from_core_json(cls, ext_attr_dict : dict):
        """"
        Creates a SmdeExtendedAttributes instance from the `mls` JSON response.

        Parameters
        ----------
        ext_attr_dict
            ext_attr JSON object from a `mls` member element.

        Returns
        -------
        SmdeExtendedAttributes
            Representation of the system managed directory entry (SMDE) extended
            attributes.
        """

        user_modified = ext_attr_dict.get("user")
        time_modified = ext_attr_dict.get("changed")

        # Check for empty user string
        if len(user_modified) == 0:
            user_modified = None

        # Parse modified time
        time_modified = datetime.strptime(time_modified, "%Y/%m/%d %H:%M:%S")

        return cls(
            ccsid = ext_attr_dict["ccsid"],
            time_modified = time_modified,
            user_modified = user_modified
        )


class Member:
    """
    Class that represents a snapshot of a z/OS partitioned dataset member.

    Attributes
    ----------
    name: str
        Name of the partitioned dataset member or member alias.

    is_alias: bool
        Whether or not this instance represents an alias for a member.

    association: str | None
        Name of the associated member for a member alias. `None` if the instance
        does not represent a member.

    ccsid: int
        Coded character set identifier. This is an SMDE extended attribute. Not
        all members contain this metadata.

    user_modified: str
        Last user that modified the member. This is an SMDE extended attribute.
        Not all members contain this metadata.

    time_modified: datetime
        Last time the member was modified. This is an SMDE extended attribute.
        Not all members contain this metadata.

    ispf_statistics: IspfMemberStatistics
        ISPF member statistics. The ISPF statistics are stored as user data in
        a partitioned dataset directory. Not all members contain this metadata.
    """

    __name : str
    __is_alias : bool
    __association : str | None
    __extended_attributes : SmdeExtendedAttributes | None
    __ispf_statistics : IspfMemberStatistics | None

    def __init__(
        self,
        name : str,
        is_alias : bool = False,
        *,
        association : str | None  = None,
        extended_attributes : SmdeExtendedAttributes | None = None,
        ispf_statistics : IspfMemberStatistics | None = None
    ):

        if not isinstance(name, str):
            raise TypeError("name parameter must be a string")

        if not isinstance(is_alias, bool):
            raise TypeError("is_alias parameter must be bool")

        if association is not None and not isinstance(association, str):
            raise TypeError("association parameter must be a string")

        if extended_attributes is not None and not isinstance(extended_attributes, SmdeExtendedAttributes):
            raise TypeError("extended_attributes parameter must be an instance of SmdeExtendedAttributes")

        if ispf_statistics is not None and not isinstance(ispf_statistics, IspfMemberStatistics):
            raise TypeError("ispf_statistics parameter must be an instance of MemberIspfStatistics")

        self.__name = name
        self.__is_alias = is_alias
        self.__association = association
        self.__extended_attributes = extended_attributes
        self.__ispf_statistics = ispf_statistics

    @property
    def name(self):
        """Name of the member or member alias"""
        return self.__name

    @property
    def is_alias(self) -> bool:
        """Whether or not this instance represents an alias for a member."""
        return self.__is_alias

    @property
    def association(self) -> str | None:
        """
        Name of the associated member for a member alias.
        `None` if the instance does not represent a member.
        """
        if self.__is_alias and self.__association is None:
            warnings.warn(f"Alias {self.name} exists without a true member name.")
        return self.__association

    @property
    def ccsid(self) -> int:
        """
        Coded character set identifier.

        Notes
        -----
        SMDE extended attribute. Not all members contain this metadata.
        """
        if self.__extended_attributes is None:
            raise SmdeExtendedAttributesUnavailable
        return self.__extended_attributes.ccsid

    @property
    def user_modified(self) -> str:
        """
        Last user that modified the member.

        Notes
        -----
        SMDE extended attribute. Not all members contain this metadata.
        """
        if self.__extended_attributes is None:
            raise SmdeExtendedAttributesUnavailable
        return self.__extended_attributes.user_modified

    @property
    def time_modified(self) -> datetime:
        """
        Last time the member was modified.

        Notes
        -----
        SMDE extended attribute. Not all members contain this metadata.
        """
        if self.__extended_attributes is None:
            raise SmdeExtendedAttributesUnavailable
        return self.__extended_attributes.time_modified

    @property
    def ispf_statistics(self) -> IspfMemberStatistics:
        """
        ISPF member statistics.

        Notes
        -----
        The ISPF statistics are stored as user data. Not all members contain
        this metadata.
        """
        if self.__ispf_statistics is None:
            raise IspfMemberStatisticsUnavailable
        return self.__ispf_statistics

    @classmethod
    def from_core_json(cls, member_as_dict: dict):

        ext_attr_dict = member_as_dict.get("ext_attr")
        ispf_stats_dict = member_as_dict.get("ispf_stats")
        assoc = member_as_dict.get("assoc", None)

        if len(ext_attr_dict) == 0:
            ext_attr = None
        else:
            ext_attr = SmdeExtendedAttributes.from_core_json(ext_attr_dict)

        if len(ispf_stats_dict) == 0:
            ispf_stats = None
        else:
            ispf_stats = IspfMemberStatistics.from_core_json(ispf_stats_dict)

        # Check for alias without association (empty assoc JSON string)
        if assoc is not None and len(assoc) == 0:
            assoc = None

        return cls(
            member_as_dict["name"],
            member_as_dict["is_alias"],
            association = assoc,
            extended_attributes = ext_attr,
            ispf_statistics = ispf_stats
        )


def fetch_members(
    dataset_name    : str,
    /,
    member_pattern  : str = "*",
    *,
    debug           : bool = False,
    verbose         : bool = False
) -> list[Member]:
    """
    Gets a list of partitioned dataset members that match the supplied pattern
    from the provided partioned dataset directory.

    Notes
    -----
    Member aliases are also listed.

    Returns
    -------
    list[Member]
        List of Member objects

    list[]
        Empty list if no members are found.

    Parameters
    ----------
    dataset_name: str
        Name of the partitioned dataset directory.

    member_pattern : str, optional
        Member pattern to match.
        Defaults to "*"

    Other parameters
    ----------------
    debug: bool, optional
        Enable debug messages (only for exceptions)

    verbose: bool, optional
        Enable verbose messages (only for exceptions)
    """

    logger.debug("fetch members function call")
    logger.debug("dataset_name: %s", dataset_name)

    if dataset_name.find("*") > 0 or dataset_name.find("?") > 0:
        raise MemberFetchInvalidParameter(
            "The wildcards '*' and '?' are not supported in the dataset_name parameter")

    options = "-AejS "
    if debug:
        options += "-d "
    if verbose:
        options += "-v "

    options += f" -- '{dataset_name}({member_pattern})'"

    logger.debug("ZOAU_CORE call: mls %s", options)
    response = call_zoau_library("mls", options)
    response = ZOAUResponse.from_dict(response)

    MLS_RC_NO_ERROR=0
    MLS_RC_NO_DATASET_MATCHES=1
    MLS_RC_NO_MEMBER_MATCHES=2

     # Error from mls call
    if response.rc == MLS_RC_NO_DATASET_MATCHES:
        raise MemberFetchException(response)
    elif response.rc == MLS_RC_NO_MEMBER_MATCHES:
        return []
    elif response.rc != MLS_RC_NO_ERROR:
        raise MemberFetchException(response)

    response_json, _ = zoau_json_load(response.stdout_response)
    logger.debug("json data: %s", response_json)

    dict_list: list = []
    try:
        dict_list = response_json.get("members")  # type: ignore
    except KeyError as exc:
        raise KeyError("Missing members key from JSON") from exc

    return [Member.from_core_json(mem_dict) for mem_dict in dict_list]
