# PySNA
Python Package for Social Network Analytics

Installation
------------

The easiest way to install the latest version from PyPI is by using
[pip](https://pip.pypa.io/):

    pip install pysna

You can also use Git to clone the repository from GitHub to install the latest
development version:

    git clone https://github.com/mathun3003/PySNA.git
    cd PySNA
    pip install .

Alternatively, install directly from the GitHub repository:

    pip install git+https://github.com/mathun3003/PySNA.git


Quick Start
------------
Import the API class for the Twitter API by writing:

```python
from pysna import TwitterAPI
```

or import utility functions, too, by writing:

```python
from pysna import *
```

Then, create an API instance by running:

```python
api = TwitterAPI("BEARER_TOKEN", "CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")
```

and invoke a function:

```python
api.user_info(...)
```

Find usage and output examples in the [examples folder](https://github.com/mathun3003/PySNA/tree/main/examples).

Functionalities
------------
This package was designed to perform data analysis on Twitter data. It extends the official Twitter API by using the open-source package [tweepy](https://github.com/tweepy/tweepy).

Thus, the following functions are added to the tweepy package:
- ``user_info``
- ``tweet_info``
- ``compare_users``
- ``compare_tweets``

Furthermore, some utility functions exist:
- ``export_to_json``
- ``append_to_json``

You can find further information on the [Documentation]().


CLI
----------------
The above mentioned functions are also available on the CLI.

To see the usage instructions and help, run:

    pysna -h

If you wish to see the usage instructions for a function, run:

    pysna <function> --help

For example, if you want to request a comparison of two users, you can run:

```bash
pysna compare-users "WWU_Muenster" "goetheuni" -c "tweets_count" "common_followers" -o "results.json" --return-timestamp
```

This will perform a comparison on the ``"WWU_Muenster"`` and ``"goetheuni"`` Twitter Accounts based on their number of composed Tweets and common followers. The results are exported to the ``results.json`` file. Also, the timestamp of the request will be returned.

NOTE: every request needs valid credentials for the official Twitter API. If you run this command from a different directory than from your project root, pass in the path to an ``.env`` file containing your secrets. Also, if you have a differend named environment file in your project root (e.g., ``local.env``), you have to pass the filename, too, using the ``--env`` flag:

    pysna compare-users [...] --env ./local.env

The default value is set to ``./.env``.


Notes
------------

- Only Python 3.10 is supported.
- Only ``.env`` files are supported for the CLI, yet.
