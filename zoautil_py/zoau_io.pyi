# ******************************************************************************
#  Licensed Materials - Property of IBM
#  (c) Copyright IBM Corporation 2023-2025. All Rights Reserved.
#
#  Note to U.S. Government Users Restricted Rights:
#  Use, duplication or disclosure restricted by GSA ADP Schedule
#  Contract with IBM Corp.
# ******************************************************************************
#
# Stub file for zoautil_py.zoau_io (the public Python façade over the
# zoautil_py._zoau_io C extension).
#
# zoau_io.py re-exports names from the C extension and adds:
#   - ZIOBase  (Python ABC wrapper around _ZIOBase)
#   - RecordIO (Python subclass of _RecordIO that adds __len__)
#   - SEEK_SET / SEEK_CUR / SEEK_END constants
#
# Pylance/mypy read this file instead of zoau_io.py, so every public name
# must be declared here with its correct type.
#

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, Literal, Optional, Tuple, Union

# ---------------------------------------------------------------------------
# Re-export the type aliases from the internal stub so callers can use them.
# Guarded by TYPE_CHECKING so Pylint/runtime never tries to import the C
# extension (which only exists on z/OS).
# ---------------------------------------------------------------------------
if TYPE_CHECKING:
    from zoautil_py._zoau_io import (
        FileMode as FileMode,
        SpaceUnit as SpaceUnit,
        SpaceTuple as SpaceTuple,
        RecordIO_TextWrapper as RecordIO_TextWrapper,
    )
else:
    FileMode = str
    SpaceUnit = object
    SpaceTuple = tuple

# ---------------------------------------------------------------------------
# Exceptions (re-exported from the C extension; __module__ patched at runtime)
# ---------------------------------------------------------------------------

class ZOAU_IO_UnsupportedOperation(OSError, ValueError):
    """Raised when an unsupported I/O operation is attempted on a stream."""
    ...

class ZOAU_IO_Error(OSError, ValueError):
    """Raised when a z/OS I/O error occurs."""
    ...

# ---------------------------------------------------------------------------
# Seek constants
# ---------------------------------------------------------------------------

SEEK_SET: int  # 0 – seek from the beginning of the file
SEEK_CUR: int  # 1 – seek from the current position
SEEK_END: int  # 2 – seek from the end of the file

# ---------------------------------------------------------------------------
# ZIOBase – public Python ABC (wraps _ZIOBase from the C extension)
# ---------------------------------------------------------------------------

class ZIOBase:
    """Abstract base class for z/OS I/O stream types.

    Calling any method (except additional calls to :meth:`close`) on a
    closed stream raises :exc:`ValueError`.
    """

    @property
    def closed(self) -> bool:
        """``True`` if the file stream is closed."""
        ...

    @property
    def openmode(self) -> Literal["TEXT", "BINARY", "RECORD", "BLOCKED"]:
        """File open mode as reported by the z/OS runtime."""
        ...

    @property
    def device(self) -> Literal[
        "DISK", "TERMINAL", "PRINTER", "TAPE", "TDQ",
        "DUMMY", "MSGFILE", "MEMORY", "HFS", "HIPERSPACE", "MSGRTN", "OTHER"
    ]:
        """Device type of the underlying dataset."""
        ...

    @property
    def access_method(self) -> Literal["UNSPEC", "BSAM", "QSAM"]:
        """Access method used for the dataset."""
        ...

    @property
    def noseek_to_seek(self) -> Literal[
        "NOSWITCH", "UPDATE", "BSAMWRITE",
        "FBS_APPEND", "LRECLX", "PARTITIONED_DIRECTORY", "PARTITIONED_INDIRECT"
    ]:
        """Reason noseek was changed to seek."""
        ...

    @property
    def recfm(self) -> str:
        """Dataset record format string (e.g. ``"FB"``, ``"VB"``, ``"U"``)."""
        ...

    @property
    def dsorg(self) -> Literal[
        "PO", "PDSmem", "PDSdir", "PS", "Concat", "Mem", "Hiper", "Temp", "VSAM"
    ]:
        """Dataset organisation."""
        ...

    @property
    def dsname(self) -> str:
        """Real name of the dataset."""
        ...

    @property
    def maxreclen(self) -> int:
        """Maximum record length (LRECL)."""
        ...

    @property
    def blksize(self) -> int:
        """Dataset block size."""
        ...

    def readable(self) -> bool:
        """Return whether the stream was opened for reading."""
        ...

    def writable(self) -> bool:
        """Return whether the stream was opened for writing."""
        ...

    def seekable(self) -> bool:
        """Return whether the stream supports random access."""
        ...

    def close(self) -> None:
        """Flush and close the stream. No-op if already closed."""
        ...

    def flush(self) -> None:
        """Flush the stream."""
        ...

    def rewind(self) -> None:
        """Reposition to the beginning of the stream."""
        ...

    def clearerr(self) -> None:
        """Reset the error and EOF indicators."""
        ...

    def readlines(self, hint: int = -1) -> list[bytes]:
        """Read and return a list of records from the stream."""
        ...

    def __enter__(self) -> ZIOBase: ...
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None: ...
    def __iter__(self) -> Iterator[bytes]: ...
    def __next__(self) -> bytes: ...

# ---------------------------------------------------------------------------
# RecordIO – public concrete binary record-stream class
# ---------------------------------------------------------------------------

class RecordIO(ZIOBase):
    """Open a z/OS dataset as a binary record stream.

    Args:
        file: Dataset name or DD name to open.

            * Fully qualified dataset: ``"//\\'MY.DATASET\\'\"``
            * Temporary dataset: ``\"//&&MYTMP\"``
            * DD name: ``\"DD:SYSPRINT\"``

        mode: Access mode string.  One of ``'r'``, ``'w'``, ``'a'``,
            ``'r+'``, ``'w+'``, ``'rb'``, ``'wb'``, ``'ab'``, ``'rb+'``,
            ``'wb+'``.  Defaults to ``'r'``.

        blksize: Dataset block size (0–32760).
        lrecl: Logical record length (0–32760).
        noseek: If ``True``, open in QSAM (no repositioning).
        recfm: Record format string (e.g. ``'FB'``, ``'VB'``, ``'U'``).
        space: Space allocation tuple
            ``(units, primary, secondary, directory, rlse)``.

    Raises:
        OSError: If the dataset cannot be opened.
        ValueError: If an invalid parameter combination is supplied.
    """

    def __init__(
        self,
        file: str,
        mode: FileMode = "r",
        *,
        blksize: int = ...,
        lrecl: int = ...,
        noseek: bool = False,
        recfm: str = ...,
        space: SpaceTuple = ...,
    ) -> None: ...

    def read(self, size: int = 1, count: int = ...) -> bytes:
        """Read up to *count* items of *size* bytes from the record stream."""
        ...

    def readrecord(self) -> bytes:
        """Read a single record from the stream."""
        ...

    def readrecords(self, nrecords: int = ...) -> list[bytes]:
        """Read *nrecords* records from the current stream position."""
        ...

    def write(self, content: bytes) -> int:
        """Write *content* to the record stream."""
        ...

    def seek(self, offset: int, origin: int = ...) -> None:
        """Change the current file position to a new record location."""
        ...

    def tell(self) -> int:
        """Return the relative record offset (0-based) of the current position."""
        ...

    def __len__(self) -> int:
        """Return the total number of records in the dataset.

        Raises:
            OSError: If the stream is not seekable.
        """
        ...

    def __enter__(self) -> RecordIO: ...
    def __iter__(self) -> Iterator[bytes]: ...
    def __next__(self) -> bytes: ...

# ---------------------------------------------------------------------------
# zopen – factory function (re-exported from the C extension)
# ---------------------------------------------------------------------------

def zopen(
    file: str,
    mode: FileMode,
    encoding: Optional[str] = None,
    type: Literal["record"] = "record",
    *,
    blksize: int = ...,
    lrecl: int = ...,
    noseek: bool = False,
    recfm: str = ...,
    space: SpaceTuple = ...,
) -> Union[RecordIO, RecordIO_TextWrapper]:
    """Open a z/OS dataset and return a stream object.

    Args:
        file: Dataset name or DD name to open.

            * Fully qualified dataset: ``"//\\'MY.DATASET\\'\"``
            * Temporary dataset: ``\"//&&MYTMP\"``
            * DD name: ``\"DD:SYSPRINT\"``

        mode: Access mode string.  One of ``'r'``, ``'w'``, ``'a'``,
            ``'r+'``, ``'w+'``, ``'rb'``, ``'wb'``, ``'ab'``, ``'rb+'``,
            ``'wb+'``.

        encoding: Optional EBCDIC single-byte encoding name (e.g.
            ``"cp1047"``).  When supplied, a :class:`RecordIO_TextWrapper`
            is returned; otherwise a :class:`RecordIO` is returned.

        type: I/O access model.  Currently only ``"record"`` is supported.

        blksize: Dataset block size (0–32760).
        lrecl: Logical record length (0–32760).
        noseek: If ``True``, open in QSAM (no repositioning).
        recfm: Record format string (e.g. ``'FB'``, ``'VB'``, ``'U'``).
        space: Space allocation tuple
            ``(units, primary, secondary, directory, rlse)`` — only valid
            when creating a new dataset by name.

    Returns:
        A :class:`RecordIO` when *encoding* is omitted, or a
        :class:`RecordIO_TextWrapper` when *encoding* is provided.

    Raises:
        OSError: If the dataset cannot be opened.
        ValueError: If an invalid parameter combination is supplied,
            or if *type* is not ``"record"``.
        TypeError: If *type* is not a string.
    """
    ...

# Made with Bob
