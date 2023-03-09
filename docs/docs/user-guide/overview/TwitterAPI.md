TwitterAPI
----------------

This class provides a Twitter API interface in order to interact with the Twitter Search API v2. It is built on top of the [```tweepy.Client```](https://docs.tweepy.org/en/stable/client.html) class. Thus, it supports all methods from the Tweepy client. Additional functions are added.

The following functions are available:

- [```user_info```](#user_info)
- [```compare_users```](#compare_users)
- [```tweet_info```](#tweet_info)
- [```compare_tweets```](#compare_tweets)

________

### Initialization

Header:

```python
TwitterAPI(bearer_token: Optional[Any] = None,
           consumer_key: Optional[Any] = None,
           consumer_secret: Optional[Any] = None,
           access_token: Optional[Any] = None,
           access_token_secret: Optional[Any] = None,
           x_rapidapi_key: Optional[Any] = None,
           x_rapidapi_host: Optional[Any] = None,
           wait_on_rate_limit: bool = True)
```

Args:

- ```bearer_token```: Twitter API OAuth 2.0 Bearer Token
- ```consumer_key```: Twitter API OAuth 1.0a Consumer Key
- ```consumer_secret```: Twitter API OAuth 1.0a Consumer Secret
- ```access_token```: Twitter API OAuth 1.0a Access Token
- ```access_token_secret```: Twitter API OAuth 1.0a Access Token Secret
- ```x_rapidapi_key```: Access Token for the [Botometer API](https://rapidapi.com/OSoMe/api/botometer-pro/details) from the [RapidAPI platform](https://rapidapi.com/hub)
- ```x_rapidapi_host```: Host for the [Botometer API](https://rapidapi.com/OSoMe/api/botometer-pro/details) from the [RapidAPI platform](https://rapidapi.com/hub)
- ```wait_on_rate_limit```: Whether to wait when rate limit is reached. Defaults to True.

________

### user_info

Function:

```python
TwitterAPI.user_info(user: str | int, attributes: List[LITERALS_USER_INFO] | str, return_timestamp: bool = False)
```

Receive requested user information from Twitter User Object.  

This function takes in a Twitter user identifier (i.e., an ID or unique screen name). The attributes are passed in by a list object or by a single string.


For a single provided attribute, only the corresponding value is returned. For multiple attributes, a dictionary with the key-value pairs of the requested attributes is returned. If the requested attribute for the objet is not available, ``None`` will be returned.

Args:

- ```user``` (str | int): Twitter User either specified by corresponding ID or screen name.
- ```attributes``` (List[LITERALS_USER_INFO] | str): Attributes of the User object.  
These must be from this list: [Detailed description of user information attributes](./literals-user-info.md). See the link for detailed description of the attributes.

- ```return_timestamp``` (bool): Add UTC Timestamp of the request to results. Defaults to False.


References:

- [https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-users-lookup)
- [https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/user](https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/user)


Example:

```python
# request user information from the University of Münster
results = api.user_info("WWU_Muenster",
					    ["id", "created_at", "last_active", "followers_count"])
print(results)
```

will print:
```
{'id': 24677217,
 'created_at': 'Mon Mar 16 11:19:30 +0000 2009',
 'last_active': 'Wed Feb 15 13:51:04 +0000 2023',
 'followers_count': 20183}
```
________

### compare_users

Function:

```python
TwitterAPI.compare_users(users: List[str | int], compare: str | List[LITERALS_COMPARE_USERS], return_timestamp: bool = False, features: List[str] | None = None)
```

Compare two or more users with the specified comparison attribute(s).  

This function takes in multiple Twitter user identifiers (i.e., IDs or unique screen names). The comparison attributes are passed in by a list object or by a single string.


For a single attribute, only the corresponding value is returned. For multiple attributes, a dictionary with the key-value pairs of the requested attributes is returned.

Args:

- ```users``` (List[str | int]):  User IDs or unique screen names.
- ```compare``` (str | List[LITERALS_COMPARE_USERS]): Comparison attribute(s) by which users are compared. These must be from this list: [Detailed description of user comparison attributes](./literals-compare-users.md). See the link for detailed description of the attributes.
- ```return_timestamp``` (bool, optional): Add UTC Timestamp of the request to results. Defaults to False.
- ```features``` (List[str], optional): Defined features of Twitter User Object on which similarity will be computed. Must be from: ```followers_count```, ```friends_count```, ```listed_count```, ```favourites_count```, ```statuses_count```. Must be provided if ```similarity``` comparison attribute was passed in. Defaults to None.


References:  

- [https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/user](https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/user)  
- [https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show](https://developer.twitter.com/en/docs/twitter-api/v1/accounts-and-users/follow-search-get-users/api-reference/get-friendships-show)


Example:

```python
# compare number of tweets
results = api.compare_users(["WWU_Muenster", "goetheuni", "UniKonstanz"], compare="tweets_count", return_timestamp=True)
print(results)
```

will print:

```
{'tweets_count': {
  'WWU_Muenster': 11670,
  'goetheuni': 7245,
  'UniKonstanz': 9857,
  'metrics': {
   'max': 11670,
   'min': 7245,
   'mean': 9590.666666666666,
   'median': 9857.0,
   'std': 1816.288584510243,
   'var': 3298904.222222222,
   'range': 4425,
   'IQR': 2212.5,
   'mad': 1563.777777777778}},
 'utc_timestamp': '2023-02-12 18:05:33.152930'}
```

________

### tweet_info

Function:

```python
tweet_info(tweet_id: str | int, attributes: List[LITERALS_TWEET_INFO] | str, return_timestamp: bool = False)
```

Receive requested Tweet information from Tweet Object.  

This function takes in a tweet ID as string or integer representation. The attributes are passed in by a list object or by a single string.

For a single provided attribute, only the corresponding value is returned. For multiple attributes, a dictionary with the key-value pairs of the requested attributes is returned. If the requested attribute for the objet is not available, ``None`` will be returned.

Args:

- ```tweet_id``` (str | int): Tweet ID either in string or integer representation.  
- ```attributes``` (List[LITERALS_TWEET_INFO] | str): Attribute(s) of the Tweet object. These must be from this list: [Detailed description of Tweet information attributes](./literals-tweet-info.md). See the link for detailed description of the attributes.  
- ```return_timestamp``` (bool, optional): Add UTC Timestamp of the request to results. Defaults to False.  

References:

- [https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup)  
- [https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet](https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet)
- [https://developer.twitter.com/en/docs/twitter-api/annotations/overview](https://developer.twitter.com/en/docs/twitter-api/annotations/overview)

Example:

```python
# request creation date, language, and sentiment attributes for specified Tweet
results = api.tweet_info(1612443577447026689, ["created_at", "lang", "sentiment"], return_timestamp=True)
print(results)
```
will print:

```
{
  'created_at': 'Mon Jan 09 13:38:01 +0000 2023',
  'lang': 'de',
  'sentiment': 'neutral',
  'utc_timestamp': '2023-02-12 18:02:52.622169'
}
```

________

### compare_tweets

Function:

```python
compare_tweets(tweet_ids: List[str | int], compare: str | List[LITERALS_COMPARE_TWEETS], return_timestamp: bool = False, features: List[str] | None = None)
```
Compare two or more Tweets with the specified comparison attribute.  

This function takes in multiple tweet IDs as string or integer representation. The comparison attributes are passed in by a list object or by a single string.


For a single attribute, only the corresponding value is returned. For multiple attributes, a dictionary with the key-value pairs of the requested attributes is returned.

Args:

- ```tweet_ids``` (List[str | int]): Tweet IDs either in string or integer representation. At least two Tweet IDs are required.  
- ```compare``` (str | List[LITERALS_COMPARE_TWEETS]): Comparison attribute(s) by which Tweets are compared. These must be from this list: [Detailed description of Tweet comparison attributes](./literals-compare-tweets.md). See the link for detailed description of the attributes.
- ```return_timestamp``` (bool optional): Add UTC Timestamp of the request to results. Defaults to False.  
- ```features``` (List[str], optional): Defined features of Tweet Object on which similarity will be computed. Must be from: ```public_metrics``` (i.e., ```retweet_count```, ```reply_count```, ```like_count```, ```quote_count```, ```impression_count```). Must be provided if ```similarity``` comparison attribute was passed in. Defaults to None.  

References:

- [https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup](https://developer.twitter.com/en/docs/twitter-api/v1/tweets/post-and-engage/api-reference/get-statuses-lookup)  
- [https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet](https://developer.twitter.com/en/docs/twitter-api/v1/data-dictionary/object-model/tweet)

Example:

```python
# get common liking users of specified Tweets
results = api.compare_tweets(tweet_ids=[1612443577447026689, 1611301422364082180, 1612823288723476480],
                             compare="common_liking_users")
print(results)
```

will print:

```
[3862364523]
```

________


For all functions, a comparison over time can be achieved by using the ```return_timestamp``` argument for each request, storing the data in a JSON or CSV file using the [```export_to_json```](./Utilities.md#export-to-json) and [```export_to_csv```](./Utilities.md#export-to-csv), respectively, and append new records to existing files with the [```append_to_json```](./Utilities.md#append-to-json) or [```append_to_csv```](./Utilities.md#append-to-csv) utility functions.

Example:

```python
# request results for Tweet comparison, return timestamp
results = api.compare_tweets([1612443577447026689, 1611301422364082180, 1612823288723476480],
                             compare=["common_liking_users"],
                             return_timestamp=True)
# export to JSON file
export_to_json(results, export_path="compare_tweets.json")

# some time later...

# generate new results that should be appended in the next step
new_results = api.compare_tweets([1612443577447026689, 1611301422364082180, 1612823288723476480],
                                 compare=["common_liking_users"],
                                 return_timestamp=True)
# append to an existing file.
append_to_json(new_results, "compare_tweets.json")
```

The ```compare_tweets.json``` could then look like this:

```json
{
  "data": [
    {
      "common_liking_users": [3862364523],
      "utc_timestamp": "2023-02-21 11:26:45.885444"
    },
    {
      "common_liking_users": [3862364523, 20965264523],
      "utc_timestamp": "2023-02-22 12:31:23.765328"
    }
  ]
}
```

________
