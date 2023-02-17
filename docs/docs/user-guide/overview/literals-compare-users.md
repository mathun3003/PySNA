Detailed Description of the Attributes for the [```compare_users```](./TwitterAPI.md#compare_users) function:


- ```relationship```: Returns detailed information about the relationship between a pair two arbitrary users. If more than two users were provided, all possible pairs of relationships will be returned.  
- ```followers_count```: Compares the number of followers the specified accounts currently have. Will return additional statistical metrics on the numbers of followers.  
- ```followees_count```:  Compares the number of friends (AKA their “followings” or "followees") the specified accounts currently have. Will return additional statistical metrics on the numbers of friends.  
- ```tweets_count```: Compares the number of composed tweets the specified accounts currently have. Will return additional statistical metrics on the numbers of tweets.  
- ```favourites_count```: Compares the number of liked tweets the specified accounts currently have. Will return additional statistical metrics on the numbers of liked tweets. British spelling used in the field name for historical reasons.  
- ```common_followers```: Returns the set of followers all specified accounts have in common.  
- ```distinct_followers```: Returns the sets of distinct followers all specified accounts have (i.e., the difference between the followers of all accounts is calculated).  
- ```common_followees```: Returns the set of friends (AKA their “followings” or "followees") all specified accounts have in common.  
- ```distinct_followees```: Returns the sets of distinct friends (AKA their “followings” or "followees") all specified accounts have (i.e., the difference between the friends of all accounts is calculated).  
- ```commonly_liked_tweets```: Returns the set of liked tweets all specified accounts have in common.  
- ```distinctly_liked_tweets```: Returns the sets of distinct liked tweets all specified accounts have (i.e., the difference between all liked tweets of all accounts is calculated).  
- ```similarity```: Computes the euclidean distance between two feature vectors. Each feature vector contains numerical attributes from each user. The features that should be contained in the feature vector have to be provided in the ```features``` argument of the function. Available features are:  
    - ```followers_count```: The number of followers this account currently has.  
    - ```friends_count```: The number of users this account is following (AKA their “followings” or "followees").  
    - ```listed_count```: The number of public lists that this user is a member of.  
    - ```favourites_count```: The number of Tweets this user has liked in the account’s lifetime. British spelling used in the field name for historical reasons.  
    - ```statuses_count```: The number of Tweets (including retweets) issued by the user.  
If more than two users were provided, all possible pairs of combinations will be returned containing a distance. The smaller the distance, the more similar the users are. Output will be sorted in ascending order, thus, most similar users are on top.
Each entry in the output contains a pair of two users.
- ```created_at```: Compares the specified accounts on their creation dates. Additional Will return additional statistical metrics on the dates.  
- ```protected```: Compares users on their ```protected``` attribute. When true, indicates that this user has chosen to protect their Tweets.
- ```verified```: Compares users on their ```verified``` attribute. When true, indicates that the user has a verified account.
