Detailed Description of the Attributes for the [```compare_tweets```](./TwitterAPI.md#compare_tweets) function:

- ```view_count```: Compares the number of views the specified Tweets currently have. Will return additional statistical metrics on the numbers of views.  
- ```like_count```: Compares the number of likes the specified Tweets currently have. Will return additional statistical metrics on the numbers of likes.  
- ```retweet_count```: Compares the number of Retweets the specified Tweets currently have. Will return additional statistical metrics on the numbers of Retweets.  
- ```quote_count```: Compares the number of quotes the specified Tweets currently have. Will return additional statistical metrics on the numbers of quotes.  
- ```reply_count```: Compares the number of replies the specified Tweets currently have. Will return additional statistical metrics on the numbers of replies.
- ```common_quoting_users```: Returns the set of quoting Twitter users all specified Tweets have in common.  
- ```distinct_quoting_users```: Returns the sets of distinct quoting Twitter users all specified Tweets have (i.e., the difference between the quoting Twitter users of all Tweets is calculated).
- ```common_liking_users```: Returns the set of liking Twitter users all specified Tweets have in common.  
- ```distinct_liking_users```: Returns the sets of distinct liking Twitter users all specified Tweets have (i.e., the difference between the liking Twitter users of all Tweets is calculated).  
- ```common_retweeters```: Returns the set of retweeters all specified Tweets have in common.  
- ```distinct_retweeters```: Returns the sets of distinct retweeters all specified Tweets have (i.e., the difference between the retweeters of all Tweets is calculated).  
- ```similarity```: Computes the euclidean distance between two feature vectors. Each feature vector contains numerical attributes from each Tweet. The features that should be contained in the feature vector have to be provided in the features argument of the function. Available features are:

    - ```retweet_count```: The number of times a tweet was retweeted.  
    - ```reply_count```: Number of replies a Tweet has.  
    - ```like_count```: Number of likes a Tweet has.  
    - ```quote_count```: Number of quotes a Tweet has.  
    - ```impression_count```: Number of views a Tweet has.  

    If more than two Tweets were provided, all possible pairs of combinations will be returned containing a distance. The smaller the distance, the more similar the Tweets are. Output will be sorted in ascending order, thus, most similar Tweets are on top. Each entry in the output contains a pair of two Tweets.

- ```created_at```: Compares the specified Tweets on their creation dates. Additional Will return additional statistical metrics on the dates.  
