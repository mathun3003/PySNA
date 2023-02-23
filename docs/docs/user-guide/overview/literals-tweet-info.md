Detailed Description of the Attributes for the [```tweet_info```](./TwitterAPI.md#tweet_info) function:

- ```id```: The integer representation of the unique identifier for this Tweet.  
- ```id_str```: The string representation of the unique identifier for this Tweet.  
- ```full_text```: The actual UTF-8 full text of the status update.  If the tweet is a retweet (marked by a leading 'RT' within the text), the text will be truncated to 140 characters. The full text of the original tweet is contained within the
- ```display_text_range```: The range of the tweet text characters provided as array containing the indexes of first and last character.  
```retweeted_status``` field. Hence, add the ```retweeted_status``` fields to the ```attributes``` list and see under ```retweeted_status``` -> ```full_text``` fields for the full text of the retweet.
- ```truncated```: Indicates whether the value of the ```text``` parameter was truncated, for example, as a result of a retweet exceeding the original Tweet text length limit of 140 characters. Truncated text will end in ellipsis, like this ... Since Twitter now rejects long Tweets vs truncating them, the large majority of Tweets will have this set to ```false``` . Note that while native retweets may have their toplevel text property shortened, the original text will be available under the ```retweeted_status``` object and the ```truncated``` parameter will be set to the value of the original status (in most cases, ```false```).  
- ```created_at```: UTC time when this Tweet was created.  
- ```entities```: Entities which have been parsed out of the text of the Tweet (hashtags, URLs, user mentions, media, symbols, polls).  
- ```tweet_annotations```: Context annotations and named entities of the Tweet object. Context annotations are derived from the analysis of a Tweet’s text and will include a domain and entity pairing which can be used to discover Tweets on topics that may have been previously difficult to surface. Named Entities are comprised of people, places, products, and organizations. Entities are delivered as part of the entity payload section. They are programmatically assigned based on what is explicitly mentioned (named-entity recognition) in the Tweet text. See the [official website](https://developer.twitter.com/en/docs/twitter-api/annotations/overview) for further details.
- ```source```: Utility used to post the Tweet, as an HTML-formatted string. Tweets from the Twitter website have a source value of ```web```.  
- ```retweeters```: Twitter user IDs from retweeters.  
- ```in_reply_to_status_id```: If the represented Tweet is a reply, this field will contain the integer representation of the original Tweet’s ID. (Nullable)  
- ```in_reply_to_status_id_str```: If the represented Tweet is a reply, this field will contain the string representation of the original Tweet’s ID. (Nullable)  
- ```in_reply_to_user_id```: If the represented Tweet is a reply, this field will contain the integer representation of the original Tweet’s author ID. This will not necessarily always be the user directly mentioned in the Tweet. (Nullable)
- ```in_reply_to_user_id_str```: If the represented Tweet is a reply, this field will contain the string representation of the original Tweet’s author ID. This will not necessarily always be the user directly mentioned in the Tweet. (Nullable)
- ```in_reply_to_screen_name```: If the represented Tweet is a reply, this field will contain the screen name of the original Tweet’s author. (Nullable)  
- ```user```: The user who posted this Tweet. See User data dictionary for complete list of attributes.
- ```contributors```: The contributors of the Tweet.  
- ```coordinates```: Represents the geographic location of this Tweet as reported by the user or client application. The inner coordinates array is formatted as geoJSON (longitude first, then latitude). (Nullable)  
- ```place```: When present, indicates that the tweet is associated (but not necessarily originating from) a place. (Nullable)  
- ```is_quote_status```: Indicates whether this is a Quoted Tweet.  
- ```public_metrics```: Public metrics for this Tweet containing (impressions_count (=views), quote_count, reply_count, retweet_count, favorite_count (=likes))  
- ```quoting_users```:  Twitter User IDs from users who quoted this Tweet.  
- ```liking_users```: Twitter User IDs from users who liked this Tweet.  
- ```favorited```: Indicates whether this Tweet has been liked by the authenticating user. (Nullable)  
- ```retweeted```: Indicates whether this Tweet has been Retweeted by the authenticating user.  
- ```retweeted_status```: Users can amplify the broadcast of Tweets authored by other users by retweeting . Retweets can be distinguished from typical Tweets by the existence of a retweeted_status attribute. This attribute contains a representation of the original Tweet that was retweeted. Note that retweets of retweets do not show representations of the intermediary retweet, but only the original Tweet.  
- ```possibly_sensitive```: This field indicates content may be recognized as sensitive. The Tweet author can select within their own account preferences and choose “Mark media you tweet as having material that may be sensitive” so each Tweet created after has this flag set. This may also be judged and labeled by an internal Twitter support agent. (Nullable)  
- ```lang```: When present, indicates a BCP 47 language identifier corresponding to the machine-detected language of the Tweet text, or ```und``` if no language could be detected. See more documentation [HERE](https://developer.twitter.com/en/docs/twitter-api/enterprise/powertrack-api/guides/operators).
- ```sentiment```: The sentiment of the Tweet, either positive, neutral, or negative. Polarity scores are returned additionally. The sentiment is detected by using [VADER](https://vadersentiment.readthedocs.io/en/latest/). It is recommended to analyze only english Tweets. In case a Tweet of a different language is analyzed, results will still be returned but might not be accurate.