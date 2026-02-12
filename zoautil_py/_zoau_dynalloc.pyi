"""Type stubs for zoautil_py._zoau_dynalloc C extension module.

This module provides an interface for dynamic allocations on z/OS.

C Extension Sources:
    - extensions/_zoau_dynalloc/_zoau_dynalloc_module.c
    - extensions/_zoau_dynalloc/data_definition.c
    - extensions/_zoau_dynalloc/param_proc.c
"""

from typing import Literal, Optional
from types import TracebackType

class DataDefinition:
    """Dynamically allocate a data definition.
    
    This class provides an interface to z/OS dynamic allocation services,
    allowing you to allocate and deallocate data definitions (DD statements)
    programmatically.
    """
    
    def __init__(
        self,
        ddname: str,
        dsname: Optional[str] = None,
        status: Optional[Literal["OLD", "NEW", "MOD", "SHR"]] = None,
        normdisp: Optional[Literal["CATLG", "UNCATLG", "DELETE", "KEEP"]] = None,
        conddisp: Optional[Literal["CATLG", "UNCATLG", "DELETE", "KEEP"]] = None,
        member: Optional[str] = None,
        recfm: Optional[str] = None,
        dsorg: Optional[str] = None,
        blksize: int = 0,
        lrecl: int = 0,
        volser: Optional[str] = None,
        primary: int = 0,
        secondary: int = 0,
        alcunit: Optional[str] = None,
        dirblk: int = 0,
        storclass: Optional[str] = None,
        mgntclass: Optional[str] = None,
        dataclass: Optional[str] = None,
        debug: bool = False
    ) -> None:
        """Dynamically allocate a data definition.
        
        Args:
            ddname: Data definition name (max 8 characters).
                    Associates a DD name with an allocation request.
                    Specify eight question marks ("????????") for a system-generated DD name.
            
            dsname: Fully qualified dataset name (max 44 characters).
                    Names the dataset to be allocated.
            
            status: Dataset status. May be one of:
                    - "OLD": Exclusive access to an existing dataset
                    - "NEW": Create a new dataset
                    - "MOD": Extend an existing dataset or create if it doesn't exist
                    - "SHR": Shared access to an existing dataset
            
            normdisp: Dataset normal termination disposition. May be one of:
                      - "CATLG": Catalog the dataset
                      - "UNCATLG": Uncatalog the dataset
                      - "DELETE": Delete the dataset
                      - "KEEP": Keep the dataset
            
            conddisp: Dataset conditional disposition (on abnormal termination).
                      May be one of:
                      - "CATLG": Catalog the dataset
                      - "UNCATLG": Uncatalog the dataset
                      - "DELETE": Delete the dataset
                      - "KEEP": Keep the dataset
            
            member: Member name specification (max 8 characters).
                    Specifies that a particular member of a dataset is to be allocated,
                    rather than the entire dataset.
            
            recfm: Dataset record format (e.g., "F", "FB", "V", "VB", "U").
            
            dsorg: Dataset organization (e.g., "PS", "PO", "DA").
            
            blksize: Dataset block size (0-32760).
            
            lrecl: Dataset logical record length (0-32760).
            
            volser: Volume serial number specification (max 6 characters).
            
            primary: Primary space allocation amount.
            
            secondary: Secondary space allocation amount.
            
            alcunit: Allocation unit type (e.g., "TRK", "CYL", "BLK").
            
            dirblk: Number of directory blocks (for partitioned datasets).
            
            storclass: Storage class name.
            
            mgntclass: Management class name.
            
            dataclass: Data class name.
            
            debug: Enable debug output to stderr.
        
        Raises:
            ValueError: If parameters are invalid or allocation fails.
                       Error includes error code and info code from dynamic allocation.
        
        Examples:
            >>> # Allocate an existing dataset
            >>> dd = DataDefinition("MYDD", dsname="USER.DATA.SET", status="SHR")
            
            >>> # Allocate a new dataset
            >>> dd = DataDefinition(
            ...     "NEWDD",
            ...     dsname="USER.NEW.DATA",
            ...     status="NEW",
            ...     normdisp="CATLG",
            ...     recfm="FB",
            ...     lrecl=80,
            ...     blksize=3120,
            ...     primary=10,
            ...     secondary=5,
            ...     alcunit="TRK"
            ... )
            
            >>> # System-generated DD name
            >>> dd = DataDefinition("????????", dsname="USER.DATA.SET", status="SHR")
        """
        ...
    
    def deallocate(self) -> None:
        """Dynamically deallocate the data definition.
        
        Frees the dynamic allocation associated with this data definition.
        If the data definition is already deallocated, this method has no effect.
        
        Raises:
            ValueError: If deallocation fails.
                       Error includes error code and info code from dynamic deallocation.
        
        Note:
            The data definition is automatically deallocated when the object
            is garbage collected, but explicit deallocation is recommended
            for resource management.
        
        Examples:
            >>> dd = DataDefinition("MYDD", dsname="USER.DATA.SET", status="SHR")
            >>> # Use the allocation
            >>> dd.deallocate()  # Explicitly free the allocation
        """
        ...
    
    def _dealloc_warn(self, source: object) -> None:
        """Internal method for deallocation warnings.
        
        This is an internal method used for debugging resource cleanup.
        Issues a ResourceWarning if the data definition is still allocated.
        
        Args:
            source: The source object being deallocated
        """
        ...
    
    @property
    def ddname(self) -> str:
        """The DD name associated with this allocation."""
        ...
    
    @property
    def allocated(self) -> bool:
        """True if the data definition is currently allocated."""
        ...
    
    def __enter__(self) -> 'DataDefinition':
        """Context manager entry.
        
        Returns:
            The DataDefinition instance.
        """
        ...
    
    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        """Context manager exit.
        
        Automatically deallocates the data definition when exiting the context.
        
        Examples:
            >>> with DataDefinition("MYDD", dsname="USER.DATA.SET", status="SHR") as dd:
            ...     # Use the allocation
            ...     pass
            >>> # Allocation is automatically freed here
        """
        ...
    
    def __del__(self) -> None:
        """Destructor.
        
        Automatically deallocates the data definition if still allocated.
        Issues a ResourceWarning if the allocation was not explicitly freed.
        """
        ...

# Made with Bob
