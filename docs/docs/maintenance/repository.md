Repository Information
--------------
# Directory Tree
```
docs/
    mkdocs.yml
    docs/
        ...
    site/
        ...
examples/
    append_to_csv.ipynb
    append_to_json.ipynb
    compare_tweets.ipynb
    compare_users.ipynb
    export_to_csv.ipynb
    export_to_json.ipynb
    tweet_info.ipynb
    user_info.ipynb
    resources/
        compare_tweets.json
        tweet_info.json
        user_info.csv
        user_info.json
pysna/
    api.py
    cli.py
    fetch.py
    process.py
    utils.py
    __init__.py
tests/
    config.py
    test_api.py
    test_fetch.py
    test_process.py
    test_utils.py
    cassettes/
        ...
    fixtures/
        ...
.pre-commit-config.yaml
build_deploy.sh
LICENSE
README.md
requirements.txt
setup.py
```

**Details**:

- The ``docs`` directory contains the documentation. The [mkdocs](https://www.mkdocs.org/) package was used to build the documentation. The ``mkdocs.yaml`` specifies the navigation and structure or the documentation. the ``docs/docs/`` directory contains the markdowns files for the documentation. The ``docs/site/`` directory contains the HTML and JavaScript files that build the website. The website is hosted on GitHub Pages.

- The ``examples`` directory contains Jupyter Notebooks that shows how the package can be used and output examples. These files are mainly used to guide the user of the package and provide additional help. The ``examples/resources/`` directory contains saved files that were generated during a function call in one of the notebooks. Users can view these examples to get an idea of how data is saved with the help of this package.

- The ``pysna`` directory contains all necessary files for the pacakge.
    - ``__init__.py`` specifies the import statement shortcuts and is mandatory to define this directory as a Python package.
    - ``api.py`` contains the ``TwitterAPI`` class.
    - ``cli.py`` contains the CLI wrappers and functions for the ``TwitterAPI`` class.
    - ``fetch.py`` contains the ``TwitterDataFetcher`` class.
    - ``process.py`` contains the ``BaseDataProcessor`` and ``TwitterDataProcessor`` classes.
    - ``utils.py`` contains the (internal) utility functions.

- The ``tests`` directory contains all unit tests for the package.
    - The ``cassettes`` folder contains all cassettes made by the [VCR.py](https://vcrpy.readthedocs.io/en/latest/) library.
    - The ``fixtures`` folder contains all byte encoded pickle fixtures.
    - ``config.py`` defines the base test case and configuration of test cases.
    - ``test_api.py`` contains all test cases for the ``TwitterAPI`` class.
    - ``test_fetch.py`` contains all test cases for the ``TwitterDataFetcher`` class.
    - ``test_process.py`` contains all test cases for the ``BaseDataProcessor`` and ``TwitterDataProcessor`` classes.
    - ``test_utils.py`` contains the test cases for internal utility functions.

- The ``.pre-commit.yaml`` files defines [pre-commit](https://pre-commit.com/) hooks. They turned out to be very useful since they ensured clean coding during the implementation. The following pre-commit hooks were defined:
    - ``check-yaml``: auto-formatting yaml files.
    - ``end-of-file-fixer``: adds an empty line to the end of the file.
    - ``trailing-whitespace``: removes trailing whitespace from any files (except markdown files for line breaks)
    - ``requirements-txt-fixer``: checks the used and specified requirements from the ``requirements.txt``
    - ``detect-private-key``: throws an exception if any string was found that looks like a private key/secret.
    - ``fix-encoding-pragma``: remove the coding pragma in a python3-only codebase.
    - ``black``: ensures [black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html) code style.
    - ``isort``: automatically sorts imports.
    - ``flake8``: ensures code style according to [flake8](https://flake8.pycqa.org/en/latest/).

- ``build_deploy.sh`` is used to push the package to the Python Package Index (PyPI). When running the script with the ``--test`` flag, the package will be pushed to the testing stage of PyPI instead of the production stage.

- ``LICENSE``: lincense specifications. MIT license.

- ``README.md``: basic readme file saying what you can do with this package.

- ``requirements.txt``: dependencies used for this package.

- ``setup.py``: setup file for package distribution.

__________________
