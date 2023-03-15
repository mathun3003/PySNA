# -*- coding: utf-8 -*-
import logging
import sys
from typing import Any, Dict, List, Set

import requests
import tweepy

# create logger instance
log = logging.getLogger(__name__)
# log to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


class TwitterDataFetcher:
    """Composition class in order to fetch data from the Twitter Search API v1 and v2."""

    def __init__(
        self,
        bearer_token: Any | None = None,
        consumer_key: Any | None = None,
        consumer_secret: Any | None = None,
        access_token: Any | None = None,
        access_token_secret: Any | None = None,
        x_rapidapi_key: Any | None = None,
        x_rapidapi_host: Any | None = None,
        wait_on_rate_limit: bool = True,
    ):
        self._bearer_token = bearer_token
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_token = access_token
        self._access_token_secret = access_token_secret
        self._x_rapidapi_key = x_rapidapi_key
        self._x_rapidapi_host = x_rapidapi_host
        self._wait_on_rate_limit = wait_on_rate_limit

        self.api = tweepy.API(tweepy.AppAuthHandler(consumer_key=self._consumer_key, consumer_secret=self._consumer_secret), wait_on_rate_limit=self._wait_on_rate_limit)

        self.client = tweepy.Client(
            bearer_token=self._bearer_token, consumer_key=self._consumer_key, consumer_secret=self._consumer_secret, access_token=self._access_token, access_token_secret=self._access_token_secret, wait_on_rate_limit=self._wait_on_rate_limit
        )

    def _manual_request(self, url: str, method: str = "GET", header: dict | None = None, payload: dict | None = None, additional_fields: Dict[str, List[str]] | None = None) -> dict:
        """Perform a manual request to the Twitter API.

        Args:
            url (str): API URL (without specified fields)
            method (str): Request method according to REST. Defaults to "GET".
            header (dict | None): Custom HTTP Header. Defaults to None.
            payload (dict | None): JSON data for HTTP requests. Defaults to None.
            additional_fields (Dict[str, List[str]] | None, optional): Fields can be specified (e.g., tweet.fields) according to the official API reference. Defaults to None.

        Raises:
            Exception: If status code != 200.

        Returns:
            dict: JSON formatted response of API request.
        """
        # if additional_fields were provided
        if additional_fields:
            # init empty string
            fields = "?"
            # create fields string dynamically for every field in additional_fields
            for field in additional_fields.keys():
                # e.g., in format "tweet.fields=lang,author_id"
                fields += f"{field}={','.join(additional_fields[field])}&"
            # append fields to url
            url += fields[:-1]
        if header is None:
            # set header
            header = {"Authorization": f"Bearer {self._bearer_token}"}
        response = requests.request(method=method, url=url, headers=header, json=payload)
        if response.status_code != 200:
            raise Exception("Request returned an error: {} {}".format(response.status_code, response.text))
        return response.json()

    def _paginate(self, func, params: Dict[str, str | int], limit: int | None = None, response_attribute: str = "data", page_attribute: str | None = None) -> list:
        """Pagination function

        Args:
            func: Function used for pagination
            params (Dict[str, str  |  int]): Dict containing request parameters. Should be of the form {'id': ..., 'max_results': ..., 'pagination_token': ...}
            limit (int | None, optional): Maximum number of results. Defaults to None, thus, no limit.
            response_attribute (str, optional): Attribute of the Response object. Defaults to "data". Options: ["data", "includes"]
            page_attribute (str, optional): The attribute that should be extracted for every entry of a page. Defaults to None.

        Raises:
            KeyError: 'id', 'max_results', and 'pagination_token' should be provided in the params dict.

        Returns:
            set: Results
        """
        # init counter
        counter = 0
        # init empty results set
        results = list()
        # set break out var
        break_out = False
        while not break_out:
            # make request
            response = func(**params)
            # if any data exists
            if response.__getattribute__(response_attribute) is not None:
                # iterate over response results
                for item in response.__getattribute__(response_attribute):
                    # add result
                    if page_attribute is None:
                        results.append(item)
                    else:
                        results.append(item.__getattribute__(page_attribute))
                    # increment counter
                    counter += 1
                    # if limit was reached, break
                    if (limit is not None) and (counter == limit):
                        # set break_out var to true
                        break_out = True
                        break
                # if last page was reached
                if "next_token" not in response.meta:
                    break
                # else, set new pagination token for next iteration
                else:
                    params["pagination_token"] = response.meta["next_token"]
            # if no data exists, break
            else:
                break
        return results

    """ User Object data methods """

    def get_user_object(self, user: str | int) -> tweepy.models.User:
        """Request Twitter User Object via tweepy

        Args:
            user (str): Either User ID or screen name

        Returns:
            tweepy.User: Twitter User object from tweepy
        """
        try:
            # check if string for user1 is convertible to int in order to check for user ID or screen name
            if (isinstance(user, int)) or (user.isdigit()):
                # get profile for user by user ID
                user_obj = self.api.get_user(user_id=user)
            else:
                # get profile for user by screen name
                user_obj = self.api.get_user(screen_name=user)
        except tweepy.errors.Forbidden as e:
            # log to stdout
            log.error("403 Forbidden: access refused or access is not allowed.")
            # if user ID was provided
            if user.isdigit() or isinstance(user, int):
                url = f"https://api.twitter.com/2/users/{user}"
            else:
                # if screen name was provided
                url = f"https://api.twitter.com/2/users/by/username/{user}"
            response = self._manual_request(url)
            # if an error occured that says the user has been suspended
            if any("User has been suspended" in error["detail"] for error in response["errors"]):
                log.error("User has been suspended from Twitter. Requested user: {}".format(user))
                raise e
            else:
                raise e
        return user_obj

    def get_user_follower_ids(self, user: str | int) -> Set[int]:
        """Request Twitter follower IDs from user

        Args:
            user (str | int): Either User ID or screen name.

        Returns:
            Set[int]: Array containing follower IDs
        """
        # check if string for user1 is convertible to int in order to check for user ID or screen name
        if (isinstance(user, int)) or (user.isdigit()):
            params = {"user_id": user}
        else:
            params = {"screen_name": user}

        follower_ids = list()
        for page in tweepy.Cursor(self.api.get_follower_ids, **params).pages():
            follower_ids.extend(page)
        return set(follower_ids)

    def get_user_followee_ids(self, user: str | int) -> Set[int]:
        """Request Twitter followee IDs from user

        Args:
            user (str): Either User ID or screen name.

        Returns:
            Set[int]: Array containing follow IDs
        """
        # check if string for user1 is convertible to int in order to check for user ID or screen name
        if (isinstance(user, int)) or (user.isdigit()):
            params = {"user_id": user}
        else:
            params = {"screen_name": user}

        followee_ids = list()
        for page in tweepy.Cursor(self.api.get_friend_ids, **params).pages():
            followee_ids.extend(page)
        return set(followee_ids)

    def get_latest_activity(self, user: str | int) -> dict:
        """Returns latest user's activity by fetching the top element from its timeline.

        Args:
            user (str | int): User ID or screen name.

        Returns:
            dict: Latest activity.
        """
        # if screen name was provided
        if (isinstance(user, str)) and (user.isdigit() is False):
            url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={user}&include_rts=true&trim_user=true&tweet_mode=extended"
        # else go with user ID
        else:
            url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?user_id={user}&include_rts=true&trim_user=true&tweet_mode=extended"
        response_json = self._manual_request(url)
        # return the first item since timeline is sorted descending
        return response_json[0]

    def get_latest_activity_date(self, user: str | int) -> str:
        """Get latest activity date from specified user by fetching the top element from its timeline.

        Args:
            user (str | int): User ID or screen name.

        Returns:
            str: Activity date of latest activity.
        """
        # if screen name was provided
        if (isinstance(user, str)) and (user.isdigit() is False):
            url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={user}&include_rts=true&trim_user=true"
        # else go with user ID
        else:
            url = f"https://api.twitter.com/1.1/statuses/user_timeline.json?user_id={user}&include_rts=true&trim_user=true"
        response_json = self._manual_request(url)
        # return the first item since timeline is sorted descending
        return response_json[0]["created_at"]

    def get_relationship(self, source_user: str | int, target_user: str | int) -> dict:
        """Get relationship between two users.

        Args:
            user1 (str | int): Source user ID or screen name.
            user2 (str | int): Target user ID or screen name.

        Returns:
            dict: Unpacked tuple of JSON from tweepy Friendship model.

        Reference: https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show#example-response
        """

        params = {"source_id": None, "source_screen_name": None, "target_id": None, "target_screen_name": None}
        # if source_user is int or a digit
        if (isinstance(source_user, int)) or (isinstance(source_user, str) and (source_user.isdigit())):
            params["source_id"] = source_user
        # else if screen name was provided
        elif (isinstance(source_user, str)) and (not source_user.isdigit()):
            params["source_screen_name"] = source_user
        else:
            log.error("No ID or username provided for {}".format(source_user))

        # if target_user is int or a digit
        if (isinstance(target_user, int)) or (isinstance(target_user, str) and (target_user.isdigit())):
            params["target_id"] = target_user
        # else if screen name was provided
        elif (isinstance(target_user, str)) and (not target_user.isdigit()):
            params["target_screen_name"] = target_user
        else:
            log.error("No ID or username provided for {}".format(target_user))

        relationship = self.api.get_friendship(**params)
        return {"source": relationship[0]._json, "target": relationship[1]._json}

    def get_relationship_pairs(self, users: List[str | int]) -> dict:
        """Creates pairs for each unique combination of provided users based on their relationship.

        Args:
            users (List[str  |  int]): List of user IDs or screen names.

        Returns:
            dict: Pairs of users containing their relationship to each other.
        """
        # init emtpy relationships dict
        relationships = dict()
        # iterate over every pair combination of provided users
        for user in users:
            for other_user in users:
                if user != other_user:
                    relationships[(user, other_user)] = self.get_relationship(source_user=user, target_user=other_user)
        return relationships

    def get_liked_tweets_ids(self, user: str | int, limit: int | None = None) -> list():
        """Get (all) liked Tweets of provided user.

        Args:
            user (str | int): User ID or screen name.
            limit (int | None): The maximum number of results to be returned. By default, each page will return the maximum number of results available.

        Returns:
            Set[int]: Tweet Objects of liked Tweets.
        """
        # if user ID was provided
        if (isinstance(user, int)) or (user.isdigit()):
            params = {"id": user, "max_results": 100, "pagination_token": None}
        else:
            user_obj = self.get_user_object(user)
            params = {"id": user_obj.id, "max_results": 100, "pagination_token": None}

        page_results = self._paginate(self.client.get_liked_tweets, params, limit=limit, page_attribute="id")
        return page_results

    def get_composed_tweets_ids(self, user: str | int, limit: int | None = None) -> list:
        """Get (all) composed Tweets of provided user by pagination.

        Args:
            user (str | int): User ID or screen name.
            limit (int | None): The maximum number of results to be returned. By default, each page will return the maximum number of results available.

        Returns:
            list: Tweet Objects of composed Tweets.
        """

        # user ID is required, if screen name was provided
        if (isinstance(user, str)) and (not user.isdigit()):
            user = self.get_user_object(user).id
        # set params
        params = {"id": user, "max_results": 100, "pagination_token": None}
        # get page results
        page_results = self._paginate(self.client.get_users_tweets, params, limit=limit, page_attribute="id")
        return page_results

    def get_botometer_scores(self, user: str | int) -> dict:
        """Returns bot scores from the Botometer API for the specified Twitter user.

        Args:
            user (str | int): User ID or screen name.

        Returns:
            dict: The raw Botometer scores for the specified user.

        Reference: https://rapidapi.com/OSoMe/api/botometer-pro/details
        """
        if (self._x_rapidapi_key is None) or (self._x_rapidapi_host is None):
            raise ValueError("'X_RAPIDAPI_KEY' and 'X_RAPIDAPI_HOST' secrets for Botometer API need to be provided.")
        # get user object
        user_obj = self.get_user_object(user)
        # get user timeline
        timeline = list(map(lambda x: x._json, self.api.user_timeline(user_id=user_obj.id, count=200)))
        # get user data
        if timeline:
            user_data = timeline[0]["user"]
        else:
            user_data = user_obj._json
        screen_name = "@" + user_data["screen_name"]
        # get latest 100 Tweets
        tweets = list(map(lambda x: x._json, self.api.search_tweets(screen_name, count=100)))
        # set payload
        payload = {"mentions": tweets, "timeline": timeline, "user": user_data}
        # set header
        headers = {"content-type": "application/json", "X-RapidAPI-Key": self._x_rapidapi_key, "X-RapidAPI-Host": self._x_rapidapi_host}
        # set url
        url = "https://botometer-pro.p.rapidapi.com/4/check_account"
        # get results
        response = self._manual_request(url, "POST", headers, payload)
        return response

    """ Tweet Object data methods """

    def get_tweet_object(self, tweet: str | int) -> tweepy.models.Status:
        """Request Twitter Tweet Object via tweepy

        Args:
            tweet (int | str): Tweet ID

        Returns:
            tweepy.models.Status: tweepy Status Model

        Reference: https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet
        """
        try:
            tweet_obj = self.api.get_status(tweet, include_entities=True, tweet_mode="extended")
        except tweepy.errors.NotFound as e:
            log.error("404 Not Found: Resource not found.")
            raise e
        except tweepy.errors.Forbidden as e:
            log.error("403 Forbidden: access refused or access is not allowed.")
            raise e
        return tweet_obj

    def get_liking_users_ids(self, tweet_id: str | int, limit: int | None = None) -> list:
        """Get (all) liking users of provided Tweet by pagination.

        Args:
            tweet (str | int): Tweet ID.
            limit (int | None): The maximum number of results to be returned. By default, each page will return the maximum number of results available.

        Returns:
            list: User Objects as list.
        """
        # set params
        params = {"id": tweet_id, "max_results": 100, "pagination_token": None}
        # get page results
        page_results = self._paginate(self.client.get_liking_users, params, limit=limit, page_attribute="id")
        return page_results

    def get_retweeters_ids(self, tweet_id: str | int, limit: int | None = None) -> list:
        """Get (all) retweeting users of provided Tweet by pagination.

        Args:
            tweet (str | int): Tweet ID.
            limit (int | None): The maximum number of results to be returned. By default, each page will return the maximum number of results available.

        Returns:
            list: User Objects of retweeting users.
        """
        params = {"id": tweet_id, "max_results": 100, "pagination_token": None}
        # get page results
        page_results = self._paginate(self.client.get_retweeters, params, limit=limit, page_attribute="id")
        return page_results

    def get_quoting_users_ids(self, tweet_id: str | int, limit: int | None = None) -> list:
        """Get (all) quoting users of provided Tweet by pagination.

        Args:
            tweet_id (str | int): Tweet ID.
            limit (int | None): The maximum number of results to be returned. By default, each page will return the maximum number of results available.

        Returns:
            list: User Objects of quoting users.
        """
        params = {"id": tweet_id, "max_results": 100, "pagination_token": None}
        # get page results
        page_results = self._paginate(self.client.get_quote_tweets, params, limit=limit, response_attribute="includes", page_attribute="id")
        return page_results

    def get_context_annotations_and_entities(self, tweet_id: str | int) -> dict | None:
        """Get context annotations and entities from a Tweet.

        Args:
            tweet_id (str | int): Tweet ID

        Returns:
            dict | None: context annotations and entities if available, else None.

        Reference: https://developer.twitter.com/en/docs/twitter-api/annotations/overview
        """
        url = f"https://api.twitter.com/2/tweets/{tweet_id}"
        response_json = self._manual_request(url, additional_fields={"tweet.fields": ["context_annotations", "entities"]})
        # if key is not awailable, return None
        if "context_annotations" or "entities" in response_json["data"]:
            return response_json["data"]
        else:
            return None

    def get_public_metrics(self, tweet_id: str | int) -> dict:
        """Get public metrics from Tweet Object

        Args:
            tweet_id (str | int): Tweet ID

        Returns:
            dict: Available public metrics for specified Tweet.

        Metrics:
            - impressions_count (=views)
            - quote_count
            - reply_count
            - retweet_count
            - favorite_count (=likes)

        Reference: https://developer.twitter.com/en/docs/twitter-api/metrics
        """
        # set URL
        url = f"https://api.twitter.com/2/tweets/{tweet_id}"
        # make request
        response_json = self._manual_request(url, additional_fields={"tweet.fields": ["public_metrics"]})
        # get public metrics from JSON response
        public_metrics = response_json["data"]["public_metrics"]
        return public_metrics
