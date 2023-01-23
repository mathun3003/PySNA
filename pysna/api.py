# -*- coding: utf-8 -*-
import logging
import operator
import sys
from datetime import datetime, timezone
from numbers import Number
from typing import Any, Dict, List, Literal, Set

import numpy as np
import requests
import tweepy

from pysna.utils import strf_datetime

# create logger instance
log = logging.getLogger(__name__)
# log to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class TwitterAPI(tweepy.Client):
    """Twitter API class in order to interact with the Twitter Search API v2."""

    LITERALS_USER_INFO = Literal[
        "id",
        "id_str",
        "name",
        "screen_name",
        "followers",
        "followees",
        "location",
        "profile_location",
        "description",
        "url",
        "entities",
        "protected",
        "followers_count",
        "friends_count",
        "listed_count",
        "created_at",
        "liked_tweets",
        "composed_tweets",
        "favourites_count",
        "utc_offset",
        "time_zone",
        "geo_enabled",
        "verified",
        "statuses_count",
        "lang",
        "status",
        "contributors_enabled",
        "is_translator",
        "is_translation_enabled",
        "profile_background_color",
        "profile_background_image_url",
        "profile_background_image_url_https",
        "profile_background_tile",
        "profile_image_url",
        "profile_image_url_https",
        "profile_banner_url",
        "profile_link_color",
        "profile_sidebar_border_color",
        "profile_sidebar_fill_color",
        "profile_text_color",
        "profile_use_background_image",
        "has_extended_profile",
        "default_profile",
        "default_profile_image",
        "following",
        "follow_request_sent",
        "notifications",
        "translator_type",
        "withheld_in_countries",
    ]

    LITERALS_TWEET_INFO = Literal[
        "id",
        "id_str",
        "text",
        "truncated",
        "created_at",
        "entities",
        "source",
        "author_info",
        "retweeters",
        "in_reply_to_status_id",
        "in_reply_to_status_id_str",
        "in_reply_to_user_id",
        "in_reply_to_user_id_str",
        "in_reply_to_screen_name",
        "user",
        "geo",
        "coordinates",
        "place",
        "contributors",
        "is_quote_status",
        "view_count",
        "retweet_count",
        "favorite_count",
        "quote_count",
        "reply_count",
        "quoting_users",
        "favorited",
        "retweeted",
        "possibly_sensitive",
        "possibly_sensitive_appealable",
        "lang",
    ]

    LITERALS_COMPARE_USERS = Literal[
        "relationship",
        "followers_count",
        "followees_count",
        "tweets_count",
        "favourites_count",
        "common_followers",
        "distinct_followers",
        "common_followees",
        "distinct_followees",
        "similarity",
        "created_at",
        "protected",
        "verified",
    ]

    LITERALS_COMPARE_TWEETS = Literal["view_count", "like_count", "retweet_count", "quote_count", "common_quoting_users", "distinct_quoting_users", "common_liking_users", "distinct_liking_users", "common_retweeters", "distinct_retweets"]

    def __init__(self, bearer_token: Any | None = None, consumer_key: Any | None = None, consumer_secret: Any | None = None, access_token: Any | None = None, access_token_secret: Any | None = None, wait_on_rate_limit: bool = True):
        # inherit from tweepy.Client __init__
        super(self.__class__, self).__init__(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, wait_on_rate_limit=wait_on_rate_limit)
        # create a tweepy.AppAuthHandler instance
        _auth = tweepy.AppAuthHandler(consumer_key=consumer_key, consumer_secret=consumer_secret)
        # create a tweepy.API instance
        self._api = tweepy.API(_auth, wait_on_rate_limit=wait_on_rate_limit)
        # create a tweepy.Client instance from parent class
        self._client = super(self.__class__, self)
        # store bearer token for manual request
        self._bearer_token = bearer_token

    def _manual_request(self, url: str, additional_fields: Dict[str, List[str]] | None = None) -> dict:
        """Perform a manual GET request to the Twitter API.

        Args:
            url (str): API URL (without specified fields)
            additional_fields (Dict[str, List[str]] | None, optional): Fields can be specified (e.g., tweet.fields) according to the official API reference. Defaults to None.

        Raises:
            Exception: If status code != 200.

        Returns:
            dict: JSON formatted response of API request.

        Reference: https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets-id
        """
        # if additional_fields were provided
        if additional_fields:
            # init empty string
            fields = "?"
            # create fields string dynamically for every field in additional_fields
            for field in additional_fields.keys():
                # e.g., in format "tweet.fields=lang,author_id"
                fields += f"{field}={','.join(additional_fields[field])}&"
            # append fields to url
            url += fields[:-1]
        # set header
        header = {"Authorization": f"Bearer {self._bearer_token}"}
        response = requests.get(url, headers=header)
        if response.status_code != 200:
            raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))
        return response.json()

    def _get_user_object(self, user: str | int) -> tweepy.User:
        """Request Twitter User Object via tweepy

        Args:
            user (str): Either User ID or screen name

        Returns:
            tweepy.User: Twitter User object from tweepy
        """
        # check if string for user1 is convertible to int in order to check for user ID or screen name
        if (user.isdigit()) or (isinstance(user, int)):
            # get profile for user by user ID
            user_obj = self._api.get_user(user_id=user)
        else:
            # get profile for user by screen name
            user_obj = self._api.get_user(screen_name=user)
        return user_obj

    def _get_user_followers(self, user: str | int) -> Set[int]:
        """Request Twitter follower IDs from user

        Args:
            user (str): Either User ID or screen name

        Returns:
            Set[int]: Array containing follower IDs
        """
        # init empty list to store user followers
        user_followers = list()
        # check if string for user1 is convertible to int in order to check for user ID or screen name
        if (user.isdigit()) or (isinstance(user, int)):
            # get all follower IDs by paginating using the user ID
            for page in tweepy.Cursor(self._api.get_follower_ids, user_id=user).pages():
                user_followers.extend(page)
        else:
            # get all follower IDs by paginating using the screen name
            for page in tweepy.Cursor(self._api.get_follower_ids, screen_name=user).pages():
                user_followers.extend(page)
        return set(user_followers)

    def _get_user_followees(self, user: str | int) -> Set[int]:
        """Request Twitter follow IDs from user

        Args:
            user (str): Either User ID or screen name

        Returns:
            Set[int]: Array containing follow IDs
        """
        user_followees = list()
        if (user.isdigit()) or (isinstance(user, int)):
            # get all followee IDs by paginating using the user ID
            for page in tweepy.Cursor(self._api.get_friend_ids, user_id=user).pages():
                user_followees.extend(page)
        else:
            # get all followee IDs by paginating using the screen name
            for page in tweepy.Cursor(self._api.get_friend_ids, screen_name=user).pages():
                user_followees.extend(page)
        return set(user_followees)

    def _get_relationship(self, user1: str | int, user2: str | int) -> dict:
        """Get relationship between two users.

        Args:
            user1 (str | int): Source user ID or screen name.
            user2 (str | int): Target user ID or screen name.

        Returns:
            dict: Unpacked tuple of JSON from tweepy Friendship model.

        Reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show#example-response
        """
        # if both strings are digits or integers
        if ((user1.isdigit()) and (user2.isdigit())) or ((isinstance(user1, int)) and (isinstance(user2, int))):
            relationship = self._api.get_friendship(source_id=user1, target_id=user2)
        # if user1 string is a digit or an integer, and user2 is a screen name
        elif ((user1.isdigit()) and (not user2.isdigit())) or ((isinstance(user1, int)) and (isinstance(user2, str))):
            relationship = self._api.get_friendship(source_id=user1, target_screen_name=user2)
        # if user1 is a screen name, and user2 is a digit or an integer
        elif ((not user1.isdigit()) and (user2.isdigit())) or ((isinstance(user1, str)) and (isinstance(user2, int))):
            relationship = self._api.get_friendship(source_screen_name=user1, target_id=user2)
        # if both strings are screen names
        else:
            relationship = self._api.get_friendship(source_screen_name=user1, target_screen_name=user2)
        return {"source": relationship[0]._json, "target": relationship[1]._json}

    def _get_tweet_object(self, tweet: str | int) -> tweepy.models.Status:
        """Request Twitter Tweet Object via tweepy

        Args:
            tweet (int | str): Tweet ID

        Returns:
            tweepy.models.Status: tweepy Status Model

        Reference: https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet
        """
        tweet_obj = self._api.get_status(tweet, include_entities=True)
        return tweet_obj

    def _calc_descriptive_metrics(self, data: Dict[str | int, Number], iterable: List[str | int]) -> dict:
        """Calculates the mean, median, and standard deviation of a given data set.

        Args:
            data (Dict[str  |  int, Number]): Data dictionary containing numeric values.
            iterable (List[str  |  int]): Iterables of the data dictionary, i.e., the desired keys.

        Returns:
            dict: Input data dictionary containing descriptive metrics.

        Metrics:
            - Max Value
            - Min Value
            - Mean Value
            - Median
            - Standard Deviation
            - Sample Variance
            - Range (Max - Min)
            - Interquartiles Range
            - Mean Absolute Deviation
        """
        # extract numeric values by iterating over data dict with iterable items
        numerics = [data[item] for item in iterable]
        data["metrics"] = dict()
        # calc max
        data["metrics"]["max"] = max(numerics)
        # calc min
        data["metrics"]["min"] = min(numerics)
        # calc mean
        data["metrics"]["mean"] = np.array(numerics).mean()
        # calc median
        data["metrics"]["median"] = np.median(numerics)
        # calc standard deviation
        data["metrics"]["std"] = np.std(numerics)
        # calc variance
        data["metrics"]["var"] = np.var(numerics)
        # calc range
        data["metrics"]["range"] = max(numerics) - min(numerics)
        # calc interquarile range
        data["metrics"]["IQR"] = np.subtract(*np.percentile(numerics, [75, 25]))
        # calc absolute mean deviation
        data["metrics"]["mad"] = np.mean(np.absolute(numerics - np.mean(numerics)))
        return data

    def _calc_datetime_metrics(self, data: Dict[str, datetime]) -> dict():
        # use the datetime's timestamp to make them comparable
        timestamps = [dt.timestamp() for dt in data.values()]
        # calc mean of creation dates
        total_time = sum(timestamps)
        mean_timestamp = total_time / len(timestamps)
        # convert mean timestamp back to datetime object with timezone information
        mean_datetime = datetime.fromtimestamp(mean_timestamp, tz=timezone.utc)

        # calculate time differences to mean datetime of every creation date
        time_diffs_mean = {user: {"days": (dt - mean_datetime).days, "seconds": (dt - mean_datetime).seconds} for user, dt in data.items()}

        # find the median of the timestamps
        median_timestamp = np.median(timestamps)
        # Convert median timestamp back to datetime object
        median_datetime = datetime.fromtimestamp(median_timestamp, tz=timezone.utc)

        # calculate time differences to median timestamp of every creation date
        time_diffs_median = {user: {"days": (dt - median_datetime).days, "seconds": (dt - median_datetime).seconds} for user, dt in data.items()}

        # calc range of creation dates
        max_date, min_date = max(data.values()), min(data.values())
        time_span = max_date - min_date

        # convert creation dates to isoformat for readability
        data = {u: dt.isoformat() for u, dt in data.items()}

        # add metrics to output
        data["metrics"] = dict()
        data["metrics"]["deviation_from_mean"] = time_diffs_mean
        data["metrics"]["deviation_from_median"] = time_diffs_median
        data["metrics"]["time_span"] = {"days": time_span.days, "seconds": time_span.seconds, "microseconds": time_span.microseconds}
        data["metrics"]["mean"] = mean_datetime.isoformat()
        data["metrics"]["median"] = median_datetime.isoformat()
        data["metrics"]["max"] = max_date.isoformat()
        data["metrics"]["min"] = min_date.isoformat()
        return data

    def get_all_liking_users(self, tweet: str | int) -> Set[int]:
        """Get all liking users of provided Tweet by pagination.

        Args:
            tweet (str | int): Tweet ID.

        Returns:
            Set[int]: User IDs as set.
        """
        # init emtpy set to store all liking users
        liking_users = set()
        # set request params
        params = {"id": tweet, "max_results": 100, "pagination_token": None}

        while True:
            # get 100 liking users per request
            response = self._client.get_liking_users(**params)
            # if response contains any data
            if response.data is not None:
                # add each liking user to set
                for user in response.data:
                    liking_users.add(user.id)
                # if last page was reached, break
                if not response.meta["next_token"]:
                    break
                # else paginate
                else:
                    params["pagination_token"] = response.meta["next_token"]
            # if no results exist, break
            else:
                break
        return liking_users

    def get_all_retweeters(self, tweet: str | int) -> Set[int]:
        """Get all retweeting users of provided Tweet by pagination.

        Args:
            tweet (str | int): Tweet ID.

        Returns:
            Set[int]: IDs of retweeting users.
        """
        # init empty set to store all retweeters
        retweeters = set()
        # set request params
        params = {"id": tweet, "max_results": 100, "pagination_token": None}

        while True:
            # get 100 retweeters per request
            response = self._client.get_retweeters(**params)
            # if response contains any data
            if response.data is not None:
                # add each retweeter to set
                for user in response.data:
                    retweeters.add(user.id)
                # if last page was reached, break
                if not response.meta["next_token"]:
                    break
                # else paginate
                else:
                    params["pagination_token"] = response.meta["next_token"]
            # if no results exist, break
            else:
                break
        return retweeters

    def get_all_quoting_users(self, tweet: str | int) -> Set[int]:
        """Get all quoting users of provided Tweet by pagination.

        Args:
            tweet (str | int): Tweet ID.

        Returns:
            Set[int]: IDs of quoting users.
        """
        # init empty set to store all quoting users
        quoting_users = set()
        # set request params
        params = {"id": tweet, "max_results": 100, "pagination_token": None}

        while True:
            response = self._client.get_quote_tweets(**params, expansions="author_id")
            # if response contains any data
            if "users" in response.includes:
                # add each quoting user to set
                for user in response.includes["users"]:
                    quoting_users.add(user.id)
                # if last page was reached, break
                if "next_token" not in response.meta:
                    break
                # else paginate
                else:
                    params["pagination_token"] = response.meta["next_token"]
            # if response does not contain any data, break
            else:
                break
        return quoting_users

    def get_all_liked_tweets(self, user: str | int) -> Set[int]:
        """Get all liked Tweets of provided user.

        Args:
            user (str | int): User ID or screen name.

        Returns:
            Set[int]: Tweet IDs of liked Tweets.
        """
        # init empty set to store all liked Tweets
        liked_tweets = set()
        # set request params
        params = {"id": user, "max_results": 100, "pagination_token": None}

        while True:
            response = self._client.get_liked_tweets(**params)
            # if response contains any data
            if response.data is not None:
                # add each Tweet Id to set
                for tweet in response.data:
                    liked_tweets.add(tweet.id)
                # if last page was reached, break
                if "next_token" not in response.meta:
                    break
                # else paginate
                else:
                    params["pagination_token"] = response.meta["next_token"]
            # if response does not contain any data, break
            else:
                break
        return liked_tweets

    def get_all_composed_tweets(self, user: str | int, **kwargs) -> Set[int]:
        """Get all composed Tweets of provided user by pagination.

        Args:
            user (str | int): User ID or screen name.

        Returns:
            Set[int]: IDs of composed Tweets.
        """
        # init empty set to store all composed Tweets
        composed_tweets = set()
        # set request params
        params = {"id": user, "max_results": 100, "pagination_token": None}

        while True:
            response = self._client.get_users_tweets(**params, **kwargs)
            # if response contains any data
            if response.data is not None:
                # add each Tweet Id to set
                for tweet in response.data:
                    composed_tweets.add(tweet.id)
                # if last page was reached, break
                if "next_token" not in response.meta:
                    break
                # else paginate
                else:
                    params["pagination_token"] = response.meta["next_token"]
            # if response does not contain any data, break
            else:
                break
        return composed_tweets

    def user_info(self, user: str | int, attributes: List[LITERALS_USER_INFO] | str, return_timestamp: bool = False) -> dict:
        """Receive requested user information from Twitter User Object.

        Args:
            user (str): Twitter User either specified by corresponding ID or screen name.
            attributes (List[str]): Attributes of the User object. These must be from id, id_str, name, screen_name, utc_timestamp, followers, followees, location, profile_location, description, url, entities, protected, followers_count, friends_count, listed_count, created_at, liked_tweets, composed_tweets, favourites_count, utc_offset, time_zone, geo_enabled, verified, statuses_count, lang, status, contributors_enabled, is_translator, is_translation_enabled, profile_background_color, profile_background_image_url, profile_background_image_url_https, profile_background_tile, profile_image_url, profile_image_url_https, profile_banner_url, profile_link_color, profile_sidebar_border_color, profile_sidebar_fill_color, profile_text_color, profile_use_background_image, has_extended_profile, default_profile, default_profile_image, following, follow_request_sent, notifications, translator_type, withheld_in_countries.

        Raises:
            KeyError: If invalid attribute was provided.

        Returns:
            dict: Requested user information.
        """
        try:
            # get user object via tweepy
            user_obj = self._get_user_object(user)
        except tweepy.errors.Forbidden as e:
            # log to stdout
            log.error("403 Forbidden: access refused or access is not allowed.")
            # if user ID was provided
            if user.isdigit() or isinstance(user, int):
                url = f"https://api.twitter.com/2/users/{user}"
            else:
                # if screen name was provided
                url = f"https://api.twitter.com/2/users/by/username/{user}"
            response = self._manual_request(url)
            # if an error occured that says the user has been suspended
            if any("User has been suspended" in error["detail"] for error in response["errors"]):
                log.error("User has been suspended from Twitter.")
                if return_timestamp:
                    return {"suspended": True, "utc_timestamp": strf_datetime(datetime.utcnow(), format="%Y-%m-%d %H:%M:%S.%f")}
                else:
                    return {"suspended": True}
            else:
                raise e

        # initialize empty dict to store requested attributes
        user_info = dict()

        # if single string was provided
        if isinstance(attributes, str):
            # convert to list for iteration
            attributes = [attributes]

        # loop through the list of attributes and add them to the dictionary
        for attr in attributes:
            if attr in user_obj._json.keys():
                user_info[attr] = user_obj._json[attr]
            # get follower information
            elif attr == "followers":
                # define dict to store follower information
                user_info[attr] = {"follower_ids": list(), "follower_names": list(), "follower_screen_names": list()}
                # get follower IDs
                user_info[attr]["follower_ids"] = user_obj.follower_ids()
                # get follower names and screen names
                for follower in user_obj.followers():
                    user_info[attr]["follower_names"].append(follower.name)
                    user_info[attr]["follower_screen_names"].append(follower.screen_name)
            # get followees information
            elif attr == "followees":
                # define dict to store followees information
                user_info[attr] = {"followees_ids": list(), "followees_names": list(), "followees_screen_names": list()}
                # get followees ID, names, and screen names
                for friend in user_obj.friends():
                    user_info[attr]["followees_ids"].append(friend.id)
                    user_info[attr]["followees_names"].append(friend.name)
                    user_info[attr]["followees_screen_names"].append(friend.screen_name)
            # get all liked Tweets
            elif attr == "liked_tweets":
                # user ID needs to be provided. Thus, check for ID
                if user.isdigit() is False:
                    # if provided string was a screen name, get User ID first
                    user_id = user_obj.id
                # if user ID as int or str was provided, continue
                else:
                    user_id = user
                # request all liked Tweets
                liked_tweets = self.get_all_liked_tweets(user_id)
                user_info[attr] = liked_tweets
            # get all composed Tweets
            elif attr == "composed_tweets":
                # user ID needs to be provided. Thus, check for ID
                if user.isdigit() is False:
                    # if provided string was a screen name, get User ID first
                    user_id = user_obj.id
                # if user ID as int or str was provided, continue
                else:
                    user_id = user
                # request all composed Tweets
                composed_tweets = self.get_all_composed_tweets(user_id)
                user_info[attr] = composed_tweets
            # if invalid attribute was provided
            else:
                raise ValueError("Invalid attribute for '{}'".format(attr))
        # if timestamp should be returned
        if return_timestamp:
            user_info["utc_timestamp"] = strf_datetime(datetime.utcnow(), format="%Y-%m-%d %H:%M:%S.%f")
        return user_info

    def compare_users(self, users: List[str | int], compare: str | List[LITERALS_COMPARE_USERS], return_timestamp: bool = False, features: List[str] | None = None) -> dict | list:
        """Compare two or more users with the specified comparison attribute.

        Args:
            users (List[str  |  int]): User IDs or screen names
            compare (str): Comparison attribute. Must be one of relationship, followers_count, followees_count, tweets_count, favourites_count, common_followers, distinct_followers, common_followees, distinct_followees, similarity, created_at, protected, verified.
            return_timestamp (bool, optional): Add UTC Timestamp to results. Defaults to False.
            features (List[str] | None, optional): Defined features of Twitter User Object on which similarity will be computed. Defaults to None.

        Raises:
            ValueError: If invalid comparison attribute was provided.

        Returns:
            dict | list: Requested comparison attribute. Provide screen names
            to display them in the results.
        """

        # users list must contain at least two elements
        assert len(users) > 1, "'users' list must contain at least two elements, {} was provided".format(len(users))

        # if single comparison attribute was provided as string
        if isinstance(compare, str):
            # change to list object
            compare = [compare]
        # init empty dict to store results
        results = dict()
        # iterate over comparison attributes
        for attr in compare:
            # match comparison attributes
            match attr:
                # compare relationships between two users
                case "relationship":
                    # init emtpy relationships dict
                    relationships = dict()
                    # iterate over every pair combination of provided users
                    for user in users:
                        for other_user in users:
                            if user != other_user:
                                relationships[(user, other_user)] = self._get_relationship(user, other_user)
                    results[attr] = relationships
                # compare number of follwoers
                case "followers_count":
                    followers = {user: self._get_user_object(user).followers_count for user in users}
                    # calc descriptive metrics
                    followers = self._calc_descriptive_metrics(followers, users)
                    results[attr] = followers
                # compare number of friends
                case "followees_count":
                    followees = {user: self._get_user_object(user).friends_count for user in users}
                    # calc descriptive metrics
                    followees = self._calc_descriptive_metrics(followees, users)
                    results[attr] = followees
                # compare number of Tweets issued by each user
                case "tweets_count":
                    tweets = {user: self._get_user_object(user).statuses_count for user in users}
                    # calc descriptive metrics
                    tweets = self._calc_descriptive_metrics(tweets, users)
                    results[attr] = tweets
                # compare number of likes issued by each user
                case "favourites_count":
                    favourites = {user: self._get_user_object(user).favourites_count for user in users}
                    # calc descriptive metrics
                    favourites = self._calc_descriptive_metrics(favourites, users)
                    results[attr] = favourites
                # compare protected attribute of users
                case "protected":
                    results[attr] = {user: self._get_user_object(user).protected for user in users}
                # compare verified attribute for users
                case "verified":
                    results[attr] = {user: self._get_user_object(user).verified for user in users}
                # compare common followers
                case "common_followers":
                    individual_followers = [self._get_user_followers(user) for user in users]
                    common_followers = set.intersection(*map(set, individual_followers))
                    results[attr] = list(common_followers)
                # compare distinct followers
                case "distinct_followers":
                    individual_followers = {user: self._get_user_followers(user) for user in users}
                    distinct_followers = dict()
                    for user, followers in individual_followers.items():
                        distinct_followers[user] = list(set(followers))
                        for other_user, other_followers in individual_followers.items():
                            if user != other_user:
                                distinct_followers[user] = list(set(distinct_followers[user]) - set(other_followers))
                    results[attr] = distinct_followers
                # compare common followees
                case "common_followees":
                    individual_followees = [self._get_user_followees(user) for user in users]
                    common_followees = set.intersection(*map(set, individual_followees))
                    results[attr] = list(common_followees)
                # compare distinct followees
                case "distinct_followees":
                    individual_followees = {user: self._get_user_followees(user) for user in users}
                    distinct_followees = dict()
                    for user, followees in individual_followees.items():
                        distinct_followees[user] = list(set(followees))
                        for other_user, other_followees in individual_followees.items():
                            if user != other_user:
                                distinct_followees[user] = list(set(distinct_followees[user]) - set(other_followees))
                    results[attr] = distinct_followees
                # compute similarity between two users basd on the followers
                case "similarity":
                    # feature list object must be defined
                    if features is None:
                        raise ValueError("'features' list must be provided.")
                    # features needs at least two elements
                    assert len(features) > 1, "'features' list must have at least two elements. {} was given".format(len(features))

                    # init empty dict to store distances
                    distances = dict()
                    # iterate over every uniqe pair
                    for i in range(len(users)):
                        for j in range(i + 1, len(users)):
                            # get user objects for each pair
                            user_i = self._get_user_object(users[i])._json
                            user_j = self._get_user_object(users[j])._json
                            # build feature vector
                            vec_i = np.array([user_i[feature] for feature in features])
                            vec_j = np.array([user_j[feature] for feature in features])
                            # feature vectors have to contain numeric values
                            assert all(isinstance(feat, Number) for feat in vec_i), "only numeric features are allowed"
                            assert all(isinstance(feat, Number) for feat in vec_j), "only numeric features are allowed"
                            # calc euclidean distance
                            distances[(users[i], users[j])] = np.linalg.norm(vec_i - vec_j, ord=2)
                    # sort dict in ascendin order
                    sorted_values = dict(sorted(distances.items(), key=operator.itemgetter(1)))
                    results[attr] = sorted_values
                # compare creation dates
                case "created_at":
                    # TODO: Sign off by the supervisor
                    # create dict of users and their respective creation dates
                    creation_dates = {user: self._get_user_object(user).created_at for user in users}
                    # calc datetime metrics
                    creation_dates = self._calc_datetime_metrics(creation_dates)
                    results[attr] = creation_dates
                # if other comparison attribute was provided
                case _:
                    raise ValueError("Invalid comparison attribute for '{}'".format(attr))
        # if timestamp should be returned
        if return_timestamp:
            results["utc_timestamp"] = strf_datetime(datetime.utcnow(), format="%Y-%m-%d %H:%M:%S.%f")
        return results

    def tweet_info(self, tweet_id: str | int, attributes: List[LITERALS_TWEET_INFO] | str, return_timestamp: bool = False) -> dict:
        """Receive requested Tweet information from Tweet Object.

        Args:
            tweet_id (str | int): Tweet ID
            attributes (List[LITERALS_TWEET_INFO] | str): Attributes of the Tweet object. These must be from id, id_str, text, truncated, created_at, entities, source, utc_timestamp, author_info, retweeters, in_reply_to_status_id, in_reply_to_status_id_str, in_reply_to_user_id, in_reply_to_user_id_str, in_reply_to_screen_name, user, geo, coordinates, place, contributors, is_quote_status, view_count, retweet_count, favorite_count, quote_count, reply_count, quoting_users, favorited, retweeted, possibly_sensitive, possibly_sensitive_appealable, lang.

        Raises:
            ValueError: If invalid attribute was provided.

        Returns:
            dict: Requested Tweet information.
        """

        try:
            # get tweet object
            tweet_obj = self._get_tweet_object(tweet_id)
        except tweepy.errors.NotFound as e:
            # log to stdout
            log.error("No Tweet found with that ID.")
            # request the Tweet via manual request
            response = self._manual_request(f"https://api.twitter.com/2/tweets/{tweet_id}")
            # if an error saying that no such Tweet was found
            if any(error["title"] == "Not Found Error" for error in response["errors"]):
                return {"available": False}
            else:
                raise e

        # initialize empty dict to store request information
        tweet_info = dict()

        # if single string was provided
        if isinstance(attributes, str):
            # convert to list for iteration
            attributes = [attributes]

        for attr in attributes:
            # get default attributes from tweepy Status model
            if attr in tweet_obj._json.keys():
                tweet_info[attr] = tweet_obj._json[attr]
            # get information about author
            elif attr == "author_info":
                author_info = dict()
                for field in tweet_obj.user._json.keys():
                    author_info[field] = tweet_obj.user._json[field]
                tweet_info[attr] = author_info
            # get all quoting users
            elif attr == "quoting_users":
                quoting_users = self.get_all_quoting_users(tweet_id)
                tweet_info[attr] = list(quoting_users)
            # get all retweeters
            elif attr == "retweeters":
                retweeters = self.get_all_retweeters(tweet_id)
                tweet_info[attr] = list(retweeters)
            # get the number of views
            elif attr == "view_count":
                # go via manual request and public metrics
                url = f"https://api.twitter.com/2/tweets/{tweet_id}"
                response_json = self._manual_request(url, {"tweet.fields": ["public_metrics"]})
                public_metrics = response_json["data"]["public_metrics"]
                tweet_info[attr] = public_metrics["impression_count"]
            # get the number of likes
            elif attr == "quote_count":
                # go via manual request and public metrics
                url = f"https://api.twitter.com/2/tweets/{tweet_id}"
                response_json = self._manual_request(url, {"tweet.fields": ["public_metrics"]})
                public_metrics = response_json["data"]["public_metrics"]
                tweet_info[attr] = public_metrics["quote_count"]
            # get the number of replies
            elif attr == "reply_count":
                # go via manual request and public metrics
                url = f"https://api.twitter.com/2/tweets/{tweet_id}"
                response_json = self._manual_request(url, {"tweet.fields": ["public_metrics"]})
                public_metrics = response_json["data"]["public_metrics"]
                tweet_info[attr] = public_metrics["reply_count"]
            # if invalid attribute was provided
            else:
                raise ValueError("Invalid attribute for '{}'".format(attr))
        # if timestamp should be returned
        if return_timestamp:
            tweet_info["utc_timestamp"] = strf_datetime(datetime.utcnow(), format="%Y-%m-%d %H:%M:%S.%f")
        return tweet_info

    def compare_tweets(self, tweets: List[str | int], compare: str | List[LITERALS_COMPARE_TWEETS], return_timestamp: bool = False, features: List[str] | None = None) -> dict:
        """Compare two or more Tweets with the specified comparison attribute.

        Args:
            tweets (List[str  |  int]): List of Tweet IDs.
            compare (str | List[LITERALS_COMPARE_TWEETS]): Comparison attribute. Needs to be one of the following: view_count, like_count, retweet_count, quote_count, common_quoting_users, distinct_quoting_users, common_liking_users, distinct_liking_users, common_retweeters, distinct_retweets.
            return_timestamp (bool, optional): Add UTC Timestamp to results. Defaults to False.
            features (List[str] | None, optional): Defined features of Twitter User Object on which similarity will be computed. Defaults to None.


        Raises:
            AssertionError: If a list of one Tweet ID was provided.
            ValueError: If invalid comparison attribute was provided.

        Returns:
            dict: Requested results for comparison attribute.
        """

        # tweets list must contain at least two IDs
        assert len(tweets) > 1, "'tweets' list object needs at least two entries, not {}".format(len(tweets))

        # if single comparison attribute was provided as string
        if isinstance(compare, str):
            # change to list object
            compare = [compare]
        # init empty dict to store results
        results = dict()
        # iterate over every given comparison atttribute
        for attr in compare:
            # match comparison attribute
            match attr:
                # compare numer of views / impressions
                case "view_count":
                    view_count = dict()
                    for tweet in tweets:
                        url = f"https://api.twitter.com/2/tweets/{tweet}"
                        response_json = self._manual_request(url, {"tweet.fields": ["public_metrics"]})
                        public_metrics = response_json["data"]["public_metrics"]
                        view_count[tweet] = public_metrics["impression_count"]
                    # calc descriptive metrics
                    view_count = self._calc_descriptive_metrics(view_count, tweets)
                    # store in results dict
                    results[attr] = view_count
                # compare number of likes
                case "like_count":
                    like_count = dict()
                    for tweet in tweets:
                        response = self._get_tweet_object(tweet)
                        like_count[tweet] = response._json["favorite_count"]
                    # calc descriptive metrics
                    like_count = self._calc_descriptive_metrics(like_count, tweets)
                    results[attr] = like_count
                # compare number of retweets
                case "retweet_count":
                    retweet_count = dict()
                    for tweet in tweets:
                        response = self._get_tweet_object(tweet)
                        retweet_count[tweet] = response._json["retweet_count"]
                    # calc descriptive metrics
                    retweet_count = self._calc_descriptive_metrics(retweet_count, tweets)
                    results[attr] = retweet_count
                # compare number of quotes
                case "quote_count":
                    quote_count = dict()
                    for tweet in tweets:
                        url = f"https://api.twitter.com/2/tweets/{tweet}"
                        response_json = self._manual_request(url, {"tweet.fields": ["public_metrics"]})
                        public_metrics = response_json["data"]["public_metrics"]
                        quote_count[tweet] = public_metrics["quote_count"]
                    # calc descriptive metrics
                    quote_count = self._calc_descriptive_metrics(quote_count, tweets)
                    results[attr] = quote_count
                # get all quoting users all Tweets have in common
                case "common_quoting_users":
                    all_quoting_users = list()
                    # get all individual quoting users for each tweet
                    for tweet in tweets:
                        # get individual quoting users
                        individual_qouting_users = self.get_all_quoting_users(tweet)
                        # add individual quoting users to list
                        all_quoting_users.append(individual_qouting_users)
                    # get intersection of individual quoting users of all tweets
                    common_quoting_users = set.intersection(*map(set, all_quoting_users))
                    # return quoting users
                    results[attr] = list(common_quoting_users)
                # get distinct quoting users of all Tweets
                case "distinct_quoting_users":
                    all_quoting_users, distinct_quoting_users = dict(), dict()
                    # get all individual quoting users for each tweet
                    for tweet in tweets:
                        # get individual quoting users
                        individual_quoting_users = self.get_all_quoting_users(tweet)
                        # add set of individual liking users of current tweet to dict
                        all_quoting_users[tweet] = individual_quoting_users

                    # filter dicts to distinct quoting users for all tweets
                    for tweet, quoting_users in all_quoting_users.items():
                        distinct_quoting_users[tweet] = list(set(quoting_users))
                        for other_tweet, other_quoting_users in all_quoting_users.items():
                            if tweet != other_tweet:
                                distinct_quoting_users[tweet] = list(set(distinct_quoting_users[tweet]) - set(other_quoting_users))
                    results[attr] = distinct_quoting_users
                # get all liking users that all Tweets have in common
                case "common_liking_users":
                    all_liking_users = list()
                    # get all individual liking users for each tweet
                    for tweet in tweets:
                        # get individual liking users
                        individual_liking_users = self.get_all_liking_users(tweet)
                        # add set of individual liking users of current tweet to list
                        all_liking_users.append(individual_liking_users)
                    # get intersection of all individual liking users of all tweets
                    common_liking_users = set.intersection(*map(set, all_liking_users))
                    results[attr] = list(common_liking_users)
                # get all distinct liking users of all tweets
                case "distinct_liking_users":
                    # init empty dicts to store all liking users and distinct liking users of all tweets
                    all_liking_users, distinct_liking_users = dict(), dict()
                    for tweet in tweets:
                        # get individual liking users
                        individual_liking_users = self.get_all_liking_users(tweet)
                        # add set of individual liking users of current tweet to dict
                        all_liking_users[tweet] = individual_liking_users

                    # filter dictionaries to distinct liking users for all tweets
                    for tweet, liking_users in all_liking_users.items():
                        distinct_liking_users[tweet] = list(set(liking_users))
                        for other_tweet, other_liking_users in all_liking_users.items():
                            if tweet != other_tweet:
                                distinct_liking_users[tweet] = list(set(distinct_liking_users[tweet]) - set(other_liking_users))
                    results[attr] = distinct_liking_users
                # compare all tweets regarding their retweeters that they have in common
                case "common_retweeters":
                    all_retweeters = list()
                    # get all individual retweeters for each tweet
                    for tweet in tweets:
                        individual_retweeters = self.get_all_retweeters(tweet)
                        # add set of individual retweeters current tweet to list
                        all_retweeters.append(individual_retweeters)
                    # get intersection of all individual retweeters of all tweets
                    common_retweeters = set.intersection(*map(set, all_retweeters))
                    results[attr] = list(common_retweeters)
                # compare all tweets regarding their distinct retweeters
                case "distinct_retweeters":
                    # init empty dicts to store all retweeters and distinct retweeters of all tweets
                    all_retweeters, distinct_retweeters = dict(), dict()
                    for tweet in tweets:
                        individual_retweeters = self.get_all_retweeters(tweet)
                        # add set of individual retweeters of current tweet to list
                        all_retweeters[tweet] = individual_retweeters

                    # filter dictionaries to distinct retweeters for all tweets
                    for tweet, retweeters in all_retweeters.items():
                        distinct_retweeters[tweet] = list(set(retweeters))
                        for other_tweet, other_retweeters in all_retweeters.items():
                            if tweet != other_tweet:
                                distinct_retweeters[tweet] = list(set(distinct_retweeters[tweet]) - set(other_retweeters))
                    results[attr] = distinct_retweeters
                # compare Tweets based on feature vectors and their respecitve distances
                case "similarity":
                    # feature list object must be defined
                    if features is None:
                        raise ValueError("'features' list must be provided.")
                    # features needs at least two elements
                    assert len(features) > 1, "'features' list must have at least two elements. {} was given".format(len(features))

                    # init empty dict to store distances
                    distances = dict()
                    # iterate over every uniqe pair
                    for i in range(len(tweets)):
                        for j in range(i + 1, len(tweets)):
                            # get Tweet objects for each pair
                            tweet_i = self._get_tweet_object(tweets[i])._json
                            tweet_j = self._get_tweet_object(tweets[j])._json
                            # build feature vector
                            vec_i = np.array([tweet_i[feature] for feature in features])
                            vec_j = np.array([tweet_j[feature] for feature in features])
                            # feature vectors have to contain numeric values
                            assert all(isinstance(feat, Number) for feat in vec_i), "only numeric features are allowed"
                            assert all(isinstance(feat, Number) for feat in vec_j), "only numeric features are allowed"
                            # calc euclidean distance
                            distances[(tweets[i], tweets[j])] = np.linalg.norm(vec_i - vec_j, ord=2)
                    # sort dict in ascendin order
                    sorted_values = dict(sorted(distances.items(), key=operator.itemgetter(1)))
                    results[attr] = sorted_values
                case "created_at":
                    creation_dates = {tweet: self._get_tweet_object(tweet).created_at for tweet in tweets}
                    # calc datetime metrics
                    creation_dates = self._calc_creation_dates(creation_dates)
                    results[attr] = creation_dates
                # if invalid comparison attribute was provided
                case _:
                    raise ValueError("Invalid comparison attribute for '{}'".format(attr))
        # if UTC timestamp should be returned
        if return_timestamp:
            results["utc_timestamp"] = strf_datetime(datetime.utcnow(), format="%Y-%m-%d %H:%M:%S.%f")
        return results
