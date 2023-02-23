# -*- coding: utf-8 -*-
import copy
import pickle
from datetime import datetime
from numbers import Number

import numpy as np
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

test_tweet = "Savage Love 🎶 #SavageLoveRemix"

test_sets = {test_user_id_1: set([1, 3, 5, 7]), test_user_id_2: set([3, 6, 7, 9]), test_user_id_3: set([0, 3, 7])}

test_dict = {test_tweet_id_1: 150, test_tweet_id_2: 23, test_tweet_id_3: 78}

dateformat = "%a %b %d %H:%M:%S %z %Y"

test_dates = {
    test_user_id_1: datetime.strptime("Mon Mar 16 11:19:30 +0000 2009", dateformat),
    test_user_id_2: datetime.strptime("Wed May 06 13:49:31 +0000 2009", dateformat),
    test_user_id_3: datetime.strptime("Sun Jun 27 19:10:20 +0000 2010", dateformat),
}


class TestBaseDataProcessor(PySNATestCase):

    maxDiff = None

    def test_calc_descriptive_metrics(self):
        # calc metrics
        results = self.data_processor.calc_descriptive_metrics(copy.deepcopy(test_dict))
        # assert instances
        self.assertIsInstance(results, dict)
        assert any(isinstance(item, dict) for item in results.values())
        # reconstruct test results
        test_results = copy.deepcopy(test_dict)
        test_dict_values = list(test_dict.values())
        test_results["metrics"] = dict()
        test_results["metrics"]["max"] = max(test_dict_values)
        test_results["metrics"]["min"] = min(test_dict_values)
        test_results["metrics"]["mean"] = np.array(test_dict_values).mean()
        test_results["metrics"]["median"] = np.median(test_dict_values)
        test_results["metrics"]["std"] = np.std(test_dict_values)
        test_results["metrics"]["var"] = np.var(test_dict_values)
        test_results["metrics"]["range"] = max(test_dict_values) - min(test_dict_values)
        test_results["metrics"]["IQR"] = np.subtract(*np.percentile(test_dict_values, [75, 25]))
        test_results["metrics"]["mad"] = np.mean(np.absolute(test_dict_values - np.mean(test_dict_values)))
        # assert results to be equal
        self.assertDictEqual(results, test_results)
        pass

    def test_calc_datetime_metrics(self):
        # calc metrics
        results = self.data_processor.calc_datetime_metrics(copy.deepcopy(test_dates))
        # assert instances
        self.assertIsInstance(results, dict)
        assert any(isinstance(item, dict) for item in results.values())
        # reconstruct test results
        test_results = copy.deepcopy(test_dates)
        # convert datetime to string
        test_results = {k: dt.isoformat() for k, dt in test_results.items()}
        metrics = {
            "deviation_from_mean": {test_user_id_1: {"days": -174, "seconds": 73983}, test_user_id_2: {"days": -123, "seconds": 82984}, test_user_id_3: {"days": 295, "seconds": 15833}},
            "deviation_from_median": {test_user_id_1: {"days": -52, "seconds": 77399}, test_user_id_2: {"days": 0, "seconds": 0}, test_user_id_3: {"days": 417, "seconds": 19249}},
            "time_span": {"days": 468, "seconds": 28250, "microseconds": 0},
            "mean": "2009-09-05T14:46:27+00:00",
            "median": "2009-05-06T13:49:31+00:00",
            "max": "2010-06-27T19:10:20+00:00",
            "min": "2009-03-16T11:19:30+00:00",
        }
        test_results["metrics"] = metrics
        # ensure response
        self.assertDictEqual(results, test_results)

    def test_intersection(self):
        # calc intersection
        results = self.data_processor.intersection(test_sets.values())
        # assert instances
        self.assertIsInstance(results, list)
        assert all(isinstance(item, Number) for item in results)
        # assert results to be equal
        self.assertListEqual(results, [3, 7])

    def test_difference(self):
        # calc difference
        results = self.data_processor.difference(test_sets)
        # assert instances
        # assert dict
        self.assertIsInstance(results, dict)
        # assert list as dict values
        assert all(isinstance(item, list) for item in results.values())
        # assert numbers as list entries
        assert all(isinstance(entry, Number) for item in results.values() for entry in item)
        # assert results to be equal
        self.assertDictEqual(results, {test_user_id_1: [1, 5], test_user_id_2: [9, 6], test_user_id_3: [0]})


class TestTwitterDataProcessor(PySNATestCase):

    maxDiff = None

    @tape.use_cassette("tests/cassettes/user_obj.yaml")
    def test_extract_followers(self):
        cassette_user = self.api.fetcher.get_user_object(test_user_id_1)
        results = self.data_processor.extract_followers(cassette_user)
        # ensure instances
        self.assertIsInstance(results, dict)
        # compare with fixture
        with open("tests/fixtures/extract_followers.pickle", "rb") as handle:
            test_results = pickle.load(handle)
        self.assertDictEqual(results, test_results)

    @tape.use_cassette("tests/cassettes/user_obj2.yaml")
    def test_extract_followees(self):
        cassette_user = self.api.fetcher.get_user_object(test_user_id_1)
        results = self.data_processor.extract_followees(cassette_user)
        # ensure instances
        self.assertIsInstance(results, dict)
        # compare with fixture
        with open("tests/fixtures/extract_followees.pickle", "rb") as handle:
            test_results = pickle.load(handle)
        self.assertDictEqual(results, test_results)

    def test_clean_tweet(self):
        # generate test result
        result = self.data_processor.clean_tweet(test_tweet)
        # ensure instances
        self.assertIsInstance(result, str)
        # compare with expected result
        self.assertEqual(result, "Savage Love SavageLoveRemix")

    def test_detect_tweet_sentiment(self):
        function_response = self.data_processor.detect_tweet_sentiment(test_tweet)
        self.assertIsInstance(function_response, dict)
        self.assertEqual(function_response["label"], "positive")

    @tape.use_cassette("tests/cassettes/calc_similarity_users.yaml")
    def test_calc_similarity_users(self):
        # get serialized user objects first
        user_objs = [self.fetcher.get_user_object(user)._json for user in [test_user_id_1, test_user_id_2, test_user_id_3]]
        # generate results
        results = self.data_processor.calc_similarity(user_objs=user_objs, features=["followers_count", "friends_count", "listed_count", "favourites_count", "statuses_count"])
        # assert instances
        self.assertIsInstance(results, dict)
        assert all(isinstance(key, tuple) for key in results.keys())
        assert all(isinstance(value, Number) for value in results.values())
        # compare with fixture
        with open("tests/fixtures/calc_similarity_users.pickle", "rb") as handle:
            test_results = pickle.load(handle)
        self.assertDictEqual(results, test_results)

    @tape.use_cassette("tests/cassettes/calc_similarity_tweets.yaml")
    def test_calc_similarity_tweet(self):
        # get public metrics from Tweet objects first
        public_metrics = {tweet_id: self.fetcher.get_public_metrics(tweet_id) for tweet_id in [test_tweet_id_1, test_tweet_id_2, test_tweet_id_3]}
        # generate results
        results = self.data_processor.calc_similarity(tweet_metrics=public_metrics, features=["retweet_count", "reply_count", "like_count"])
        # assert instances
        self.assertIsInstance(results, dict)
        assert all(isinstance(key, tuple) for key in results.keys())
        assert all(isinstance(value, Number) for value in results.values())
        # compare with fixture
        with open("tests/fixtures/calc_similarity_tweets.pickle", "rb") as handle:
            test_results = pickle.load(handle)
        self.assertDictEqual(results, test_results)
