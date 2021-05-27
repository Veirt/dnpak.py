import binascii
import os
import struct
import zlib


class EtFile:
	__filedata = None
	__filedatacomp = None
	__filesize = None
	__filesizecomp = None
	__location = None
	__offset = None

	def __init__(self, file_name, location):
		self.__filesize = os.stat(file_name).st_size

		with open(file_name, "rb") as handle:
			self.__filedata = handle.read(self.__filesize)

		self.__filedatacomp = zlib.compress(self.__filedata, 1)
		self.__location = location
		self.__filesizecomp = len(binascii.hexlify(self.__filedatacomp)) // 2

	def get_file_data(self):
		return self.__filedatacomp

	def set_offset(self, offset):
		self.__offset = offset

	def get_binary(self):
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
	__current_file = None

	HEADER_MAGIC = "EyedentityGames Packing File 0.1"
	HEADER_VERSION = 0xB
	FILE_COUNT = 123654
	FILE_OFFSET = 8888

	__files = []

	def __init__(self, file_name):
		self.__file = open(file_name, 'wb')
		self.__current_file = file_name
		self.write_header()

	def add_file(self, file_name, location):
		if os.path.exists(file_name):
			self.__files.append(EtFile(file_name, location))
		else:
			raise FileNotFoundError("File doesn't exist")

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


pak = EtFileSystem("mine.pak")
pak.add_file("resource/ext/accounteffecttable.dnt", "\\resource\\ext\\accounteffecttable.dnt")
pak.close_file_system()
