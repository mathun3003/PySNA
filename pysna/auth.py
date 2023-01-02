# -*- coding: utf-8 -*-
from tweepy import AppAuthHandler
from tweepy.auth import OAuth2UserHandler, OAuthHandler
from tweepy.client import Client


class TwitterClient(Client):
    pass


class TwitterAppAuthHandler(AppAuthHandler):
    pass


class TwitterUserHandler(OAuth2UserHandler):
    pass


class TwitterOAuthHandler(OAuthHandler):
    pass


# TODO: add Telegram API Client
