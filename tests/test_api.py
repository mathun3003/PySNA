# -*- coding: utf-8 -*-
import os
import pickle
from typing import get_args

import tweepy
import vcr
from config import PySNATestCase
from dotenv import load_dotenv

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
        user_info = self.api.user_info(test_username_1, get_args(self.api.LITERALS_USER_INFO))
        # Assert that the response matches the saved cassette
        cassette_response = user_info
        with open("tests/fixtures/user_info.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @vcr.use_cassette("tests/cassettes/tweet_info.yaml")
    def test_tweet_info(self):
        cassette_response = self.api.tweet_info(test_tweet_id_1, get_args(self.api.LITERALS_TWEET_INFO))
        with open("tests/fixtures/tweet_info.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @vcr.use_cassette("tests/cassettes/compare_users.yaml")
    def test_compare_users(self):
        cassette_response = self.api.compare_users([test_username_1, test_username_2, test_username_3], get_args(self.api.LITERALS_COMPARE_USERS), features=["followers_count", "followees_count"])
        with open("tests/fixtures/compare_users.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @vcr.use_cassette("tests/cassettes/compare_tweets.yaml")
    def test_compare_tweets(self):
        cassette_response = self.api.compare_tweets(
            [test_tweet_id_1, test_tweet_id_2, test_tweet_id_3],
            get_args(self.api.LITERALS_COMPARE_TWEETS),
            features=["view_count", "retweet_count", "quote_count", "reply_count"],
        )
        with open("tests/fixtures/compare_tweets.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @vcr.use_cassette("tests/cassettes/manual_request.yaml")
    def test_manual_request(self):
        url = f"https://api.twitter.com/2/users/{test_user_id_1}"
        cassette_response = self.api._manual_request(url, "GET", additional_fields={"user.fields": ["username"]})
        self.assertIsInstance(cassette_response, dict)
        self.assertEqual(cassette_response["data"]["username"], test_username_1)
        with open("tests/fixtures/manual_request.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @vcr.use_cassette("tests/cassettes/get_user_object.yaml")
    def test_get_user_object(self):
        # by screen name
        cassette_response_1 = self.api._get_user_object(test_username_1)
        # by ID
        cassette_response_2 = self.api._get_user_object(test_user_id_1)
        # by string ID
        cassette_response_3 = self.api_get_user_object(str(test_user_id_1))
        # ensure tweepy.models.User instance
        self.assertIsInstance(cassette_response_1, tweepy.models.User)
        self.assertIsInstance(cassette_response_2, tweepy.models.User)
        self.assertIsInstance(cassette_response_3, tweepy.models.User)
        # ensure same User
        self.assertEqual(cassette_response_1._json["id"], test_user_id_1)
        self.assertEqual(cassette_response_2._json["screen_name"], test_username_1)
        self.assertEqual(cassette_response_3._json["screen_name"].test_username_1)
        # ensure same user object
        self.assertEqual(cassette_response_1, cassette_response_2)
        self.assertEqual(cassette_response_1, cassette_response_3)
        self.assertEqual(cassette_response_2, cassette_response_3)
        with open("tests/fixtures/get_user_object.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertDictEqual(cassette_response_1._json, expected_response)
        self.assertDictEqual(cassette_response_2._json, expected_response)
        self.assertDictEqual(cassette_response_3._json, expected_response)

    @vcr.use_cassette("tests/cassettes/get_user_followers.yaml")
    def test_get_user_followers(self):
        # by screen name
        cassette_response_1 = self.api._get_user_followers(test_username_1)
        # by ID
        cassette_response_2 = self.api._get_user_followers(test_user_id_1)
        # by string ID
        cassette_response_3 = self.api._get_user_followers(str(test_user_id_1))
        # ensure Set instance
        self.assertIsInstance(cassette_response_1, set)
        self.assertIsInstance(cassette_response_2, set)
        self.assertIsInstance(cassette_response_3, set)
        with open("tests/fixtures/get_user_followers.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertSetEqual(cassette_response_1, expected_response)
        self.assertSetEqual(cassette_response_2, expected_response)
        self.assertSetEqual(cassette_response_3, expected_response)

    @vcr.use_cassette("tests/cassettes/get_user_followees.yaml")
    def test_get_user_followees(self):
        # by screen name
        cassette_response_1 = self.api._get_user_followees(test_username_1)
        # by ID
        cassette_response_2 = self.api._get_user_followees(test_user_id_1)
        # by string ID
        cassette_response_3 = self.api._get_user_followees(str(test_user_id_1))
        # ensure Set instance
        self.assertIsInstance(cassette_response_1, set)
        self.assertIsInstance(cassette_response_2, set)
        self.assertIsInstance(cassette_response_3, set)
        with open("tests/fixtures/get_user_followees.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertSetEqual(cassette_response_1, expected_response)
        self.assertSetEqual(cassette_response_2, expected_response)
        self.assertSetEqual(cassette_response_3, expected_response)

    @vcr.use_cassette("tests/cassettes/get_relationship.yaml")
    def test_get_relationship(self):
        # by screen name
        cassette_response_1 = self.api._get_relationship(test_username_1, test_username_2)
        # by ID
        cassette_response_2 = self.api._get_relationship(test_user_id_1, test_user_id_2)
        # by string ID
        cassette_response_3 = self.api._get_relationship(str(test_user_id_1), str(test_user_id_2))
        # by ID and string ID
        cassette_response_4 = self.api._get_relationship(str(test_user_id_1), test_user_id_2)
        cassette_response_5 = self.api._get_relationship(test_user_id_1, str(test_user_id_2))
        # ensure Set instance
        self.assertIsInstance(cassette_response_1, dict)
        self.assertIsInstance(cassette_response_2, dict)
        self.assertIsInstance(cassette_response_3, dict)
        self.assertIsInstance(cassette_response_4, dict)
        self.assertIsInstance(cassette_response_5, dict)
        with open("tests/fixtures/get_relationship.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertDictEqual(cassette_response_1, expected_response)
        self.assertDictEqual(cassette_response_2, expected_response)
        self.assertDictEqual(cassette_response_3, expected_response)
        self.assertDictEqual(cassette_response_4, expected_response)
        self.assertDictEqual(cassette_response_5, expected_response)

    @vcr.use_cassette("tests/cassettes/get_tweet_object.yaml")
    def test_get_tweet_object(self):
        # by int
        cassette_response_1 = self.api._get_tweet_object(test_tweet_id_1)
        # by str
        cassette_response_2 = self.api._get_tweet_object(str(test_tweet_id_1))
        # ensure tweepy.models.Status instance
        self.assertIsInstance(cassette_response_1, tweepy.models.Status)
        self.assertIsInstance(cassette_response_2, tweepy.models.Status)
        # ensure same status object
        self.assertEqual(cassette_response_1, cassette_response_2)
        with open("tests/fixtures/get_tweet_object.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertDictEqual(cassette_response_1._json, expected_response)
        self.assertDictEqual(cassette_response_2._json, expected_response)

    @vcr.use_cassette("tests/cassettes/get_all_liking_users.yaml")
    def test_get_all_liking_users(self):
        cassette_response_1 = self.api.get_all_liking_users(test_tweet_id_1)
        cassette_response_2 = self.api.get_all_liking_users(str(test_tweet_id_1))
        # ensure set instances
        self.assertIsInstance(cassette_response_1, set)
        self.assertIsInstance(cassette_response_2, set)
        # ensure same responses
        self.assertSetEqual(cassette_response_1, cassette_response_2)
        with open("tests/fixtures/get_all_liking_users.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertSetEqual(cassette_response_1, expected_response)
        self.assertSetEqual(cassette_response_2, expected_response)

    @vcr.use_cassette("tests/cassettes/get_all_retweeters.yaml")
    def test_get_all_retweeters(self):
        cassette_response_1 = self.api.get_all_retweeters(test_tweet_id_1)
        cassette_response_2 = self.api.get_all_retweeters(str(test_tweet_id_1))
        # ensure set instances
        self.assertIsInstance(cassette_response_1, set)
        self.assertIsInstance(cassette_response_2, set)
        # ensure same responses
        self.assertSetEqual(cassette_response_1, cassette_response_2)
        with open("tests/fixtures/get_all_retweeters.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertSetEqual(cassette_response_1, expected_response)
        self.assertSetEqual(cassette_response_2, expected_response)

    @vcr.use_cassette("tests/cassettes/get_all_quoting_users.yaml")
    def test_get_all_quoting_users(self):
        cassette_response_1 = self.api.get_all_quoting_users(test_tweet_id_1)
        cassette_response_2 = self.api.get_all_quoting_users(str(test_tweet_id_1))
        # ensure set instances
        self.assertIsInstance(cassette_response_1, set)
        self.assertIsInstance(cassette_response_2, set)
        # ensure same responses
        self.assertSetEqual(cassette_response_1, cassette_response_2)
        with open("tests/fixtures/get_all_quoting_users.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertSetEqual(cassette_response_1, expected_response)
        self.assertSetEqual(cassette_response_2, expected_response)

    @vcr.use_cassette("tests/cassettes/get_all_liked_tweets.yaml")
    def test_get_all_liked_tweets(self):
        cassette_response_1 = self.api.get_all_liked_tweets(test_user_id_1)
        cassette_response_2 = self.api.get_all_liked_tweets(str(test_user_id_1))
        cassette_response_3 = self.api.get_all_liked_tweets(test_username_1)
        # ensure set instances
        self.assertIsInstance(cassette_response_1, set)
        self.assertIsInstance(cassette_response_2, set)
        self.assertIsInstance(cassette_response_3, set)
        # ensure same responses
        self.assertSetEqual(cassette_response_1, cassette_response_2)
        self.assertSetEqual(cassette_response_1, cassette_response_3)
        self.assertSetEqual(cassette_response_2, cassette_response_3)
        with open("tests/fixtures/get_all_liked_tweets.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertSetEqual(cassette_response_1, expected_response)
        self.assertSetEqual(cassette_response_2, expected_response)
        self.assertSetEqual(cassette_response_3, expected_response)

    # TODO: test after function was rewritten
    @vcr.use_cassette("tests/cassettes/get_all_composed_tweets.yaml")
    def test_get_all_composed_tweets(self):
        cassette_response_1 = self.api.get_all_composed_tweets(test_user_id_1)
        cassette_response_2 = self.api.get_all_composed_tweets(str(test_user_id_1))
        cassette_response_3 = self.api.get_all_composed_tweets(test_username_1)
        # ensure set instances
        self.assertIsInstance(cassette_response_1, set)
        self.assertIsInstance(cassette_response_2, set)
        self.assertIsInstance(cassette_response_3, set)
        # ensure same responses
        self.assertSetEqual(cassette_response_1, cassette_response_2)
        self.assertSetEqual(cassette_response_1, cassette_response_3)
        self.assertSetEqual(cassette_response_2, cassette_response_3)
        with open("tests/fixtures/get_all_composed_tweets.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertSetEqual(cassette_response_1, expected_response)
        self.assertSetEqual(cassette_response_2, expected_response)
        self.assertSetEqual(cassette_response_3, expected_response)

    @vcr.use_cassette("tests/cassettes/get_botometer_scores.yaml")
    def test_get_botometer_scores(self):
        cassette_response_1 = self.api.get_botometer_scores(test_user_id_1)
        cassette_response_2 = self.api.get_botometer_scores(str(test_user_id_1))
        cassette_response_3 = self.api.get_botometer_scores(test_username_1)
        # ensure dict instances
        self.assertIsInstance(cassette_response_1, dict)
        self.assertIsInstance(cassette_response_2, dict)
        self.assertIsInstance(cassette_response_3, dict)
        # ensure same responses
        self.assertDictEqual(cassette_response_1, cassette_response_2)
        self.assertDictEqual(cassette_response_1, cassette_response_3)
        self.assertDictEqual(cassette_response_2, cassette_response_3)
        with open("tests/fixtures/get_botometer_scores.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertDictEqual(cassette_response_1, expected_response)
        self.assertDictEqual(cassette_response_2, expected_response)
        self.assertDictEqual(cassette_response_3, expected_response)

    def test_calc_descriptive_metrics(self):
        # TODO
        pass

    def test_calc_datetime_metrics(self):
        # TODO
        pass

    def test_get_tweet_sentiment(self):
        function_response = self.api.get_tweet_sentiment(test_tweet)
        self.assertIsInstance(function_response, str)
        self.assertEqual(function_response, "neutral")
