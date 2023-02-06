# -*- coding: utf-8 -*-
from typing import Any

import tweepy
from tweepy import API, Client
from tweepy.auth import OAuth1UserHandler, OAuth2UserHandler, OAuthHandler


class TwitterClient(Client):
    def __init__(self, bearer_token: Any | None = None, consumer_key: Any | None = None, consumer_secret: Any | None = None, access_token: Any | None = None, access_token_secret: Any | None = None, wait_on_rate_limit: bool = True, **kwargs):
        # super(self.__class__, self).__init__(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret, wait_on_rate_limit=wait_on_rate_limit)
        self.bearer_token = bearer_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.wait_on_rate_limit = wait_on_rate_limit
        Client.__init__(
            self, bearer_token=self.bearer_token, consumer_key=self.consumer_key, consumer_secret=self.consumer_secret, access_token=self.access_token, access_token_secret=self.access_token_secret, wait_on_rate_limit=self.wait_on_rate_limit
        )

    pass


class TwitterAppAuthHandler(API):
    def __init__(self, consumer_key: Any | None, consumer_secret: Any | None, wait_on_rate_limit: bool = True, **kwargs):
        # super(self.__class__, self).__init__(tweepy.AppAuthHandler(consumer_key, consumer_secret), wait_on_rate_limit=wait_on_rate_limit)
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.wait_on_rate_limit = wait_on_rate_limit
        API.__init__(self, tweepy.AppAuthHandler(self.consumer_key, self.consumer_secret), wait_on_rate_limit=self.wait_on_rate_limit)

    pass


class TwitterUserHandler(OAuth2UserHandler):
    pass


class TwitterOAuthHandler(OAuthHandler):
    pass


class TwitterOAuth1UserHandler(OAuth1UserHandler):
    pass


# TODO: add Telegram API Client
