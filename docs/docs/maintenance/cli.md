Command-line Interface Functions
----------------

The functions for the CLI are implemented using the [argparse](https://docs.python.org/3/library/argparse.html) Python library.

Initially, the usage message is set that users can receive by calling ``pysna --help``. Then, the package version is collected by using a regular expression search for the version specification in the ``__init__.py``. The version is added to the main parser argument for ``--version``.  
Then, the required secrets (i.e., secrets for the Twitter API. See [here](../user-guide/overview/TwitterAPI.md#initialization) for more information) and optional secrets (i.e., Botometer API secrets) are set.

Since every function call via the CLI will generate a new CLI session, it is technically infeasible to store the secrets across all CLI sessions and function calls. To avoid passing in the secrets every time the user calls a function, a config file path is defined where the secrets will be stored. Then, the parsers will read the configured secrets from this config file path, so the user does not need to pass in the secrets manually for every function call.

The ``config_file_path`` is set under the home directory: ``~/.pysna/config/secrets.env``. The ``.pysna`` folder is hidden.

For the CLI tool, two parsers were defined: The main parser reacting to the ``pysna`` command and the ``--version`` and ``-help`` flags. The subparser is used to define subcommands for the main parser such that commands/functions can be chained (e.g., ``pysna user-info``).

For every subcommand, the help instructions can be found via the ``--help`` flag (e.g., ``pysna user-info --help``).

____________

# Internal Functions

Internal functions are used to process data, parse file contents, or handle user input.

### read_secrets

This function reads the secrets from the specified environment path. For default, the ``config_file_path`` variable is passed in by all user functions. If any other path is provided, the function will read the secrets from this file. Only ``.env`` files are supported.

Function:

```python
read_secrets(env_path: str)
```

The ``.env`` file must be of the form:
```
BEARER_TOKEN=
CONSUMER_KEY=
CONSUMER_SECRET=
ACCESS_TOKEN=
ACCESS_TOKEN_SECRET=
X_RAPIDAPI_KEY=
X_RAPIDAPI_HOST=
```

The function will read the secrets and return a dictionary containing the lowered keys and secrets from the ``.env`` file.

<details>
<summary>Source Code</summary>
```python
def read_secrets(env_path: str) -> dict:
    if not os.path.exists(env_path):
        raise Exception("No config file found for secrets. Use the 'set-secrets' function to create a config file or provide a .env file using the '--env' flag.")
    else:
        load_dotenv(env_path)
        # catch environmental variables
        for secret in REQUIRED_SECRETS:
            if secret not in os.environ:
                raise KeyError(f"{secret} must be provided in the environment variables.")
        # collect secrets
        secrets = {secret.lower(): os.getenv(secret) for secret in REQUIRED_SECRETS + OPTIONAL_SECRETS}
        return secrets
```
</details>

____________
### output

The output function receives the data returned by one of the user functions. Then, this function decides based on the provided arguments if the data should be printed to the console, exported to a file (CSV or JSON) or appended to a file.

In case, the user specified a file path using the ``--output`` flag but does not specify the ``--append`` flag, then the data will be written to a JSON (if the path ends with a ``.json``) or CSV (if the path ends with a ``.csv``) file. If the user also specified the ``--append`` flag, then the data will be appended to the specified file. Otherwise, the data will be printed to stdout.

Function:

```python
output(data: dict, encoding: str, path: str | None = None, append: bool = False)
```

Args:  

- ``data`` (dict): input data that has been fetched by a function.
- ``encoding`` (str): encoding option of the export. Defaults to UTF-8.
- ``path`` (str | None): the path to the file. Defaults to None.
- ``append`` (bool): wheather to append the data or not. Defaults to false.

This function is used for every main user function. It handles the specified flags by the user (i.e., ``return_timestamp``, ``append``, ``encoding``)

<details>
<summary>Source Code</summary>
```python
def output(data: dict, encoding: str, path: str | None = None, append: bool = False):
    # either print results if '--output' arg was provided
    if (path is not None) and (append is False):
        if path.endswith(".json"):
            export_to_json(data, path, encoding)
        elif path.endswith(".csv"):
            export_to_csv(data, path, encoding)
    # or append to existing file
    elif (path is not None) and (append is True):
        if path.endswith(".json"):
            append_to_json(data, path, encoding)
        elif path.endswith(".csv"):
            append_to_csv(data, path, encoding)
    # or print them to the CLI in JSON format
    else:
        print(json.dumps(data, ensure_ascii=False))
    pass
```
</details>

____________
### argument

Convenience function to properly format arguments to pass to the subcommand decorator.

Function:
```python
argument(*name_or_flags, **kwargs)
```

This function returns a tuple of a list of names or flags and the specified keyword arguments. It is a helper function used to pass in arguments to the decorator [``subcommand``](./cli.md#subcommand-decorator)

<details>
<summary>Source Code</summary>
```python
def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the subcommand decorator."""
    return (list(name_or_flags), kwargs)
```
</details>

____________
### subcommand (decorator)

Decorator to define a new subcommand in a sanity-preserving way.
The function will be stored in the ``func`` variable when the parser parses arguments so that it can be called directly like so:

```python
args = cli.parse_args()
args.func(args)
```

Usage example:

```python
@subcommand([argument("-d", help="Enable debug mode", action="store_true")])
def subcommand(args):
    print(args)
```

Then on the command line:
```bash
python cli.py subcommand -d
```

This function is a Python decorator defining a function as a subcommand to the main parser. It adds a new argument to the subparser. Developers can define the function name using the ``function_name`` argument (e.g., ``user-info``) and pass in the function arguments using the ``args`` argument in combination with the [``argument``](./cli.md#argument) function.

<details>
<summary>Source Code</summary>
```python
def subcommand(function_name: str, args=[], parent=subparsers):
    """Decorator to define a new subcommand in a sanity-preserving way.
    The function will be stored in the ``func`` variable when the parser
    parses arguments so that it can be called directly like so::
        args = cli.parse_args()
        args.func(args)
    Usage example::
        @subcommand([argument("-d", help="Enable debug mode", action="store_true")])
        def subcommand(args):
            print(args)
    Then on the command line::
        $ python cli.py subcommand -d
    """

    def decorator(func):
        parser = parent.add_parser(function_name, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)

    return decorator
```
</details>

____________
### main

This function is called when the user runs the ``pysna`` command on the console. It parses the provided arguments (such as the subcommands and related arguments) or prints the help or usage instructions to the console.

<details>
<summary>Source Code</summary>
```python
def main():
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)
```
</details>

____________

# User Functions

User functions are designed to be used by the package user. They form the basis for interaction with the package.

### set_secrets

Since every CLI sessions requires secrets for authentification with the Twitter API, this function serves a way to store the secrets at a hidden place under the ``config_file_path``.

The user has to run this function once to set the secrets. Whenever the user wishes to change/overwrite set secrets, he or she can rerun this function. The user has to pass in a file path to a ``.env`` file. The ``.env`` file must be of the form:

```
BEARER_TOKEN=
CONSUMER_KEY=
CONSUMER_SECRET=
ACCESS_TOKEN=
ACCESS_TOKEN_SECRET=
X_RAPIDAPI_KEY=
X_RAPIDAPI_HOST=
```

In case, any secrets was not provided, an exception will be thrown.

If all secrets were collected by the function, it creates the ``config_file_path`` under the home directory of the user and copies the ``.env`` file to this path.

After copying, a message wil be prompted saying the user that the secrets has been set.

<details>
<summary>Source Code</summary>
```python
@subcommand("set-secrets", args=[argument("secrets_file", type=str, help="Path to the secrets file. Only .env files are supported.")])
def set_secrets(args):
    """CLI function to set or overwrite a config file for storing API secrets. Config file will be set to '~/.pysna/config/secrets.env'."""
    if not args.secrets_file.endswith(".env"):
        raise Exception("Only .env files are supported. Please pass in a .env file.")
    # check .env file format
    load_dotenv(args.secrets_file)
    for secret in REQUIRED_SECRETS:
        if secret not in os.environ:
            raise Exception(
                f"{secret} must be provided in the {args.secrets_file} file."
                f"\nMake sure that your {args.secrets_file} has the following format:"
                f"\nBEARER_TOKEN=...\nCONSUMER_KEY=...\nCONSUMER_SECRET=...\nACCESS_TOKEN=...\nACCESS_TOKEN_SECRET=..."
                f"\nIf you wish to use the Botometer API, also provide the {', '.join(OPTIONAL_SECRETS)} keys in the {args.secrets_file} file."
            )
    # create folders if it does not exist yet
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
    # copy file content from args.secrets_file to config file path
    shutil.copy2(args.secrets_file, config_file_path)
    print(f"Secrets from {args.secrets_file} file were set.")
```
</details>

____________
### user_info_cli

CLI function equivalent to the [TwitterAPI.user_info](./TwitterAPI.md#user_info) function. This function is a wrapper around the [TwitterAPI.user_info](./TwitterAPI.md#user_info) function and handles the inputs and outputs to the console.

Args:

- ``user``: User ID or screen name.
- ``attributes`` (List): User attributes. Must be from [his list](../user-guide/overview/literals-user-info.md).
- ``env`` (str, optional): Path to ``.env`` file. Defaults to ``config_file_path``. If the user wishes to use different secrets for authentification, he or she can pass in the path to another ``.env`` file. This file must also have the same form, as described in the [``read_secrets``](./cli.md#read_secrets) function section.
- ``return_timestamp`` (bool, optional): Wheather to return the Unix timestamp of the request. Defaults to false.
- ``output`` (str, optional): Export file path. This argument is also used in combination with the ``append`` argument to specify that the data should be added to an existing file. If both arguments were provided, data is appended.
- ``encoding`` (str, optional): Encoding of the data. Defaults to UTF-8.
- ``append`` (bool, optional): Wheather to append the data to an existing file or not. If the flag is provided (i.e., true), the file path needs to be specified with the ``output`` argument.

First, the secrets are loaded from the environment file path. Then, the authentication to the TwitterAPI using the ``TwitterAPI`` class is performed. After that, the ``TwitterAPI`` instance calls the ``user_info`` function with the specified arguments. The results are either printed to the console, exported to a file, or appended to a file.

<details>
<summary>Source Code</summary>
```python
@subcommand(
    "user-info",
    args=[
        argument("user", help="Twitter User ID or screen name"),
        argument("attributes", nargs="+", default=[], help=f"List or string of desired User attributes. Must be from {', '.join(get_args(TwitterAPI.LITERALS_USER_INFO))}"),
        argument("--env", "-e", type=str, default=config_file_path, required=False, help=f"Path to .env file. Defaults to {config_file_path}."),
        argument("--return-timestamp", type=bool, default=False, required=False, action=argparse.BooleanOptionalAction, help="Returns the UTC timestamp of the request."),
        argument(
            "--output",
            "-o",
            type=str,
            default=None,
            required=False,
            help="Store results in a JSON or CSV file. Specify output file path (including file name). File extension specifies file export (e.g., '.csv' for CSV file export and '.json' for JSON file export)",
        ),
        argument("--encoding", type=str, default="utf-8", required=False, help="Encoding of the output file. Defaults to UTF-8."),
        argument("--append", "-a", type=bool, default=False, required=False, action=argparse.BooleanOptionalAction, help="Add results to an existing JSON file. File needs to be specified in the --output flag."),
    ],
)
def user_info_cli(args):
    """CLI function to request information from the specified Twitter user."""
    # read secrets
    secrets = read_secrets(args.env)
    # establish connection to the API
    api = TwitterAPI(**secrets)
    # get results
    result = api.user_info(user=args.user, attributes=args.attributes, return_timestamp=args.return_timestamp)
    # handle output
    output(result, path=args.output, encoding=args.encoding, append=args.append)
    pass
```
</details>

____________
### tweet_info_cli

CLI function equivalent to the [TwitterAPI.tweet_info](./TwitterAPI.md#tweet_info) function. This function is a wrapper around the [TwitterAPI.tweet_info](./TwitterAPI.md#tweet_info) function and handles the inputs and outputs to the console.

Args:  

- ``tweet_id``: The tweet ID
- ``attributes`` (List): Tweet attributes. Must be from [this list](../user-guide/overview/literals-tweet-info.md).
- ``env`` (str, optional): Path to ``.env`` file. Defaults to ``config_file_path``. If the user wishes to use different secrets for authentification, he or she can pass in the path to another ``.env`` file. This file must also have the same form, as described in the [``read_secrets``](./cli.md#read_secrets) function section.
- ``return_timestamp`` (bool, optional): Wheather to return the Unix timestamp of the request. Defaults to false.
- ``output`` (str, optional): Export file path. This argument is also used in combination with the ``append`` argument to specify that the data should be added to an existing file. If both arguments were provided, data is appended.
- ``encoding`` (str, optional): Encoding of the data. Defaults to UTF-8.
- ``append`` (bool, optional): Wheather to append the data to an existing file or not. If the flag is provided (i.e., true), the file path needs to be specified with the ``output`` argument.

First, the secrets are loaded from the environment file path. Then, the authentication to the TwitterAPI using the ``TwitterAPI`` class is performed. After that, the ``TwitterAPI`` instance calls the ``tweet_info`` function with the specified arguments. The results are either printed to the console, exported to a file, or appended to a file.

<details>
<summary>Source Code</summary>
```python
@subcommand(
    "tweet-info",
    args=[
        argument("tweet_id", help="Tweet ID"),
        argument("attributes", nargs="+", default=[], help=f"List or string of desired Tweet attribute. Must be from {', '.join(get_args(TwitterAPI.LITERALS_TWEET_INFO))}"),
        argument("--env", "-e", type=str, default=config_file_path, required=False, help=f"Path to .env file. Defaults to {config_file_path}."),
        argument("--return-timestamp", type=bool, default=False, required=False, action=argparse.BooleanOptionalAction, help="Returns the UTC timestamp of the request."),
        argument(
            "--output",
            "-o",
            type=str,
            default=None,
            required=False,
            help="Store results in a JSON or CSV file. Specify output file path (including file name). File extension specifies file export (e.g., '.csv' for CSV file export and '.json' for JSON file export)",
        ),
        argument("--encoding", type=str, default="utf-8", required=False, help="Encoding of the output file. Defaults to UTF-8."),
        argument("--append", "-a", type=bool, default=False, required=False, action=argparse.BooleanOptionalAction, help="Add results to an existing JSON file. File needs to be specified in the --output flag."),
    ],
)
def tweet_info_cli(args):
    """CLI function to request information from the specified Tweet."""
    # read secrets
    secrets = read_secrets(args.env)
    # establish connection to the API
    api = TwitterAPI(**secrets)
    # get results
    result = api.tweet_info(tweet_id=args.tweet_id, attributes=args.attributes, return_timestamp=args.return_timestamp)
    # handle output
    output(result, path=args.output, encoding=args.encoding, append=args.append)
    pass
```
</details>

____________
### compare_users_cli

CLI function equivalent to the [TwitterAPI.compare_users](./TwitterAPI.md#compare_users) function. This function is a wrapper around the [TwitterAPI.compare_users](./TwitterAPI.md#compare_users) function and handles the inputs and outputs to the console.

Args:  

- ``users`` (List): User IDs or screen names.
-- ``compare`` (List): Comparison attributes for Twitter users. Must be from [this list](../user-guide/overview/literals-compare-users.md). Short form: ``-c``.
- ``features`` (List): Features that should be contained within the feature vectors for the ``similarity`` comparison attribute. Must be from [this list](../user-guide/overview/literals-compare-users.md). Short form: ``-f``
- ``env`` (str, optional): Path to ``.env`` file. Defaults to ``config_file_path``. If the user wishes to use different secrets for authentification, he or she can pass in the path to another ``.env`` file. This file must also have the same form, as described in the [``read_secrets``](./cli.md#read_secrets) function section.
- ``return_timestamp`` (bool, optional): Wheather to return the Unix timestamp of the request. Defaults to false.
- ``output`` (str, optional): Export file path. This argument is also used in combination with the ``append`` argument to specify that the data should be added to an existing file. If both arguments were provided, data is appended.
- ``encoding`` (str, optional): Encoding of the data. Defaults to UTF-8.
- ``append`` (bool, optional): Wheather to append the data to an existing file or not. If the flag is provided (i.e., true), the file path needs to be specified with the ``output`` argument.

First, the secrets are loaded from the environment file path. Then, the authentication to the TwitterAPI using the ``TwitterAPI`` class is performed. After that, the ``TwitterAPI`` instance calls the ``compare_users`` function with the specified arguments. The results are either printed to the console, exported to a file, or appended to a file.

<details>
<summary>Source Code</summary>
```python
@subcommand(
    "compare-users",
    args=[
        argument("users", nargs="+", default=[], help="The IDs or screen names of the users."),
        argument("--compare", "-c", nargs="+", default=[], required=True, help=f"The comparison attribute(s). Must be from following: {', '.join(get_args(TwitterAPI.LITERALS_COMPARE_USERS))}."),
        argument(
            "--features",
            "-f",
            nargs="+",
            default=[],
            required=False,
            help=f"Features that should be contained in the feature vector for similarity comparison. Must be from: {', '.join(get_args(TwitterAPI.SIMILARITY_FEATURES_COMPARE_USERS))}",
        ),
        argument("--env", "-e", type=str, default=config_file_path, required=False, help=f"Path to .env file. Defaults to {config_file_path}."),
        argument("--return-timestamp", type=bool, default=False, required=False, action=argparse.BooleanOptionalAction, help="Returns the UTC timestamp of the request."),
        argument(
            "--output",
            "-o",
            type=str,
            default=None,
            required=False,
            help="Store results in a JSON or CSV file. Specify output file path (including file name). File extension specifies file export (e.g., '.csv' for CSV file export and '.json' for JSON file export)",
        ),
        argument("--encoding", type=str, default="utf-8", required=False, help="Encoding of the output file. Defaults to UTF-8."),
        argument("--append", "-a", type=bool, default=False, required=False, action=argparse.BooleanOptionalAction, help="Add results to an existing JSON file. File needs to be specified in the --output flag."),
    ],
)
def compare_users_cli(args):
    """CLI function to compare multiple Twitter users with the specified comparision attribute(s)."""
    # read secrets
    secrets = read_secrets(args.env)
    # establish connection to the API
    api = TwitterAPI(**secrets)
    # get results
    result = api.compare_users(users=args.users, compare=args.compare, return_timestamp=args.return_timestamp, features=args.features)
    # handle output
    output(result, path=args.output, encoding=args.encoding, append=args.append)
    pass
```
</details>

____________
### compare_tweets_cli

CLI function equivalent to the [TwitterAPI.compare_tweets](./TwitterAPI.md#compare_tweets) function. This function is a wrapper around the [TwitterAPI.compare_tweets](./TwitterAPI.md#compare_tweets) function and handles the inputs and outputs to the console.

Args:  


- ``tweets`` (List): Tweet IDs
- ``compare`` (List): Comparison attributes for Twitter users. Must be from [this list](../user-guide/overview/literals-compare-tweets.md). Short form: ``-c``.
- ``features`` (List): Features that should be contained within the feature vectors for the ``similarity`` comparison attribute. Must be from [this list](../user-guide/overview/literals-compare-tweets.md). Short form: ``-f``
- ``env`` (str, optional): Path to ``.env`` file. Defaults to ``config_file_path``. If the user wishes to use different secrets for authentification, he or she can pass in the path to another ``.env`` file. This file must also have the same form, as described in the [``read_secrets``](./cli.md#read_secrets) function section.
- ``return_timestamp`` (bool, optional): Wheather to return the Unix timestamp of the request. Defaults to false.
- ``output`` (str, optional): Export file path. This argument is also used in combination with the ``append`` argument to specify that the data should be added to an existing file. If both arguments were provided, data is appended.
- ``encoding`` (str, optional): Encoding of the data. Defaults to UTF-8.
- ``append`` (bool, optional): Wheather to append the data to an existing file or not. If the flag is provided (i.e., true), the file path needs to be specified with the ``output`` argument.

First, the secrets are loaded from the environment file path. Then, the authentication to the TwitterAPI using the ``TwitterAPI`` class is performed. After that, the ``TwitterAPI`` instance calls the ``compare_tweets`` function with the specified arguments. The results are either printed to the console, exported to a file, or appended to a file.

<details>
<summary>Source Code</summary>
```python
@subcommand(
    "compare-tweets",
    args=[
        argument("tweets", nargs="+", default=[], help="The IDs of the Tweets."),
        argument("--compare", "-c", nargs="+", default=[], required=True, help=f"The comparison attribute(s). Must be the following: {', '.join(get_args(TwitterAPI.LITERALS_COMPARE_TWEETS))}."),
        argument(
            "--features", "-f", nargs="+", default=[], required=False, help=f"Features that should be contained in the feature vector for similarity comparison. Must be from: {', '.join(get_args(TwitterAPI.SIMILARITY_FEATURES_COMPARE_TWEETS))}"
        ),
        argument("--env", "-e", type=str, default=config_file_path, required=False, help=f"Path to .env file. Defaults to {config_file_path}."),
        argument("--return-timestamp", type=bool, default=False, required=False, action=argparse.BooleanOptionalAction, help="Returns the UTC timestamp of the request."),
        argument(
            "--output",
            "-o",
            type=str,
            default=None,
            required=False,
            help="Store results in a JSON or CSV file. Specify output file path (including file name). File extension specifies file export (e.g., '.csv' for CSV file export and '.json' for JSON file export)",
        ),
        argument("--encoding", type=str, default="utf-8", required=False, help="Encoding of the output file. Defaults to UTF-8."),
        argument("--append", "-a", type=bool, default=False, required=False, action=argparse.BooleanOptionalAction, help="Add results to an existing JSON file. File needs to be specified in the --output flag."),
    ],
)
def compare_tweets_cli(args):
    """CLI function to compare multiple Tweets with the specified comparision attribute(s)."""
    # read secrets
    secrets = read_secrets(args.env)
    # establish connection to the API
    api = TwitterAPI(**secrets)
    # get results
    result = api.compare_tweets(tweet_ids=args.tweets, compare=args.compare, return_timestamp=args.return_timestamp, features=args.features)
    # handle output
    output(result, path=args.output, encoding=args.encoding, append=args.append)
    pass
```
</details>

____________
