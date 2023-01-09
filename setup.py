# -*- coding: utf-8 -*-
import pathlib
import re

from setuptools import find_packages, setup

VERSION_FILE = "pysna/__init__.py"
with open(VERSION_FILE) as version_file:
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.MULTILINE)

if match:
    version = match.group(1)
else:
    raise RuntimeError(f"Unable to find version string in {VERSION_FILE}.")

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

INSTALL_REQUIRES = ["tweepy", "argparse", "pandas", "python-dotenv"]

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
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "pysna compare_users = pysna.cli:compare_users_cli",
            "pysna user_info = pysna.cli.user_info_cli",
            "pysna compare_users_list = pysna.cli.compare_users_list_cli",
        ]
    },
)
