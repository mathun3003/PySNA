# -*- coding: utf-8 -*-
import logging
from typing import Dict, List, Literal, Set

import tweepy

from pysna.auth import TwitterAppAuthHandler, TwitterClient
from pysna.utils import strf_datetime

log = logging.getLogger(__name__)


class TwitterAPI():
    """Twitter API class in order to interact with the Twitter Search API v2."""

    def __init__(self, bearer_token: str, consumer_key: str, consumer_secret: str,
                 access_token: str, access_token_secret: str):

        _auth = TwitterAppAuthHandler(consumer_key=consumer_key,
                                     consumer_secret=consumer_secret)
        _api = tweepy.API(_auth)
        TwitterClient()
        _client = TwitterClient(bearer_token=bearer_token, consumer_key=consumer_key,
                                consumer_secret=consumer_secret, access_token=access_token,
                                access_token_secret=access_token_secret)

        self._auth = _auth
        self._api = _api
        self._client = _client


    def _get_user_object(self, user: str) -> tweepy.User:
        """Request Twitter User Object via tweepy

        Args:
            user (str): Either User ID or screen name

        Returns:
            tweepy.User: Twitter User object from tweepy
        """
        # check if string for user1 is convertible to int in order to check for user ID or screen name
        if user.isdigit():
            # get profile for user1 by user ID
            user_obj = self._api.get_user(user_id=user)
        else:
            # get profile for user1 by screen name
            user_obj = self._api.get_user(screen_name=user)
        return user_obj

    def _get_user_followers(self, user: str) -> Set[int]:
        """Request Twitter follower IDs from user

        Args:
            user (str): Either User ID or screen name

        Returns:
            Set[int]: Array containing follower IDs
        """
        # check if string for user1 is convertible to int in order to check for user ID or screen name
        if user.isdigit():
            # get profile for user1 by user ID
            user_followers = self._api.get_follower_ids(user_id=user)
        else:
            # get profile for user1 by screen name
            user_followers = self._api.get_follower_ids(screen_name=user)
        return set(user_followers)

    def _get_user_follows(self, user: str) -> Set[int]:
        """Request Twitter follow IDs from user

        Args:
            user (str): Either User ID or screen name

        Returns:
            Set[int]: Array containing follow IDs
        """
        if user.isdigit():
            user_follows = self._api.get_friend_ids(user_id=user)
        else:
            user_follows = self._api.get_friend_ids(screen_name=user)
        return set(user_follows)

    def _get_tweet_object(self, tweet: int | str, additional_fields: Dict[str, List[str]]):
        """_summary_

        Args:
            tweet (str): _description_

        Returns:
            tweepy.Tweet: _description_

        Reference: https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet
        """
        tweet = self._client.get_tweet(id=tweet, **additional_fields)
        return tweet

    LITERALS_USER_INFO = Literal['id', 'id_str', 'name', 'screen_name', 'followers_info',
            'follows_info', 'location', 'profile_location', 'description', 'url', 'entities',
            'protected', 'followers_count', 'friends_count', 'listed_count', 'created_at',
            'favourites_count', 'utc_offset', 'time_zone', 'geo_enabled', 'verified', 'statuses_count',
            'lang', 'status', 'contributors_enabled', 'is_translator', 'is_translation_enabled', 'profile_background_color',
            'profile_background_image_url', 'profile_background_image_url_https', 'profile_background_tile', 'profile_image_url',
            'profile_image_url_https', 'profile_banner_url', 'profile_link_color', 'profile_sidebar_border_color',
            'profile_sidebar_fill_color', 'profile_text_color', 'profile_use_background_image', 'has_extended_profile',
            'default_profile', 'default_profile_image', 'following', 'follow_request_sent', 'notifications',
            'translator_type', 'withheld_in_countries']

    def user_info(self, user: str, attributes: List[LITERALS_USER_INFO]) -> dict:
        """Receive requested user information from Twitter User Object.

        Args:
            user (str): Twitter User either specified by corresponding ID or screen name.
            attributes (List[str]): 'id', 'id_str', 'name', 'screen_name', 'followers_info',
            'follows_info', 'location', 'profile_location', 'description', 'url', 'entities',
            'protected', 'followers_count', 'friends_count', 'listed_count', 'created_at',
            'favourites_count', 'utc_offset', 'time_zone', 'geo_enabled', 'verified', 'statuses_count',
            'lang', 'status', 'contributors_enabled', 'is_translator', 'is_translation_enabled', 'profile_background_color',
            'profile_background_image_url', 'profile_background_image_url_https', 'profile_background_tile', 'profile_image_url',
            'profile_image_url_https', 'profile_banner_url', 'profile_link_color', 'profile_sidebar_border_color',
            'profile_sidebar_fill_color', 'profile_text_color', 'profile_use_background_image', 'has_extended_profile',
            'default_profile', 'default_profile_image', 'following', 'follow_request_sent', 'notifications',
            'translator_type', 'withheld_in_countries'

        Raises:
            KeyError: If undefined attribute was provided.

        Returns:
            dict: Requested user information.
        """

        # get user object via tweepy
        user_obj = self._get_user_object(user)

        # initialize empty dict to store requested attributes
        user_info = dict()

        # loop through the list of attributes and add them to the dictionary
        for attr in attributes:
            if attr in user_obj._json.keys():
                user_info[attr] = user_obj._json[attr]
            # get follower information
            elif attr == "followers_info":
                # define dict to store follower information
                user_info[attr] = {"follower_ids": list(), "follower_names": list(), "follower_screen_names": list()}
                # get follower IDs
                user_info[attr]["follower_ids"] = user_obj.follower_ids()
                # get follower names and screen names
                for follower in user_obj.followers():
                    user_info[attr]["follower_names"].append(follower.name)
                    user_info[attr]["follower_screen_names"].append(follower.screen_name)
            # get follows information
            elif attr == "follows_info":
                # define dict to store follows information
                user_info[attr] = dict.fromkeys(["follows_ids", "follows_names", "follows_screen_names"])
                # get follows ID, names, and screen names
                for friend in user_obj.friends():
                    user_info[attr]["follows_ids"].append(friend.id)
                    user_info[attr]["follows_names"].append(friend.name)
                    user_info[attr]["follows_screen_names"].append(friend.screen_name)
            elif attr == "liked_tweets":
                # TODO: client.get_liked_tweets()
                pass
            else:
                raise ValueError("Invalid attribute for {}".format(attr))

        return user_info

    LITERALS_COMPARE_USERS = Literal['num_followers', 'num_follows', 'common_followers',
            'distinct_followers', 'common_follows', 'distinct_follows', 'created_at']

    def compare_users(self, user1: str, user2: str, compare: LITERALS_COMPARE_USERS) -> dict | list:
        """Compare two users with the specified comparison attribute

        Args:
            user1 (str): User ID or screen name
            user2 (str): User ID or screen name
            compare (str): 'num_followers', 'num_follows', 'common_followers',
            'distinct_followers', 'common_follows', 'distinct_follows', 'created_at'

        Raises:
            ValueError: If invalid comparison attribute was provided.

        Returns:
            dict | list: Requested comparison attribute for specified users.
        """

        # match comparison attributes
        match compare:
            # compare number of followers
            case "num_followers":
                user1_obj, user2_obj = self._get_user_object(user1), self._get_user_object(user2)
                return {f"{user1}_followers": user1_obj.followers_count,
                        f"{user2}_followers": user2_obj.followers_count}
            # compare number of friends
            case "num_follows":
                user1_obj, user2_obj = self._get_user_object(user1), self._get_user_object(user2)
                return {f"{user1}_follows": user1_obj.friends_count,
                        f"{user2}_follows": user2_obj.friends_count}
            # compare common followers
            case "common_followers":
                user1_followers, user2_followers = self._get_user_followers(user1), self._get_user_followers(user2)
                # get intersection of both users
                common_followers = user1_followers.intersection(user2_followers)
                return list(common_followers)
            # compare distinct followers
            case "distinct_followers":
                user1_followers, user2_followers = self._get_user_followers(user1), self._get_user_followers(user2)
                # get distinct followers
                user1_distinct_followers = user1_followers.difference(user2_followers)
                user2_distinct_followers = user2_followers.difference(user1_followers)
                return {f"{user1}_distinct_followers": list(user1_distinct_followers),
                        f"{user2}_distinct_followers": list(user2_distinct_followers)}
            # compare common follows
            case "common_follows":
                user1_follows, user2_follows = self._get_user_follows(user1), self._get_user_follows(user2)
               # get intersectoin of both users
                common_follows = user1_follows.intersection(user2_follows)
                return list(common_follows)
            # compare distinct follows
            case "distinct_follows":
                user1_follows, user2_follows = self._get_user_follows(user1), self._get_user_follows(user2)
                # get distinct followers
                user1_distinct_follows = user1_follows.difference(user2_follows)
                user2_distinct_follows = user2_follows.difference(user1_follows)
                return {f"{user1}_distinct_follows": list(user1_distinct_follows),
                        f"{user2}_distinct_follows": list(user2_distinct_follows)}
            # compare creation date
            case "created_at":
                user1_obj, user2_obj = self._get_user_object(user1), self._get_user_object(user2)
                # FIXME: #? time diff will be negative if user1 was created after user2. Still okay? #?
                time_difference_in_seconds = (user2_obj.created_at - user1_obj.created_at).total_seconds()
                time_difference_in_days = time_difference_in_seconds // 86400
                time_difference_in_weeks = time_difference_in_days // 7
                time_difference_in_hours = time_difference_in_seconds // 3600
                return {f"{user1}_creation_date": strf_datetime(user1_obj.created_at),
                        f"{user2}_creation_date": strf_datetime(user2_obj.created_at),
                        "time_difference_in_seconds": time_difference_in_seconds,
                        "time_difference_in_hours": time_difference_in_hours,
                        "time_difference_in_days": time_difference_in_days,
                        "time_difference_in_weeks": time_difference_in_weeks}
            # if other comparison attribute was provided
            case _:
                raise ValueError("Invalid comparison attribute for {}".format(compare))

    #? same with list of users
    def compare_users_list(self, users: List[str], compare: str) -> dict | list:
        """Compare two or more users with the specified comparison attribute.

        Args:
            users (List[str]): User IDs or screen names
            compare (str): 'num_followers', 'num_follows', 'common_followers',
            'distinct_followers', 'common_follows', 'distinct_follows'

        Raises:
            ValueError: If users list only contains one entry.
            ValueError: If invalid comparison attribute was provided.

        Returns:
            dict | list: Requested comparison attribute. Provide screen names
            to display them in the results.
        """
        # list must contain at least two elements
        if len(users) < 2:
            raise ValueError("{} list must contain at least two elements.".format(users))

        # match comparison attributes
        match compare:
            # compare number of follwoers
            case "num_followers":
                followers_dict = dict()
                for user in users:
                    tmp_user_obj = self._get_user_object(user)
                    followers_dict[user] = tmp_user_obj.followers_count
                return followers_dict
            # compare number of friends
            case "num_follows":
                follows_dict = dict()
                for user in users:
                    tmp_user_obj = self._get_user_object(user)
                    follows_dict[user] = tmp_user_obj.friends_count
                return follows_dict
            # compare common followers
            case "common_followers":
                individual_followers = [self._get_user_followers(user) for user in users]
                common_followers = set.intersection(*map(set, individual_followers))
                return list(common_followers)
            # compare distinct followers
            case "distinct_followers":
                individual_followers = {user: self._get_user_followers(user) for user in users}
                distinct_followers = dict()
                for user, followers in individual_followers.items():
                    distinct_followers[user] = list(set(followers))
                    for other_user, other_followers in individual_followers.items():
                        if user != other_user:
                            distinct_followers[user] = list(set(distinct_followers[user]) - set(other_followers))
                return distinct_followers
            # compare common follows
            case "common_follows":
                individual_follows = [self._get_user_follows(user) for user in users]
                common_follows = set.intersection(*map(set, individual_follows))
                return list(common_follows)
            # compare distinct follows
            case "distinct_follows":
                individual_follows = {user: self._get_user_follows(user) for user in users}
                distinct_follows = dict()
                for user, follows in individual_follows.items():
                    distinct_follows[user] = list(set(follows))
                    for other_user, other_follows in individual_follows.items():
                        if user != other_user:
                            distinct_follows[user] = list(set(distinct_follows[user]) - set(other_follows))
                return distinct_follows
            # if other comparison attribute was provided
            case _:
                raise ValueError("Invalid comparison attribute for {}".format(compare))

    def tweet_info(self, tweet_id: str, attributes: List[str]) -> dict:
        """_summary_

        Args:
            tweet_id (str): _description_
            attributes (List[str]): _description_

        Returns:
            dict: _description_

        Reference: https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference/get-tweets-id
        """
        # get tweet object
        tweet_obj = self._get_tweet_object(tweet_id)

        # initialize empty dict to store request information
        tweet_info = dict()

        for attr in attributes:
            # TODO: finish if default field was provided from expansions or user.fields, tweet.fields
            if attr in []:
                tweet_info[attr] = None
            # get quoting users
            elif attr == "quoting_users":
                # Initialize a list to store the quoting users
                quoting_users = []

                # Set the initial search parameters
                params = {
                    "id": tweet_id,
                    "max_results": 100,  # The maximum allowed by the Twitter API
                    "next_token": None
                }

                while True:
                    quote_results = self._client.get_quote_tweets(**params,
                                                                  expansions="author_id")
                    for user in quote_results.includes['users']:
                        # Add the user to the list
                        quoting_users.append({
                            "id": user.id,
                            "name": user.name,
                            "screen_name": user.username
                        })

                    # Break out of the loop if we have reached the end of the search results
                    if not quote_results.meta["next_token"]:
                        break
                    else:
                        # Update the search parameters for the next iteration
                        params["next_token"] = quote_results.meta["next_token"]

                # store in tweet_info dict
                tweet_info['quoting_users'] = quoting_users
            # TODO: add more attributes
            elif attr == "":
                pass

        # FIXME
        # loop through the list of attributes and add them to the dictionary
        for attr in attributes:
            if attr in tweet_obj.keys():
                tweet_info[attr] = tweet_obj.__dict__[attr]

        return tweet_info

    LITERALS_COMPARE_TWEETS = Literal['num_views', 'num_likes', 'num_retweets', 'num_quotes', 'common_quoting_users',
                                      'distinct_quoting_users', 'common_liking_users', 'distinct_liking_users',
                                      'common_retweeters', 'distinct_retweets']

    def compare_tweets(self, tweets: List[str | int], compare: str & LITERALS_COMPARE_TWEETS) -> dict | set:
        """Compare two or more Tweets with the specified comparison attribute.

        Args:
            tweets (List[str  |  int]): List of Tweet IDs.
            compare (str): Comparison attribute. Needs to be one of the following: 'num_views', 'num_likes', 'num_retweets', 'num_quotes',
            'common_quoting_users', 'distinct_quoting_users', 'common_liking_users', 'distinct_liking_users', 'common_retweeters', 'distinct_retweets'.

        Raises:
            ValueError: If a list of one Tweet ID was provided.
            ValueError: If invalid comparison attribute was provided.

        Returns:
            dict | set: Requested results for comparison attribute.
        """

        # tweets list must contain at least two IDs
        if len(tweets) < 2:
            raise ValueError("tweets list object needs at least two entries, not {}".format(len(tweets)))

        # match comparison attribute
        match compare:
            case "num_views":
                num_views = dict()
                for tweet in tweets:
                    response = self._get_tweet_object(tweet, additional_fields={
                        "tweet_fields": ["public_metrics"],
                        "expansions": ["attachments.media_keys"],
                        "media_fields": ["public_metrics"]
                    })
                    public_metrics = response.includes["media"][0].public_metrics
                    num_views[tweet] = public_metrics["view_count"]
                return num_views
            case "num_likes":
                num_likes = dict()
                for tweet in tweets:
                    response = self._get_tweet_object(tweet, additional_fields={
                        "tweet_fields": ["public_metrics"],
                        "expansions": ["attachments.media_keys"],
                        "media_fields": ["public_metrics"]
                    })
                    public_metrics = response.data[0].public_metrics
                    num_likes[tweet] = public_metrics["like_count"]
                return num_likes
            case "num_retweets":
                num_retweets = dict()
                for tweet in tweets:
                    response = self._get_tweet_object(tweet, additional_fields={
                        "tweet_fields": ["public_metrics"],
                        "expansions": ["attachments.media_keys"],
                        "media_fields": ["public_metrics"]
                    })
                    public_metrics = response.data[0].public_metrics
                    num_retweets[tweet] = public_metrics["retweet_count"]
                return num_retweets
            case "num_quotes":
                num_quotes = dict()
                for tweet in tweets:
                    response = self._get_tweet_object(tweet, additional_fields={
                        "tweet_fields": ["public_metrics"],
                        "expansions": ["attachments.media_keys"],
                        "media_fields": ["public_metrics"]
                    })
                    public_metrics = response.data[0].public_metrics
                    num_quotes[tweet] = public_metrics["quote_count"]
                return num_quotes
            # get all quoting users all Tweets have in common
            # FIXME: #! wrong request -> implement own function to receive all qouting users
            case "common_quoting_users":
                all_quoting_users = list()
                # get all individual quoting users for each tweet
                for tweet in tweets:
                    # init empty dict to store quoting users for current tweet
                    individual_qouting_users = set()
                    # Set the initial search parameters
                    params = {
                        "id": tweet,
                        "max_results": 100,  # The maximum allowed by the Twitter API
                        "next_token": None
                    }
                    # get all quoting users of that tweet
                    while True:
                        #! get_quote_tweets is the wrong request
                        quote_results = self._client.get_quote_tweets(**params,
                                                                    expansions="author_id")
                        for user in quote_results.includes['users']:
                            # Add the user to the list
                            individual_qouting_users.append({
                                "id": user.id,
                                "name": user.name,
                                "screen_name": user.username
                            })

                        # Break out of the loop if we have reached the end of the search results
                        if not quote_results.meta["next_token"]:
                            break
                        else:
                            # Update the search parameters for the next iteration
                            params["next_token"] = quote_results.meta["next_token"]
                    # store quoting users of the current tweet
                    all_quoting_users[tweet] = individual_qouting_users
                # get intersection of individual quoting users of all tweets
                common_quoting_users =  set.intersection(*map, all_quoting_users)
                # return quoting users
                return common_quoting_users
            # get distinct quoting users of all Tweets
            case "distinct_quoting_users":
                # TODO
                pass
            # get all liking users that all Tweets have in common
            case "common_liking_users":
                all_liking_users = list()
                # get all individual liking users for each tweet
                for tweet in tweets:
                    individual_liking_users = set()
                    # Set the initial search parameters
                    params = {
                        "id": tweet,
                        "max_results": 100,  # The maximum allowed by the Twitter API
                        "next_token": None
                    }
                    # get all liking users of that tweet
                    while True:
                        like_results = self._client.get_liking_users(**params)
                        for user in like_results.data:
                            # Add the user to the list
                            individual_liking_users.add({
                                "id": user.id,
                                "name": user.name,
                                "screen_name": user.username
                            })

                        # Break out of the loop if we have reached the end of the search results
                        if not like_results.meta["next_token"]:
                            break
                        else:
                            # Update the search parameters for the next iteration
                            params["next_token"] = like_results.meta["next_token"]
                    # add set of individual liking users of current tweet to list
                    all_liking_users.append(individual_liking_users)
                # get intersection of all individual liking users of all tweets
                common_liking_users = set.intersection(*map, all_liking_users)
                return common_liking_users
            # get all distinct liking users of all tweets
            case "distinct_liking_users":
                # init empty dicts to store all liking users and distinct liking users of all tweets
                all_liking_users = dict()
                distinct_liking_users = list()
                for tweet in tweets:
                    individual_liking_users = list()
                    # Set the initial search parameters
                    params = {
                        "id": tweet,
                        "max_results": 100,  # The maximum allowed by the Twitter API
                        "next_token": None
                    }
                    # get all liking users of that tweet
                    while True:
                        like_results = self._client.get_liking_users(**params)
                        for user in like_results.data:
                            # Add the user to the list
                            individual_liking_users.add({
                                "id": user.id,
                                "name": user.name,
                                "screen_name": user.username
                            })

                        # Break out of the loop if we have reached the end of the search results
                        if not like_results.meta["next_token"]:
                            break
                        else:
                            # Update the search parameters for the next iteration
                            params["next_token"] = like_results.meta["next_token"]
                    # add set of individual liking users of current tweet to list
                    all_liking_users[tweet] = individual_liking_users

                # filter dictionaries to distinct liking users for all tweets
                for tweet, liking_users in all_liking_users.items():
                    distinct_liking_users[tweet] = list(set(liking_users))
                    for other_tweet, other_liking_users in all_liking_users.items():
                        if tweet != other_tweet:
                            distinct_liking_users[tweet] = list(set(distinct_liking_users[tweet]) - set(other_liking_users))
                return distinct_liking_users
            # compare all tweets regarding their retweeters that they have in common
            case "common_retweeters":
                all_retweeters = list()
                # get all individual retweeters for each tweet
                for tweet in tweets:
                    individual_retweeters = set()
                    # Set the initial search parameters
                    params = {
                        "id": tweet,
                        "max_results": 100,  # The maximum allowed by the Twitter API
                        "next_token": None
                    }
                    # get all retweeters of that tweet
                    while True:
                        retweeters = self._client.get_retweeters(**params)
                        for user in retweeters.data:
                            # Add retweeters to the list
                            individual_retweeters.add({
                                "id": user.id,
                                "name": user.name,
                                "screen_name": user.username
                            })

                        # Break out of the loop if we have reached the end of the search results
                        if not retweeters.meta["next_token"]:
                            break
                        else:
                            # Update the search parameters for the next iteration
                            params["next_token"] = retweeters.meta["next_token"]
                    # add set of individual retweeters current tweet to list
                    all_retweeters.append(individual_retweeters)
                # get intersection of all individual retweeters of all tweets
                common_retweeters = set.intersection(*map, all_retweeters)
                return common_retweeters
            # compare all tweets regarding their distinct retweeters
            case "distinct_retweeters":
                # init empty dicts to store all retweeters and distinct retweeters of all tweets
                all_retweeters = dict()
                distinct_retweeters = list()
                for tweet in tweets:
                    individual_retweeters = list()
                    # Set the initial search parameters
                    params = {
                        "id": tweet,
                        "max_results": 100,  # The maximum allowed by the Twitter API
                        "next_token": None
                    }
                    # get all retweeters of that tweet
                    while True:
                        retweeters_results = self._client.get_retweeters(**params)
                        for user in retweeters_results.data:
                            # Add the user to the list
                            individual_retweeters.add({
                                "id": user.id,
                                "name": user.name,
                                "screen_name": user.username
                            })

                        # Break out of the loop if we have reached the end of the search results
                        if not retweeters_results.meta["next_token"]:
                            break
                        else:
                            # Update the search parameters for the next iteration
                            params["next_token"] = retweeters_results.meta["next_token"]
                    # add set of individual retweeters of current tweet to list
                    all_retweeters[tweet] = individual_retweeters

                # filter dictionaries to distinct retweeters for all tweets
                for tweet, retweeters in all_retweeters.items():
                    distinct_retweeters[tweet] = list(set(retweeters))
                    for other_tweet, other_retweeters in all_retweeters.items():
                        if tweet != other_tweet:
                            distinct_retweeters[tweet] = list(set(distinct_retweeters[tweet]) - set(other_retweeters))
                return distinct_retweeters
            # if invalid comparison attribute was provided
            case _:
                raise ValueError("Invalid comparison attribute for {}".format(compare))
