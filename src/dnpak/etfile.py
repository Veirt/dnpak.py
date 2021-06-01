import binascii
import os
import struct
import zlib
from pathlib import Path


class EtFile:
    __location: str = None
    __filedata: bytes = None
    __filedatacomp: bytes = None
    __filesize: int = None
    __filesizecomp: int = None
    __offset: int = None
    __alloc_size: int = None

    def __init__(self, file_name: str = None, location: str = None):
        """
        Initialize file inside pak

        :param file_name: File name to add inside pak
        :type file_name: str

        :param location: Location of file inside pak
        :type location: str
        """

        if file_name is not None:
            try:
                self.__filesize = os.stat(file_name).st_size

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

        self.__location = str(Path(location))

    def set_offset(self, offset: int):
        self.__offset = offset

    def set_file_info(self, filesizecomp: int = None, filesize: int = None,
                      alloc_size: int = None, offset: int = None,
                      filedatacomp: bytes = None):
        """
        Set file info

        :param filesizecomp: File size after data is compressed
        :type filesizecomp: int

        :param filesize: File size before data is compressed
        :type filesizecomp: int

        :param alloc_size: Allocation size of compressed data
        :type alloc_size: int

        :param offset: A pointer to the location of compressed data
        :type alloc_size: int

        :param filedatacomp: zlib compressed data
        :type filedatacomp: bytes
        """

        self.__filesizecomp = filesizecomp or self.__filesizecomp
        self.__filesize = filesize or self.__filesize
        self.__alloc_size = alloc_size or self.__alloc_size
        self.__offset = offset or self.__offset
        self.__filedatacomp = filedatacomp or self.__filedatacomp

    def get_location(self) -> str:
        return self.__location

    def get_file_size(self) -> int:
        return self.__filesize

    def get_compressed_file_size(self) -> int:
        return self.__filesizecomp

    def get_decompressed_data(self) -> bytes:
        """
        Get the decompressed data

        :rtype: bytes
        :return: Decompressed data
        """
        try:
            return zlib.decompress(self.__filedatacomp)
        except zlib.error as err:
            raise err

    def get_compressed_data(self) -> bytes:
        """
        Get the compressed data

        :rtype: bytes
        :return: Compressed data
        """
        return self.__filedatacomp

    def get_file_info(self) -> bytes:
        """
        Get the file information:

        **Location**: Location of file inside pak - FBSTR[256] \n
        **Raw Size**: Size of file after compressed - UINT32 \n
        **Real Size**: Size of file before compressed - UINT32 \n
        **Compressed Size**: Size of file after compressed
        (Should be the same as Raw Size) - UINT32 \n
        **Offset**: Pointer to the location of compressed data - UINT32
        **SeedValue**: ? - UINT32 \n
        **Checksum**: ? - UINT32 \n
        **cReserved**: ? - 36 bytes

        :rtype: bytes
        :return: Compressed data
        """
        data = self.__location.encode("utf-8")
        data += struct.pack("<x") * (256 - len(self.__location))
        data += struct.pack("<I", int(self.__filesizecomp))
        data += struct.pack("<I", self.__filesize)
        data += struct.pack("<I", int(self.__filesizecomp))
        data += struct.pack("<I", self.__offset)
        data += struct.pack("<I", 0)
        data += struct.pack("<I", 0)
        data += struct.pack("<x") * 36
        return data
