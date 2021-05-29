from setuptools import setup

VERSION = "1.0.0"
DESCRIPTION = "A python package to manipulate DragonNest pak file"

setup(
      name="dnpak.py",
      version=VERSION,
      author="Muhammad Dony Mulya",
      author_email="exlog@protonmail.com",
      url="https://github.com/ExLog/dnpak-py",
      description=DESCRIPTION,
      license="WTFPL",
      keywords=["dragonnest"],
      packages=["dnpak"],
      package_dir={"": "src"},
      classifiers=[
            "Programming Language :: Python :: 3.6",
      ]
)
