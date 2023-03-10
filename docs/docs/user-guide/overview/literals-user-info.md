Detailed Description of the Attributes for the [```user_info```](./TwitterAPI.md#user_info) function:


- ```id```: The integer representation of the unique identifier for this User.
- ```id_str```: The string representation of the unique identifier for this User.
- ```name```: The name of the user, as they’ve defined it.
- ```screen_name```: The screen name, handle, or alias that this user identifies themselves with.
- ```followers```: IDs, names, and screen names of the user's followers.
- ```followees```: IDs, names, and screen names of the user's followees.
- ```location```: The user-defined location for this account’s profile. (Nullable)
- ```description```: The user-defined UTF-8 string describing their account. (Nullable)
- ```url```: A URL provided by the user in association with their profile. (Nullable)
- ```entities```: Entities of the user object.
- ```protected```: When true, indicates that this user has chosen to protect their Tweets.
- ```followers_count```: The number of followers this account currently has.
- ```friends_count```: The number of users this account is following (AKA their “followings” or "followees").
- ```listed_count```: The number of public lists that this user is a member of.
- ```created_at```: The UTC datetime that the user account was created on Twitter.
- ```latest_activity```: Latest acitivity according to the users timeline. If the latest activity is a retweet (marked by a leading 'RT' in the text), the text will be truncated to 140 characters. The full text of the original tweet is in the ```retweeted_status``` field of the JSON response. Hence, see under the ```latest_activity``` -> ```retweeted_status``` -> ```full_text``` field.  
- ```last_active```: Datetime of the latest activity according to the users timeline.
- ```liked_tweets```:  List of IDs of the liked tweets by the user.
- ```composed_tweets```: List of IDs of the composed tweet by the user.
- ```favourites_count```: The number of Tweets this user has liked in the account’s lifetime. British spelling used in the field name for historical reasons.
- ```verified```: When true, indicates that the user has a verified account.
- ```statuses_count```: The number of Tweets (including retweets) issued by the user.
- ```status```: Latest tweet object according to the user's timeline.
- ```contributors_enabled```: Whether contributors are enabled for this account.
- ```profile_image_url_https```: A HTTPS-based URL pointing to the user’s profile image.
- ```profile_banner_url```: The HTTPS-based URL pointing to the standard web representation of the user’s uploaded profile banner.
- ```default_profile```: When true, indicates that the user has not altered the theme or background of their user profile.
- ```default_profile_image```: When true, indicates that the user has not uploaded their own profile image and a default image is used instead.
- ```withheld_in_countries```: When present, indicates a list of uppercase two-letter country codes this content is withheld from.
- ```bot_scores```:  Estimation for bot-like behavior from the [Botometer API](https://rapidapi.com/OSoMe/api/botometer-pro/details).
