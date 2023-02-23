# -*- coding: utf-8 -*-
import pickle
from typing import get_args

from config import PySNATestCase, tape

test_user_id_1 = 24677217
test_username_1 = "WWU_Muenster"

test_user_id_2 = 38180826
test_username_2 = "goetheuni"

test_user_id_3 = 160286320
test_username_3 = "UniKonstanz"

test_tweet_id_1 = 1612443577447026689
test_tweet_id_2 = 1611301422364082180
test_tweet_id_3 = 1612823288723476480

test_tweet = "Next I'm buying Coca-Cola to put the cocaine back in."


class TestTwitterAPI(PySNATestCase):

    maxDiff = None

    @tape.use_cassette("tests/cassettes/user_info.yaml")
    def test_user_info(self):
        user_info = self.api.user_info(test_username_1, get_args(self.api.LITERALS_USER_INFO))
        # Assert that the response matches the saved cassette
        cassette_response = user_info
        with open("tests/fixtures/user_info.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @tape.use_cassette("tests/cassettes/tweet_info.yaml")
    def test_tweet_info(self):
        cassette_response = self.api.tweet_info(test_tweet_id_1, get_args(self.api.LITERALS_TWEET_INFO))
        with open("tests/fixtures/tweet_info.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @tape.use_cassette("tests/cassettes/compare_users.yaml")
    def test_compare_users(self):
        cassette_response = self.api.compare_users([test_username_1, test_username_2, test_username_3], get_args(self.api.LITERALS_COMPARE_USERS), features=["followers_count", "friends_count", "listed_count", "favourites_count", "statuses_count"])
        with open("tests/fixtures/compare_users.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @tape.use_cassette("tests/cassettes/compare_tweets.yaml")
    def test_compare_tweets(self):
        cassette_response = self.api.compare_tweets(
            [test_tweet_id_1, test_tweet_id_2, test_tweet_id_3],
            get_args(self.api.LITERALS_COMPARE_TWEETS),
            features=["retweet_count", "like_count"],
        )
        with open("tests/fixtures/compare_tweets.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)
