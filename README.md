# dnpak.py
![PyPI](https://img.shields.io/pypi/v/dnpak.py?color=success)
 [![License: WTFPL](https://img.shields.io/badge/License-WTFPL-brightgreen.svg)](http://www.wtfpl.net/about/)

A python package to manipulate Dragon Nest pak file.

Based on data definitions from [vincentzhang96/DragonNestFileFormats](http://vincentzhang96.github.io/DragonNestFileFormats/files/pak)

- [Installation](#installation)
- [Getting Started](#getting-started)
  * [Write a new PAK and add files to it](#write-a-new-pak-and-add-files-to-it)
  * [Read PAK and extract files inside](#read-pak-and-extract-files-inside-it)
- [Developing](#developing)
  * [Install package locally](#install-package-locally)
  * [Build package](#build-package)

## Installation
Make sure you have pip installed, and run this command:
```shell
$ pip install dnpak.py
```

## Getting Started

With this package you can write and read to pak file
### Write a new PAK and add files to it
```python
import dnpak

pak = dnpak.EtFileSystem.write("filename.pak")
pak.add_file("path/to/file", "/file/location/in/pak/")
pak.add_file("another/file", "/another/file/location/in/pak")
pak.close_file_system()  # Make sure to close file
```
### Read PAK and extract files inside
```python
pak = dnpak.EtFileSystem.read("filename.pak")
pak.extract()
pak.close_file_system()
```

## Developing
Guide for developing, if you're interested in developing this feel free to make a pull request

### Install package locally
```shell
$ pip install -e .
```
### Build package
Make sure you have the latest version of PyPA’s ```build``` installed:
```shell
$ py -m pip install --upgrade build
```
Now run this command from the same directory where ```pyproject.toml``` is located:
```shell
$ py -m build
```