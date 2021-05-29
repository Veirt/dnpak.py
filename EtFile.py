import binascii
import os
import struct
import zlib
from pathlib import Path


class EtFile:
    location: str = None

    __filedata: bytes = None
    __filedatacomp: bytes = None
    __filesize: int = None
    __filesizecomp: int = None
    __offset: int = None
    __alloc_size: int = None

    def __init__(self, file_name: str = None, location: str = None):
        if file_name is not None:
            self.__filesize = os.stat(file_name).st_size

            try:
                with open(file_name, "rb") as handle:
                    self.__filedata = handle.read(self.__filesize)
            except FileNotFoundError:
                raise FileNotFoundError

            try:
                self.__filedatacomp = zlib.compress(self.__filedata, 1)
            except zlib.error as err:
                raise err

            self.__filesizecomp = len(binascii.hexlify(
                self.__filedatacomp)) // 2

        self.location = str(Path(location))

    def set_offset(self, offset: int):
        self.__offset = offset

    def set_file_info(self, filesizecomp, filesize, alloc_size, offset,
                      filedatacomp):
        self.__filesizecomp = filesizecomp
        self.__filesize = filesize
        self.__alloc_size = alloc_size
        self.__offset = offset
        self.__filedatacomp = filedatacomp

    def get_decompressed_data(self):
        try:
            return zlib.decompress(self.__filedatacomp)
        except zlib.error as err:
            raise err

    def get_file_data(self):
        return self.__filedatacomp

    def get_binary(self) -> bytes:
        data = self.location.encode("utf-8")
        data += struct.pack("<x") * (256 - len(self.location))
        data += struct.pack("<I", int(self.__filesizecomp))
        data += struct.pack("<I", self.__filesize)
        data += struct.pack("<I", int(self.__filesizecomp))
        data += struct.pack("<I", self.__offset)
        data += struct.pack("<I", 0)
        data += struct.pack("<I", 0)
        data += struct.pack("<x") * 36
        return data
