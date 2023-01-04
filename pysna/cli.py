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
        description="CLI function to request information from the specified Twitter user."
    )
    # set first input param
    parser.add_argument(
        "user",
        type=str,
        required=True,
        help="The ID or screen name of the Twitter user."
    )
    # set second input param
    parser.add_argument(
        "attributes",
        type=List[str],
        required=True,
        help="""Available user information. Needs to be one of the following: 'id', 'id_str', 'name', 'screen_name', 'followers_info',
            'follows_info', 'location', 'profile_location', 'description', 'url', 'entities',
            'protected', 'followers_count', 'friends_count', 'listed_count', 'created_at',
            'favourites_count', 'utc_offset', 'time_zone', 'geo_enabled', 'verified', 'statuses_count',
            'lang', 'status', 'contributors_enabled', 'is_translator', 'is_translation_enabled', 'profile_background_color',
            'profile_background_image_url', 'profile_background_image_url_https', 'profile_background_tile', 'profile_image_url',
            'profile_image_url_https', 'profile_banner_url', 'profile_link_color', 'profile_sidebar_border_color',
            'profile_sidebar_fill_color', 'profile_text_color', 'profile_use_background_image', 'has_extended_profile',
            'default_profile', 'default_profile_image', 'following', 'follow_request_sent', 'notifications',
            'translator_type', 'withheld_in_countries'"""
    )
    # set fourth input argument (optional)
    parser.add_argument("--output", "-o", type=str, required=False, help="Output file path. Include file name.")
    
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

def compare_users_cli():
    """CLI function of the TwitterAPI.compare_users function"""
    # define parser
    parser = argparse.ArgumentParser(
        description="CLI function to compare two Twitter users with the specified comparison attribute."
    )
    # set first input param
    parser.add_argument("user1", type=str, required=True, help="The ID or screen name of the first user.")
    # set second input param
    parser.add_argument("user2", type=str, required=True, help="The ID or screen name of the second user.")
    # set third input param
    parser.add_argument(
        "compare",
        type=str,
        required=True,
        help="The comparison attribute. Needs to be one of the following: 'num_followers', 'num_follows', 'common_followers', 'unique_followers', 'common_follows', 'unique_follows', 'created_at'",
    )
    # set fourth input argument (optional)
    parser.add_argument("--output", "-o", type=str, required=False, help="Output file path. Include file name.")
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
    result = api.compare_users(user1=args.user1, user2=args.user2, compare=args.compare)
    # either print results if '--output' arg was provided
    if args.output is not None:
        with open(args.output, "w") as f:
            json.dump(result, f, indent=4)
    # or print them to the CLI
    else:
        print(result)


if __name__ == "__main__":
    compare_users_cli()
    user_info_cli()
