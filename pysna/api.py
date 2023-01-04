# -*- coding: utf-8 -*-
import logging
from typing import List, Set

import tweepy
from tweepy import API, Client


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

    def user_info(self, user: str, attributes: List[str]) -> dict:
        """Receive requested user information from Twitter User Object

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
            KeyError: If undefined attribute was provided

        Returns:
            dict: Requested user information
        """

        # get user object via tweepy
        user_obj = self._get_user_object(user)

        # initialize empty dict to store requested attributes
        user_info = dict()

        # loop through the list of attributes and add them to the dictionary
        for attr in attributes:
            if attr in user_obj._json.keys():
                user_info[attr] = user_obj._json[attr]
            elif attr == "followers_info":
                # TODO: optimize runtime with only one list walk through
                user_info[attr] = {
                    "follower_ids": user_obj.follower_ids(),
                    "follower_names": [follower.name for follower in user_obj.followers()],
                    "follower_screen_names": [follower.screen_name for follower in user_obj.followers()],
                }
            elif attr == "follows_info":
                # TODO: optimize runtime with only one list walk through
                follows_ids = [friend.id for friend in user_obj.friends()]
                user_info[attr] = {
                    "follows_ids": follows_ids,
                    "follows_names": [friend.name for friend in user_obj.friends()],
                    "follows_screen_names": [friend.screen_name for friend in user_obj.friends()],
                }
            else:
                raise ValueError("Invalid attribute for {}".format(attr))

        return user_info

    def compare_users(self, user1: str, user2: str, compare: str) -> dict | list:
        """Compare two users with the specified comparison attribute

        Args:
            user1 (str): User ID or screen name
            user2 (str): User ID or screen name
            compare (str): 'num_followers', 'num_follows', 'common_followers',
            'unique_followers', 'common_follows', 'unique_follows', 'created_at'
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
            # compare unique followers
            case "unique_followers":
                user1_followers, user2_followers = self._get_user_followers(user1), self._get_user_followers(user2)
                # get unique followers
                user1_unique_followers = user1_followers.difference(user2_followers)
                user2_unique_followers = user2_followers.difference(user1_followers)
                return {f"{user1}_unique_followers": list(user1_unique_followers),
                        f"{user2}_unique_followers": list(user2_unique_followers)}
            # compare common follows
            case "common_follows":
                user1_follows, user2_follows = self._get_user_follows(user1), self._get_user_follows(user2)
               # get intersectoin of both users
                common_follows = user1_follows.intersection(user2_follows)
                return list(common_follows)
            # compare unique follows
            case "unique_follows":
                user1_follows, user2_follows = self._get_user_follows(user1), self._get_user_follows(user2)
                # get unique followers
                user1_unique_follows = user1_follows.difference(user2_follows)
                user2_unique_follows = user2_follows.difference(user1_follows)
                return {f"{user1}_unique_follows": list(user1_unique_follows),
                        f"{user2}_unique_follows": list(user2_unique_follows)}
            # compare creation date
            case "created_at":
                user1_obj, user2_obj = self._get_user_object(user1), self._get_user_object(user2)
                # FIXME: #? time diff will be negative if user1 was created after user2. Still okay? #?
                time_difference_in_seconds = (user2_obj.created_at - user1_obj.created_at).total_seconds()
                time_difference_in_days = time_difference_in_seconds // 86400
                time_difference_in_weeks = time_difference_in_days // 7
                time_difference_in_hours = time_difference_in_seconds // 3600
                return {"time_difference_in_seconds": time_difference_in_seconds,
                        "time_difference_in_hours": time_difference_in_hours,
                        "time_difference_in_days": time_difference_in_days,
                        "time_difference_in_weeks": time_difference_in_weeks}
            # if other comparison attribute was provided
            case _:
                raise ValueError("Invalid comparison attribute for {}".format(compare))


        #* alternative using list attribute as input

        # def compare_users(users, compare):
        #     # Authenticate to Twitter API
        #     auth = tweepy.OAuth1UserHandler(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        #     api = tweepy.API(auth)

        #     # Get user objects for all users in the list
        #     user_objs = []
        #     for user in users:
        #         user_objs.append(api.get_user(user))

        #     # Compare all users in the list based on the requested attribute
        #     if compare == 'num_followers':
        #         # Return the number of followers for each user
        #         followers = {}
        #         for user_obj in user_objs:
        #             followers[user_obj.screen_name] = user_obj.followers_count
        #         return followers
        #     elif compare == 'num_follows':
        #         # Return the number of follows for each user
        #         follows = {}
        #         for user_obj in user_objs:
        #             follows[user_obj.screen_name] = user_obj.friends_count
        #         return follows
        #     elif compare == 'common_followers':
        #         # Find the followers that all users have in common
        #         all_followers = []
        #         for user_obj in user_objs:
        #             all_followers.extend(api.followers_ids(user_obj.screen_name))
        #         common_followers = set(all_followers)
        #         for user_obj in user_objs:
        #             common_followers = common_followers.intersection(api.followers_ids(user_obj.screen_name))
        #         return list(common_followers)
        #     elif compare == 'unique_followers':
        #         # Find the unique followers for each user
        #         unique_followers = {}
        #         for user_obj in user_objs:
        #             user_followers = set(api.followers_ids(user_obj.screen_name))
        #             for other_user_obj in user_objs:
        #                 if user_obj.screen_name == other_user_obj.screen_name:
        #                     continue
        #                 user_followers = user_followers.difference(api.followers_ids(other_user_obj.screen_name))
        #             unique_followers[user_obj.screen_name] = list(user_followers)
        #         return unique_followers
        #     elif compare == 'created_at':
        #         # Compare the creation dates of all users
        #         time_differences = {}
        #         for i, user1_obj in enumerate(user_objs):
        #             for j, user2_obj in enumerate(user_objs):
        #                 if i == j:
        #                     continue
        #                 time_difference_in_seconds = (user2_obj.created_at - user1_obj.created_at).total_seconds()
        #                 time_differences[f"{user1_obj.screen_name} - {user2_obj.screen_name}"] = time_difference_in_seconds
        #         return time_differences
        #     else:
        #         return 'Invalid compare attribute'


    #* same with list of users
    def compare_users_list(self, users: List[str], compare):

        # Get user objects for all users in the list
        user_objs = [self._get_user_object(user) for user in users]

        # Compare all users in the list based on the requested attribute
        comparison_results = {}
        for i, user1_obj in enumerate(user_objs):
            user1 = user1_obj.screen_name
            comparison_results[user1] = {}
            for j, user2_obj in enumerate(user_objs):
                if i == j:
                    continue
                user2 = user2_obj.screen_name
                if compare == 'followers':
                    comparison_results[user1][user2] = {'user1_followers': user1_obj.followers_count, 'user2_followers': user2_obj.followers_count}
                elif compare == 'friends':
                    comparison_results[user1][user2] = {'user1_friends': user1_obj.friends_count, 'user2_friends': user2_obj.friends_count}
                elif compare == 'common_followers':
                    user1_followers = set(API.get_follower_ids(self, user_id=user1))
                    user2_followers = set(API.get_follower_ids(self, user_id=user2))
                    common_followers = user1_followers.intersection(user2_followers)
                    comparison_results[user1][user2] = list(common_followers)
                elif compare == 'unique_follows':
                    user1_friends = set(API.get_friend_ids(self, user_id=user1))
                    user2_friends = set(API.get_friend_ids(self, user_id=user2))
                    user1_unique_follows = user1_friends.difference(user2_friends)
                    user2_unique_follows = user2_friends.difference(user1_friends)
                    comparison_results[user1][user2] = {'user1_unique_follows': list(user1_unique_follows), 'user2_unique_follows': list(user2_unique_follows)}
                elif compare == 'created_at':
                    time_difference_in_seconds = (user2_obj.created_at - user1_obj.created_at).total_seconds()
                    time_difference_in_days = time_difference_in_seconds // 86400
                    time_difference_in_weeks = time_difference_in_days // 7
                    time_difference_in_hours = time_difference_in_seconds // 3600
                    comparison_results[user1][user2] = {'time_difference_in_seconds': time_difference_in_seconds}


        pass

    def tweet_info(self, tweet_url: str, attributes: List[str]) -> dict:
        # get tweet object
        tweet_obj = self._get_tweet_object(tweet_url)

        # initialize empty dict to store request information
        tweet_info = dict()

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
