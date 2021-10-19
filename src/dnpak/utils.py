import os


def to_unix_path(location: str) -> str:
    return location.replace("\\", "/")


def to_windows_path(location: str) -> str:
    return location.replace(os.sep, "\\")
