# -*- coding: utf-8 -*-
import os
import unittest

import vcr
from dotenv import load_dotenv

from pysna.api import TwitterAPI

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
use_replay = os.environ.get("USE_REPLAY", True)


tape = vcr.VCR(
    cassette_library_dir="tests/cassettes",
    filter_headers=["Authorization"],
    # Either use existing cassettes, or never use recordings:
    record_mode="none" if use_replay else "all",
)


class PySNATestCase(unittest.TestCase):
    def setUp(self):
        self.bearer_token = bearer_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret

        self.api = TwitterAPI(self.bearer_token, self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret, self.rapidapi_key, self.rapidapi_host)
