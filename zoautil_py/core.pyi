"""Type stub for zoautil_py.core C extension module."""

from typing import Any, Dict, Optional

def call_zoau_library(
    command: str,
    options: str,
) -> Dict[str, Any]:
    """
    Call ZOAU library function with text output format.
    
    Args:
        command: The ZOAU command to execute (e.g., 'dls', 'mls', 'jls')
        options: Command-line options/arguments as a string
    
    Returns:
        Dictionary containing:
            - rc (int): Return code from the command
            - response_format (str): "UTF-8" for text format
            - stdout_response (str): Standard output as string
            - stderr_response (str): Standard error as string
            - command (str): Full command that was executed
    
    Raises:
        ValueError: If command is unsupported or library initialization fails
    """
    ...

def call_zoau_library_bin(
    command: str,
    options: str,
) -> Dict[str, Any]:
    """
    Call ZOAU library function with binary output format.
    
    Args:
        command: The ZOAU command to execute (e.g., 'dls', 'mls', 'jls')
        options: Command-line options/arguments as a string
    
    Returns:
        Dictionary containing:
            - rc (int): Return code from the command
            - response_format (str): "binary" for binary format
            - stdout_response (bytes): Standard output as bytes
            - stderr_response (bytes): Standard error as bytes
            - command (str): Full command that was executed
    
    Raises:
        ValueError: If command is unsupported or library initialization fails
    """
    ...
