import binascii
import os
import struct
import zlib
from typing import Final, List


class EtFile:
	__filedata: bytes = None
	__filedatacomp: bytes = None
	__filesize: int = None
	__filesizecomp: int = None
	__location: str = None
	__offset: int = None

	def __init__(self, file_name: str, location: str):
		self.__filesize = os.stat(file_name).st_size

		with open(file_name, "rb") as handle:
			self.__filedata = handle.read(self.__filesize)

		self.__filedatacomp = zlib.compress(self.__filedata, 1)
		self.__location = location
		self.__filesizecomp = len(binascii.hexlify(self.__filedatacomp)) // 2

	def get_file_data(self):
		return self.__filedatacomp

	def set_offset(self, offset: int):
		self.__offset = offset

	def get_binary(self) -> bytes:
		data = self.__location.encode('utf-8')
		data += struct.pack("<x") * (256 - len(self.__location))
		data += struct.pack("<I", int(self.__filesizecomp))
		data += struct.pack("<I", self.__filesize)
		data += struct.pack("<I", int(self.__filesizecomp))
		data += struct.pack("<I", self.__offset)
		data += struct.pack("<I", 0)
		data += struct.pack("<I", 0)
		data += struct.pack("<x") * 36
		return data


class EtFileSystem:
	__file = None
	__current_file: str = None

	HEADER_MAGIC: Final[str] = "EyedentityGames Packing File 0.1"
	HEADER_VERSION: Final[int] = 0xB
	FILE_COUNT: Final[int] = 0
	FILE_OFFSET: Final[int] = 0

	__files: List[EtFile] = []

	def __init__(self, file_name: str):
		"""
		Write the specified pak in binary mode

		:param file_name: File path for pak
		:type file_name: str
		"""

		self.__file = open(file_name, 'wb')
		self.__current_file = file_name
		self.write_header()

	def add_file(self, file_name, location):
		"""
		Add the specified file to the pak

		:param file_name: Path of the specified file
		:type file_name: str
		:param location: Location of the file that will be put in the pak
		:type location: str
		"""

		if not os.path.exists(file_name):
			raise FileNotFoundError("File doesn't exist")

		self.__files.append(EtFile(file_name, location))

	def close_file_system(self):
		self.write_data()
		self.write_footer()
		self.__file.close()

	def write_header(self):
		self.__file.write(bytes(self.HEADER_MAGIC, "utf-8"))
		self.__file.write(struct.pack("<x") * 224)
		self.__file.write(struct.pack("<I", self.HEADER_VERSION))
		self.__file.write(struct.pack("<I", self.FILE_COUNT))
		self.__file.write(struct.pack("<I", self.FILE_OFFSET))
		self.__file.write(struct.pack("<I", 0))
		self.__file.write(struct.pack("<x") * 752)

	def rewrite_header(self):
		self.FILE_COUNT = len(self.__files)
		self.FILE_OFFSET = self.__file.tell()

		self.__file.seek(256+4)
		self.__file.write(struct.pack("<I", self.FILE_COUNT))
		self.__file.write(struct.pack("<I", self.FILE_OFFSET))
		self.__file.seek(self.FILE_OFFSET, os.SEEK_SET)

	def write_data(self):
		for f in self.__files:
			f.set_offset(self.__file.tell())
			self.__file.write(f.get_file_data())

	def write_footer(self):
		self.rewrite_header()
		for f in self.__files:
			self.__file.write(f.get_binary())
