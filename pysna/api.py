# -*- coding: utf-8 -*-
import logging
from typing import List, Literal, Set

import tweepy
from tweepy import API, Client

from pysna.utils import strf_datetime


class TwitterAPI(API, Client):
    """Twitter API class in order to interact with the Twitter Search API v2. Inherited from tweepy API class"""

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
            user_obj = API.get_user(self, user_id=user)
        else:
            # get profile for user1 by screen name
            user_obj = API.get_user(self, screen_name=user)
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
            user_followers = API.get_follower_ids(self, user_id=user)
        else:
            # get profile for user1 by screen name
            user_followers = API.get_follower_ids(self, screen_name=user)
        return set(user_followers)

    def _get_user_follows(self, user: str) -> Set[int]:
        """Request Twitter follow IDs from user

        Args:
            user (str): Either User ID or screen name

        Returns:
            Set[int]: Array containing follow IDs
        """
        if user.isdigit():
            user_follows = API.get_friend_ids(self, user_id=user)
        else:
            user_follows = API.get_friend_ids(self, screen_name=user)
        return set(user_follows)

    def _get_tweet_object(self, tweet: str) -> tweepy.Tweet:
        """_summary_

        Args:
            tweet (str): _description_

        Returns:
            tweepy.Tweet: _description_

        Reference: https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet
        """
        tweet_obj = API.get_oembed(self, url=tweet)
        return tweet_obj

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

    def tweet_info(self, tweet_url: str, attributes: List[str]) -> dict:
        # get tweet object
        tweet_obj = self._get_tweet_object(tweet_url)

        # initialize empty dict to store request information
        tweet_info = dict()
        # FIXME
        # loop through the list of attributes and add them to the dictionary
        for attr in attributes:
            if attr in tweet_obj.keys():
                tweet_info[attr] = tweet_obj.__dict__[attr]

        return tweet_info

    def compare_tweets(self, tweets: List[str], compare: str):
        """_summary_
        # TODO: fill me
        Args:
            tweets (List[str]): _description_
            compare (str): _description_
        """
        pass
