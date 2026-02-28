# ----------------------------------------------------------------------------
# PID 5698-PA1
# Copyright IBM Corp. 2023, 2025
#
# Note to U.S. Government Users Restricted Rights:
# Use, duplication or disclosure restricted by GSA ADP
# Schedule Contract with IBM Corp.
# ----------------------------------------------------------------------------
import abc

import zoautil_py._zoau_io

__all__ = ["zopen", "RecordIO", "RecordIO", "SEEK_SET", "SEEK_CUR", "SEEK_END"]

from zoautil_py._zoau_io import (RecordIO_TextWrapper, ZOAU_IO_Error,
                                 ZOAU_IO_UnsupportedOperation, zopen)

# Pretend these exceptions were created here:
ZOAU_IO_UnsupportedOperation.__module__ = "zoau_io"
ZOAU_IO_Error.__module__ = "zoau_io"

# Constants for seek
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

# Implementation of the abstract protocol
# Actual methods, members and implementations are inherited from the extension
class ZIOBase(zoautil_py._zoau_io._ZIOBase, metaclass=abc.ABCMeta):
    __doc__ = zoautil_py._zoau_io._ZIOBase.__doc__

class RecordIO(zoautil_py._zoau_io._RecordIO, ZIOBase):
    def __len__(self):
        if not self.seekable():
            raise OSError("Stream is not seekable. Stream length can not be obtained.")
        current_cursor = self.tell()
        self.seek(0,SEEK_END)
        length = self.tell()
        self.seek(current_cursor)
        return length

ZIOBase.register(RecordIO)
