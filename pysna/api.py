# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, List, Literal, Set

import tweepy

from pysna.utils import strf_datetime

log = logging.getLogger(__name__)


class TwitterAPI(tweepy.Client):
    """Twitter API class in order to interact with the Twitter Search API v2."""

    def __init__(self, bearer_token: Any | None = None, consumer_key: Any | None = None, consumer_secret: Any | None = None,
                 access_token: Any | None = None, access_token_secret: Any | None = None, wait_on_rate_limit: bool = True):
        # inherit from tweepy.Client __init__
        super(self.__class__, self).__init__(bearer_token, consumer_key,
                                             consumer_secret, access_token,
                                             access_token_secret,
                                             wait_on_rate_limit=wait_on_rate_limit)
        # create a tweepy.AppAuthHandler instance
        _auth = tweepy.AppAuthHandler(consumer_key=consumer_key,
                                     consumer_secret=consumer_secret)
        # create a tweepy.API instance
        self._api = tweepy.API(_auth, wait_on_rate_limit=wait_on_rate_limit)
        # create a tweepy.Client instance from parent class
        self._client = super(self.__class__, self)


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

    def _get_user_followees(self, user: str) -> Set[int]:
        """Request Twitter follow IDs from user

        Args:
            user (str): Either User ID or screen name

        Returns:
            Set[int]: Array containing follow IDs
        """
        if user.isdigit():
            user_followees = self._api.get_friend_ids(user_id=user)
        else:
            user_followees = self._api.get_friend_ids(screen_name=user)
        return set(user_followees)

    def _get_tweet_object(self, tweet: int | str, additional_fields: Dict[str, List[str]]):
        """_summary_

        Args:
            tweet (str): _description_

        Returns:
            tweepy.Tweet: _description_

        Reference: https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet
        """
        tweet_obj = self._client.get_tweet(id=tweet, **additional_fields)
        return tweet_obj

    def _get_all_liking_users(self, tweet: str | int) -> Set[int]:
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

    def _get_all_retweeters(self, tweet: str | int) -> Set[int]:
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

    def _get_all_quoting_users(self, tweet: str | int) -> Set[int]:
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

    def _get_all_liked_tweets(self, user: str | int) -> set:
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

    def _get_all_composed_tweets(self, user: str | int):
        # init empty set to store all composed Tweets
        composed_tweets = set()
        # set request params
        params = {"id": user, "max_results": 100, "pagination_token": None}

        while True:
            response = self._client.get_users_tweets(**params)
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


    LITERALS_USER_INFO = Literal['id', 'id_str', 'name', 'screen_name', 'followers_info',
            'followees_info', 'location', 'profile_location', 'description', 'url', 'entities',
            'protected', 'followers_count', 'friends_count', 'listed_count', 'created_at', 'liked_tweets', 'composed_tweets',
            'favourites_count', 'utc_offset', 'time_zone', 'geo_enabled', 'verified', 'statuses_count',
            'lang', 'status', 'contributors_enabled', 'is_translator', 'is_translation_enabled', 'profile_background_color',
            'profile_background_image_url', 'profile_background_image_url_https', 'profile_background_tile', 'profile_image_url',
            'profile_image_url_https', 'profile_banner_url', 'profile_link_color', 'profile_sidebar_border_color',
            'profile_sidebar_fill_color', 'profile_text_color', 'profile_use_background_image', 'has_extended_profile',
            'default_profile', 'default_profile_image', 'following', 'follow_request_sent', 'notifications',
            'translator_type', 'withheld_in_countries']

    def user_info(self, user: str | int, attributes: List[LITERALS_USER_INFO]) -> dict:
        """Receive requested user information from Twitter User Object.

        Args:
            user (str): Twitter User either specified by corresponding ID or screen name.
            attributes (List[str]): 'id', 'id_str', 'name', 'screen_name', 'followers_info', 'liked_tweets',
            'followees_info', 'location', 'profile_location', 'description', 'url', 'entities', 'composed_tweets',
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
            # get followees information
            elif attr == "followees_info":
                # define dict to store followees information
                user_info[attr] = dict.fromkeys(["followees_ids", "followees_names", "followees_screen_names"])
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
                liked_tweets = self._get_all_liked_tweets(user_id)
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
                composed_tweets = self._client._get_all_composed_tweets(user_id)
                user_info[attr] = composed_tweets
            # if invalid comparison attribute was provided
            else:
                raise ValueError("Invalid attribute for {}".format(attr))

        return user_info

    LITERALS_COMPARE_USERS = Literal['num_followers', 'num_followees', 'common_followers',
            'distinct_followers', 'common_followees', 'distinct_followees', 'created_at']

    def compare_users(self, user1: str, user2: str, compare: LITERALS_COMPARE_USERS) -> dict | list:
        """Compare two users with the specified comparison attribute

        Args:
            user1 (str): User ID or screen name
            user2 (str): User ID or screen name
            compare (str): 'num_followers', 'num_followees', 'common_followers',
            'distinct_followers', 'common_followees', 'distinct_followees', 'created_at'

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
            case "num_followees":
                user1_obj, user2_obj = self._get_user_object(user1), self._get_user_object(user2)
                return {f"{user1}_followees": user1_obj.friends_count,
                        f"{user2}_followees": user2_obj.friends_count}
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
            # compare common followees
            case "common_followees":
                user1_followees, user2_followees = self._get_user_followees(user1), self._get_user_followees(user2)
               # get intersectoin of both users
                common_followees = user1_followees.intersection(user2_followees)
                return list(common_followees)
            # compare distinct followees
            case "distinct_followees":
                user1_followees, user2_followees = self._get_user_followees(user1), self._get_user_followees(user2)
                # get distinct followers
                user1_distinct_followees = user1_followees.difference(user2_followees)
                user2_distinct_followees = user2_followees.difference(user1_followees)
                return {f"{user1}_distinct_followees": list(user1_distinct_followees),
                        f"{user2}_distinct_followees": list(user2_distinct_followees)}
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
            compare (str): 'num_followers', 'num_followees', 'common_followers',
            'distinct_followers', 'common_followees', 'distinct_followees'

        Raises:
            ValueError: If users list only contains one entry.
            ValueError: If invalid comparison attribute was provided.

        Returns:
            dict | list: Requested comparison attribute. Provide screen names
            to display them in the results.
        """
        # list must contain at least two elements
        assert len(users) > 1, "users list must contain at least two elements, {} was provided".format(len(users))

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
            case "num_followees":
                followees_dict = dict()
                for user in users:
                    tmp_user_obj = self._get_user_object(user)
                    followees_dict[user] = tmp_user_obj.friends_count
                return followees_dict
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
            # compare common followees
            case "common_followees":
                individual_followees = [self._get_user_followees(user) for user in users]
                common_followees = set.intersection(*map(set, individual_followees))
                return list(common_followees)
            # compare distinct followees
            case "distinct_followees":
                individual_followees = {user: self._get_user_followees(user) for user in users}
                distinct_followees = dict()
                for user, followees in individual_followees.items():
                    distinct_followees[user] = list(set(followees))
                    for other_user, other_followees in individual_followees.items():
                        if user != other_user:
                            distinct_followees[user] = list(set(distinct_followees[user]) - set(other_followees))
                return distinct_followees
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

    def compare_tweets(self, tweets: List[str | int], compare: LITERALS_COMPARE_TWEETS) -> dict | set:
        """Compare two or more Tweets with the specified comparison attribute.

        Args:
            tweets (List[str  |  int]): List of Tweet IDs.
            compare (str): Comparison attribute. Needs to be one of the following: 'num_views', 'num_likes', 'num_retweets', 'num_quotes',
            'common_quoting_users', 'distinct_quoting_users', 'common_liking_users', 'distinct_liking_users', 'common_retweeters', 'distinct_retweets'.

        Raises:
            AssertionError: If a list of one Tweet ID was provided.
            ValueError: If invalid comparison attribute was provided.

        Returns:
            dict | set: Requested results for comparison attribute.
        """
        # tweets list must contain at least two IDs
        assert len(tweets) > 1, "tweets list object needs at least two entries, not {}".format(len(tweets))

        # match comparison attribute
        match compare:
            # FIXME: #! media key object not found
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
            # FIXME: #! public_metrics not accessible
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
            case "common_quoting_users":
                all_quoting_users = list()
                # get all individual quoting users for each tweet
                for tweet in tweets:
                    # get individual quoting users
                    individual_qouting_users = self._get_all_quoting_users(tweet)
                    # add individual quoting users to list
                    all_quoting_users.append(individual_qouting_users)
                # get intersection of individual quoting users of all tweets
                common_quoting_users =  set.intersection(*map(set, all_quoting_users))
                # return quoting users
                return list(common_quoting_users)
            # get distinct quoting users of all Tweets
            case "distinct_quoting_users":
                all_quoting_users, distinct_quoting_users = dict(), dict()
                # get all individual quoting users for each tweet
                for tweet in tweets:
                    # get individual quoting users
                    individual_quoting_users = self._get_all_quoting_users(tweet)
                    # add set of individual liking users of current tweet to dict
                    all_quoting_users[tweet] = individual_quoting_users

                # filter dicts to distinct quoting users for all tweets
                for tweet, quoting_users in all_quoting_users.items():
                    distinct_quoting_users[tweet] = list(set(quoting_users))
                    for other_tweet, other_quoting_users in all_quoting_users.items():
                        if tweet != other_tweet:
                            distinct_quoting_users[tweet] = list(set(distinct_quoting_users[tweet]) - set(other_quoting_users))
                return distinct_quoting_users
            # get all liking users that all Tweets have in common
            case "common_liking_users":
                all_liking_users = list()
                # get all individual liking users for each tweet
                for tweet in tweets:
                    # get individual liking users
                    individual_liking_users = self._get_all_liking_users(tweet)
                    # add set of individual liking users of current tweet to list
                    all_liking_users.append(individual_liking_users)
                # get intersection of all individual liking users of all tweets
                common_liking_users = set.intersection(*map(set, all_liking_users))
                return list(common_liking_users)
            # get all distinct liking users of all tweets
            case "distinct_liking_users":
                # init empty dicts to store all liking users and distinct liking users of all tweets
                all_liking_users, distinct_liking_users = dict(), dict()
                for tweet in tweets:
                    # get individual liking users
                    individual_liking_users = self._get_all_liking_users(tweet)
                    # add set of individual liking users of current tweet to dict
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
                    individual_retweeters = self._get_all_retweeters(tweet)
                    # add set of individual retweeters current tweet to list
                    all_retweeters.append(individual_retweeters)
                # get intersection of all individual retweeters of all tweets
                common_retweeters = set.intersection(*map(set, all_retweeters))
                return list(common_retweeters)
            # compare all tweets regarding their distinct retweeters
            case "distinct_retweeters":
                # init empty dicts to store all retweeters and distinct retweeters of all tweets
                all_retweeters, distinct_retweeters = dict(), dict()
                for tweet in tweets:
                    individual_retweeters = self._get_all_retweeters(tweet)
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
