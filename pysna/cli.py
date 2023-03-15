# -*- coding: utf-8 -*-
import argparse
import json
import os
import pathlib
import re
import shutil
from typing import get_args

from dotenv import load_dotenv

from pysna.api import TwitterAPI
from pysna.utils import append_to_csv, append_to_json, export_to_csv, export_to_json

msg = """
The command-line interface for the PySNA package

Reference: https://mathun3003.github.io/PySNA/user-guide/overview/cli/

Usage:
  pysna set-secrets <path>
  pysna user-info <user> <attributes> [--return-timestamp] [--output] [--append] [--encoding] [--env]
  pysna compare-users <users> -c <compare> [--features] [--return-timestamp] [--output] [--append] [--encoding] [--env]
  pysna tweet-info <tweet> <attributes> [--return-timestamp] [--output] [--append] [--encoding] [--env]
  pysna compare-tweets <tweets> -c <compare> [--features] [--return-timestamp] [--output] [--append] [--encoding] [--env]

Options:
  -h --help        Show this screen.
  --version        Show version.
"""

# get version from __init__.py
HERE = pathlib.Path(__file__).parent
VERSION_FILE = f"{HERE}/__init__.py"
with open(VERSION_FILE) as version_file:
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.MULTILINE)

if match:
    version = match.group(1)
else:
    raise RuntimeError(f"Unable to find version string in {VERSION_FILE}.")

# set constant for required and optional secrets
REQUIRED_SECRETS = ["BEARER_TOKEN", "CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]
OPTIONAL_SECRETS = ["X_RAPIDAPI_KEY", "X_RAPIDAPI_HOST"]
# set config file path under "~/.pysna/config/secrets.env"
config_file_path = os.path.join(os.path.expanduser("~"), ".pysna", "config", "secrets.env")

# set main parser
parser = argparse.ArgumentParser(prog="pysna", usage=msg)
# set subparser
subparsers = parser.add_subparsers(dest="subcommand")
# add version argument
parser.add_argument("--version", action="version", version="%(prog)s {version}".format(version=version))


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


def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the subcommand decorator."""
    return (list(name_or_flags), kwargs)


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


def main():
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
