# -*- coding: utf-8 -*-
"""
The command-line interface for the PySNA package
"""
import argparse
import json
import os
from typing import List

from .api import TwitterAPI
from .auth import TwitterAppAuthHandler


def user_info_cli():
    """CLI function of the TwitterAPI.user_info function"""
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
        help="""Available user information. Needs to be one of the following: 'id', 'id_str', 'name', 'screen_name', 'followers_info',
            'followees_info', 'location', 'profile_location', 'description', 'url', 'entities',
            'protected', 'followers_count', 'friends_count', 'listed_count', 'created_at',
            'favourites_count', 'utc_offset', 'time_zone', 'geo_enabled', 'verified', 'statuses_count',
            'lang', 'status', 'contributors_enabled', 'is_translator', 'is_translation_enabled', 'profile_background_color',
            'profile_background_image_url', 'profile_background_image_url_https', 'profile_background_tile', 'profile_image_url',
            'profile_image_url_https', 'profile_banner_url', 'profile_link_color', 'profile_sidebar_border_color',
            'profile_sidebar_fill_color', 'profile_text_color', 'profile_use_background_image', 'has_extended_profile',
            'default_profile', 'default_profile_image', 'following', 'follow_request_sent', 'notifications',
            'translator_type', 'withheld_in_countries'""",
    )
    # set fourth input argument (optional)
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")

    # parse args
    args = parser.parse_args()
    # catch environmental variables
    if not "TWITTER_CONSUMER_KEY" in os.environ:
        raise KeyError("TWITTER_CONSUMER_KEY must be provided in the environment variables.")
    elif not "TWITTER_CONSUMER_SECRET" in os.environ:
        raise KeyError("TWITTER_CONSUMER_SECRET must be provided in the environment variables.")

    # authorization from environment variables
    auth = TwitterAppAuthHandler(
        consumer_key=os.environ.get("TWITTER_CONSUMER_KEY"), consumer_secret=os.environ.get("TWITTER_CONSUMER_SECRET")
    )
    # establish connection to the API
    api = TwitterAPI(auth)
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
    """CLI function of the TwitterAPI.compare_users_list function"""
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
        help="The comparison attribute. Needs to be one of the following: 'num_followers', 'num_followees', 'common_followers', 'distinct_followers', 'common_followees', 'distinct_followees', 'created_at'",
    )
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")
    args = parser.parse_args()
    # catch environmental variables
    if not "TWITTER_CONSUMER_KEY" in os.environ:
        raise KeyError("TWITTER_CONSUMER_KEY must be provided in the environment variables.")
    elif not "TWITTER_CONSUMER_SECRET" in os.environ:
        raise KeyError("TWITTER_CONSUMER_SECRET must be provided in the environment variables.")

    auth = TwitterAppAuthHandler(
        consumer_key=os.environ.get("TWITTER_CONSUMER_KEY"), consumer_secret=os.environ.get("TWITTER_CONSUMER_SECRET")
    )
    api = TwitterAPI(auth)
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
    """CLI function to the TwitterAPI.compare_tweets function."""

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
        help="The comparison attribute. Needs to be one of the following: 'num_views', 'num_likes', 'num_retweets', 'num_quotes', 'common_quoting_users', 'distinct_quoting_users', 'common_liking_users', 'distinct_liking_users', 'common_retweeters', 'distinct_retweeters'",
    )
    # add optional output argument
    parser.add_argument("-o", "--output", type=str, required=False, help="Output file path. Include file name.")
    # parse args
    args = parser.parse_args()
    # catch environmental variables
    req_secrets = ["BEARER_TOKEN", "CONSUMER_KEY", "CONSUMER_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]
    for secret in req_secrets:
        if not f"TWITTER_{secret}" in os.environ:
            raise KeyError(f"TWITTER_{secret} must be provided in the environment variables.")
    # collect secrets
    secrets = {f"{secret}".lower(): os.getenv(f"TWITTER_{secret}") for secret in req_secrets}
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
