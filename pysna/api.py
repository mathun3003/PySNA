# -*- coding: utf-8 -*-
import logging
from typing import List

from tweepy import API


class TwitterAPI(API):
    """_summary_
    # TODO: fill me
    Args:
        API (_type_): Twitter API class in order to interact with the Twitter Search API v2. Enhanced tweepy.API object.
    """

    def _get_user_object(self, user: str):
        """_summary_
        # TODO: fill me
        Args:
            user (str): _description_

        Returns:
            _type_: _description_
        """
        # check if string for user1 is convertible to int in order to check for user ID or screen name
        if user.isdigit():
            # get profile for user1 by user ID
            user_obj = API.get_user(self, user_id=user)
        else:
            # get profile for user1 by screen name
            user_obj = API.get_user(self, screen_name=user)
        return user_obj

    def _get_user_followers(self, user: str):
        """_summary_
        # TODO: fill me
        Args:
            user (str): _description_

        Returns:
            _type_: _description_
        """
        # check if string for user1 is convertible to int in order to check for user ID or screen name
        if user.isdigit():
            # get profile for user1 by user ID
            user_followers = API.get_follower_ids(self, user_id=user)
        else:
            # get profile for user1 by screen name
            user_followers = API.get_follower_ids(self, screen_name=user)
        return user_followers

    def _get_user_follows(self, user: str):
        """_summary_
        # TODO: fill me
        Args:
            user (str): _description_

        Returns:
            _type_: _description_
        """
        if user.isdigit():
            user_follows = API.get_friend_ids(self, user_id=user)
        else:
            user_follows = API.get_friend_ids(self, screen_name=user)
        return user_follows

    def user_info(self, user: str, attributes: List[str], **kwargs) -> dict:
        """_summary_
        Receive requested user information from Twitter User Object
        Args:
            user (str): Twitter User either specified by corresponding ID or screen name.
            attributes (List[str]): 'id', 'id_str', 'name', 'screen_name', 'followers_info', 'follows_info', 'location', 'profile_location', 'description', 'url', 'entities', 'protected', 'followers_count', 'friends_count', 'listed_count', 'created_at', 'favourites_count', 'utc_offset', 'time_zone', 'geo_enabled', 'verified', 'statuses_count', 'lang', 'status', 'contributors_enabled', 'is_translator', 'is_translation_enabled', 'profile_background_color', 'profile_background_image_url', 'profile_background_image_url_https', 'profile_background_tile', 'profile_image_url', 'profile_image_url_https', 'profile_banner_url', 'profile_link_color', 'profile_sidebar_border_color', 'profile_sidebar_fill_color', 'profile_text_color', 'profile_use_background_image', 'has_extended_profile', 'default_profile', 'default_profile_image', 'following', 'follow_request_sent', 'notifications', 'translator_type', 'withheld_in_countries'

        Raises:
            ValueError: User ID must be provided in string format.
            ValueError: User name must be provided in string format.
            TypeError: Eiher user ID or user name has to be provided, not both.
            TypeError: Either user ID or user name has to be provided.
        """

        # get user object via tweepy
        user_obj = self._get_user_object(user)

        # initialize dict to store requested attributes
        user_info = {"id": user_obj.id, "name": user_obj.name, "screen_name": user_obj.screen_name}

        # loop through the list of attributes and add them to the dictionary
        for attr in attributes:
            if attr in user_obj._json.keys():
                user_info[attr] = user_obj._json[attr]
            elif attr == "followers_info":
                user_info[attr] = {
                    "follower_ids": user_obj.follower_ids(),
                    "follower_names": [follower.name for follower in user_obj.followers()],
                    "follower_screen_names": [follower.screen_name for follower in user_obj.followers()],
                }
            elif attr == "follows_info":
                follows_ids = [friend.id for friend in user_obj.friends()]
                user_info[attr] = {
                    "follows_ids": follows_ids,
                    "follows_names": [friend.name for friend in user_obj.friends()],
                    "follows_screen_names": [friend.screen_name for friend in user_obj.friends()],
                }
            else:
                raise KeyError("Invalid attribute for {}".format(attr))

        return user_info

    # TODO: convert to list of users and list of compare attributes
    def compare_users(self, user1: str, user2: str, compare: str):
        """_summary_
        # TODO: fill me
        Args:
            user1 (_type_): _description_
            user2 (_type_): _description_
            compare (str): _description_
        """

        # match compare attributes
        match compare:
            # compare number of followers
            case "num_followers":
                user1_obj, user2_obj = self._get_user_object(user1), self._get_user_object(user2)
                return {"user1_followers": user1_obj.followers_count(),
                        "user2_followers": user2_obj.followers_count()}
            # compare number of friends
            case "num_friends":
                user1_obj, user2_obj = self._get_user_object(user1), self._get_user_object(user2)
                return {"user1_friends": user1_obj.friends_count(),
                        "user2_friends": user2_obj.friends_count()}
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
                return {"user1_unique_followers": list(user1_unique_followers),
                        "user2_unique_followers": list(user2_unique_followers)}
            # compare common follows
            case "common_follows":
                user1_follows, user2_follows = self._get_user_follows(user1), self._get_user_follows(user2)
               # get intersectoin of both users
                common_followers = user1_follows.intersection(user2_follows)
                return list(common_followers)
            # compare unique follows
            case "unique_follows":
                user1_follows, user2_follows = self._get_user_follows(user1), self._get_user_follows(user2)
                # get unique followers
                user1_unique_follows = user1_follows.difference(user2_follows)
                user2_unique_follows = user2_follows.difference(user1_follows)
                return {"user1_unique_follows": list(user1_unique_follows),
                        "user2_unique_follows": list(user2_unique_follows)}
            case "created_at":
                user1_obj, user2_obj = self._get_user_object(user1), self._get_user_object(user2)
                # FIXME: #? time diff will be negative if user1 was created after user2. Still okay? #?
                time_difference_in_seconds = (user2_obj.created_at - user1_obj.created_at).total_seconds()
                time_difference_in_days = time_difference_in_seconds // 86400
                time_difference_in_weeks = time_difference_in_days // 7
                time_difference_in_hours = time_difference_in_seconds // 3600
                return {"time_difference_in_seconds": time_difference_in_seconds,
                        "time_difference_in_days": time_difference_in_days,
                        "time_difference_in_weeks": time_difference_in_weeks,
                        "time_difference_in_hours": time_difference_in_hours}
            case _:
                raise ValueError("Invalid compare attribute for {}".format(compare))


        #* response from ChatGPT

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

    def compare_tweets(self, tweets: List[str], compare: str):
        """_summary_
        # TODO: fill me
        Args:
            tweets (List[str]): _description_
            compare (str): _description_
        """
        pass
