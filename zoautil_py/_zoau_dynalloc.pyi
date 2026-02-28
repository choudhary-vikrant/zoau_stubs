# ******************************************************************************
#  Licensed Materials - Property of IBM
#  (c) Copyright IBM Corporation 2025. All Rights Reserved.
#
#  Note to U.S. Government Users Restricted Rights:
#  Use, duplication or disclosure restricted by GSA ADP Schedule
#  Contract with IBM Corp.
# ******************************************************************************
#
# Stub file for the '_zoau_dynalloc' C extension module
# (zoautil_py._zoau_dynalloc).
#
# This module is a Python C extension compiled only for z/OS. This stub
# provides type information so that IDEs and type-checkers can work with
# the module on non-z/OS platforms (macOS, Windows, Linux).
#
# Sources:
#   mvsutil-python/extensions/_zoau_dynalloc/_zoau_dynalloc_module.c
#   mvsutil-python/extensions/_zoau_dynalloc/data_definition.c
#   mvsutil-python/extensions/_zoau_dynalloc/include/zoau_dynalloc.h
#   mvsutil-python/extensions/_zoau_dynalloc/include/data_definition.h
#   mvsutil-python/extensions/_zoau_dynalloc/include/param_proc.h
#
# NOTE on naming:
#   The C extension registers the concrete type as ``_DataDefinition``
#   (with a leading underscore), matching the tp_name
#   ``"_zoau_dynalloc._DataDefinition"``.
#   A public ``DataDefinition`` alias is provided at the bottom of this
#   file for IDE convenience.
#

from __future__ import annotations

from typing import Literal, Optional

# ---------------------------------------------------------------------------
# Valid string literals for keyword parameters
# ---------------------------------------------------------------------------

#: Valid ``status`` values for :class:`_DataDefinition`.
DatasetStatus = Literal["OLD", "NEW", "MOD", "SHR"]

#: Valid ``normdisp`` / ``conddisp`` values for :class:`_DataDefinition`.
DatasetDisposition = Literal["CATLG", "UNCATLG", "DELETE", "KEEP"]

#: Valid ``alcunit`` values for :class:`_DataDefinition`.
AllocationUnit = Literal["CYL", "TRK", "BLK"]


# ---------------------------------------------------------------------------
# _DataDefinition – dynamic allocation class (C extension type name)
# ---------------------------------------------------------------------------
# The C extension registers this type as ``_DataDefinition`` (with a leading
# underscore), matching tp_name ``"_zoau_dynalloc._DataDefinition"``.
# A public ``DataDefinition`` alias is provided below for IDE convenience.

class _DataDefinition:
    """Dynamically allocate a z/OS data definition (DD).

    Performs a dynamic allocation (``dynalloc``) on construction and a
    dynamic deallocation (``dynfree``) on :meth:`deallocate` or when the
    object is garbage-collected while still allocated.

    Supports use as a context manager: the DD is deallocated automatically
    on ``__exit__``.

    Args:
        ddname: Data definition name (1–8 characters).  Associates a DD
            name with the allocation request.  Specify eight question marks
            (``"????????"``) to request a system-generated DD name.

        dsname: Fully qualified dataset name to allocate.
        status: Dataset status.  One of ``"OLD"``, ``"NEW"``, ``"MOD"``,
            ``"SHR"``.
        normdisp: Normal termination disposition.  One of ``"CATLG"``,
            ``"UNCATLG"``, ``"DELETE"``, ``"KEEP"``.
        conddisp: Conditional (abnormal) termination disposition.  One of
            ``"CATLG"``, ``"UNCATLG"``, ``"DELETE"``, ``"KEEP"``.
        member: Member name.  Specifies that a particular member of a
            partitioned dataset is to be allocated rather than the entire
            dataset.
        recfm: Dataset record format (e.g. ``"FB"``, ``"VB"``, ``"U"``).
        dsorg: Dataset organisation (e.g. ``"PS"``, ``"PO"``).
        blksize: Dataset block size in bytes.
        lrecl: Dataset logical record length in bytes.
        volser: Volume serial number.
        primary: Primary space allocation quantity.
        secondary: Secondary space allocation quantity.
        alcunit: Space allocation unit.  One of ``"CYL"`` (cylinders),
            ``"TRK"`` (tracks), or ``"BLK"`` (blocks).
        dirblk: Number of directory blocks (for PDS datasets).
        storclass: SMS storage class name.
        mgntclass: SMS management class name.
        dataclass: SMS data class name.
        debug: If ``True``, print diagnostic information to ``stderr``.

    Raises:
        ValueError: If *ddname* exceeds 8 characters, if any parameter
            value is invalid, or if the dynamic allocation fails (includes
            the dynalloc error code and info code in the message).
    """

    def __init__(
        self,
        ddname: str,
        dsname: Optional[str] = None,
        status: Optional[DatasetStatus] = None,
        normdisp: Optional[DatasetDisposition] = None,
        conddisp: Optional[DatasetDisposition] = None,
        member: Optional[str] = None,
        recfm: Optional[str] = None,
        dsorg: Optional[str] = None,
        blksize: int = 0,
        lrecl: int = 0,
        volser: Optional[str] = None,
        primary: int = 0,
        secondary: int = 0,
        alcunit: Optional[AllocationUnit] = None,
        dirblk: int = 0,
        storclass: Optional[str] = None,
        mgntclass: Optional[str] = None,
        dataclass: Optional[str] = None,
        debug: bool = False,
    ) -> None: ...

    # ------------------------------------------------------------------
    # Read-only properties (backed by C getset descriptors)
    # ------------------------------------------------------------------

    @property
    def ddname(self) -> str:
        """The data definition name assigned to this allocation.

        When a system-generated DD name was requested (``"????????"``),
        this property returns the name assigned by the system after a
        successful allocation.
        """
        ...

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def deallocate(self) -> None:
        """Dynamically deallocate the data definition.

        Calls ``dynfree`` to release the DD allocation.  If the data
        definition is already deallocated this method has no effect.

        Raises:
            ValueError: If the dynamic deallocation fails (includes the
                dynfree error code and info code in the message).
        """
        ...

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> _DataDefinition:
        """Enter the runtime context; returns ``self``.

        Raises:
            ValueError: If the data definition is not currently allocated.
        """
        ...

    def __exit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        """Exit the runtime context and deallocate the data definition."""
        ...


# ---------------------------------------------------------------------------
# Public alias
# ---------------------------------------------------------------------------

#: Public alias for the C-level ``_DataDefinition`` type.
DataDefinition = _DataDefinition

# Made with Bob
