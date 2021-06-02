import os

import pytest

from src.dnpak.etfile import EtFile
from src.dnpak.etfilesystem import EtFileSystem

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


def create_pak(tmp_path):
    pak = EtFileSystem.write(f"{tmp_path}\\pak1.test.pak")
    for file in file_list:
        pak.add_file(file["path"], file["location"])

    pak.close_file_system()

    return pak


def test_create_error_pak(tmp_path):
    with pytest.raises(FileNotFoundError):
        pak = EtFileSystem.write(f"{tmp_path}\\pak2.test.pak")
        pak.add_file("tests/unavailable.dnt", "/resource/ext/unavailable.dnt")
        pak.close_file_system()


def test_error_pak_location(tmp_path):
    with pytest.raises(NameError):
        pak = EtFileSystem.write(f"{tmp_path}\\pak3.test.pak")
        pak.add_file(file_list[0]["path"], "resource/etc/freeze.msh")
        pak.close_file_system()


def test_read_error_pak(tmp_path):
    with pytest.raises(FileNotFoundError):
        pak = EtFileSystem.read(f"{tmp_path}\\unavailable.test.pak")
        pak.extract()
        pak.close_file_system()


def test_write_pak_count(tmp_path):
    assert create_pak(tmp_path).FILE_COUNT == 2


def test_read_pak_count(tmp_path):
    create_pak(tmp_path)

    pak = EtFileSystem.read(f"{tmp_path}\\pak1.test.pak")
    assert pak.FILE_COUNT == 2


def test_read_pak_extract(tmp_path):
    create_pak(tmp_path)

    pak = EtFileSystem.read(f"{tmp_path}\\pak1.test.pak")
    pak.extract()
    assert os.path.exists(f"{tmp_path}\\pak1.test") is True

    for file in file_list:
        with open(file["path"], "rb") as f:
            before_pak = f.read()

        with open(f"{tmp_path}\\pak1.test{file['location']}", "rb") as f:
            after_pak = f.read()

        assert before_pak == after_pak


def test_read_pak_extract_strict(tmp_path):
    create_pak(tmp_path)

    pak = EtFileSystem.read(f"{tmp_path}\\pak1.test.pak")
    pak.extract("strict")
    assert os.path.exists(f"{tmp_path}\\pak1.test") is True
    assert os.path.exists(f"{tmp_path}\\pak1.test\\resource") is True

    for file in file_list:
        with open(file["path"], "rb") as f:
            before_pak = f.read()

        with open(f"{tmp_path}\\pak1.test{file['location']}", "rb") as f:
            after_pak = f.read()

        assert before_pak == after_pak


def test_read_pak_extract_directory(tmp_path):
    create_pak(tmp_path)

    directory = f"{tmp_path}\\specific.test"
    pak = EtFileSystem.read(f"{tmp_path}\\pak1.test.pak")
    pak.extract("strict", directory)
    assert os.path.exists(directory) is True
    assert os.path.exists(f"{directory}/resource") is True

    for file in file_list:
        with open(file["path"], "rb") as f:
            before_pak = f.read()

        with open(f"{directory}{file['location']}", "rb") as f:
            after_pak = f.read()

        assert before_pak == after_pak

    pak.close_file_system()


def test_read_add_files(tmp_path):
    create_pak(tmp_path)

    pak = EtFileSystem.write(f"{tmp_path}\\pak4.test.pak")
    pak.add_files("tests/test_etfilesystem")
    pak.close_file_system()

    pak1 = EtFileSystem.read(f"{tmp_path}\\pak4.test.pak")
    pak2 = EtFileSystem.read(f"{tmp_path}\\pak1.test.pak")

    assert pak1.get_files() == pak2.get_files()

    pak1.close_file_system()
    pak2.close_file_system()


def test_read_add_file(tmp_path):
    create_pak(tmp_path)

    pak = EtFileSystem.read(f"{tmp_path}\\pak1.test.pak")

    for file in file_list:
        pak.add_file(file["path"], file["location"])

    assert pak.FILE_COUNT == 2
    assert len(pak.get_files()) == 4
    pak.close_file_system()

    assert pak.FILE_COUNT == 4


def test_edit_file(tmp_path):
    create_pak(tmp_path)

    pak = EtFileSystem.read(f"{tmp_path}\\pak1.test.pak")
    pak.add_file("tests/test_etfilesystem/test.txt", "/test.txt")
    pak.close_file_system()

    pak = EtFileSystem.read(f"{tmp_path}\\pak1.test.pak")
    test_txt = pak.find_file(EtFile(location="/test.txt").get_location())
    decompressed = test_txt.get_decompressed_data().decode("utf-8")

    assert decompressed == "test"

    new_data = "test change".encode("utf-8")
    pak.edit_file(test_txt, new_data)
    pak.close_file_system()

    pak = EtFileSystem.read(f"{tmp_path}\\pak1.test.pak")
    new_test_txt = pak.find_file(
        EtFile(location="/test.txt").get_location()
    ).get_decompressed_data()

    assert new_data == new_test_txt
