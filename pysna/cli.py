# -*- coding: utf-8 -*-
import argparse
import json
import os
import pathlib
import re
from typing import get_args

from dotenv import load_dotenv

from pysna.api import TwitterAPI
from pysna.utils import append_to_csv, append_to_json, export_to_csv, export_to_json

# TODO: add link for documentation in usage message
msg = """
The command-line interface for the PySNA package

Usage:
  pysna user-info <user> <attributes> [--return-timestamp] [--output] [--append] [--encoding] [--env]
  pysna compare-users <users> <compare> [--features] [--return-timestamp] [--output] [--append] [--encoding] [--env]
  pysna tweet-info <tweet> <attributes> [--return-timestamp] [--output] [--append] [--encoding] [--env]
  pysna compare-tweets <tweets> <attributes> [--features] [--return-timestamp] [--output] [--append] [--encoding] [--env]

Options:
  -h --help        Show this screen.
  --version        Show version.
"""


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

# set main parser
parser = argparse.ArgumentParser(prog="pysna", usage=msg)
# set subparser
subparsers = parser.add_subparsers(dest="subcommand")


def read_secrets(env_path: str) -> dict:
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


@subcommand(
    "user-info",
    args=[
        argument("user", help="Twitter User ID or screen name"),
        argument("attributes", nargs="+", default=[], help=f"List or string of desired User attributes. Must be from {', '.join(get_args(TwitterAPI.LITERALS_USER_INFO))}"),
        argument("--env", "-e", type=str, default=".env", required=False, help="Path to .env file. Defaults to './.env'."),
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
        argument("--env", "-e", type=str, default=".env", required=False, help="Path to .env file. Defaults to './.env'."),
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
        argument("--compare", "-c", nargs="+", default=[], required=True, help=f"The comparison attribute(s). Must be one of the following: {', '.join(get_args(TwitterAPI.LITERALS_COMPARE_USERS))}."),
        argument("--features", "-f", nargs="+", default=[], required=False, help="Features that should be contained in the feature vector for similarity comparison."),
        argument("--env", "-e", type=str, default=".env", required=False, help="Path to .env file. Defaults to './.env'."),
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
        argument("--compare", "-c", nargs="+", default=[], required=True, help=f"The comparison attribute(s). Needs to be one of the following: {', '.join(get_args(TwitterAPI.LITERALS_COMPARE_TWEETS))}."),
        argument("--features", "-f", nargs="+", default=[], required=False, help="Features that should be contained in the feature vector for similarity comparison."),
        argument("--env", "-e", type=str, default=".env", required=False, help="Path to .env file. Defaults to './.env'."),
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
    result = api.compare_tweets(tweets=args.tweets, compare=args.compare, return_timestamp=args.return_timestamp, features=args.features)
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
