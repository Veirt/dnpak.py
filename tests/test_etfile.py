import os
from pathlib import Path

import pytest

from src.dnpak.etfilesystem import EtFile

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


def test_compress_data():
    for file in file_list:
        data_before = open(file["path"], "rb").read()
        data_after = EtFile(file["path"], file["location"])

        assert data_after.get_decompressed_data() == data_before


def test_check_file_size():
    for file in file_list:
        data_before = os.stat(file["path"]).st_size
        data_after = EtFile(file["path"], file["location"])

        assert data_after.get_file_size() == data_before


def test_check_file_location():
    for file in file_list:
        data_after = EtFile(file["path"], file["location"])

        assert data_after.location == str(Path(file["location"]))


def test_error_path():
    with pytest.raises(FileNotFoundError) as err:
        data = EtFile("tests/test_etfilesystem/resource/ext/unavailable.dnt",
                      "/unavailable.dnt")
