"""Type stubs for zoautil_py._zoau_io C extension module.

This module provides Python interfaces to z/OS data sets opened in a record
stream model.

C Extension Sources:
    - extensions/_zoau_io/_io.c
    - extensions/_zoau_io/_param_utils.c
    - extensions/_zoau_io/_zoau_iomodule.c
    - extensions/_zoau_io/recordio.c
    - extensions/_zoau_io/ziobase.c
"""

from typing import Any, Literal, Optional, Tuple, Union, Iterator, List
from types import TracebackType

# Exception classes
class ZOAU_IO_UnsupportedOperation(OSError, ValueError):
    """Exception raised when an unsupported I/O operation is attempted."""
    ...

class ZOAU_IO_Error(OSError, ValueError):
    """Exception raised for z/OS I/O specific errors."""
    ...

# Base class
class ZIOBase:
    """Abstract base class for z/OS I/O classes.
    
    This class does not provide implementations for open, read and write
    because their signatures will vary.
    
    Implementations may raise ZOAU_IO_UnsupportedOperation when operations
    they do not support are called.
    
    Note that calling any method (except additional calls to close(),
    which are ignored) on a closed stream should raise a ValueError.
    """
    
    @property
    def closed(self) -> bool:
        """True if the stream is closed."""
        ...
    
    def close(self) -> None:
        """Close the file stream.
        
        A closed file cannot be used for further I/O operations, but
        this function can be called more than once without error.
        """
        ...
    
    def flush(self) -> None:
        """Flush the stream.
        
        Causes the buffered write blocks to be updated in the system.
        """
        ...
    
    def readable(self) -> bool:
        """Return True if file was opened in read mode."""
        ...
    
    def writable(self) -> bool:
        """Return True if file was opened in write mode."""
        ...
    
    def seekable(self) -> bool:
        """Return True if file supports random-access."""
        ...
    
    def seek(self, offset: int, whence: int = 0) -> None:
        """Change the stream position.
        
        Args:
            offset: Position offset
            whence: Reference point (0=start, 1=current, 2=end)
        
        Raises:
            ZOAU_IO_UnsupportedOperation: If seeking is not supported
        """
        ...
    
    def tell(self) -> int:
        """Return the current stream position.
        
        Raises:
            ZOAU_IO_UnsupportedOperation: If tell is not supported
        """
        ...
    
    def rewind(self) -> None:
        """Set position to the beginning of the file and clear the file error."""
        ...
    
    def clearerr(self) -> None:
        """Reset the error indicator and EOF indicator of the stream."""
        ...
    
    def _zio_error(self) -> None:
        """Internal method for additional I/O error diagnostics.
        
        This is an internal method used for debugging and error reporting.
        """
        ...
    
    def readlines(self, hint: int = -1) -> List[bytes]:
        """Read and return a list of lines from the stream.
        
        Args:
            hint: If positive, limits the number of bytes read
        
        Returns:
            List of lines as bytes objects
        """
        ...
    
    def __enter__(self) -> 'ZIOBase':
        """Context manager entry."""
        ...
    
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Context manager exit."""
        ...
    
    def __iter__(self) -> Iterator[bytes]:
        """Return an iterator over the stream."""
        ...
    
    def __next__(self) -> bytes:
        """Return the next line from the stream."""
        ...

# RecordIO class
class RecordIO(ZIOBase):
    """Binary record I/O for z/OS data sets.
    
    This class supports dataset I/O using record streams in binary mode.
    """
    
    def __init__(
        self,
        file: str,
        mode: str = "r",
        *,
        abend: Optional[Literal["abend", "recover"]] = None,
        asis: bool = False,
        blksize: Optional[int] = None,
        byteseek: bool = False,
        lrecl: Optional[int] = None,
        noseek: bool = False,
        recfm: Optional[str] = None,
        samethread: bool = False,
        space: Optional[Tuple[Union[str, int], int, Optional[int], Optional[int], bool]] = None
    ) -> None:
        """Open a file record stream.
        
        Args:
            file: Data set name or ddname
            mode: File mode string (r, w, a, rb, wb, ab, r+, w+, a+, rb+, wb+, ab+)
            abend: Abend handling ("abend" or "recover")
            asis: If True, use ASIS mode
            blksize: Block size (0-32760)
            byteseek: If True, enable byte-level seeking
            lrecl: Logical record length (0-32760)
            noseek: If True, disable seeking (use QSAM)
            recfm: Record format (F, FB, V, VB, U, etc.)
            samethread: If True, restrict I/O to same thread
            space: Space allocation tuple (unit, primary, secondary, directory, release)
                   unit: "TRK", "CYL", or integer for BLKSIZE
                   primary: Primary space allocation
                   secondary: Secondary space allocation (optional)
                   directory: Directory blocks (optional)
                   release: True for RLSE, False for NORLSE
        
        Raises:
            OSError: If file cannot be opened
            ValueError: If parameters are invalid
        """
        ...
    
    def read(self, size: int = 1, count: Optional[int] = None) -> bytes:
        """Read at most count items of the specified size from a record.
        
        Args:
            size: Size of each item (default: 1)
            count: Number of items to read (default: max record length)
        
        Returns:
            Bytes object containing the data read
            Empty bytes object at EOF
        
        Raises:
            ValueError: If file is closed
            OSError: If read error occurs
        """
        ...
    
    def readrecord(self) -> bytes:
        """Read an entire record.
        
        Returns:
            Bytes object containing the record
            Empty bytes object at EOF
        """
        ...
    
    def readrecords(self, nrecords: int = -1) -> List[bytes]:
        """Read a quantity of records.
        
        Args:
            nrecords: Number of records to read (-1 for all remaining)
        
        Returns:
            List of records as bytes objects
        """
        ...
    
    def write(self, data: bytes) -> int:
        """Write the buffer to the record.
        
        Not all data may be written. Any string longer than the record
        length is truncated at the record length.
        
        Args:
            data: Bytes to write
        
        Returns:
            Number of items successfully written
        
        Raises:
            ValueError: If file is closed or not writable
            OSError: If write error occurs
        """
        ...
    
    def seek(self, offset: int, whence: int = 0) -> None:
        """Change the current file position.
        
        For record I/O, offset is a relative record number.
        
        Args:
            offset: Record offset
            whence: Reference point (0=SEEK_SET, 1=SEEK_CUR, 2=SEEK_END)
        
        Raises:
            ValueError: If file is closed or not seekable
            OSError: If seek fails
        """
        ...
    
    def tell(self) -> int:
        """Return the current relative record offset.
        
        Returns:
            Current record position
        
        Raises:
            ValueError: If file is closed or not seekable
            OSError: If tell fails
        """
        ...
    
    def _dealloc_warn(self, source: object) -> None:
        """Internal method for deallocation warnings.
        
        This is an internal method used for debugging resource cleanup.
        
        Args:
            source: The source object being deallocated
        """
        ...
    
    def __iter__(self) -> Iterator[bytes]:
        """Return an iterator over records."""
        ...
    
    def __next__(self) -> bytes:
        """Return the next record."""
        ...

# RecordIO TextWrapper class
class RecordIO_TextWrapper:
    """Text wrapper for RecordIO streams.
    
    This class provides a text interface, encoding/decoding an underlying
    record stream object.
    """
    
    def __init__(
        self,
        record_stream: RecordIO,
        encoding: str,
        errors: str = "strict"
    ) -> None:
        """Create a text wrapper around a RecordIO stream.
        
        Args:
            record_stream: The underlying RecordIO instance
            encoding: Text encoding (e.g., "cp037", "cp1047", "iso8859-1")
            errors: Error handling strategy ("strict", "ignore", "replace")
        
        Raises:
            ValueError: If encoding is not supported
        
        Note:
            Supported encodings include EBCDIC variants (cp037, cp1047, etc.)
            and some SBCS encodings (iso8859-1, latin1).
        """
        ...
    
    def read(self, size: int = -1) -> str:
        """Read and decode text from the stream.
        
        Args:
            size: Number of characters to read (-1 for entire record)
        
        Returns:
            Decoded string
        """
        ...
    
    def readrecord(self) -> str:
        """Read and decode an entire record.
        
        Returns:
            Decoded string
        """
        ...
    
    def readrecords(self, nrecords: int = -1) -> List[str]:
        """Read and decode multiple records.
        
        Args:
            nrecords: Number of records to read (-1 for all)
        
        Returns:
            List of decoded strings
        """
        ...
    
    def write(self, text: str) -> int:
        """Encode and write text to the stream.
        
        Args:
            text: String to encode and write
        
        Returns:
            Number of characters written
        """
        ...
    
    def detach(self) -> RecordIO:
        """Detach and return the underlying record stream object.
        
        After calling this method, the TextWrapper is no longer usable.
        The underlying RecordIO object is returned and can be used directly.
        
        Returns:
            The underlying RecordIO stream object
        
        Raises:
            ValueError: If the stream is already detached or closed
        """
        ...
    
    def close(self) -> None:
        """Close the underlying stream."""
        ...
    
    def flush(self) -> None:
        """Flush the underlying stream."""
        ...
    
    def readable(self) -> bool:
        """Return True if underlying stream is readable."""
        ...
    
    def writable(self) -> bool:
        """Return True if underlying stream is writable."""
        ...
    
    def seekable(self) -> bool:
        """Return True if underlying stream is seekable."""
        ...
    
    def seek(self, offset: int, whence: int = 0) -> None:
        """Seek in the underlying stream."""
        ...
    
    def tell(self) -> int:
        """Return position in the underlying stream."""
        ...
    
    def rewind(self) -> None:
        """Reposition the file position indicator to the beginning.
        
        A call to rewind is equivalent to a call of seek() to the beginning
        of the file except that rewind() also clears the error indicator of
        the underlying stream.
        """
        ...
    
    def clearerr(self) -> None:
        """Reset the error and EOF indicators of the underlying stream."""
        ...
    
    @property
    def closed(self) -> bool:
        """True if the stream is closed."""
        ...
    
    @property
    def encoding(self) -> str:
        """The encoding being used."""
        ...
    
    @property
    def errors(self) -> str:
        """The error handling strategy."""
        ...
    
    def __enter__(self) -> 'RecordIO_TextWrapper':
        """Context manager entry."""
        ...
    
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Context manager exit."""
        ...
    
    def __iter__(self) -> Iterator[str]:
        """Return an iterator over records."""
        ...
    
    def __next__(self) -> str:
        """Return the next decoded record."""
        ...

# Factory function
def zopen(
    file: str,
    mode: str = "r",
    encoding: Optional[str] = None,
    type: Literal["record"] = "record",
    *,
    abend: Optional[Literal["abend", "recover"]] = None,
    asis: bool = False,
    blksize: Optional[int] = None,
    byteseek: bool = False,
    lrecl: Optional[int] = None,
    noseek: bool = False,
    recfm: Optional[str] = None,
    samethread: bool = False,
    space: Optional[Tuple[Union[str, int], int, Optional[int], Optional[int], bool]] = None
) -> Union[RecordIO, RecordIO_TextWrapper]:
    """Factory function to open z/OS data sets.
    
    Args:
        file: Data set name or ddname
        mode: File mode string
        encoding: Text encoding (if specified, returns RecordIO_TextWrapper)
        type: I/O type (currently only "record" is supported)
        abend: Abend handling
        asis: ASIS mode flag
        blksize: Block size
        byteseek: Byte-level seeking flag
        lrecl: Logical record length
        noseek: Disable seeking flag
        recfm: Record format
        samethread: Same-thread restriction flag
        space: Space allocation parameters
    
    Returns:
        RecordIO instance if encoding is None
        RecordIO_TextWrapper instance if encoding is specified
    
    Raises:
        ValueError: If parameters are invalid
        OSError: If file cannot be opened
    
    Examples:
        >>> # Binary record I/O
        >>> with zopen("MY.DATASET", "rb") as f:
        ...     data = f.readrecord()
        
        >>> # Text record I/O with encoding
        >>> with zopen("MY.DATASET", "r", encoding="cp037") as f:
        ...     text = f.readrecord()
    """
    ...

# Made with Bob
