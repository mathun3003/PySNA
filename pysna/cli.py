# -*- coding: utf-8 -*-
"""
The command-line interface for the PySNA package

Usage:
  pysna user-info <user> <attributes> [--return-timestamp] [--output] [--encoding] [--ensure-ascii]
  pysna compare-users <users> <compare> [--return-timestamp] [--output] [--encoding] [--ensure-ascii]
  pysna tweet-info <tweet> <attributes> [--return-timestamp] [--output]
  pysna compare-tweets <tweets> <attributes> [--return-timestamp]
  pysna load-secrets <env-path>

Options:
  -h --help        Show this screen.
"""
import argparse
import json
import os
import pathlib
import re
from typing import List, get_args

from docopt import docopt
from dotenv import load_dotenv

import pysna
from pysna.api import TwitterAPI

HERE = pathlib.Path(__file__).parent
VERSION_FILE = f"{HERE}/__init__.py"
with open(VERSION_FILE) as version_file:
    match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file.read(), re.MULTILINE)

if match:
    version = match.group(1)
else:
    raise RuntimeError(f"Unable to find version string in {VERSION_FILE}.")


# set constant for required secrets
REQUIRED_SECRETS = ["BEARER_TOKEN", "CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]


def _read_secrets() -> dict:
    # catch environmental variables
    for secret in REQUIRED_SECRETS:
        if secret not in os.environ:
            raise KeyError(f"{secret} must be provided in the environment variables.")
    # collect secrets
    secrets = {secret.lower(): os.getenv(secret) for secret in REQUIRED_SECRETS}
    return secrets


def _output(data: dict, encoding: str, ensure_ascii: bool, export_path: str | None = None):
    # either print results if '--output' arg was provided
    if export_path is not None:
        with open(export_path, "w", encoding=encoding) as f:
            json.dump(data, f, indent=4, ensure_ascii=ensure_ascii)
    # or print them to the CLI
    else:
        print(data)
    pass


def load_secrets(env_path: str):
    """CLI helper function to load secrets to environment variables."""
    load_dotenv(env_path)
    print("secrets loaded from {}".format(env_path))


def user_info_cli():
    """CLI function of the TwitterAPI().user_info function"""
    # define parser
    parser = argparse.ArgumentParser(prog="pysna", description="CLI function to request information from the specified Twitter user.")
    # set first input param
    parser.add_argument("user", type=str, help="The ID or screen name of the Twitter user.")
    # set second input param
    parser.add_argument(
        "attributes",
        type=List[str] | str,
        help=f"""Available user information attributes. These must be from: {', '.join(get_args(TwitterAPI.LITERALS_USER_INFO))}.""",
    )
    # set third input param
    parser.add_argument("--return-timestamp", type=bool, required=False, default=False, help="Return UTC timestamp of the request.")
    # set fourth input argument (optional)
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")
    # set optional encoding and ascii parameters
    parser.add_argument("--encoding", type=str, required=False, default="utf-8", help="File export encoding. Defaults to UTF-8.")
    parser.add_argument("--ensure-ascii", type=bool, required=False, default=False, help="Ensure ASCII encoding during file export.")

    # parse args
    args = parser.parse_args()
    # load secrets
    secrets = _read_secrets()

    # establish connection to the API
    api = TwitterAPI(**secrets)
    # get results
    result = api.user_info(user=args.user, attributes=args.attributes, return_timestamp=args.return_timestamp)
    # handle output
    _output(result, export_path=args.output, encoding=args.encoding, ensure_ascii=args.ensure_ascii)
    pass


def compare_users_cli():
    """CLI function of the TwitterAPI().compare_users_list function"""
    # define parser
    parser = argparse.ArgumentParser(
        prog="pysna",
        description="CLI function to compare multiple Twitter users with the specified comparision attribute.",
    )
    parser.add_argument("users", type=List[str], nargs="+", default=[], help="The IDs or screen names of the users.")
    parser.add_argument(
        "compare",
        type=List[str] | str,
        help=f"The comparison attribute. Needs to be one of the following: {', '.join(get_args(TwitterAPI.LITERALS_COMPARE_USERS))}.",
    )
    parser.add_argument("--return-timestamp", type=bool, required=False, default=False, help="Return UTC timestamp of the request.")
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")
    # set optional encoding and ascii parameters
    parser.add_argument("--encoding", type=str, required=False, default="utf-8", help="File export encoding. Defaults to UTF-8.")
    parser.add_argument("--ensure-ascii", type=bool, required=False, default=False, help="Ensure ASCII encoding during file export.")

    args = parser.parse_args()
    # load secrets
    secrets = _read_secrets()

    api = TwitterAPI(**secrets)
    result = api.compare_users(users=args.users, compare=args.compare, return_timestamp=args.return_timestamp)
    # handle output
    _output(result, export_path=args.output, encoding=args.encoding, ensure_ascii=args.ensure_ascii)
    pass


def tweet_info_cli():
    """CLI function to the TwitterAPI().tweet_info function."""
    # define parser
    parser = argparse.ArgumentParser(prog="pysna", description="CLI function to request information from the specified Tweet.")
    # set first input argument
    parser.add_argument("tweet", type=str, help="The ID of the Tweet.")
    # set second input argument
    parser.add_argument(
        "attributes",
        type=List[str] | str,
        help=f"""Available Tweet information attributes. These must be from: {', '.join(get_args(TwitterAPI.LITERALS_TWEET_INFO))}.""",
    )
    # set third input param
    parser.add_argument("--return-timestamp", type=bool, required=False, default=False, help="Return UTC timestamp of the request.")
    # set fourth input argument (optional)
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")
    # set optional encoding and ascii parameters
    parser.add_argument("--encoding", type=str, required=False, default="utf-8", help="File export encoding. Defaults to UTF-8.")
    parser.add_argument("--ensure-ascii", type=bool, required=False, default=False, help="Ensure ASCII encoding during file export.")
    # parse args
    args = parser.parse_args()
    # load secrets
    secrets = _read_secrets()
    # create API obj
    api = TwitterAPI(**secrets)
    result = api.tweet_info(tweet=args.tweet, attributes=args.attributes, return_timestamp=args.return_timestamp)
    # handle output
    _output(result, export_path=args.output, encoding=args.encoding, ensure_ascii=args.ensure_ascii)
    pass


def compare_tweets_cli():
    """CLI function to the TwitterAPI().compare_tweets function."""

    # define parser
    parser = argparse.Argumentparser(prog="pysna", description="CLI function to compare multiple Tweets with the specified comparision attribute.")
    # add tweets argument
    parser.add_argument("tweets", type=List[str], nargs="+", default=[], help="The IDs of the Tweets.")
    # add compare argument
    parser.add_argument(
        "compare",
        type=List[str] | str,
        nargs=1,
        help=f"The comparison attribute. Needs to be one of the following: {', '.join(get_args(TwitterAPI.LITERALS_COMPARE_TWEETS))}.",
    )

    parser.add_argument("--return-timestamp", type=bool, required=False, default=False, help="Return UTC timestamp of the request.")
    # add optional output argument
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")
    # set optional encoding and ascii parameters
    parser.add_argument("--encoding", type=str, required=False, default="utf-8", help="File export encoding. Defaults to UTF-8.")
    parser.add_argument("--ensure-ascii", type=bool, required=False, default=False, help="Ensure ASCII encoding during file export.")
    # parse args
    args = parser.parse_args()
    # load secrets
    secrets = _read_secrets()
    # create API obj
    api = TwitterAPI(**secrets)
    result = api.compare_tweets(tweets=args.tweets, compare=args.compare, return_timestamp=args.return_timestamp)
    # handle output
    _output(result, export_path=args.output, encoding=args.encoding, ensure_ascii=args.ensure_ascii)
    pass


args = docopt(__doc__, version="pysna {}".format(version))


def main():
    if args["user-info"]:
        pysna.cli.user_info_cli()
    elif args["compare-users"]:
        pysna.cli.compare_users_cli(args)
    elif args["tweet-info"]:
        pysna.cli.compare_users_cli(args)
    elif args["compare-tweets"]:
        pysna.cli.compare_tweets_cli(args)
    elif args["load-secrets"]:
        pysna.cli.load_secrets(args)
    else:
        print("No argument found for {}".format(args[0]))
    pass


if __name__ == "__main__":
    main()


# TODO: rewrite to subparsers
"""
import argparse

def user_info(user, attributes):
    print("User:", user)
    print("Attributes:", attributes)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='pysna')
    sub_parsers = parser.add_subparsers()
    user_info_parser = sub_parsers.add_parser('user-info')
    user_info_parser.add_argument("user", type=str)
    user_info_parser.add_argument("attributes", type=str, nargs='+')
    user_info_parser.set_defaults(func=user_info)
    args = parser.parse_args()
    args.func(**vars(args))
"""
# ? using decorators?
"""
import argparse
from typing import Union, List
from datetime import datetime

parser = argparse.ArgumentParser(prog='pysna')

def cli_function(parser: argparse.ArgumentParser, function_name: str):
    def cli_function_decorator(func):
        sub_parser = parser.add_subparsers().add_parser(function_name)
        sub_parser.set_defaults(func=func)
        for arg in func.__annotations__:
            if arg == 'return_timestamp':
                sub_parser.add_argument('--' + arg, type=func.__annotations__[arg], default=False)
            else:
                sub_parser.add_argument(arg, type=func.__annotations__[arg])
        return func
    return cli_function_decorator

@cli_function(parser=parser, function_name='user-info')
def user_info(user: Union[str,int], attributes: List[str], return_timestamp: bool):
    print("User:", user)
    print("Attributes:", attributes)
    if return_timestamp:
        print("UTC Timestamp:", datetime.utcnow())

@cli_function(parser=parser, function_name='tweet-info')
def tweet_info(tweet_id: int, username: str):
    print("Tweet ID:", tweet_id)
    print("Username:", username)

@cli_function(parser=parser, function_name='load-secrets')
def load_secrets(env_path: str):
    '''CLI helper function to load secrets to environment variables.'''
    load_dotenv(env_path)
    print("secrets loaded from {}".format(env_path))

def main():
    args = parser.parse_args()
    args.func(**vars(args))


"""
# ? then inside the setup.py:
"""
entry_points={
        'console_scripts': [
            'pysna = cli:main',
        ],
"""
