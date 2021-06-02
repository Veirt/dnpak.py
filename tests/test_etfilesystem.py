import os
import pytest

from src.dnpak.etfilesystem import EtFileSystem
from src.dnpak.etfile import EtFile

file_list = [
    {
        "path": "tests/test_etfilesystem/resource/etc/freeze.msh",
        "location": "/resource/etc/freeze.msh",
    },
    {
        "path": "tests/test_etfilesystem/resource/etc/freeze.skn",
        "location": "/resource/etc/freeze.skn",
    },
]


def create_pak():
    pak = EtFileSystem.write("pak1.test.pak")
    for file in file_list:
        pak.add_file(file["path"], file["location"])

    pak.close_file_system()

    return pak


def test_create_error_pak():
    with pytest.raises(FileNotFoundError):
        pak = EtFileSystem.write("pak2.test.pak")
        pak.add_file("tests/unavailable.dnt", "/resource/ext/unavailable.dnt")
        pak.close_file_system()


def test_error_pak_location():
    with pytest.raises(NameError):
        pak = EtFileSystem.write("pak3.test.pak")
        pak.add_file(file_list[0]["path"], "resource/etc/freeze.msh")
        pak.close_file_system()


def test_read_error_pak():
    with pytest.raises(FileNotFoundError):
        pak = EtFileSystem.read("unavailable.test.pak")
        pak.extract()
        pak.close_file_system()


def read_pak():
    pak = EtFileSystem.read("pak1.test.pak")
    return pak


def test_write_pak_count():
    assert create_pak().FILE_COUNT == 2


def test_read_pak_count():
    assert read_pak().FILE_COUNT == 2


def test_read_pak_extract():
    read_pak().extract()
    assert os.path.exists("pak1.test") is True

    for file in file_list:
        with open(file["path"], "rb") as f:
            before_pak = f.read()

        with open(f"pak1.test{file['location']}", "rb") as f:
            after_pak = f.read()

        assert before_pak == after_pak


def test_read_pak_extract_strict():
    read_pak().extract("strict")
    assert os.path.exists("pak1.test") is True
    assert os.path.exists("pak1.test/resource") is True

    for file in file_list:
        with open(file["path"], "rb") as f:
            before_pak = f.read()

        with open(f"pak1.test{file['location']}", "rb") as f:
            after_pak = f.read()

        assert before_pak == after_pak


def test_read_pak_extract_directory():
    directory = "specific.test"
    read_pak().extract("strict", directory)
    assert os.path.exists(directory) is True
    assert os.path.exists(f"{directory}/resource") is True

    for file in file_list:
        with open(file["path"], "rb") as f:
            before_pak = f.read()

        with open(f"{directory}{file['location']}", "rb") as f:
            after_pak = f.read()

        assert before_pak == after_pak

    read_pak().close_file_system()


def test_read_add_files():
    pak = EtFileSystem.write("pak4.test.pak")
    pak.add_files("tests/test_etfilesystem")
    pak.close_file_system()

    pak1 = EtFileSystem.read("pak4.test.pak")
    pak2 = EtFileSystem.read("pak1.test.pak")

    assert pak1.get_files() == pak2.get_files()

    pak1.close_file_system()
    pak2.close_file_system()


def test_read_add_file():
    pak = EtFileSystem.read("pak1.test.pak")

    for file in file_list:
        pak.add_file(file["path"], file["location"])

    assert pak.FILE_COUNT == 2
    assert len(pak.get_files()) == 4
    pak.close_file_system()

    assert pak.FILE_COUNT == 4


def test_edit_file():
    pak = EtFileSystem.read("pak1.test.pak")
    pak.add_file("tests/test_etfilesystem/test.txt", "/test.txt")
    pak.close_file_system()

    pak = EtFileSystem.read("pak1.test.pak")
    test_txt = pak.find_file(EtFile(location="/test.txt").get_location())
    decompressed = test_txt.get_decompressed_data().decode("utf-8")

    assert decompressed == "test"

    new_data = "test change".encode("utf-8")
    pak.edit_file(test_txt, new_data)
    pak.close_file_system()

    pak = EtFileSystem.read("pak1.test.pak")
    new_test_txt = pak.find_file(EtFile(location="/test.txt").get_location()).get_decompressed_data()

    assert new_data == new_test_txt
