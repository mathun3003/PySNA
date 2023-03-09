TwitterDataFetcher
----------------

The TwitterDataFetcher class is used to specifically query Twitter data. To simplify
the queries to the Twitter API, this software component uses already existing
open-source software for interacting with the API, namely the [Tweepy Python package](https://github.com/tweepy/tweepy).

It uses the Tweepy Client class to query the data dictionaries of the Twitter
Search API v2 as well as the Tweepy API class to access the data dictionaries based
on the Twitter Search API v1.

The Twitter Search API v1 is mainly used to query user and tweet objects. Although this API version is partially deprecated, it offers a comparable content to the latest API version and often requires less API calls to receive the same information compared to the v2 API.

Additional direct requests to the Twitter Search
API v2 are performed, too, using the Python ```requests``` library to query endpoints
that have been migrated or deprecated in the Tweepy package.


This class can also be used to in isolation to collect Twitter data. It requires, therefore, authentication for the Twitter platform. Provide the secrets for the Twitter API and, if desired, for the Botometer API. You can find a list of required secrets in the [user guide for the TwitterAPI](../user-guide/overview/TwitterAPI.md) class.

This class has the concern to fetch Twitter data. No further processing is performed within this class.

# Initialization

If you want to use this class for data processing or other package components, follow the steps below.

Import the ```TwitterDataFetcher``` class from the ```fetch``` module.

```python
from pysna.fetch import TwitterDataFetcher

fetcher = TwitterDataFetcher()
```

and invoke a function:

```python
user_id = 123450897612
fetcher.get_latest_activity(user_id)
```

# Methods

## Private Methods

### manual_request

Performs a manual request to the Twitter API. Returns JSON formatted API response.

Function:
```python
TwitterDataFetcher._manual_request(url: str, method: str = "GET", header: dict | None = None, payload: dict | None = None, additional_fields: Dict[str, List[str]] | None = None)
```

Args:

- ```url``` (str): API URL (without specified fields)  
- ```method``` (str): Request method according to REST. Defaults to "GET".  
- ``header``: Custom HTTP Header. Defaults to None.  
- ``payload``: JSON data for HTTP requests. Defaults to None.  
- ``additional_fields`` (Dict[str, List[str]] | None, optional): Fields can be specified (e.g., tweet.fields) according to the official API reference. Defaults to None.  

The function will raise an exception if the response status code is unlike 200.

With this function, performig manual requests is facilitated as the query string is built by the function based on the provided input arguments.

The ```url``` argument has to be provided in raw form (i.e., without any parameters or fields).  
The ```method``` argument allows to specify the REST request method (i.e., GET, POST, PUT, DELETE). Defaults to GET.  
The ```header``` argument allows to specify a custom header. This is useful if another API besides the Twitter API is fetched. If no custom header is provided, the default header for the Twitter API authentification is used based on the provided ```bearer_token``` during instantiation.  
The ```payload``` argument allows to send data for a POST or PUT request. The data must be provided as a dictionary.  
The ```additional_fields``` argument is used to specify Twitter fields (i.e., user fields or tweet fields) and, thus, enhance the query and return additional information. The argument can be used as follows:

```python
{"tweet.fields": ["public_metrics"]}
```

The function will then build the query string and send it to the API.

You can find the full list of Twitter fields in the documentation: [https://developer.twitter.com/en/docs/twitter-api/fields](https://developer.twitter.com/en/docs/twitter-api/fields)

<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________

### paginate

Custom pagination function

It turns out that the pagination functions from the Tweepy Python packge are considerably slower than doing the pagination manually. For this reason, this function was designed.

Function:
```python
TwitterDataFetcher._paginate(func, params: Dict[str, str | int], limit: int | None = None, response_attribute: str = "data", page_attribute: str | None = None)
```

Args:

- ``func``: Function used for pagination
- ``params`` (Dict[str, str  |  int]): Dict containing request parameters. Must be of the form ``{'id': ..., 'limit': ..., 'pagination_token': ...}``
- ``limit`` (int | None, optional): Maximum number of results. Defaults to None, thus, no limit.
- ``response_attribute`` (str, optional): Attribute of the Response object. Defaults to "data". Options: ["data", "includes"]
- ``page_attribute`` (str, optional): The attribute that should be extracted for every entry of a page. Defaults to None.

The ``params`` argument is used to specify the parameters for the next page. Therefore, an ``id`` is needed as well as a key indicating the maximm number of results (i.e., ``limit``). ``None`` indicates that no limit is desired and, thus, all available results will be returned. The ``pagination_token`` key can be set to ``None`` initially. This pagination token will be reset during iteraion. In case, you wish to start from a different page than the first one, provide a pagination token. All parameters must be provided via a dictionary of the form:

```python
{"id": 1234456,
"limit": None, # no limit
"pagination_token": None}
```

The ``response_attribute`` argument specifies where to collect the data from the response. If ``data`` is specified, the results are received from the default attribute field of the response. If ``includes`` is specified, the results are obtained from the additional information provided by the Twitter fields.`

The ``page_attribute`` argument specifies what attribute should be extracted for every entry of a page. For instance, if this argument is set to ``id``, then the IDs will be extracted from every entry (e.g., user IDs of user objects).

Inside that function, a counter is incremented for every result that has been fetched. If the limit was reached, the function will break out the loop and will return immediately the obtained results. Otherwise, the function will check if last page was reached and will fetch the next page (if available).

<details>
<summary>Source Code</summary>
```python
def _paginate(self, func, params: Dict[str, str | int], limit: int | None = None, response_attribute: str = "data", page_attribute: str | None = None) -> list:
    """Pagination function

    Args:
        func: Function used for pagination
        params (Dict[str, str  |  int]): Dict containing request parameters. Should be of the form {'id': ..., 'max_results': ..., 'pagination_token': ...}
        limit (int | None, optional): Maximum number of results. Defaults to None, thus, no limit.
        response_attribute (str, optional): Attribute of the Response object. Defaults to "data". Options: ["data", "includes"]

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
```
</details>

_____________

## Twitter user related methods

### get_user_object

Request Twitter user object using Tweepy. The user object is fetched from the Twitter Search API v1. For this, the Tweepy API class is used.

Function:
```python
TwitterDataFetcher.get_user_object(user: str | int)
```

The function takes in either the user ID as string or integer or the user's unique screen name. It returns the requested API v1 user object.

The function handles the performed request based on what user identifier was given.

If the requested user has been suspended from Twitter, an error will be returned and a messeage will be logged to stdout.

<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________

### get_user_follower_ids

Request Twitter follower IDs from user.

Function:
```python
TwitterDataFetcher.get_user_follower_ids(user: str | int)
```

This function takes in a Twitter user identifier (either ID or unique screen name). It returns all follower user IDs from the specified user as a set. Here, the ``tweepy.Cursor```is used for pagination.

The function handles the performed request based on what user identifier was given.

<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________


### get_user_followee_ids

Request Twitter followee IDs from user.

Function:
```python
TwitterDataFetcher.get_user_followee_ids(user: str | int)
```

This function takes in a Twitter user identifier (i.e., either ID or unique screen name) and returns a set containing all IDs from the user's followees (AKA friends or follows).

The function handles the performed request based on what user identifier was given.

<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________

### get_latest_activity

Returns latest user's activity by fetching the top element from its timeline.

Function:
```python
TwitterDataFetcher.get_latest_activity(user: str | int)
```

This function takes in a Twitter user identifier (i.e., either ID or unique screen name) and returns the latest activity from the user's timeline. Therefore, the [``_manual_request``](./TwitterDataFetcher.md#manual_request) function is used to request the [corresponding endpoint](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline).

Often, this will be a tweet composed by the user itself. Then, all available data of that tweet will be returned as a dictionary.

The function handles the performed request based on what user identifier was given.

<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________

### get_latest_activity_date

Get latest activity date from specified user by fetching the top element from its timeline and extract the creation date.

Function:
```python
TwitterDataFetcher.get_latest_activity_date(user: str | int)
```

This function takes in a Twitter user identifier (i.e., either ID or unique screen name) and returns the latest activity date from the user's timeline. Therefore, the [``_manual_request``](./TwitterDataFetcher.md#manual_request) function is used to request the [corresponding endpoint](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/timelines/api-reference/get-statuses-user_timeline).

The latest activity date is determined by fetching the latest activity from the user's timeline first, and then extracting the creation date. Usually, this will be a tweet composed by the user. If this is the case, the creation date of that tweet will be returned, representing the latest public available activity date.

<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________

### get_relationship

Get relationship between two Twitter users.

Function:
```python
TwitterDataFetcher.get_relationship(source_user: str | int, target_user: str | int)
```

The function takes in a source and a target user identifier. It uses the [Tweepy.API.get_friendship](https://docs.tweepy.org/en/stable/api.html#tweepy.API.get_friendship) function to get the relationship. Therefore, this function handles the performed query based on the provided user identifiers.

The function will return the parsed JSON relationship for the source and target user as a dictionary.

<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________

### get_relationship_pairs

Creates pairs for each uniqie combination of provided users based on their relationship.

Function:
```python
TwitterDataFetcher.get_relationship_pairs(users: List[str | int])
```

This function takes in a list of user identifiers (i.e., IDs or unique screen names). It will create a pair of each combination of the provided users and returns their individual relationships.

For instance, if three users ``WWU_Muenster``, ``goetheuni``, ``UniKonstanz`` were provided, the pairs are determined as follows:

1. (``WWU_Muenster``, ``goetheuni``)
2. (``WWU_Muenster``, ``UniKonstanz``)
3. (``goetheuni``, ``WWU_Muenster``)
4. (``goetheuni``, ``UniKonstanz``)
5. (``UniKonstanz``, ``WWU_Muenster``)
6. (``UniKonstanz``, ``goehteuni``)

These pairs are set as dictionary keys. The respective relationships are stored as dictionary values.


<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________


### get_liked_tweets_ids

Get (all) liked tweet IDs of the provided user.

Function:
```python
TwitterDataFetcher.get_liked_tweets_ids(user: str | int, limit: int | None = None)
```

Args:  

- ``user`` (str | int): User ID or screen name.
- ``limit`` (int | None): The maximum number of results to be returned. By default, each page will return the maximum number of results available.

This function uses the custom [``TwitterDataFetcher._paginate``](./TwitterDataFetcher.md#paginate) function to get the specified number of results. To get the tweet IDs, the [tweepy.Client.get_liked_tweets](https://docs.tweepy.org/en/stable/client.html#tweepy.Client.get_liked_tweets) function is used.

The function wil return a Python set of the IDs of the liked tweets by the user.

The function handles the performed request based on what user identifier was given.

<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________

### get_composed_tweets_ids

Get (all) composed tweet IDs of provided user by pagination.

Function:
```python
TwitterDataFetcher.get_composed_tweets_ids(user: str | int, limit: int | None = None)
```

Args:  

- ``user`` (str | int): User ID or screen name.
- ``limit`` (int | None): The maximum number of results to be returned. By default, each page will return the maximum number of results available.

This function uses the custom [``TwitterDataFetcher._paginate``](./TwitterDataFetcher.md#paginate) function to get the specified number of results. To get the tweet IDs, the [tweepy.Client.get_users_tweets](https://docs.tweepy.org/en/stable/client.html?#tweepy.Client.get_users_tweets) function is used.

The function wil return a Python set of the IDs of the composed tweets by the user.

The function handles the performed request based on what user identifier was given.

<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________


### get_botometer_scores

Returns bot scores from the Botometer API for the specified Twitter account.

Function:
```python
TwitterDataFetcher.get_botometer_scores(user: str | int)
```

This function takes in a Twitter account identifier (i.e., ID or unique screen name.)

This function relies on the external [Botometer API](https://rapidapi.com/OSoMe/api/botometer-pro/details). To use this function, the corresponding RapidAPI secrets need to be provided. See the [secrets overview](../user-guide/overview/TwitterAPI.md#initialization) for more details.

The function gets the user's timeline first and takes the latest 100 tweets from its timeline. Then, this data is send via the ```payload`` argument of the [``TwitterDataFetcher._manual_request``](./TwitterDataFetcher.md#manual_request) function using a POST request. Then, the JSON response is returned.


<details>
<summary>Source Code</summary>
```python
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
```
</details>

_____________


## Tweet related methods

### get_tweet_objects

_____________

### get_liking_users_ids

_____________

### get_retweeters_ids

_____________

### get_quoting_users_ids

_____________

### get_context_annotations_and_entities

_____________

### get_public_metrics

_____________
