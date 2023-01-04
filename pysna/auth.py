# -*- coding: utf-8 -*-
from tweepy import AppAuthHandler, Client
from tweepy.auth import OAuth2UserHandler, OAuthHandler


class TwitterClient(Client):
    pass


class TwitterAppAuthHandler(AppAuthHandler):
    pass


class TwitterUserHandler(OAuth2UserHandler):
    pass


class TwitterOAuthHandler(OAuthHandler):
    pass


# TODO: add Telegram API Client
