# -*- coding: utf-8 -*-
from tweepy.auth import OAuth2UserHandler
from tweepy.client import Client


class TwitterClient(Client):
    pass


class TwitterUserHandler(OAuth2UserHandler):
    pass


# TODO: add Telegram API Client
