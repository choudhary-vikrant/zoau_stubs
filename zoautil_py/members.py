import logging
from dataclasses import dataclass
from datetime import datetime
from zoautil_py.common import clean_dataset_name as clean_dataset_name, zoau_json_load as zoau_json_load
from zoautil_py.core import call_zoau_library as call_zoau_library
from zoautil_py.exceptions import IspfMemberStatisticsUnavailable as IspfMemberStatisticsUnavailable, MemberFetchException as MemberFetchException, MemberFetchInvalidParameter as MemberFetchInvalidParameter, SmdeExtendedAttributesUnavailable as SmdeExtendedAttributesUnavailable
from zoautil_py.ztypes import ZOAUResponse as ZOAUResponse

logger: logging.Logger

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
    version: int
    modification_level: int
    current_lines: int
    initial_lines: int
    modified_lines: int
    date_created: datetime
    time_changed: datetime
    modified_user: str
    def __post_init__(self) -> None: ...
    @classmethod
    def from_core_json(cls, stats_as_dict: dict): ...

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
    ccsid: int | None
    time_modified: datetime | None
    user_modified: str | None
    def __post_init__(self) -> None: ...
    @classmethod
    def from_core_json(cls, ext_attr_dict: dict):
        '''"
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
        '''

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
    def __init__(self, name: str, is_alias: bool = False, *, association: str | None = None, extended_attributes: SmdeExtendedAttributes | None = None, ispf_statistics: IspfMemberStatistics | None = None) -> None: ...
    @property
    def name(self):
        """Name of the member or member alias"""
    @property
    def is_alias(self) -> bool:
        """Whether or not this instance represents an alias for a member."""
    @property
    def association(self) -> str | None:
        """
        Name of the associated member for a member alias.
        `None` if the instance does not represent a member.
        """
    @property
    def ccsid(self) -> int:
        """
        Coded character set identifier.

        Notes
        -----
        SMDE extended attribute. Not all members contain this metadata.
        """
    @property
    def user_modified(self) -> str:
        """
        Last user that modified the member.

        Notes
        -----
        SMDE extended attribute. Not all members contain this metadata.
        """
    @property
    def time_modified(self) -> datetime:
        """
        Last time the member was modified.

        Notes
        -----
        SMDE extended attribute. Not all members contain this metadata.
        """
    @property
    def ispf_statistics(self) -> IspfMemberStatistics:
        """
        ISPF member statistics.

        Notes
        -----
        The ISPF statistics are stored as user data. Not all members contain
        this metadata.
        """
    @classmethod
    def from_core_json(cls, member_as_dict: dict): ...

def fetch_members(dataset_name: str, /, member_pattern: str = '*', *, debug: bool = False, verbose: bool = False) -> list[Member]:
    '''
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
    '''
