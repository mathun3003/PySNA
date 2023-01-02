# -*- coding: utf-8 -*-
from typing import List, Optional

from tweepy import API


class TwitterAPI(API):
    """_summary_
    # TODO: fill me
    Args:
        API (_type_): Twitter API class in order to interact with the Twitter Search API v2. Enhanced tweepy.API object.
    """

    def user_info(self, *, user_id=None, screen_name=None, attributes: List[str], **kwargs) -> dict:
        """_summary_
        Receive requested user information from Twitter User Object
        Args:
            user_id (str, optional): Twitter User ID. Defaults to None.
            username (str, optional): Twitter Username or Screen Name respectively. Defaults to None.
            attributes (List[str]): 'id', 'id_str', 'name', 'screen_name', 'followers_info', 'friends_info', 'location', 'profile_location', 'description', 'url', 'entities', 'protected', 'followers_count', 'friends_count', 'listed_count', 'created_at', 'favourites_count', 'utc_offset', 'time_zone', 'geo_enabled', 'verified', 'statuses_count', 'lang', 'status', 'contributors_enabled', 'is_translator', 'is_translation_enabled', 'profile_background_color', 'profile_background_image_url', 'profile_background_image_url_https', 'profile_background_tile', 'profile_image_url', 'profile_image_url_https', 'profile_banner_url', 'profile_link_color', 'profile_sidebar_border_color', 'profile_sidebar_fill_color', 'profile_text_color', 'profile_use_background_image', 'has_extended_profile', 'default_profile', 'default_profile_image', 'following', 'follow_request_sent', 'notifications', 'translator_type', 'withheld_in_countries'

        Raises:
            ValueError: User ID must be provided in string format.
            ValueError: User name must be provided in string format.
            TypeError: Eiher user ID or user name has to be provided, not both.
            TypeError: Either user ID or user name has to be provided.
        """

        # if user ID is provided
        if user_id:
            # check instance
            if not isinstance(user_id, str):
                raise ValueError("User ID must be a string, not {}".format(type(user_id)))
        # if username if provided
        elif screen_name:
            # check instance
            if not isinstance(screen_name, str):
                raise ValueError("User must be a string, not {}".format(type(screen_name)))
        # if both were provided
        elif screen_name and user_id:
            raise TypeError("Expected user ID or username, not both")
        # if none was provided
        else:
            raise TypeError("ID or username is required")

        # get user via tweepy
        user = API.get_user(self, user_id=user_id, screen_name=screen_name, kwargs=kwargs)

        # initialize dict to store requested attributes
        user_info = {"id": user.id, "name": user.name, "screen_name": user.screen_name}

        # loop through the list of attributes and add them to the dictionary
        for attr in attributes:
            if attr in user._json.keys():
                user_info[attr] = user._json[attr]
            elif attr == "followers_info":
                user_info[attr] = {
                    "follower_ids": user.follower_ids(),
                    "follower_names": [follower.name for follower in user.followers()],
                    "follower_screen_names": [follower.screen_name for follower in user.followers()],
                }
            elif attr == "friends_info":
                friend_ids = [friend.id for friend in user.friends()]
                user_info[attr] = {
                    "friend_ids": friend_ids,
                    "friend_names": [friend.name for friend in user.friends()],
                    "friend_screen_names": [friend.screen_name for friend in user.friends()],
                }
            else:
                raise KeyError("Invalid attribute for {}".format(attr))

        return user_info

    def compare_users(self, user1, user2, compare: str):
        """_summary_
        # TODO: fill me
        Args:
            user1 (_type_): _description_
            user2 (_type_): _description_
            compare (str): _description_
        """
        pass

    def compare_tweets(self, tweets: List[str], compare: str):
        """_summary_
        # TODO: fill me
        Args:
            tweets (List[str]): _description_
            compare (str): _description_
        """
        pass
