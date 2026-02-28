# ******************************************************************************
#  Licensed Materials - Property of IBM
#  (c) Copyright IBM Corporation 2023-2024. All Rights Reserved.
#
#  Note to U.S. Government Users Restricted Rights:
#  Use, duplication or disclosure restricted by GSA ADP Schedule
#  Contract with IBM Corp.
# ******************************************************************************
#
# Stub file for the '_zoau_io' C extension module (zoautil_py._zoau_io).
#
# This module is a Python C extension compiled only for z/OS. This stub
# provides type information so that IDEs and type-checkers can work with
# the module on non-z/OS platforms (macOS, Windows, Linux).
#
# Sources:
#   mvsutil-python/extensions/_zoau_io/_zoau_iomodule.c
#   mvsutil-python/extensions/_zoau_io/ziobase.c
#   mvsutil-python/extensions/_zoau_io/recordio.c
#   mvsutil-python/extensions/_zoau_io/include/_zoau_iomodule.h
#   mvsutil-python/extensions/_zoau_io/include/ziobase.h
#   mvsutil-python/extensions/_zoau_io/include/recordio.h
#   mvsutil-python/extensions/_zoau_io/include/recordio_textwrapper.h
#
# NOTE on naming:
#   The C extension registers the concrete record-IO type as ``_RecordIO``
#   (with a leading underscore).  ``zoau_io.py`` subclasses it:
#       class RecordIO(zoautil_py._zoau_io._RecordIO, ZIOBase): ...
#   A public ``RecordIO`` alias is provided at the bottom of this file for
#   IDE convenience when working directly with this internal module.
#

from __future__ import annotations

from typing import Iterator, Literal, Optional, Tuple, Union

# ---------------------------------------------------------------------------
# Module-level exceptions
# ---------------------------------------------------------------------------

class ZOAU_IO_UnsupportedOperation(OSError, ValueError):
    """Raised when an unsupported I/O operation is attempted on a stream.

    Inherits from both :exc:`OSError` and :exc:`ValueError`, matching the
    dynamic type created in ``PyInit__zoau_io``.
    """
    ...


class ZOAU_IO_Error(OSError, ValueError):
    """Raised when a z/OS I/O error occurs.

    Inherits from both :exc:`OSError` and :exc:`ValueError`, matching the
    dynamic type created in ``PyInit__zoau_io``.
    """
    ...


# ---------------------------------------------------------------------------
# Module-level constants (re-exported from <stdio.h> via the C layer)
# ---------------------------------------------------------------------------

SEEK_SET: int  # 0 – seek from the beginning of the file
SEEK_CUR: int  # 1 – seek from the current position
SEEK_END: int  # 2 – seek from the end of the file

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

#: Valid ``mode`` strings accepted by :class:`_RecordIO` and :func:`zopen`.
FileMode = Literal["r", "w", "a", "r+", "w+", "rb", "wb", "ab", "rb+", "wb+"]

#: Valid ``space`` unit strings.
SpaceUnit = Union[Literal["CYL", "TRK"], int]

#: Full ``space`` tuple: (units, primary, secondary|None, directory|None, rlse)
SpaceTuple = Tuple[SpaceUnit, int, Optional[int], Optional[int], bool]


# ---------------------------------------------------------------------------
# _ZIOBase – abstract base class
# ---------------------------------------------------------------------------

class _ZIOBase:
    """Abstract base class for z/OS OS I/O classes.

    Provides the common interface shared by all z/OS stream types.
    Calling any method (except additional calls to :meth:`close`) on a
    closed stream raises :exc:`ValueError`.

    Implementations may raise :exc:`ZOAU_IO_UnsupportedOperation` when
    operations they do not support are called.
    """

    # ------------------------------------------------------------------
    # Read-only properties (backed by C getset descriptors on ziobase)
    # ------------------------------------------------------------------

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
        """Access method used for the dataset (valid for PS or PO dsorg)."""
        ...

    @property
    def noseek_to_seek(self) -> Literal[
        "NOSWITCH", "UPDATE", "BSAMWRITE",
        "FBS_APPEND", "LRECLX", "PARTITIONED_DIRECTORY", "PARTITIONED_INDIRECT"
    ]:
        """Reason noseek was changed to seek (valid for PS or PO dsorg)."""
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
        """Real name of the dataset (for DASD datasets)."""
        ...

    @property
    def maxreclen(self) -> int:
        """Maximum record length of the dataset (``lrecl``)."""
        ...

    @property
    def blksize(self) -> int:
        """Dataset block size."""
        ...

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def readable(self) -> bool:
        """Return whether the file stream was opened for reading."""
        ...

    def writable(self) -> bool:
        """Return whether the file stream was opened for writing."""
        ...

    def seekable(self) -> bool:
        """Return whether the file stream supports random access."""
        ...

    def close(self) -> None:
        """Flush and close the file stream IO object.

        This method has no effect if the file is already closed.
        """
        ...

    def flush(self) -> None:
        """Flush the file stream.

        This function has no effect for blocked I/O files.
        """
        ...

    def rewind(self) -> None:
        """Reposition the file position indicator to the beginning of the stream.

        Equivalent to ``seek(0, SEEK_SET)`` but also clears the error
        indicator of the stream.
        """
        ...

    def clearerr(self) -> None:
        """Reset the error indicator and EOF indicator of the file stream."""
        ...

    def readlines(self, hint: int = -1) -> list[bytes]:
        """Read and return a list of records from the stream.

        Args:
            hint: If specified, no more bytes than *hint* will be read in
                total.  Pass ``-1`` (the default) to read all records.

        Returns:
            A list of ``bytes`` objects, one per record.
        """
        ...

    def __enter__(self) -> _ZIOBase: ...
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None: ...
    def __iter__(self) -> Iterator[bytes]: ...
    def __next__(self) -> bytes: ...


# ---------------------------------------------------------------------------
# _RecordIO – concrete binary record-stream class (C extension type name)
# ---------------------------------------------------------------------------
# The C extension registers this type as ``_RecordIO`` (with a leading
# underscore).  ``zoau_io.py`` subclasses it:
#     class RecordIO(zoautil_py._zoau_io._RecordIO, ZIOBase): ...
# A public ``RecordIO`` alias is provided below for IDE convenience.

class _RecordIO(_ZIOBase):
    """Open a z/OS dataset as a binary record stream.

    Inherits all properties and methods from :class:`_ZIOBase`.

    Args:
        file: Dataset name or DD name to open.

            * Fully qualified dataset: ``"//\\'MY.DATASET\\'\"``
            * Temporary dataset: ``\"//&&MYTMP\"``
            * DD name: ``\"DD:SYSPRINT\"``

        mode: Access mode string.  One of ``'r'``, ``'w'``, ``'a'``,
            ``'r+'``, ``'w+'``, ``'rb'``, ``'wb'``, ``'ab'``, ``'rb+'``,
            ``'wb+'``.  Defaults to ``'r'``.

        blksize: Dataset block size (0–32760).  Must match the existing
            dataset when opening for read or append.
        lrecl: Logical record length (0–32760).  Must match the existing
            dataset when opening for read or append.
        noseek: If ``True``, open in QSAM (no repositioning).  Defaults
            to BSAM (repositioning allowed).
        recfm: Record format string (e.g. ``'FB'``, ``'VB'``, ``'U'``,
            ``'*'``, ``'+'``).
        space: Space allocation tuple
            ``(units, primary, secondary, directory, rlse)`` — only valid
            when creating a new dataset by name.

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

    # ------------------------------------------------------------------
    # Read methods
    # ------------------------------------------------------------------

    def read(self, size: int = 1, count: int = ...) -> bytes:
        """Read up to *count* items of *size* bytes from the record stream.

        Reads one record per call.  If the request exceeds the record
        length, one full record is returned and the position advances to
        the next record.

        Args:
            size: Size in bytes of each item to read.  Defaults to ``1``.
            count: Number of items to read.  Defaults to ``LRECL``.

        Returns:
            The bytes read; an empty ``bytes`` object when past EOF.

        Raises:
            ValueError: If the stream is closed.
            ZOAU_IO_UnsupportedOperation: If the stream is not readable.
        """
        ...

    def readrecord(self) -> bytes:
        """Read a single record from the record stream.

        Returns:
            The content of the record as ``bytes``; empty ``bytes`` past EOF.

        Raises:
            ValueError: If the stream is closed.
            ZOAU_IO_UnsupportedOperation: If the stream is not readable.
        """
        ...

    def readrecords(self, nrecords: int = ...) -> list[bytes]:
        """Read *nrecords* records from the current stream position.

        Args:
            nrecords: Number of records to read.  Omit to read until EOF.

        Returns:
            A list of ``bytes`` objects; empty list when past EOF.

        Raises:
            ValueError: If the stream is closed.
            ZOAU_IO_UnsupportedOperation: If the stream is not readable.
        """
        ...

    # ------------------------------------------------------------------
    # Write methods
    # ------------------------------------------------------------------

    def write(self, content: bytes) -> int:
        """Write *content* to the record stream.

        Args:
            content: Bytes to write.  Length must be ≤ ``LRECL``.

        Returns:
            Number of bytes successfully written.

        Raises:
            ValueError: If the stream is closed or *content* exceeds LRECL.
            ZOAU_IO_UnsupportedOperation: If the stream is not writable.
        """
        ...

    # ------------------------------------------------------------------
    # Positioning methods
    # ------------------------------------------------------------------

    def seek(self, offset: int, origin: int) -> None:
        """Change the current file position to a new record location.

        Args:
            offset: Relative record number offset.
            origin: One of :data:`SEEK_SET` (0), :data:`SEEK_CUR` (1),
                or :data:`SEEK_END` (2).

        Raises:
            ValueError: If the stream is closed or noseek is set.
            ZOAU_IO_UnsupportedOperation: If the stream does not support
                repositioning.
        """
        ...

    def tell(self) -> int:
        """Return the relative record offset of the current position.

        The first record of a file is relative record 0.

        Returns:
            Relative record number of the current position.

        Raises:
            ValueError: If the stream is closed or noseek is set.
            ZOAU_IO_UnsupportedOperation: If the stream does not support
                repositioning.
        """
        ...

    def __enter__(self) -> _RecordIO: ...
    def __iter__(self) -> Iterator[bytes]: ...
    def __next__(self) -> bytes: ...


#: Public alias for the C-level ``_RecordIO`` type.
#: ``zoau_io.RecordIO`` subclasses this via ``zoautil_py._zoau_io._RecordIO``.
RecordIO = _RecordIO


# ---------------------------------------------------------------------------
# RecordIO_TextWrapper – text layer over a _RecordIO stream
# ---------------------------------------------------------------------------

class RecordIO_TextWrapper:
    """A text encoding/decoding wrapper around a :class:`_RecordIO` stream.

    Provides the same interface as :class:`_RecordIO` but encodes strings
    to bytes on write and decodes bytes to strings on read, using the
    specified EBCDIC single-byte character set encoding.

    Args:
        record_stream: An open :class:`_RecordIO` instance to wrap.
        encoding: Name of the EBCDIC single-byte encoding to use for
            encode/decode operations (e.g. ``"cp1047"``).
    """

    def __init__(self, record_stream: _RecordIO, encoding: str) -> None: ...

    # ------------------------------------------------------------------
    # Delegation / introspection
    # ------------------------------------------------------------------

    def detach(self) -> _RecordIO:
        """Detach and return the underlying :class:`_RecordIO` stream object.

        Returns:
            The underlying :class:`_RecordIO` instance.
        """
        ...

    # ------------------------------------------------------------------
    # State queries (delegated to the underlying _RecordIO)
    # ------------------------------------------------------------------

    def readable(self) -> bool:
        """Return whether the underlying stream supports reading."""
        ...

    def writable(self) -> bool:
        """Return whether the underlying stream supports writing."""
        ...

    def seekable(self) -> bool:
        """Return whether the underlying stream supports repositioning."""
        ...

    # ------------------------------------------------------------------
    # Read methods (return str instead of bytes)
    # ------------------------------------------------------------------

    def read(self, nchars: int = ...) -> str:
        """Read up to *nchars* characters from the underlying record stream.

        Args:
            nchars: Character count to read.  Defaults to ``LRECL``.

        Returns:
            Decoded string; empty string past EOF.

        Raises:
            ValueError: If the stream is closed.
            ZOAU_IO_UnsupportedOperation: If the stream is not readable.
        """
        ...

    def readrecord(self) -> str:
        """Read a single record and return it as a decoded string.

        Returns:
            Decoded string content of the record; empty string past EOF.

        Raises:
            ValueError: If the stream is closed.
            ZOAU_IO_UnsupportedOperation: If the stream is not readable.
        """
        ...

    def readrecords(self, nrecords: int = ...) -> list[str]:
        """Read *nrecords* records and return them as decoded strings.

        Args:
            nrecords: Number of records to read.  Omit to read until EOF.

        Returns:
            A list of decoded strings; empty list when past EOF.

        Raises:
            ValueError: If the stream is closed.
            ZOAU_IO_UnsupportedOperation: If the stream is not readable.
        """
        ...

    # ------------------------------------------------------------------
    # Write methods (accept str instead of bytes)
    # ------------------------------------------------------------------

    def write(self, content: str) -> int:
        """Encode *content* and write it to the underlying record stream.

        Args:
            content: String to write.  Character count must be ≤ ``LRECL``.

        Returns:
            Number of bytes successfully written.

        Raises:
            ValueError: If the stream is closed or *content* exceeds LRECL.
            ZOAU_IO_UnsupportedOperation: If the stream is not writable.
        """
        ...

    # ------------------------------------------------------------------
    # Positioning / lifecycle (delegated to the underlying _RecordIO)
    # ------------------------------------------------------------------

    def seek(self, offset: int, origin: int) -> None:
        """Change the current file position in the underlying record stream.

        Args:
            offset: Relative record number offset.
            origin: One of :data:`SEEK_SET` (0), :data:`SEEK_CUR` (1),
                or :data:`SEEK_END` (2).

        Raises:
            ValueError: If the stream is closed or noseek is set.
            ZOAU_IO_UnsupportedOperation: If repositioning is not supported.
        """
        ...

    def tell(self) -> int:
        """Return the relative record offset of the current position.

        Returns:
            Relative record number of the current position.

        Raises:
            ValueError: If the stream is closed or noseek is set.
        """
        ...

    def rewind(self) -> None:
        """Reposition the underlying stream to the beginning of the file."""
        ...

    def clearerr(self) -> None:
        """Reset the error and EOF indicators of the underlying stream."""
        ...

    def flush(self) -> None:
        """Flush the underlying record stream."""
        ...

    def close(self) -> None:
        """Close the underlying record stream.

        This method has no effect if the file is already closed.
        """
        ...

    def __enter__(self) -> RecordIO_TextWrapper: ...
    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    def __next__(self) -> str: ...


# ---------------------------------------------------------------------------
# Module-level factory function
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
) -> Union[_RecordIO, RecordIO_TextWrapper]:
    """Open a z/OS dataset and return a stream object.

    Factory function that constructs and returns either a :class:`_RecordIO`
    or a :class:`RecordIO_TextWrapper` instance depending on whether the
    *encoding* argument is supplied.

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
            is returned; otherwise a :class:`_RecordIO` is returned.

        type: I/O access model.  Currently only ``"record"`` is supported.

        blksize: Dataset block size (0–32760).
        lrecl: Logical record length (0–32760).
        noseek: If ``True``, open in QSAM (no repositioning).
        recfm: Record format string (e.g. ``'FB'``, ``'VB'``, ``'U'``).
        space: Space allocation tuple
            ``(units, primary, secondary, directory, rlse)`` — only valid
            when creating a new dataset by name.

    Returns:
        A :class:`_RecordIO` when *encoding* is omitted, or a
        :class:`RecordIO_TextWrapper` when *encoding* is provided.

    Raises:
        OSError: If the dataset cannot be opened.
        ValueError: If an invalid parameter combination is supplied,
            or if *type* is not ``"record"``.
        TypeError: If *type* is not a string.
    """
    ...

# Made with Bob
