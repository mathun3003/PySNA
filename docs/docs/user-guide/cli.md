Command-line Interface Tool
----------------
The main functions from the TwitterAPI class are also available on the CLI.

To see the usage instructions and help, run:

```bash
pysna -h
```

If you wish to see the usage instructions for a function, run:

```bash
pysna <function> --help
```

For example, if you want to request a comparison of two users, you can run:

```bash
pysna compare-users "WWU_Muenster" "goetheuni" -c "tweets_count" "common_followers" -o "results.json" --return-timestamp
```

This will perform a comparison on the ``"WWU_Muenster"`` and ``"goetheuni"`` Twitter Accounts based their number of composed Tweets and their common followers. The results are exported to the ``results.json`` file. Also, the timestamp of the request will be returned.

**NOTE**: every request needs valid credentials for the official Twitter API. If you run this command from a different directory than from your project root, pass in the path to an ``.env`` file containing your secrets. Also, if you have a differend named environment file in your project root (e.g., ``local.env``), you have to pass the filename, too, using the ``--env`` flag:

```bash
pysna compare-users [...] --env ./local.env
```

The default value is set to ``./.env``.

**NOTE**: The ```.env``` file must be of the form:

```
BEARER_TOKEN=...
CONSUMER_KEY=...
CONSUMER_SECRET=...
ACCESS_TOKEN=...
ACCESS_TOKEN_SECRET=...
X_RAPIDAPI_KEY=...
X_RAPIDAPI_HOST=...
```

- ```BEARER_TOKEN```: Twitter API OAuth 2.0 Bearer Token
- ```CONSUMER_KEY```: Twitter API OAuth 1.0a Consumer Key
- ```CONSUMER_SECRET```: Twitter API OAuth 1.0a Consumer Secret
- ```ACCESS_TOKEN```: Twitter API OAuth 1.0a Access Token
- ```ACCESS_TOKEN_SECRET```: Twitter API OAuth 1.0a Access Token Secret
- ```X_RAPIDAPI_KEY```: Access Token for the [Botometer API](https://rapidapi.com/OSoMe/api/botometer-pro/details) from the [RapidAPI platform](https://rapidapi.com/hub)
- ```X_RAPIDAPI_HOST```: Host for the [Botometer API](https://rapidapi.com/OSoMe/api/botometer-pro/details) from the [RapidAPI platform](https://rapidapi.com/hub)

________

Functions
------------
### user-info

Command:

```pysna user-info <user> <attributes> [--return-timestamp] [--output] [--append] [--encoding] [--env]```

Args:

- ```user``` (required): Twitter User ID or unique screen name
- ```attributes``` (required): pass in desired attributes separated by space. For a list of attributes, see the corresponding section in the [overview](overview.md).
- ```return-timestamp``` (optional): return UTC timestamp of the query.
- ```output``` (optional): writes the output to a file. Pass in the file path and file name including the extension. If empty, output is printed to the CLI. Currently, CSV and JSON exports are supported. (e.g., write ```output.json``` for JSON export.).
Flag short form:```-o```.
- ```append``` (optional): appends the output to an existing file. Pass in the path to the existing file with the ```output``` flag.
- ```encoding``` (optional): specify file encoding. Defaults to UTF-8.
- ```env``` (positional): specify path to environment file. Defaults to ```.env```.
Flag short form:```-e```.

________

### compare-users

Command:

```pysna compare-users <users> -c <compare> [--features] [--return-timestamp] [--output] [--append] [--encoding] [--env]```

Args:

- ```users``` (required): IDs or unique screen names of Twitter users. Pass in the users separated by space.
- ```compare``` (required): Comparison attributes Must be from the following: ```relationship```, ```followers_count```, ```followees_count```, ```tweets_count```, ```favourites_count```, ```common_followers```, ```distinct_followers```, ```common_followees```, ```distinct_followees```, ```commonly_liked_tweets```, ```distinctly_liked_tweets```, ```similarity```, ```created_at```, ```protected```, ```verified```.
For an overview of what the comparison attributes do, see the corresponding section in the [overview](overview.md).
Provide the comparison attributes separated by space after the ```-c``` flag.
- ```features``` (positional): Define the components of the feature vector for the ```similarity``` comparison attribute. Must be passed in if the aforementioned comparison attribute was provided.
Features must be from: ```followers_count```, ```friends_count```, ```listed_count```, ```favourites_count```, ```statuses_count```.
- ```return-timestamp``` (optional): return UTC timestamp of the query.
- ```output``` (optional): writes the output to a file. Pass in the file path and file name including the extension. If empty, output is printed to the CLI. Currently, CSV and JSON exports are supported. (e.g., write ```output.json``` for JSON export.).
Flag short form:```-o```.
- ```append``` (optional): appends the output to an existing file. Pass in the path to the existing file with the ```output``` flag.
- ```encoding``` (optional): specify file encoding. Defaults to UTF-8.
- ```env``` (positional): specify path to environment file. Defaults to ```.env```.
Flag short form:```-e```.

________

### tweet-info

Command:

```pysna tweet-info <tweet> <attributes> [--return-timestamp] [--output] [--append] [--encoding] [--env]```

Args:

- ```tweet``` (required): Unique Tweet ID.
- ```attributes``` (required): pass in desired attributes separated by space. For a list of attributes, see the corresponding section in the [overview](overview.md).
- ```return-timestamp``` (optional): return UTC timestamp of the query.
- ```output``` (optional): writes the output to a file. Pass in the file path and file name including the extension. If empty, output is printed to the CLI. Currently, CSV and JSON exports are supported. (e.g., write ```output.json``` for JSON export.)
Flag short form:```-o```.
- ```append``` (optional): appends the output to an existing file. Pass in the path to the existing file with the ```output``` flag.
- ```encoding``` (optional): specify file encoding. Defaults to UTF-8.
- ```env``` (positional): specify path to environment file. Defaults to ```.env```.
Flag short form:```-e```.

________

### compare-tweets

Command:

```pysna compare-tweets <tweets> -c <compare> [--features] [--return-timestamp] [--output] [--append] [--encoding] [--env]```

Args:

- ```tweets``` (required): Unique Tweet IDs separated by space.
- ```compare``` (required): Comparison attributes Must be from the following: ```view_count```, ```like_count```, ```retweet_count```, ```quote_count```, ```reply_count```, ```common_quoting_users```, ```distinct_quoting_users```, ```common_liking_users```, ```distinct_liking_users```, ```common_retweeters```, ```distinct_retweeters```, ```similarity```, ```created_at```.
For an overview of what the comparison attributes do, see the corresponding section in the [overview](overview.md).
Provide the comparison attributes separated by space after the ```-c``` flag.
- ```features``` (positional): Define the components of the feature vector for the ```similarity``` comparison attribute. Must be passed in if the aforementioned comparison attribute was provided.
Features must be from: ```retweet_count```, ```favorite_count```.
- ```return-timestamp``` (optional): return UTC timestamp of the query.
- ```output``` (optional): writes the output to a file. Pass in the file path and file name including the extension. If empty, output is printed to the CLI. Currently, CSV and JSON exports are supported. (e.g., write ```output.json``` for JSON export.).
Flag short form:```-o```.
- ```append``` (optional): appends the output to an existing file. Pass in the path to the existing file with the ```output``` flag.
- ```encoding``` (optional): specify file encoding. Defaults to UTF-8.
- ```env``` (positional): specify path to environment file. Defaults to ```.env```.
Flag short form:```-e```.

________

Notes
------------
- Only ``.env`` files are supported for the CLI, yet.
