from setuptools import setup

with open("README.md") as file:
    LONG_DESCRIPTION = file.read()

VERSION = "1.0.7"
DESCRIPTION = "A python package to manipulate DragonNest pak file"

setup(
      name="dnpak.py",
      version=VERSION,
      author="Muhammad Dony Mulya",
      author_email="exlog@protonmail.com",
      url="https://github.com/ExLog/dnpak-py",
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      license="WTFPL",
      keywords=["dragonnest"],
      packages=["dnpak"],
      package_dir={"": "src"},
      classifiers=[
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Intended Audience :: Developers",
            "License :: Other/Proprietary License"
      ]
)
