# -*- coding: utf-8 -*-
"""
The command-line interface for the PySNA package
"""
import argparse
import json
import os
from typing import List, get_args

from dotenv import load_dotenv

from .api import TwitterAPI

REQUIRED_SECRETS = ["BEARER_TOKEN", "CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]


def user_info_cli():
    """CLI function of the TwitterAPI().user_info function"""
    # define parser
    parser = argparse.ArgumentParser(
        prog="pysna", description="CLI function to request information from the specified Twitter user."
    )
    # set first input param
    parser.add_argument("user", type=str, required=True, help="The ID or screen name of the Twitter user.")
    # set second input param
    parser.add_argument(
        "attributes",
        type=List[str],
        required=True,
        help=f"""Available user information attributes. These must be from: {', '.join(get_args(TwitterAPI.LITERALS_USER_INFO))}.""",
    )
    # set fourth input argument (optional)
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")
    # set optional argument in order to read secrets from .env file
    parser.add_argument("-e", "--env", type=str, required=False, help="Path to an .env file including the secrets.")

    # parse args
    args = parser.parse_args()
    # if path to .env file was provided
    if args.env is not None:
        load_dotenv(args.env)
    # catch environmental variables
    for secret in REQUIRED_SECRETS:
        if not str(secret) in os.environ:
            raise KeyError(f"{secret} must be provided in the environment variables or .env file.")
    # collect secrets
    secrets = {str(secret).lower(): os.getenv(str(secret)) for secret in REQUIRED_SECRETS}

    # establish connection to the API
    api = TwitterAPI(**secrets)
    # get results
    result = api.user_info(user=args.user, attributes=args.attributes)
    # either print results if '--output' arg was provided
    if args.output is not None:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=4)
    # or print them to the CLI
    else:
        print(result)
    pass


def compare_users_cli():
    """CLI function of the TwitterAPI().compare_users_list function"""
    # define parser
    parser = argparse.ArgumentParser(
        prog="pysna",
        description="CLI function to compare multiple Twitter users with the specified comparision attribute.",
    )
    parser.add_argument(
        "users", type=List[str], nargs="+", required=True, default=[], help="The IDs or screen names of the users."
    )
    parser.add_argument(
        "compare",
        type=str,
        required=True,
        help=f"The comparison attribute. Needs to be one of the following: {', '.join(get_args(TwitterAPI.LITERALS_COMPARE_USERS))}.",
    )
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")
    # set optional argument in order to read secrets from .env file
    parser.add_argument("-e", "--env", type=str, required=False, help="Path to an .env file including the secrets.")

    args = parser.parse_args()
    # if path to .env file was provided
    if args.env is not None:
        load_dotenv(args.env)
    # catch environmental variables
    for secret in REQUIRED_SECRETS:
        if not str(secret) in os.environ:
            raise KeyError(f"{secret} must be provided in the environment variables or .env file.")
    # collect secrets
    secrets = {str(secret).lower(): os.getenv(str(secret)) for secret in REQUIRED_SECRETS}

    api = TwitterAPI(**secrets)
    result = api.compare_users_list(users=args.users, compare=args.compare)
    # either print results if '--output' arg was provided
    if args.output is not None:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=4)
    # or print them to the CLI
    else:
        print(result)
    pass


def compare_tweets_cli():
    """CLI function to the TwitterAPI().compare_tweets function."""

    # define parser
    parser = argparse.Argumentparser(
        prog="pysna", description="CLI function to compare multiple Tweets with the specified comparision attribute."
    )
    # add tweets argument
    parser.add_argument("tweets", type=List[str], required=True, nargs="+", default=[], help="The IDs of the Tweets.")
    # add compare argument
    parser.add_argument(
        "compare",
        type=str,
        required=True,
        nargs=1,
        help=f"The comparison attribute. Needs to be one of the following: {', '.join(get_args(TwitterAPI.LITERALS_COMPARE_TWEETS))}.",
    )
    # add optional output argument
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")
    # parse args
    args = parser.parse_args()
    # catch environmental variables
    for secret in REQUIRED_SECRETS:
        if not str(secret) in os.environ:
            raise KeyError(f"{secret} must be provided in the environment variables or .env file.")
    # collect secrets
    secrets = {str(secret).lower(): os.getenv(str(secret)) for secret in REQUIRED_SECRETS}
    # create API obj
    api = TwitterAPI(**secrets)
    result = api.compare_tweets(tweets=args.tweets, compare=args.compare)
    # either print results if '--output' arg was provided
    if args.output is not None:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=4)
    # or print them to the CLI
    else:
        print(result)
    pass


if __name__ == "__main__":
    compare_users_cli()
    user_info_cli()
    compare_tweets_cli()
