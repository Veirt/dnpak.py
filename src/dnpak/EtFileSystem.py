import os
import struct
from .EtFile import EtFile
from typing import Final
from typing import List


class EtFileSystem:
    __file = None
    __current_file: str = None

    HEADER_MAGIC: Final[str] = "EyedentityGames Packing File 0.1"
    HEADER_VERSION: Final[int] = 0xB
    FILE_COUNT: int = 0
    FILE_OFFSET: int = 0

    __files: List[EtFile] = []

    def __init__(self, file_name: str):
        """
        Write the specified pak in binary mode

        :param file_name: File path for pak
        :type file_name: str
        """

        self.__current_file = file_name
        if not file_name or file_name[-4:] != ".pak":
            raise NameError("Invalid file name")

    @classmethod
    def write(cls, file_name: str):
        cls.__file = open(file_name, "wb")
        cls.write_header()
        return cls(file_name)

    @classmethod
    def read(cls, file_name: str):
        cls.__file = open(file_name, "rb+")

        cls.__file.seek(260)
        cls.FILE_COUNT = struct.unpack(
            "<I",
            cls.__file.read(4))[0]  # [0] because the return type is a tuple

        cls.__file.seek(264)
        cls.FILE_OFFSET = struct.unpack("<I", cls.__file.read(4))[0]

        cls.__file.seek(cls.FILE_OFFSET)
        offset_now = 0
        for f in range(cls.FILE_COUNT):
            cls.__file.seek(cls.FILE_OFFSET + offset_now)

            # Sanitize the file name
            location = cls.__file.read(256).decode("utf-8", "ignore").split("\x00", 1)[0]
            if not location.isalnum() or location in "._-":
                location = "".join(x for x in location if (x.isalnum() or x in "/\\._- "))

            file = EtFile(location=location)

            file_info = []
            for i in range(4):
                file_info.append(struct.unpack("<I", cls.__file.read(4))[0])

            # seek to offset, and read till allocSize
            cls.__file.seek(file_info[3])
            file_info.append(cls.__file.read(file_info[2]))

            file.set_file_info(*file_info)

            cls.__files.append(file)
            offset_now += 316

        return cls(file_name)

    def extract(self):
        folder_name = self.__current_file[:-4]  # :-4 to remove ".pak"

        for file in self.__files:
            os.makedirs(os.path.dirname(f"{folder_name}\\{file.location}"),
                        exist_ok=True)
            with open(f"{folder_name}{file.location}", "wb") as f:
                f.write(file.get_decompressed_data())

    def add_file(self, file_name, location):
        """
        Add the specified file to the pak

        :param file_name: Path of the specified file
        :type file_name: str
        :param location: Location of the file that will be put in the pak. Must start with slash ('/') or backslash ('\')
        :type location: str
        """

        if not os.path.exists(file_name):
            raise FileNotFoundError("File doesn't exist")

        if location[0] != "/" and location[0] != "\\":
            raise NameError("File location must start with \"/\" or \"\\\" ")

        self.__files.append(EtFile(file_name, location))

    def close_file_system(self):
        self.__write_data()
        self.__write_footer()
        self.__file.close()

    @classmethod
    def write_header(cls):
        cls.__file.write(bytes(cls.HEADER_MAGIC, "utf-8"))
        cls.__file.write(struct.pack("<x") * 224)
        cls.__file.write(struct.pack("<I", cls.HEADER_VERSION))
        cls.__file.write(struct.pack("<I", cls.FILE_COUNT))
        cls.__file.write(struct.pack("<I", cls.FILE_OFFSET))
        cls.__file.write(struct.pack("<I", 0))
        cls.__file.write(struct.pack("<x") * 752)

    def __rewrite_header(self):
        self.FILE_COUNT = len(self.__files)
        self.FILE_OFFSET = self.__file.tell()

        self.__file.seek(256 + 4)
        self.__file.write(struct.pack("<I", self.FILE_COUNT))
        self.__file.write(struct.pack("<I", self.FILE_OFFSET))
        self.__file.seek(self.FILE_OFFSET, os.SEEK_SET)

    def __write_data(self):
        for f in self.__files:
            f.set_offset(self.__file.tell())
            self.__file.write(f.get_file_data())

    def __write_footer(self):
        self.__rewrite_header()
        for f in self.__files:
            self.__file.write(f.get_binary())
