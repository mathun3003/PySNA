# -*- coding: utf-8 -*-
import os
import unittest

from dotenv import load_dotenv

from pysna.api import TwitterAPI
from pysna.fetch import TwitterDataFetcher
from pysna.process import TwitterDataProcessor

load_dotenv("local.env")

user_id = os.environ.get("TWITTER_USER_ID", "1072250532645998596")
username = os.environ.get("TWITTER_USERNAME", "TweepyDev")
bearer_token = os.environ.get("BEARER_TOKEN", "")
consumer_key = os.environ.get("CONSUMER_KEY", "")
consumer_secret = os.environ.get("CONSUMER_SECRET", "")
access_token = os.environ.get("ACCESS_KEY", "")
access_token_secret = os.environ.get("ACCESS_SECRET", "")
rapidapi_key = os.environ.get("X_RAPIDAPI_KEY")
rapidapi_host = os.environ.get("X_RAPIDAPI_HOST")


class PySNATestCase(unittest.TestCase):
    def setUp(self):
        self.bearer_token = bearer_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.rapidapi_key = rapidapi_key
        self.rapidapi_host = rapidapi_host

        self.api = TwitterAPI(self.bearer_token, self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret, self.rapidapi_key, self.rapidapi_host)

        self.fetcher = TwitterDataFetcher(self.bearer_token, self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret, self.rapidapi_key, self.rapidapi_host)

        self.data_processor = TwitterDataProcessor()
