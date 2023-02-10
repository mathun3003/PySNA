# -*- coding: utf-8 -*-
import os
import pathlib
import re
import sys
from subprocess import call

from setuptools import find_packages, setup
from setuptools.command.install import install as _install

VERSION_FILE = "pysna/__init__.py"
with open(VERSION_FILE) as version_file:
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.MULTILINE)

if match:
    version = match.group(1)
else:
    raise RuntimeError(f"Unable to find version string in {VERSION_FILE}.")

HERE = pathlib.Path(__file__).parent

VERSION = version
PACKAGE_NAME = "pysna"
AUTHOR = "Mathis Hunke"
AUTHOR_EMAIL = "mhunke1@uni-muenster.de"
URL = "https://github.com/mathun3003/PySNA"

LICENSE = "MIT License"
DESCRIPTION = "Python Package for Social Network Analytics"
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = ["tweepy>=4.12.1", "argparse>=1.4.0", "numpy>=1.24.0", "python-dotenv>=0.21.0", "textblob>=0.17.1", "pandas>=1.5.3"]


def _post_install(dir):
    call([sys.executable, "textblob.download_corpora"], cwd=os.path.join(dir, PACKAGE_NAME))


class install(_install):
    def run(self):
        _install.run(self)
        self.execute(_post_install, (self.install_lib,), msg="Running post install task")


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
    entry_points={"console_scripts": ["pysna = pysna.cli:main"]},
    cmdclass={"install": install},
)
