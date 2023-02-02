# -*- coding: utf-8 -*-
import os
import pickle
from typing import get_args

import vcr
from config import PySNATestCase
from dotenv import load_dotenv

test_user_id = "24677217"
test_username = "WWU_Muenster"
test_tweet_id = 1612443577447026689

load_dotenv("local.env")

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


class TestTwitterAPI(PySNATestCase):

    maxDiff = None

    @vcr.use_cassette("tests/cassettes/user_info.yaml")
    def test_user_info(self):
        user_info = self.api.user_info(test_username, get_args(self.api.LITERALS_USER_INFO))
        # Assert that the response matches the saved cassette
        cassette_response = user_info
        with open("tests/fixtures/user_info.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @vcr.use_cassette("tests/cassettes/tweet_info.yaml")
    def test_tweet_info(self):
        cassette_response = self.api.tweet_info(test_tweet_id, get_args(self.api.LITERALS_TWEET_INFO))
        with open("tests/fixtures/tweet_info.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @vcr.use_cassette("tests/cassettes/compare_users.yaml")
    def test_compare_users(self):
        cassette_response = self.api.compare_users(["WWU_Muenster", "goetheuni", "UniKonstanz"], get_args(self.api.LITERALS_COMPARE_USERS), features=["followers_count", "followees_count"])
        with open("tests/fixtures/compare_users.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @vcr.use_cassette("tests/cassettes/compare_tweets.yaml")
    def test_compare_tweets(self):
        cassette_response = self.api.compare_tweets(
            [1612443577447026689, 1611301422364082180, 1612823288723476480],
            get_args(self.api.LITERALS_COMPARE_TWEETS),
            features=["view_count", "retweet_count", "quote_count", "reply_count"],
        )
        with open("tests/fixtures/compare_tweets.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)
