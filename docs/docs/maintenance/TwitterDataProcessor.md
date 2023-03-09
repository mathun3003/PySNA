TwitterDataProcessor
----------------

The ```TwitterDataProcessor``` has the purpose to process Twitter-specific data and respective data dictionaries (i.e., user or tweet data dictionaries). This class is used inside the ```TwitterAPI``` class as a component class through composition.

This class can also be used to process previously collected data. It requires no authentication for the Twitter platform and, thus, can be used in isolation.

This class has a separated concern compared to the other package's classes, namely to process Twitter-related data.

# Initialization

If you want to use this class for data processing or other package components, follow the steps below.

Import the ```TwitterDataProcessor``` class from the ```process``` module.

```python
from pysna.process import TwitterDataProcessor

data_processor = TwitterDataProcessor()
```

and invoke a function:

```python
tweet = "Savage Love 🎶 #SavageLoveRemix"
data_processor.clean_tweet(tweet)
```

# Methods

### extract_followers
Extract IDs, names, and screen names from a user's followers. This function takes in a Tweepy user object from the v1 API version and returns a dictionary containing the extracted information.

Function:
```python
TwitterDataProcessor.extract_followers(user_object: tweepy.User)
```

This function will return a dictionary of the form
```python
{"followers_ids": [],
"followers_names": [],
"followers_screen_names": []}
```

**NOTE**: This function needs a recently fetched Twitter user object from the API v1. Stored user objects (e.g., using the ```pickle``` module) that are to be analyzed later will lead to an error.


<details>
<summary>Source Code</summary>
```python
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
```
</details>
______________

### extract_followees
Extract IDs, names, and screen names from a user's followees (i.e., their follows). This function takes in a Tweepy user object from the v1 API version and returns a dictionary containing the extracted information.

Function:
```python
TwitterDataProcessor.extract_followees(user_object: tweepy.User)
```

This function will return a dictionary of the form
```python
{"followees_ids": [],
"followees_names": [],
"followees_screen_names": []}
```

**NOTE**: This function needs a recently fetched Twitter user object from the API v1. Stored user objects (e.g., using the ```pickle``` module) that are to be analyzed later will lead to an error.

<details>
<summary>Source Code</summary>
```python
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
```
</details>

______________


### clean_tweet

Utility function to clean tweet text by removing links, special characters using simple regex statements. It takes in the raw text of a tweet.

Function:
```python
TwitterDataProcessor.clean_tweet(tweet: str)
```

This function is used before the ```detect_tweet_sentiment``` function. Thus, the tweet is cleaned first and then its sentiment is determined. Both functions are used in combination within the ```TwitterAPI``` class.

<details>
<summary>Source Code</summary>
```python
def clean_tweet(self, tweet: str) -> str:
    """Utility function to clean tweet text by removing links, special characters using simple regex statements.

    Args:
        tweet (str): Raw text of the Tweet.

    Returns:
        str: Cleaned Tweet
    """
    return " ".join(re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
```
</details>

______________


### detect_tweet_sentiment

Utility function to classify sentiment of passed tweet using vader sentiment analyzer. English Tweets only. The function takes in the text of a tweet (cleaned from special characters, linkes, emojis, etc.) and will return the tweet sentiment as well as the polarity scores.

Function:
```python
TwitterDataProcessor.detect_tweet_sentiment(tweet: str)
```

For sentiment detection, the [Vader sentiment analyzer](https://github.com/cjhutto/vaderSentiment) is used as this one turned out to be more accurate for tweets compared to NLTK sentiment analyzers.

The function will return a dictionary containing the label of the sentiment (i.e., positive, neutral, or negative) and the polarity scores:

```python
{"label": label,
"polarity_scores": polarity_score}
```

<details>
<summary>Source Code</summary>
```python
def detect_tweet_sentiment(self, tweet: str) -> dict:
    """Utility function to classify sentiment of passed tweet using textblob's sentiment method. English Tweets only.

    Args:
        tweet (str): The raw text of the Tweet.

    Returns:
        str: the sentiment of the Tweet (either positive, neutral, or negative) and the polarity scores.
    """
    # create VADER instance
    analyser = SentimentIntensityAnalyzer()
    # get polarity scores from cleaned tweet
    polarity_scores = analyser.polarity_scores(self.clean_tweet(tweet))
    # define label
    if polarity_scores["compound"] >= 0.05:
        label = "positive"
    elif polarity_scores["compound"] <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    # return label and polarity scores
    return {"label": label, "polarity_scores": polarity_scores}
```
</details>

______________


### calc_similarity

This function is used to calculate the similarity between multiple user or tweet objects. The function takes in either a list of user objects or a list of public tweet metrics as well as a ```features``` list. Either user objects or tweet metrics need to be provided, not both.

The user objects must be recently fetched from the Twitter API v1. A stored object (e.g., by using the ```pickle``` Python module) will not have the necessary properties to be resolved by this function. Otherwise, an error will be returned.

The similarity is calculated based on a feature vector containing numeric values. Thus, for a given set of user or tweet attributes, the features must be provided on which the similarity will be computed.

As a distance measure and, thus, the similarity of feature vectors, the vector norm of second order will be calculated which is equivalent to the euclidean distance. Therefore, the [```numpy.linalg.norm```](https://numpy.org/doc/stable/reference/generated/numpy.linalg.norm.html) function is used. The smaller the distance, the more similar the two vectors are.

The function will determine the distance between a distinct pair of user or tweet objects. For instance, when three user objects for the Twitter accounts ```12355```, ```734231```, ```9083468``` are provided, the following output will be generated:

```python
{(12355, 734231): 4567.098,
(12355, 9083468): 5980.076,
(734231, 9083468): 8763.32}
```

The output dictionary contains the distinct pairs of objects as a tuple as dictionary keys. The distances for each distinct pair is given as dictionary value. The output is sorted in ascending order. Hence, the minimal distance and, thus, the most similar pair is provided as first dictionary entry.

Function:
```python
TwitterDataProcessor.calc_similarity(user_objs: List[dict] | None = None, tweet_metrics: List[Dict[int, dict]] | None = None, *, features: List[str])
```

Args:

- ``user_objs`` (List[dict] | None, optional): List of serialized Twitter user objects from Twitter Search API v1. Defaults to None.
- ``tweet_metrics`` (List[Dict[int | dict]] | None, optional): List of public Tweet metrics as dictionaries with Tweet IDs as keys. Defaults to None.
- ``features`` (List[str]): Features that should be contained in the feature vector. Features have to be numeric and must belong to the respective object (i.e., user or tweet.)


The features that can be provided for the ```features``` list can be found in the [detailed description of the attributes for the ```compare_tweets``` function](../user-guide/overview/literals-compare-tweets.md) and the [detailed description of the attributes for the  ```compare_users``` function](../user-guide/overview/literals-compare-users.md).



The implementation design of this function allows a comparison of Twitter users or tweets based on the available metrics. The implementation was inspired by the characterics of social bots on Twitter as they often have a similar number of followers or followees and their posted tweets often have a similar number of likes. Thus, the calculated similarities might help to identify bot-like behavior of Twitter accounts as well as identify deviations from normal Twitter accounts. If their similarities are small, they are likely to have a similar behavior on Twitter (i.e., a bot could be analyzed).


<details>
<summary>Source Code</summary>
```python
def calc_similarity(self, user_objs: List[dict] | None = None, tweet_metrics: List[Dict[int, dict]] | None = None, *, features: List[str]) -> dict:
    """Calculates the euclidean distance of users/tweets based on a feature vector. Either user objects or Tweet objects must be specified, not both.

    Args:
        user_objs (List[dict] | None, optional): List of serialized Twitter user objects from Twitter Search API v1. Defaults to None.
        tweet_metrics (List[Dict[int | dict]] | None, optional): List of public Tweet metrics as dictionaries with Tweet IDs as keys. Defaults to None.
        features (List[str]): Features that should be contained in the feature vector. Features have to be numeric and must belong to the respective object (i.e., user or tweet.)

    Raises:
        ValueError: If either 'user_objs' and 'tweet_objs' or none of them were provided.
        AssertionError: If non-numeric feature was provided in the 'features' list.

    Returns:
        dict: Unique pair of users/tweets containing the respective euclidean distance. Sorted in ascending order.
    """
    # init empty dict to store distances
    distances = dict()
    # if users and tweets were provided
    if user_objs and tweet_metrics:
        raise ValueError("Either 'user_objs' or 'tweet_metrics' must be specified, not both.")
    # if only user_objs were provided
    elif user_objs:
        # iterate over every uniqe pair
        for i in range(len(user_objs)):
            for j in range(i + 1, len(user_objs)):
                # get user objects for each pair
                user_i = user_objs[i]
                user_j = user_objs[j]
                # build feature vector
                vec_i = np.array([user_i[feature] for feature in features])
                vec_j = np.array([user_j[feature] for feature in features])
                # feature vectors have to contain numeric values
                assert all(isinstance(feat, Number) for feat in vec_i), "only numeric features are allowed"
                assert all(isinstance(feat, Number) for feat in vec_j), "only numeric features are allowed"
                # calc euclidean distance
                distances[(user_i["id"], user_j["id"])] = np.linalg.norm(vec_i - vec_j, ord=2)
    elif tweet_metrics:
        # iterate over every uniqe pair
        for i in range(len(tweet_metrics)):
            for j in range(i + 1, len(tweet_metrics)):
                # get Tweet objects for each pair
                tweet_i = list(tweet_metrics.values())[i]
                tweet_j = list(tweet_metrics.values())[j]
                # build feature vector
                vec_i = np.array([tweet_i[feature] for feature in features])
                vec_j = np.array([tweet_j[feature] for feature in features])
                # feature vectors have to contain numeric values
                assert all(isinstance(feat, Number) for feat in vec_i), "only numeric features are allowed"
                assert all(isinstance(feat, Number) for feat in vec_j), "only numeric features are allowed"
                # calc euclidean distance
                distances[(list(tweet_metrics.keys())[i], list(tweet_metrics.keys())[j])] = np.linalg.norm(vec_i - vec_j, ord=2)
    # if none was provided
    else:
        raise ValueError("Either 'user_objs' or 'tweet_metrics' must be provided.")
    # sort dict in ascendin order
    sorted_values = dict(sorted(distances.items(), key=operator.itemgetter(1)))
    return sorted_values
```
</details>
______________
