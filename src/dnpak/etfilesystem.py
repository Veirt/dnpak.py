import binascii
import os
import struct
import zlib
from glob import glob
from typing import Final
from typing import List

from .utils import *
from .etfile import EtFile


class EtFileSystem:
    __type = None
    __file = None
    __current_file = None

    HEADER_MAGIC: Final[str] = "EyedentityGames Packing File 0.1"
    HEADER_VERSION: Final[int] = 0xB
    FILE_COUNT: int = 0
    FILE_OFFSET: int = 0

    __files: List[EtFile] = []

    def __init__(self, file_name: str):
        self.__current_file = file_name
        if not file_name or file_name[-4:] != ".pak":
            raise NameError("Invalid file name")

    def __repr__(self):
        return str({
            "current_file": self.__current_file,
            "file_count": self.FILE_COUNT,
            "file_offset": self.FILE_OFFSET,
        })

    @classmethod
    def write(cls, file_name: str):
        """
        Write the specified PAK in binary mode

        :param file_name: PAK file name to write
        :type file_name: str
        """

        cls.__type = "write"

        if os.path.exists(file_name):
            raise FileExistsError("File already exists. Did you mean to read?")

        cls.__file = open(file_name, "wb")
        cls.write_header()
        return cls(file_name)

    @classmethod
    def read(cls, file_name: str):
        """
        Read (and write) the specified PAK in binary mode

        :param file_name: PAK file name to read
        :type file_name: str
        """

        cls.__type = "read"

        cls.__file = open(file_name, "rb+")

        cls.__file.seek(260)
        cls.FILE_COUNT = struct.unpack(
            "<I",
            cls.__file.read(4))[0]  # [0] because the return type is a tuple

        cls.__file.seek(264)
        cls.FILE_OFFSET = struct.unpack("<I", cls.__file.read(4))[0]

        cls.__file.seek(cls.FILE_OFFSET)
        offset_now = 0
        for _ in range(cls.FILE_COUNT):
            cls.__file.seek(cls.FILE_OFFSET + offset_now)

            # Sanitize the file name
            location = (cls.__file.read(256).decode("utf-8",
                                                    "ignore").split("\x00",
                                                                    1)[0])
            if not location.isalnum() or location in "._-":
                location = "".join(x for x in location
                                   if (x.isalnum() or x in "/\\._- "))

            file = EtFile(location=location)

            file_info = {
                "filesizecomp": struct.unpack("<I", cls.__file.read(4))[0],
                "filesize": struct.unpack("<I", cls.__file.read(4))[0],
                "alloc_size": struct.unpack("<I", cls.__file.read(4))[0],
                "offset": struct.unpack("<I", cls.__file.read(4))[0],
            }

            # seek to offset, and read till allocSize
            cls.__file.seek(file_info["offset"])
            file_info["filedatacomp"] = cls.__file.read(
                file_info["alloc_size"])

            file.set_file_info(**file_info)

            cls.__files.append(file)
            offset_now += 316

        return cls(file_name)

    def extract(self, mode=None, directory=None):
        """
        Extract compressed data inside PAK

        :param mode: Use 'strict' mode to prevent extracting 0 byte files
        :type mode: str

        :param directory: Specified directory name for the extracted files
        :type mode: str
        """

        # :-4 to remove ".pak"
        folder_name = directory if directory is not None else self.__current_file[:-4]

        for file in self.__files:
            if (mode == "strict" and file.get_file_size() == 0
                    and file.get_compressed_file_size() == 0):
                pass
            else:
                file_path = f"{folder_name}{convert_path(file.get_location())}"
                os.makedirs(
                    os.path.dirname(file_path),
                    exist_ok=True,
                )
                try:
                    with open(file_path, "wb") as f:
                        f.write(file.get_decompressed_data())
                except PermissionError:
                    pass

    def get_files(self) -> List[EtFile]:
        """
        A getter for files inside pak

        :return: List of EtFile objects
        :rtype: List[EtFile]
        """

        return self.__files

    def find_file(self, location: str) -> EtFile:
        """
        :param location: Location of the file in pak
        :type location: str

        :return: EtFile object that match the location
        :rtype: EtFile
        """

        filtered_file = next(
            filter(lambda file: file.get_location() == location, self.__files),
            None)

        return filtered_file

    def add_file(self, file_name, location):
        """
        Add the specified file to the pak

        :param file_name: Path of the specified file
        :type file_name: str

        :param location: Location of the file that
        will be put in the pak. Must start with slash ('/') or backslash ('\')
        :type location: str
        """

        self.__type = "write"

        if not os.path.exists(file_name):
            raise FileNotFoundError("File doesn't exist")

        if location[0] != "/" and location[0] != "\\":
            raise NameError('File location must start with "/" or "\\" ')

        self.__files.append(EtFile(file_name, location))

    def add_files(self, folder: str):
        """
        Add the all files inside specified folder to the pak

        :param folder: Path of the folder
        :type folder: str
        """

        self.__type = "write"

        if not os.path.exists(folder):
            raise FileNotFoundError("Folder doesn't exist")

        files = glob(f"{folder}/**/*.*", recursive=True)
        locations = [file.replace(folder, "") for file in files]
        for file, location in zip(files, locations):
            self.__files.append(EtFile(file, location))

    def edit_file(self, file: EtFile, filedata: bytes):
        """
        Edit the specified EtFile object data

        :param file: Object of EtFile that will be edited
        :type file: EtFile

        :param filedata: File data that will be written
        :type filedata: bytes
        :return:
        """
        self.__type = "write"
        try:
            filedatacomp = zlib.compress(filedata, 1)
            filesizecomp = len(binascii.hexlify(filedatacomp)) // 2
            file_info = {
                "filedatacomp": filedatacomp,
                "filesizecomp": filesizecomp
            }
            file_index = self.__files.index(file)
            print(file_info)
            self.__files[file_index].set_file_info(**file_info)
        except zlib.error as err:
            raise err

    def close_file_system(self):
        """
        Required every time you read or write PAK

        Write header, compressed data, and file information to PAK
        """

        if self.__type == "write":
            self.__file.seek(1024)
            self.__write_data()
            self.__write_footer()

        self.__files.clear()
        self.__file.close()

    @classmethod
    def write_header(cls):
        """
        Write header with dummy file count and offset

        **Signature**: PAK file magic number/identifier string - FBSTR[256] \n
        **Version**: ? Always 11 0x0B - INT32 \n
        **File Count**: Number of files in this PAK - UINT32 \n
        **File Information Offset**: Pointer to the location of
        file information list - UINT32 \n
        **Padding**: Padding bytes to make the PAK header
        1024 bytes in total - UINT8
        """

        cls.__file.write(bytes(cls.HEADER_MAGIC, "utf-8"))
        cls.__file.write(struct.pack("<x") * 224)
        cls.__file.write(struct.pack("<I", cls.HEADER_VERSION))
        cls.__file.write(struct.pack("<I", cls.FILE_COUNT))
        cls.__file.write(struct.pack("<I", cls.FILE_OFFSET))
        cls.__file.write(struct.pack("<I", 0))
        cls.__file.write(struct.pack("<x") * 752)

    def __rewrite_header(self):
        """
        Rewrite header with real file count and offset
        """

        self.FILE_COUNT = len(self.__files)
        self.FILE_OFFSET = self.__file.tell()

        self.__file.seek(256 + 4)
        self.__file.write(struct.pack("<I", self.FILE_COUNT))
        self.__file.write(struct.pack("<I", self.FILE_OFFSET))
        self.__file.seek(self.FILE_OFFSET, os.SEEK_SET)

    def __write_data(self):
        """
        Write compressed data to PAK
        """
        for f in self.__files:
            f.set_offset(self.__file.tell())
            self.__file.write(f.get_compressed_data())

    def __write_footer(self):
        """
        Write file information to PAK
        """
        self.__rewrite_header()
        for f in self.__files:
            self.__file.write(f.get_file_info())

