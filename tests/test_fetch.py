# -*- coding: utf-8 -*-
import pickle

import tweepy
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


class TestTwitterDataFetcher(PySNATestCase):

    maxDiff = None

    @tape.use_cassette("tests/cassettes/manual_request.yaml")
    def test_manual_request(self):
        url = f"https://api.twitter.com/2/users/{test_user_id_1}"
        cassette_response = self.fetcher._manual_request(url, "GET", additional_fields={"user.fields": ["username"]})
        self.assertIsInstance(cassette_response, dict)
        self.assertEqual(cassette_response["data"]["username"], test_username_1)
        with open("tests/fixtures/manual_request.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        self.assertDictEqual(cassette_response, expected_response)

    @tape.use_cassette("tests/cassettes/get_user_object.yaml")
    def test_get_user_object(self):
        # by screen name
        cassette_response_1 = self.fetcher.get_user_object(test_username_1)
        # by ID
        cassette_response_2 = self.fetcher.get_user_object(test_user_id_1)
        # ensure tweepy.models.User instance
        self.assertIsInstance(cassette_response_1, tweepy.models.User)
        self.assertIsInstance(cassette_response_2, tweepy.models.User)
        # ensure same User
        self.assertEqual(cassette_response_1._json["id"], test_user_id_1)
        self.assertEqual(cassette_response_2._json["screen_name"], test_username_1)
        # ensure same user object
        self.assertEqual(cassette_response_1, cassette_response_2)
        with open("tests/fixtures/get_user_object.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertDictEqual(cassette_response_1._json, expected_response)
        self.assertDictEqual(cassette_response_2._json, expected_response)

    @tape.use_cassette("tests/cassettes/get_user_follower_ids.yaml")
    def test_get_user_follower_ids(self):
        # by screen name
        cassette_response_1 = self.fetcher.get_user_follower_ids(test_username_1)
        # by ID
        cassette_response_2 = self.fetcher.get_user_follower_ids(test_user_id_1)
        # by string ID
        cassette_response_3 = self.fetcher.get_user_follower_ids(str(test_user_id_1))
        # ensure Set instance
        self.assertIsInstance(cassette_response_1, set)
        self.assertIsInstance(cassette_response_2, set)
        self.assertIsInstance(cassette_response_3, set)
        with open("tests/fixtures/get_user_follower_ids.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertSetEqual(cassette_response_1, expected_response)
        self.assertSetEqual(cassette_response_2, expected_response)
        self.assertSetEqual(cassette_response_3, expected_response)

    @tape.use_cassette("tests/cassettes/get_user_followee_ids.yaml")
    def test_get_user_followee_ids(self):
        # by screen name
        cassette_response_1 = self.fetcher.get_user_followee_ids(test_username_1)
        # by ID
        cassette_response_2 = self.fetcher.get_user_followee_ids(test_user_id_1)
        # by string ID
        cassette_response_3 = self.fetcher.get_user_followee_ids(str(test_user_id_1))
        # ensure Set instance
        self.assertIsInstance(cassette_response_1, set)
        self.assertIsInstance(cassette_response_2, set)
        self.assertIsInstance(cassette_response_3, set)
        with open("tests/fixtures/get_user_followee_ids.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertSetEqual(cassette_response_1, expected_response)
        self.assertSetEqual(cassette_response_2, expected_response)
        self.assertSetEqual(cassette_response_3, expected_response)

    @tape.use_cassette("tests/cassettes/get_latest_activity.yaml")
    def test_get_latest_activity(self):
        # by screen name
        cassette_response_1 = self.fetcher.get_latest_activity(test_username_1)
        # by ID
        cassette_response_2 = self.fetcher.get_latest_activity(test_user_id_1)
        # ensure dict instance
        self.assertIsInstance(cassette_response_1, dict)
        self.assertIsInstance(cassette_response_2, dict)
        # ensure that both cassettes are equal
        self.assertDictEqual(cassette_response_1, cassette_response_2)
        with open("tests/fixtures/get_latest_activity.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertDictEqual(cassette_response_1, expected_response)
        self.assertDictEqual(cassette_response_2, expected_response)

    @tape.use_cassette("tests/cassettes/get_lastest_activity_date.yaml")
    def test_get_latest_activity_date(self):
        # by screen name
        cassette_response_1 = self.fetcher.get_latest_activity_date(test_username_1)
        # by ID
        cassette_response_2 = self.fetcher.get_latest_activity_date(test_user_id_1)
        # ensure dict instance
        self.assertIsInstance(cassette_response_1, str)
        self.assertIsInstance(cassette_response_2, str)
        # ensure that both cassettes are equal
        self.assertEqual(cassette_response_1, cassette_response_2)
        with open("tests/fixtures/get_latest_activity_date.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertEqual(cassette_response_1, expected_response)
        self.assertEqual(cassette_response_2, expected_response)

    @tape.use_cassette("tests/cassettes/get_relationship.yaml")
    def test_get_relationship(self):
        # by screen name
        cassette_response_1 = self.fetcher.get_relationship(test_username_1, test_username_2)
        # by ID
        cassette_response_2 = self.fetcher.get_relationship(test_user_id_1, test_user_id_2)
        # by string ID
        cassette_response_3 = self.fetcher.get_relationship(str(test_user_id_1), str(test_user_id_2))
        # by ID and string ID
        cassette_response_4 = self.fetcher.get_relationship(str(test_user_id_1), test_user_id_2)
        cassette_response_5 = self.fetcher.get_relationship(test_user_id_1, str(test_user_id_2))
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

    @tape.use_cassette("tests/cassettes/get_relationship_pairs.yaml")
    def test_get_relationship_pairs(self):
        # generate results
        results = self.fetcher.get_relationship_pairs([test_user_id_1, test_user_id_2, test_user_id_3])
        # assert instances
        self.assertIsInstance(results, dict)
        assert all(isinstance(key, tuple) for key in results.keys())
        assert all(isinstance(value, dict) for value in results.values())
        # compare with fixture
        with open("tests/fixtures/get_relationship_pairs.pickle", "rb") as handle:
            test_results = pickle.load(handle)
        self.assertDictEqual(results, test_results)

    @tape.use_cassette("tests/cassettes/get_tweet_object.yaml")
    def test_get_tweet_object(self):
        # by int
        cassette_response_1 = self.fetcher.get_tweet_object(test_tweet_id_1)
        # by str
        cassette_response_2 = self.fetcher.get_tweet_object(str(test_tweet_id_1))
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

    @tape.use_cassette("tests/cassettes/get_liking_users_ids.yaml")
    def test_get_liking_users_ids(self):
        cassette_response_1 = self.fetcher.get_liking_users_ids(test_tweet_id_1)
        cassette_response_2 = self.fetcher.get_liking_users_ids(str(test_tweet_id_1))
        # ensure set instances
        self.assertIsInstance(cassette_response_1, list)
        self.assertIsInstance(cassette_response_2, list)
        # ensure same responses
        self.assertListEqual(cassette_response_1, cassette_response_2)
        # ensure all items are IDs
        assert all(isinstance(item, int) for item in cassette_response_1)
        assert all(isinstance(item, int) for item in cassette_response_2)
        with open("tests/fixtures/get_liking_users_ids.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertListEqual(cassette_response_1, expected_response)
        self.assertListEqual(cassette_response_2, expected_response)

    @tape.use_cassette("tests/cassettes/get_retweeters_ids.yaml")
    def test_get_retweeters_ids(self):
        cassette_response_1 = self.fetcher.get_retweeters_ids(test_tweet_id_1)
        cassette_response_2 = self.fetcher.get_retweeters_ids(str(test_tweet_id_1))
        # ensure set instances
        self.assertIsInstance(cassette_response_1, list)
        self.assertIsInstance(cassette_response_2, list)
        # ensure same responses
        self.assertListEqual(cassette_response_1, cassette_response_2)
        # ensure all items are IDs
        assert all(isinstance(item, int) for item in cassette_response_1)
        assert all(isinstance(item, int) for item in cassette_response_2)
        with open("tests/fixtures/get_retweeters_ids.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertListEqual(cassette_response_1, expected_response)
        self.assertListEqual(cassette_response_2, expected_response)

    @tape.use_cassette("tests/cassettes/get_quoting_users_ids.yaml")
    def test_get_quoting_users_ids(self):
        cassette_response_1 = self.fetcher.get_quoting_users_ids(test_tweet_id_1)
        cassette_response_2 = self.fetcher.get_quoting_users_ids(str(test_tweet_id_1))
        # ensure set instances
        self.assertIsInstance(cassette_response_1, list)
        self.assertIsInstance(cassette_response_2, list)
        # ensure same responses
        self.assertListEqual(cassette_response_1, cassette_response_2)
        # ensure all items are IDs
        assert all(isinstance(item, int) for item in cassette_response_1)
        assert all(isinstance(item, int) for item in cassette_response_2)
        with open("tests/fixtures/get_quoting_users_ids.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertListEqual(cassette_response_1, expected_response)
        self.assertListEqual(cassette_response_2, expected_response)

    @tape.use_cassette("tests/cassettes/get_liked_tweets_ids.yaml")
    def test_get_liked_tweets_ids(self):
        cassette_response_1 = self.fetcher.get_liked_tweets_ids(test_user_id_1, limit=10)
        cassette_response_2 = self.fetcher.get_liked_tweets_ids(str(test_user_id_1), limit=10)
        cassette_response_3 = self.fetcher.get_liked_tweets_ids(test_username_1, limit=10)
        # ensure set instances
        self.assertIsInstance(cassette_response_1, list)
        self.assertIsInstance(cassette_response_2, list)
        self.assertIsInstance(cassette_response_3, list)
        # ensure same responses
        self.assertListEqual(cassette_response_1, cassette_response_2)
        self.assertListEqual(cassette_response_1, cassette_response_3)
        self.assertListEqual(cassette_response_2, cassette_response_3)
        with open("tests/fixtures/get_liked_tweets_ids.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertListEqual(cassette_response_1, expected_response)
        self.assertListEqual(cassette_response_2, expected_response)
        self.assertListEqual(cassette_response_3, expected_response)

    @tape.use_cassette("tests/cassettes/get_composed_tweets_ids.yaml")
    def test_get_composed_tweets_ids(self):
        cassette_response_1 = self.fetcher.get_composed_tweets_ids(test_user_id_1, limit=100)
        cassette_response_2 = self.fetcher.get_composed_tweets_ids(str(test_user_id_1), limit=100)
        cassette_response_3 = self.fetcher.get_composed_tweets_ids(test_username_1, limit=100)
        # ensure set instances
        self.assertIsInstance(cassette_response_1, list)
        self.assertIsInstance(cassette_response_2, list)
        self.assertIsInstance(cassette_response_3, list)
        # ensure all items are IDs
        assert all(isinstance(item, int) for item in cassette_response_1)
        assert all(isinstance(item, int) for item in cassette_response_2)
        assert all(isinstance(item, int) for item in cassette_response_3)
        # ensure same responses
        self.assertListEqual(cassette_response_1, cassette_response_2)
        self.assertListEqual(cassette_response_1, cassette_response_3)
        self.assertListEqual(cassette_response_2, cassette_response_3)
        with open("tests/fixtures/get_composed_tweets_ids.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertListEqual(cassette_response_1, expected_response)
        self.assertListEqual(cassette_response_2, expected_response)
        self.assertListEqual(cassette_response_3, expected_response)

    @tape.use_cassette("tests/cassettes/get_botometer_scores.yaml")
    def test_get_botometer_scores(self):
        cassette_response_1 = self.fetcher.get_botometer_scores(test_user_id_1)
        cassette_response_2 = self.fetcher.get_botometer_scores(str(test_user_id_1))
        cassette_response_3 = self.fetcher.get_botometer_scores(test_username_1)
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

    @tape.use_cassette("tests/cassettes/get_context_annotations.yaml")
    def test_get_context_annotations(self):
        # by string
        cassette_response_1 = self.fetcher.get_context_annotations_and_entities(str(test_tweet_id_1))
        # by int
        cassette_response_2 = self.fetcher.get_context_annotations_and_entities(test_tweet_id_1)
        # ensure dict instance
        self.assertIsInstance(cassette_response_1, dict)
        self.assertIsInstance(cassette_response_2, dict)
        # ensure same responses
        self.assertDictEqual(cassette_response_1, cassette_response_2)
        with open("tests/fixtures/get_context_annotations_and_entities.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertDictEqual(cassette_response_1, expected_response)
        self.assertDictEqual(cassette_response_2, expected_response)

    @tape.use_cassette("tests/cassettes/get_public_metrics.yaml")
    def test_get_public_metrics(self):
        # by string
        cassette_response_1 = self.fetcher.get_public_metrics(str(test_tweet_id_1))
        # by int
        cassette_response_2 = self.fetcher.get_public_metrics(test_tweet_id_1)
        # ensure dict instance
        self.assertIsInstance(cassette_response_1, dict)
        self.assertIsInstance(cassette_response_2, dict)
        # ensure same responses
        self.assertDictEqual(cassette_response_1, cassette_response_2)
        with open("tests/fixtures/get_public_metrics.pickle", "rb") as handle:
            expected_response = pickle.load(handle)
        # ensure expected response
        self.assertDictEqual(cassette_response_1, expected_response)
        self.assertDictEqual(cassette_response_2, expected_response)
