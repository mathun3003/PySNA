# -*- coding: utf-8 -*-
from typing import List

from tweepy import API


class TwitterAPI(API):
    """_summary_
    # TODO: fill me
    Args:
        tweepy (_type_): _description_
    """

    def user_info(self, user_identifier: str, attributes: List[str], additional_fields: List[str] = list()):
        """_summary_
        # TODO: fill me
        Args:
            user_identifier (str): _description_
            attributes (List[str]): _description_
        """
        # TODO: user_identifier should be either the user ID or the screen name

        pass

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
