# -*- coding: utf-8 -*-
import operator
import re
from datetime import datetime, timezone
from numbers import Number
from typing import Dict, List

import numpy as np
import tweepy
from textblob import TextBlob

from pysna.fetch import TwitterDataFetcher


class BaseDataProcessor:
    """Base component class in order to process social data."""

    def calc_descriptive_metrics(self, data: Dict[str | int, Number]) -> dict:
        """Calculates descriptive metrics of a given data set.

        Args:
            data (Dict[str  |  int, Number]): Data dictionary containing numeric values.

        Raises:
            ValueError: If non-numeric values are contained in the data dictionary.

        Returns:
            dict: Input data dictionary containing descriptive metrics.

        Metrics:
            - Max Value
            - Min Value
            - Mean Value
            - Median
            - Standard Deviation
            - Sample Variance
            - Range (Max - Min)
            - Interquartiles Range
            - Mean Absolute Deviation
        """
        if not any(isinstance(value, Number) for value in data.values()):
            raise ValueError("Only numeric values are allowed.")
        # extract numeric values by iterating over data dict with iterable items
        numerics = list(data.values())
        # init empty dict to store descriptive metrics
        metrics = dict()
        # calc max
        metrics["max"] = max(numerics)
        # calc min
        metrics["min"] = min(numerics)
        # calc mean
        metrics["mean"] = np.array(numerics).mean()
        # calc median
        metrics["median"] = np.median(numerics)
        # calc standard deviation
        metrics["std"] = np.std(numerics)
        # calc variance
        metrics["var"] = np.var(numerics)
        # calc range
        metrics["range"] = max(numerics) - min(numerics)
        # calc interquarile range
        metrics["IQR"] = np.subtract(*np.percentile(numerics, [75, 25]))
        # calc absolute mean deviation
        metrics["mad"] = np.mean(np.absolute(numerics - np.mean(numerics)))
        # add metrics
        data["metrics"] = metrics
        return data

    def calc_datetime_metrics(self, dates: Dict[str, datetime]) -> dict():
        """Calculates descriptive metrics on datetime objects.

        Args:
            dates (Dict[str, datetime]): Dictionary containing identifiers as keys and datetime objects as values.

        Returns:
            dict: Input dates with added datetime metrics.

        Metrics:
            - Mean
            - Median
            - Max
            - Min
            - Time Span (in days, seconds, and microseconds)
            - Deviation from mean (in days and seconds). Negative values indicate below average, positive ones above average.
            - Deviation from median (in days and seconds). Negative values indicate below median, positive ones above average.
        """
        # use the datetime's timestamp to make them comparable
        timestamps = [dt.timestamp() for dt in dates.values()]
        # calc mean of creation dates
        total_time = sum(timestamps)
        mean_timestamp = total_time / len(timestamps)
        # convert mean timestamp back to datetime object with timezone information
        mean_datetime = datetime.fromtimestamp(mean_timestamp, tz=timezone.utc)

        # calculate time differences to mean datetime of every creation date
        time_diffs_mean = {key: {"days": (dt - mean_datetime).days, "seconds": (dt - mean_datetime).seconds} for key, dt in dates.items()}

        # find the median of the timestamps
        median_timestamp = np.median(timestamps)
        # Convert median timestamp back to datetime object
        median_datetime = datetime.fromtimestamp(median_timestamp, tz=timezone.utc)

        # calculate time differences to median timestamp of every creation date
        time_diffs_median = {key: {"days": (dt - median_datetime).days, "seconds": (dt - median_datetime).seconds} for key, dt in dates.items()}

        # calc range of creation dates
        max_date, min_date = max(dates.values()), min(dates.values())
        time_span = max_date - min_date

        # convert creation dates to isoformat for readability
        dates = {key: dt.isoformat() for key, dt in dates.items()}

        # add metrics to output
        dates["metrics"] = dict()
        dates["metrics"]["deviation_from_mean"] = time_diffs_mean
        dates["metrics"]["deviation_from_median"] = time_diffs_median
        dates["metrics"]["time_span"] = {"days": time_span.days, "seconds": time_span.seconds, "microseconds": time_span.microseconds}
        dates["metrics"]["mean"] = mean_datetime.isoformat()
        dates["metrics"]["median"] = median_datetime.isoformat()
        dates["metrics"]["max"] = max_date.isoformat()
        dates["metrics"]["min"] = min_date.isoformat()
        return dates

    def intersection(self, iterable: List[set]) -> list:
        """Calculates the intersection of multiple sets.

        Args:
            iterable (List[set]): List containing sets.

        Returns:
            list: intersection set casted to list.
        """
        intersection = set.intersection(*map(set, iterable))
        return list(intersection)

    def difference(self, sets: Dict[int | str, set]) -> dict:
        """Calculates the difference of multiple sets.

        Args:
            sets (Dict[set]): Dictionary containing sets where keys are identifiers.

        Returns:
            dict: Individual difference of each set that was provided.
        """
        # init empty dict to store individual differences for each set
        differences = dict()
        for key, values in sets.items():
            differences[key] = list(set(values))
            for other_key, other_values in sets.items():
                if key != other_key:
                    differences[key] = list(set(differences[key]) - set(other_values))
        return differences


class TwitterDataProcessor(BaseDataProcessor):
    """Component class in order to process Twitter data."""

    def extract_followers(self, user_object: tweepy.User) -> Dict[str, str | int]:
        """Extract IDs, names, and screen names from a user's followers.

        Args:
            user_object (tweepy.User): Tweepy User Object.

        Returns:
            Dict[str, str | int]: Dictionary containing IDs, names, and screen names.
        """
        info = {"followers_ids": list(), "followers_names": list(), "followers_screen_names": list()}
        # extract follower IDs
        info["followers_ids"] = user_object.follower_ids()
        # extract names and screen names
        for follower in user_object.followers():
            info["followers_names"].append(follower.name)
            info["followers_screen_names"].append(follower.screen_name)
        return info

    def extract_followees(self, user_object: tweepy.User) -> Dict[str, str | int]:
        """Extract IDs, names, and screen names from a user's followees.

        Args:
            user_object (tweepy.User): Tweepy User Object.

        Returns:
            Dict[str, str | int]: Dictionary containing IDs, names, and screen names.
        """
        info = {"followees_ids": list(), "followees_names": list(), "followees_screen_names": list()}
        # extract IDs, names and screen names
        for followee in user_object.friends():
            info["followees_ids"].append(followee.id)
            info["followees_names"].append(followee.name)
            info["followees_screen_names"].append(followee.screen_name)
        return info

    def clean_tweet(self, tweet: str) -> str:
        """Utility function to clean tweet text by removing links, special characters using simple regex statements.

        Args:
            tweet (str): Raw text of the Tweet.

        Returns:
            str: Cleaned Tweet
        """
        return " ".join(re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def detect_tweet_sentiment(self, tweet: str) -> str:
        """Utility function to classify sentiment of passed tweet using textblob's sentiment method. English Tweets only.

        Args:
            tweet (str): The raw text of the Tweet.

        Returns:
            str: the sentiment of the Tweet. Either positive, neutral, or negative.
        """
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return "positive"
        elif analysis.sentiment.polarity == 0:
            return "neutral"
        else:
            return "negative"

    def compare_relationships(self, users: List[str | int], fetcher: TwitterDataFetcher) -> dict:
        """Creates pairs for each unique combination of provided users based on their relationship.

        Args:
            users (List[str  |  int]): List of user IDs or screen names.
            fetcher (TwitterDataFetcher): Fetcher instance in order to receive necessary data from Twitter.

        Returns:
            dict: Pairs of users containing their relationship to each other.
        """
        # init emtpy relationships dict
        relationships = dict()
        # iterate over every pair combination of provided users
        for user in users:
            for other_user in users:
                if user != other_user:
                    relationships[(user, other_user)] = fetcher.get_relationship(source_user=user, target_user=other_user)
        return relationships

    def calc_similarity(self, users: List[int | str] | None = None, tweet_ids: List[str | int] | None = None, *, features: List[str], fetcher: TwitterDataFetcher) -> dict:
        """Calculates the euclidean distance of users/tweets based on a feature vector. Either users or Tweets must be specified, not both.

        Args:
            features (List[str]): Features that should be contained in the feature vector. Features have to be numeric and must belong to the respective object (i.e., user or tweet.)
            users (List[int  |  str] | None, optional): List of user IDs or screen names. Defaults to None.
            tweet_ids (List[str  |  int] | None, optional): Tweet IDs. Defaults to None.
            fetcher (TwitterDataFetcher): Fetcher instance in order to receive necessary data from Twitter.

        Raises:
            ValueError: If either 'users' and 'tweet_ids' or none of them were provided.
            AssertionError: If non-numeric feature was provided in the 'features' list.

        Returns:
            dict: Unique pair of users/tweets containing the respective euclidean distance. Sorted in ascending order.
        """
        # init empty dict to store distances
        distances = dict()
        # if users and tweets were provided
        if users and tweet_ids:
            raise ValueError("Either 'users' or 'tweet_ids' must be specified, not both.")
        # if only users were provided
        elif users:
            # iterate over every uniqe pair
            for i in range(len(users)):
                for j in range(i + 1, len(users)):
                    # get user objects for each pair
                    user_i = fetcher.get_user_object(users[i])._json
                    user_j = fetcher.get_user_object(users[j])._json
                    # build feature vector
                    vec_i = np.array([user_i[feature] for feature in features])
                    vec_j = np.array([user_j[feature] for feature in features])
                    # feature vectors have to contain numeric values
                    assert all(isinstance(feat, Number) for feat in vec_i), "only numeric features are allowed"
                    assert all(isinstance(feat, Number) for feat in vec_j), "only numeric features are allowed"
                    # calc euclidean distance
                    distances[(users[i], users[j])] = np.linalg.norm(vec_i - vec_j, ord=2)
        elif tweet_ids:
            # iterate over every uniqe pair
            for i in range(len(tweet_ids)):
                for j in range(i + 1, len(tweet_ids)):
                    # get Tweet objects for each pair
                    tweet_i = fetcher.get_tweet_object(tweet_ids[i])._json
                    tweet_j = fetcher.get_tweet_object(tweet_ids[j])._json
                    # build feature vector
                    vec_i = np.array([tweet_i[feature] for feature in features])
                    vec_j = np.array([tweet_j[feature] for feature in features])
                    # feature vectors have to contain numeric values
                    assert all(isinstance(feat, Number) for feat in vec_i), "only numeric features are allowed"
                    assert all(isinstance(feat, Number) for feat in vec_j), "only numeric features are allowed"
                    # calc euclidean distance
                    distances[(tweet_ids[i], tweet_ids[j])] = np.linalg.norm(vec_i - vec_j, ord=2)
        # if none was provided
        else:
            raise ValueError("'users' or 'tweet_ids' must be provided.")
        # sort dict in ascendin order
        sorted_values = dict(sorted(distances.items(), key=operator.itemgetter(1)))
        return sorted_values
