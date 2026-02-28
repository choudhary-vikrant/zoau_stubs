# ******************************************************************************
#  Licensed Materials - Property of IBM
#  (c) Copyright IBM Corporation 2019-2023. All Rights Reserved.
#
#  Note to U.S. Government Users Restricted Rights:
#  Use, duplication or disclosure restricted by GSA ADP Schedule
#  Contract with IBM Corp.
# ******************************************************************************
#
# Stub file for the 'core' C extension module (zoautil_py.core).
#
# This module is a Python C extension compiled only for z/OS. This stub
# provides type information so that IDEs and type-checkers can work with
# the module on non-z/OS platforms (macOS, Windows, Linux).
#
# Source: mvsutil-python/extensions/core/core.c
#

from typing import Literal, Union

# ---------------------------------------------------------------------------
# Valid ZOAU command names
# ---------------------------------------------------------------------------
# These are the exact string values accepted by the ``command`` parameter of
# :func:`call_zoau_library` and :func:`call_zoau_library_bin`.  They map
# one-to-one to the function pointers in the ``zoautil_vector4_t`` struct
# (see ``include/zoautil.h``) that are dispatched by ``get_zoau_function()``
# in ``extensions/core/core.c``.
ZOAUCommand = Literal[
    "apfadm",       # APF dataset administration
    "dcp",          # Dataset copy
    "ddiff",        # Dataset diff
    "ddls",         # DD name list
    "decho",        # Dataset echo
    "dgrep",        # Dataset grep
    "dhead",        # Dataset head
    "dinfo",        # Dataset info
    "dls",          # Dataset list
    "dmod",         # Dataset modify
    "dmv",          # Dataset move
    "drm",          # Dataset remove
    "dsed",         # Dataset sed
    "dtail",        # Dataset tail
    "dtouch",       # Dataset touch (create)
    "dunzip",       # Dataset unzip
    "dwhence",      # Dataset whence (locate)
    "dzip",         # Dataset zip
    "hlq",          # High-level qualifier
    "jcan",         # Job cancel
    "jls",          # Job list
    "jsub",         # Job submit
    "llwhence",     # Load library whence
    "mls",          # Member list
    "mmv",          # Member move
    "mrm",          # Member remove
    "mvscmd",       # MVS command
    "mvscmdauth",   # MVS command (authorised)
    "mvstmp",       # MVS temporary dataset name
    "opercmd",      # Operator command
    "parmgrep",     # PARMLIB grep
    "parmwhence",   # PARMLIB whence
    "pcon",         # Print console
    "pdc",          # Print data class
    "pjdd",         # Print JES DD
    "pll",          # Print load library
    "pparm",        # Print PARMLIB
    "pproc",        # Print PROCLIB
    "procgrep",     # PROCLIB grep
    "procwhence",   # PROCLIB whence
    "vf",           # Volume free space
    "vls",          # Volume list
    "vtocls",       # VTOC list
    "zinfo",        # z/OS system info
    "zoaversion",   # ZOAU version
]

def call_zoau_library(
    command: ZOAUCommand,
    options: str,
) -> dict[str, Union[int, str]]:
    """Call a ZOAU shared library function and return a text response.

    Invokes the named ZOAU utility function via the ZOAU shared library
    vector table and returns the result as a dictionary whose stdout and
    stderr streams are UTF-8 strings.

    Args:
        command: Name of the ZOAU utility to invoke.  Must be one of the
            :data:`ZOAUCommand` literals (e.g. ``"dls"``, ``"mvscmd"``,
            ``"jsub"``).  Pylance / pyright will offer autocomplete for
            all valid values.
        options: Command-line options string to pass to the utility.

    Returns:
        A dictionary with the following keys:

        * ``"rc"`` (``int``) – Return code from the ZOAU utility.
        * ``"response_format"`` (``str``) – Always ``"UTF-8"`` for this
          variant.
        * ``"stdout_response"`` (``str``) – Standard output from the
          utility, sanitized to printable characters.
        * ``"stderr_response"`` (``str``) – Standard error from the
          utility, sanitized to printable characters.
        * ``"command"`` (``str``) – The full command string that was
          executed (``command + " " + options``).

    Raises:
        ValueError: If the ZOAU shared library cannot be initialised, the
            version does not match, *command* is not a recognised ZOAU
            function, or a response buffer cannot be sanitized.
        MemoryError: If memory allocation for the command string fails.
    """
    ...


def call_zoau_library_bin(
    command: ZOAUCommand,
    options: str,
) -> dict[str, Union[int, str, bytes]]:
    """Call a ZOAU shared library function and return a binary response.

    Identical to :func:`call_zoau_library` except that the stdout and
    stderr streams are returned as raw ``bytes`` objects rather than
    decoded strings.  Use this variant when the utility output may
    contain non-text data.

    Args:
        command: Name of the ZOAU utility to invoke.  Must be one of the
            :data:`ZOAUCommand` literals (e.g. ``"dls"``, ``"mvscmd"``,
            ``"jsub"``).  Pylance / pyright will offer autocomplete for
            all valid values.
        options: Command-line options string to pass to the utility.

    Returns:
        A dictionary with the following keys:

        * ``"rc"`` (``int``) – Return code from the ZOAU utility.
        * ``"response_format"`` (``str``) – Always ``"binary"`` for this
          variant.
        * ``"stdout_response"`` (``bytes``) – Raw standard output from
          the utility.
        * ``"stderr_response"`` (``bytes``) – Raw standard error from
          the utility.
        * ``"command"`` (``str``) – The full command string that was
          executed (``command + " " + options``).

    Raises:
        ValueError: If the ZOAU shared library cannot be initialised, the
            version does not match, or *command* is not a recognised ZOAU
            function.
        MemoryError: If memory allocation for the command string fails.
    """
    ...

# Made with Bob
