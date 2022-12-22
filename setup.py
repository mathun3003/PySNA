# -*- coding: utf-8 -*-
import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = "0.1.0"
PACKAGE_NAME = "PySNA"
AUTHOR = "Mathis Hunke"
AUTHOR_EMAIL = "mhunke1@uni-muenster.de"
URL = "https://github.com/mathun3003/PySNA"

LICENSE = "MIT License"
DESCRIPTION = "Python Package for Social Network Analytics"
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = ["tweepy", "tweepy[async]", "argparse", "pandas", "python-dotenv"]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    packages=find_packages(),
)
