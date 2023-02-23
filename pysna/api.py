# -*- coding: utf-8 -*-
import logging
import sys
from datetime import datetime
from typing import Any, List, Literal, get_args

import tweepy

from pysna.fetch import TwitterDataFetcher
from pysna.process import TwitterDataProcessor
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
    """Twitter API interface in order to interact with the Twitter Search API v2."""

    LITERALS_USER_INFO = Literal[
        "id",
        "id_str",
        "name",
        "screen_name",
        "followers",
        "followees",
        "location",
        "description",
        "url",
        "entities",
        "protected",
        "followers_count",
        "friends_count",
        "listed_count",
        "created_at",
        "latest_activity",
        "last_active",
        "liked_tweets",
        "composed_tweets",
        "favourites_count",
        "verified",
        "statuses_count",
        "status",
        "contributors_enabled",
        "profile_image_url_https",
        "profile_banner_url",
        "default_profile",
        "default_profile_image",
        "withheld_in_countries",
        "bot_scores",
    ]

    LITERALS_TWEET_INFO = Literal[
        "id",
        "id_str",
        "full_text",
        "display_text_range",
        "truncated",
        "created_at",
        "entities",
        "tweet_annotations",
        "source",
        "retweeters",
        "in_reply_to_status_id",
        "in_reply_to_status_id_str",
        "in_reply_to_user_id",
        "in_reply_to_user_id_str",
        "in_reply_to_screen_name",
        "user",
        "contributors",
        "coordinates",
        "place",
        "is_quote_status",
        "public_metrics",
        "quoting_users",
        "liking_users",
        "favorited",
        "retweeted",
        "retweeted_status",
        "possibly_sensitive",
        "lang",
        "sentiment",
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
        "commonly_liked_tweets",
        "distinctly_liked_tweets",
        "similarity",
        "created_at",
        "protected",
        "verified",
    ]

    SIMILARITY_FEATURES_COMPARE_USERS = Literal["followers_count", "friends_count", "listed_count", "favourites_count", "statuses_count"]

    LITERALS_COMPARE_TWEETS = Literal[
        "view_count",
        "like_count",
        "retweet_count",
        "quote_count",
        "reply_count",
        "common_quoting_users",
        "distinct_quoting_users",
        "common_liking_users",
        "distinct_liking_users",
        "common_retweeters",
        "distinct_retweeters",
        "similarity",
        "created_at",
    ]

    SIMILARITY_FEATURES_COMPARE_TWEETS = Literal["retweet_count", "reply_count", "like_count", "quote_count", "impression_count"]

    def __init__(
        self,
        bearer_token: Any | None = None,
        consumer_key: Any | None = None,
        consumer_secret: Any | None = None,
        access_token: Any | None = None,
        access_token_secret: Any | None = None,
        x_rapidapi_key: Any | None = None,
        x_rapidapi_host: Any | None = None,
        wait_on_rate_limit: bool = True,
    ):
        super(self.__class__, self).__init__(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, wait_on_rate_limit=wait_on_rate_limit)

        self._bearer_token = bearer_token
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_token = access_token
        self._access_token_secret = access_token_secret
        self._x_rapidapi_key = x_rapidapi_key
        self._x_rapidapi_host = x_rapidapi_host
        self._wait_on_rate_limit = wait_on_rate_limit

        # init TwitterDataFetcher
        self.fetcher = TwitterDataFetcher(self._bearer_token, self._consumer_key, self._consumer_secret, self._access_token, self._access_token_secret, self._x_rapidapi_key, self._x_rapidapi_host)

        # init DataProcessor
        self.data_processor = TwitterDataProcessor()

    def _handle_output(self, output: dict) -> Any:
        """Returns either the single value from one-key dictionary or the dictionary itself.

        Args:
            output (dict): Input dictionary, usually the output of a function.

        Returns:
            Any: Either the single value from one-key dictionary or the dictionary itself.
        """
        # if output has only one key
        if len(output) == 1:
            # return single value
            return next(iter(output.values()))
        else:
            # else return original output
            return output

    def user_info(self, user: str | int, attributes: List[LITERALS_USER_INFO] | str, return_timestamp: bool = False) -> Any:
        """Receive requested user information from Twitter User Object.

        For one attribute, only the corresponding value is returned. For multiple attributes, a dictionary with the key-value pairs of the requested attributes is returned.

        Args:
            user (str | int): Twitter User either specified by corresponding ID or screen name.
            attributes (List[str] | str): Attributes of the User object. These must be from: id, id_str, name, screen_name, followers, followees, location, description, url, entities, protected, followers_count, friends_count, listed_count, created_at, latest_activity, last_active, liked_tweets, composed_tweets, favourites_count, verified, statuses_count, status, contributors_enabled, profile_image_url_https, profile_banner_url, default_profile, default_profile_image, withheld_in_countries, bot_scores
            return_timestamp (bool, optional): Add UTC Timestamp to results. Defaults to False.

        Raises:
            KeyError: If invalid attribute was provided.
            ValueError: If Botometer secrets were not provided.

        Returns:
            dict: Requested user information.

        References: https://mathun3003.github.io/PySNA/user-guide/overview/TwitterAPI/#user_info
        """
        # catch Botometer API secrets before iteration over attributes.
        if "bot_scores" in attributes:
            if (self._x_rapidapi_key is None) or (self._x_rapidapi_host is None):
                raise ValueError("'X_RAPIDAPI_KEY' and 'X_RAPIDAPI_HOST' secrets for Botometer API need to be provided.")

        # initialize empty dict to store requested attributes
        user_info = dict()
        # if single string was provided
        if isinstance(attributes, str):
            # convert to list for iteration
            attributes = [attributes]
        # get user object
        user_obj = self.fetcher.get_user_object(user)
        # loop through the list of attributes and add them to the dictionary
        for attr in attributes:
            # if invalid attribute was provided
            if attr not in get_args(self.LITERALS_USER_INFO):
                raise ValueError("Invalid attribute for '{}'".format(attr))
            # if the desired attribute is in default user object returned by the v1 Search API
            elif attr in user_obj._json.keys():
                user_info[attr] = user_obj._json[attr]
            # get information about user's followers
            elif attr == "followers":
                user_info[attr] = self.data_processor.extract_followers(user_obj)
            # get information about user's followees
            elif attr == "followees":
                user_info[attr] = self.data_processor.extract_followees(user_obj)
            # get all liked tweets of user
            elif attr == "liked_tweets":
                # get page results first
                liked_tweets = self.fetcher.get_liked_tweets_ids(user)
                user_info[attr] = liked_tweets
            # get all composed tweets
            elif attr == "composed_tweets":
                # get page results first
                composed_tweets = self.fetcher.get_composed_tweets_ids(user)
                user_info[attr] = composed_tweets
            # get user's latest activity
            elif attr == "latest_activity":
                user_info[attr] = self.fetcher.get_latest_activity(user)
            # get user's latest activity date
            elif attr == "last_active":
                user_info[attr] = self.fetcher.get_latest_activity_date(user)
            # get user's botometer scores
            elif attr == "bot_scores":
                user_info[attr] = self.fetcher.get_botometer_scores(user)
            # if attribute was not found
            else:
                user_info[attr] = None
            # if timestamp should be returned
        if return_timestamp:
            user_info["utc_timestamp"] = strf_datetime(datetime.utcnow(), format="%Y-%m-%d %H:%M:%S.%f")

        return self._handle_output(user_info)

    def compare_users(self, users: List[str | int], compare: str | List[LITERALS_COMPARE_USERS], return_timestamp: bool = False, features: List[str] | None = None) -> Any:
        """Compare two or more users with the specified comparison attribute(s).

        For one attribute, only the corresponding value is returned. For multiple attributes, a dictionary with the key-value pairs of the requested attributes is returned.

        Args:
            users (List[str  |  int]): User IDs or screen names
            compare (str): Comparison attribute. Must be from: relationship, followers_count, followees_count, tweets_count, favourites_count, common_followers, distinct_followers, common_followees, distinct_followees, commonly_liked_tweets, distinctly_liked_tweets, similarity, created_at, protected, verified.
            return_timestamp (bool, optional): Add UTC Timestamp to results. Defaults to False.
            features (List[str] | None, optional): Defined features of Twitter User Object on which similarity will be computed. Must be from: followers_count, friends_count, listed_count, favourites_count, statuses_count. Defaults to None.

        Raises:
            ValueError: If invalid comparison attribute was provided.

        Returns:
            dict | list: Results of requested comparison attribute(s).

        Referencs: https://mathun3003.github.io/PySNA/user-guide/overview/TwitterAPI/#compare_users
        """
        # users list must contain at least two elements
        assert len(users) > 1, "'users' list must contain at least two elements, {} was/were provided".format(len(users))

        # catch if feature vector contains only numeric values, and contains at least two elements
        if features:
            assert len(features) > 1, "'features' list must have at least two elements. {} was/were given".format(len(features))
            for feat in features:
                if feat not in get_args(self.SIMILARITY_FEATURES_COMPARE_USERS):
                    raise ValueError(f"Only numeric features are supported. Must be from: {', '.join(get_args(self.SIMILARITY_FEATURES_COMPARE_USERS))}. You passed in {feat}")

        # if single comparison attribute was provided as string
        if isinstance(compare, str):
            # change to list object
            compare = [compare]
        # init empty dict to store results
        results = dict()
        # iterate over comparison attributes
        for attr in compare:
            # if invalid attribute was provided
            if attr not in get_args(self.LITERALS_COMPARE_USERS):
                raise ValueError("Invalid attribute for '{}'".format(attr))
            # match comparison attributes
            match attr:
                # compare relationships between two users
                case "relationship":
                    results[attr] = self.fetcher.get_relationship_pairs(users)
                # compare number of followers
                case "followers_count":
                    # get individual followers
                    followers = {user: self.fetcher.get_user_object(user).followers_count for user in users}
                    # add descriptive metrics
                    followers_with_metrics = self.data_processor.calc_descriptive_metrics(followers)
                    results[attr] = followers_with_metrics
                # compare number of friends
                case "followees_count":
                    # get individual followees
                    followees = {user: self.fetcher.get_user_object(user).friends_count for user in users}
                    # add descriptive metrics
                    followees = self.data_processor.calc_descriptive_metrics(followees)
                    results[attr] = followees
                # compare number of Tweets issued by each user
                case "tweets_count":
                    # get individual statuses counts
                    tweets = {user: self.fetcher.get_user_object(user).statuses_count for user in users}
                    # add descriptive metrics
                    tweets = self.data_processor.calc_descriptive_metrics(tweets)
                    results[attr] = tweets
                # compare number of likes issued by each user
                case "favourites_count":
                    # get individual likes
                    likes = {user: self.fetcher.get_user_object(user).favourites_count for user in users}
                    # add descriptive metrics
                    likes = self.data_processor.calc_descriptive_metrics(likes)
                    results[attr] = likes
                # compare protected attribute of users
                case "protected":
                    results[attr] = {user: self.fetcher.get_user_object(user).protected for user in users}
                # compare verified attribute for users
                case "verified":
                    results[attr] = {user: self.fetcher.get_user_object(user).verified for user in users}
                # get common followers
                case "common_followers":
                    # get individual followers first
                    individual_followers = [self.fetcher.get_user_follower_ids(user) for user in users]
                    # get common followers by calculating the intersection
                    common_followers = self.data_processor.intersection(individual_followers)
                    results[attr] = common_followers
                # get distinct followers
                case "distinct_followers":
                    # get individual followers first
                    individual_followers = {user: self.fetcher.get_user_follower_ids(user) for user in users}
                    # get distinct followers by calculating the difference of each set
                    distinct_followers = self.data_processor.difference(individual_followers)
                    results[attr] = distinct_followers
                # get common followees
                case "common_followees":
                    # get individual followees first
                    individual_followees = [self.fetcher.get_user_followee_ids(user) for user in users]
                    # get common followees by calculating the intersection
                    common_followees = self.data_processor.intersection(individual_followees)
                    results[attr] = common_followees
                # get distinct followees
                case "distinct_followees":
                    # get individual followees first
                    individual_followees = {user: self.fetcher.get_user_followee_ids(user) for user in users}
                    # get distinct followees by calculating the difference of each set
                    distinct_followees = self.data_processor.difference(individual_followees)
                    results[attr] = distinct_followees
                # get common liked tweets
                case "commonly_liked_tweets":
                    # get individual liked tweets first
                    individual_likes = [self.fetcher.get_liked_tweets_ids(user) for user in users]
                    # get common liked tweets by calculating the intersection
                    common_likes = self.data_processor.intersection(individual_likes)
                    results[attr] = common_likes
                # get distinct liked tweets
                case "distinctly_liked_tweets":
                    # get individual liked tweets first
                    individual_likes = {user: self.fetcher.get_liked_tweets_ids(user) for user in users}
                    # get distinct liked tweets by calculating the difference for each set
                    distinct_likes = self.data_processor.difference(individual_likes)
                    results[attr] = distinct_likes
                # compute similarity between two users basd on the defined features
                case "similarity":
                    # feature list object must be defined
                    if features is None:
                        raise ValueError("'features' list must be provided.")
                    # get serialized user objects first
                    user_objs = [self.fetcher.get_user_object(user)._json for user in users]
                    # calculate similarity based on defined feature vector
                    results[attr] = self.data_processor.calc_similarity(user_objs=user_objs, features=features)
                # compare creaation dates
                case "created_at":
                    # get individual creation dates first
                    creation_dates = {user: self.fetcher.get_user_object(user).created_at for user in users}
                    # add datetime metrics
                    creation_dates = self.data_processor.calc_datetime_metrics(creation_dates)
                    results[attr] = creation_dates
                # if comparison attribute was not found
                case _:
                    results[attr] = None
        # if timestamp should be returned
        if return_timestamp:
            results["utc_timestamp"] = strf_datetime(datetime.utcnow(), format="%Y-%m-%d %H:%M:%S.%f")

        return self._handle_output(results)

    def tweet_info(self, tweet_id: str | int, attributes: List[LITERALS_TWEET_INFO] | str, return_timestamp: bool = False) -> Any:
        """Receive requested Tweet information from Tweet Object.

        For one attribute, only the corresponding value is returned. For multiple attributes, a dictionary with the key-value pairs of the requested attributes is returned.

        Args:
            tweet_id (str | int): Tweet ID
            attributes (List[LITERALS_TWEET_INFO] | str): Attributes of the Tweet object. These must be from: id, id_str, full_text, display_text_range, truncated, created_at, entities, tweet_annotations, source, retweeters, in_reply_to_status_id, in_reply_to_status_id_str, in_reply_to_user_id, in_reply_to_user_id_str, in_reply_to_screen_name, user, contributors, coordinates, place, is_quote_status, public_metrics, quoting_users, liking_users, favorited, retweeted, retweeted_status, possibly_sensitive, lang, sentiment.
            return_timestamp (bool, optional): Add UTC Timestamp to results. Defaults to False.

        Raises:
            ValueError: If invalid attribute was provided.

        Returns:
            dict: Requested Tweet information.

        References: https://mathun3003.github.io/PySNA/user-guide/overview/TwitterAPI/#tweet_info
        """
        # get tweet object
        tweet_obj = self.fetcher.get_tweet_object(tweet_id)

        # initialize empty dict to store request information
        tweet_info = dict()

        # if single string was provided
        if isinstance(attributes, str):
            # convert to list for iteration
            attributes = [attributes]
        for attr in attributes:
            # if invalid attribute was provided
            if attr not in get_args(self.LITERALS_TWEET_INFO):
                raise ValueError("Invalid attribute for '{}'".format(attr))
            # get default attributes from tweepy Status model
            elif attr in tweet_obj._json.keys():
                tweet_info[attr] = tweet_obj._json[attr]
            # get all quoting users
            elif attr == "quoting_users":
                quoting_users = self.fetcher.get_quoting_users_ids(tweet_id)
                tweet_info[attr] = quoting_users
            # get all liking users
            elif attr == "liking_users":
                liking_users = self.fetcher.get_liking_users_ids(tweet_id)
                tweet_info[attr] = liking_users
            # get all retweeters
            elif attr == "retweeters":
                retweeters = self.fetcher.get_retweeters_ids(tweet_id)
                tweet_info[attr] = retweeters
            # get public metrics
            elif attr == "public_metrics":
                tweet_info[attr] = self.fetcher.get_public_metrics(tweet_id)
            # get context annotations
            elif attr == "tweet_annotations":
                tweet_info[attr] = self.fetcher.get_context_annotations_and_entities(tweet_id)
            # get tweet sentiment
            elif attr == "sentiment":
                tweet_info[attr] = self.data_processor.detect_tweet_sentiment(tweet_obj.full_text)
            # if attribute was not found
            else:
                tweet_info[attr] = None
        # if timestamp should be returned
        if return_timestamp:
            tweet_info["utc_timestamp"] = strf_datetime(datetime.utcnow(), format="%Y-%m-%d %H:%M:%S.%f")

        return self._handle_output(tweet_info)

    def compare_tweets(self, tweet_ids: List[str | int], compare: str | List[LITERALS_COMPARE_TWEETS], return_timestamp: bool = False, features: List[str] | None = None) -> Any:
        """Compare two or more Tweets with the specified comparison attribute.

        For one attribute, only the corresponding value is returned. For multiple attributes, a dictionary with the key-value pairs of the requested attributes is returned.

        Args:
            tweets (List[str  |  int]): List of Tweet IDs.
            compare (str | List[LITERALS_COMPARE_TWEETS]): Comparison attribute. Needs to be from the following: view_count, like_count, retweet_count, quote_count, reply_count, common_quoting_users, distinct_quoting_users, common_liking_users, distinct_liking_users, common_retweeters, distinct_retweeters, similarity, created_at.
            return_timestamp (bool, optional): Add UTC Timestamp to results. Defaults to False.
            features (List[str] | None, optional): Defined features of Twitter User Object on which similarity will be computed. Must be from: retweet_count, reply_count, like_count, quote_count, impression_count. Defaults to None.

        Raises:
            AssertionError: If a list of one Tweet ID was provided.
            ValueError: If invalid comparison attribute was provided.

        Returns:
            dict: Requested results for comparison attribute.

        References: https://mathun3003.github.io/PySNA/user-guide/overview/TwitterAPI/#compare_tweets
        """
        # tweets list must contain at least two IDs
        assert len(tweet_ids) > 1, "'tweets' list object needs at least two entries, not {}".format(len(tweet_ids))

        # catch if feature vector contains only numeric values, and contains at least two elements
        if features:
            assert len(features) > 1, "'features' list must have at least two elements. {} was/were given".format(len(features))
            for feat in features:
                if feat not in get_args(self.SIMILARITY_FEATURES_COMPARE_TWEETS):
                    raise ValueError(f"Only numeric features are supported. Must be from: {', '.join(get_args(self.SIMILARITY_FEATURES_COMPARE_TWEETS))}. You passed in {feat}.")

        # if single comparison attribute was provided as string
        if isinstance(compare, str):
            # change to list object
            compare = [compare]
        # init empty dict to store results
        results = dict()
        # iterate over every given comparison atttribute
        for attr in compare:
            # if invalid attribute was provided
            if attr not in get_args(self.LITERALS_COMPARE_TWEETS):
                raise ValueError("Invalid attribute for '{}'".format(attr))
            # match comparison attribute
            match attr:
                # compare numer of views / impressions
                case "view_count":
                    # get individual view_counts
                    view_counts = {tweet_id: self.fetcher.get_public_metrics(tweet_id)["impression_count"] for tweet_id in tweet_ids}
                    # add descriptive metrics
                    view_counts = self.data_processor.calc_descriptive_metrics(view_counts)
                    results[attr] = view_counts
                # compare number of likes
                case "like_count":
                    # get individual like_counts
                    like_counts = {tweet_id: self.fetcher.get_public_metrics(tweet_id)["like_count"] for tweet_id in tweet_ids}
                    # add descriptive metrics
                    like_counts = self.data_processor.calc_descriptive_metrics(like_counts)
                    results[attr] = like_counts
                # compare number or retweets
                case "retweet_count":
                    # get individual number of retweets
                    retweet_counts = {tweet_id: self.fetcher.get_public_metrics(tweet_id)["retweet_count"] for tweet_id in tweet_ids}
                    # add descriptive metrics
                    retweet_counts = self.data_processor.calc_descriptive_metrics(retweet_counts)
                    results[attr] = retweet_counts
                # compare number of quotes
                case "quote_count":
                    # get individual number of quotes
                    quote_counts = {tweet_id: self.fetcher.get_public_metrics(tweet_id)["quote_count"] for tweet_id in tweet_ids}
                    # add descriptive metrics
                    quote_counts = self.data_processor.calc_descriptive_metrics(quote_counts)
                    results[attr] = quote_counts
                # compare number of commonts
                case "reply_count":
                    # get individual number of replies first
                    reply_counts = {tweet_id: self.fetcher.get_public_metrics(tweet_id)["reply_count"] for tweet_id in tweet_ids}
                    # add descriptive metrics
                    reply_counts = self.data_processor.calc_descriptive_metrics(reply_counts)
                    results[attr] = reply_counts
                # get all quoting users all Tweets have in common
                case "common_quoting_users":
                    # get individual quoting users first
                    quoting_users = [self.fetcher.get_quoting_users_ids(tweet_id) for tweet_id in tweet_ids]
                    # get common quoting users by calculating the intersection
                    common_quoting_users = self.data_processor.intersection(quoting_users)
                    # return quoting users
                    results[attr] = common_quoting_users
                # get distinct quoting users for each tweet
                case "distinct_quoting_users":
                    # get individual quoting users first
                    quoting_users = {tweet_id: self.fetcher.get_quoting_users_ids(tweet_id) for tweet_id in tweet_ids}
                    # get distinct quoting users for each tweet by calculating the difference for each set
                    distinct_quoting_users = self.data_processor.difference(quoting_users)
                    results[attr] = distinct_quoting_users
                # get all liking users that all tweets have in common
                case "common_liking_users":
                    # get individual liking users first
                    liking_users = [self.fetcher.get_liking_users_ids(tweet_id) for tweet_id in tweet_ids]
                    # get common liking users by calculating the intersection
                    common_liking_users = self.data_processor.intersection(liking_users)
                    # return common liking users
                    results[attr] = common_liking_users
                # get distinct liking users of all tweets
                case "distinct_liking_users":
                    # get individual liking users first
                    liking_users = {tweet_id: self.fetcher.get_liking_users_ids(tweet_id) for tweet_id in tweet_ids}
                    # get distinct liking users for each tweet by calculating the difference for each set
                    distinct_liking_users = self.data_processor.difference(liking_users)
                    results[attr] = distinct_liking_users
                # get all retweeters all tweets have in common
                case "common_retweeters":
                    # get individual retweeters first
                    retweeters = [self.fetcher.get_retweeters_ids(tweet_id) for tweet_id in tweet_ids]
                    # get common retweeters by calculating the intersection
                    common_retweeters = self.data_processor.intersection(retweeters)
                    # return common retweeters
                    results[attr] = common_retweeters
                # get distinct retweeters of all tweets
                case "distinct_retweeters":
                    # get individual retweeters first
                    retweeters = {tweet_id: self.fetcher.get_retweeters_ids(tweet_id) for tweet_id in tweet_ids}
                    # get distinct retweeters by calculating the difference for each set
                    distinct_retweeters = self.data_processor.difference(retweeters)
                    results[attr] = distinct_retweeters
                # compute similarity between two tweets basd on the defined features
                case "similarity":
                    # feature list object must be defined
                    if features is None:
                        raise ValueError("'features' list must be provided.")
                    # get public metrics for Tweet objects first
                    public_metrics = {tweet_id: self.fetcher.get_public_metrics(tweet_id) for tweet_id in tweet_ids}
                    # calculate similarity based on defined feature vector
                    results[attr] = self.data_processor.calc_similarity(tweet_metrics=public_metrics, features=features)
                # compare creation dates of tweets
                case "created_at":
                    # get individual creation dates first
                    creation_dates = {tweet_id: self.fetcher.get_tweet_object(tweet_id).created_at for tweet_id in tweet_ids}
                    # add datetime metrics
                    creation_dates = self.data_processor.calc_datetime_metrics(creation_dates)
                    results[attr] = creation_dates
                # if attribute was not found
                case _:
                    results[attr] = None
        # if UTC timestamp should be returned
        if return_timestamp:
            results["utc_timestamp"] = strf_datetime(datetime.utcnow(), format="%Y-%m-%d %H:%M:%S.%f")

        return self._handle_output(results)
