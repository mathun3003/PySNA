Software Testing
----------------

During the implementation process, a mixture of manual and automated testing was performed.

For automated testing, the library [VCR.py](https://vcrpy.readthedocs.io/en/latest/) is used. Thereby, cassettes (i.e., separate files) allow recording HTTP interactions (and their metadata) from external dependencies that use HTTP requests. They are stored under the ``tests/cassettes`` folder of the repository. When the test case is rerun, the cassettes are used to simulate an HTTP request and its responses caused by the client by recreating it from the prerecorded interactions without producing any traffic on the external services.

**NOTE**: Whenever any function using a cassette or fixture for testing is modified in its behavior, it is likely that the cassette and fixture have to be recreated as they store the results of a previous version of the function. This is especially the case when a new (comparison) attribute is made available to any of the four main functions of the ``TwitterAPI`` class.

After a function was implemented, it was tested manually first, and then the cassette was recoreded. A fixture with the expected results has been stored beforehand. During the implementation, regression testing was performed to ensure the correct functionality of the software component. The fixtures are saved under the ``tests/fixtures`` directory of the repository.

All fixtures are byte encoded are stored in pickle files.

Besides the VCR.py package, the ``unittest`` library was used to design test cases.

### Config

Within the ``config.py``, the secrets are loaded and a ``unittest.Testcase`` instance was created. This test case stores the secrets as well as class instances and forms the basis for other test cases.

For testing with VCR.py, bearer tokens are filtered from the headers.

<details>
<summary>Source Code</summary>
```python
tape = vcr.VCR(filter_headers=["Authorization"])


class PySNATestCase(unittest.TestCase):
    def setUp(self):
        self.bearer_token = bearer_token
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.rapidapi_key = rapidapi_key
        self.rapidapi_host = rapidapi_host

        self.api = TwitterAPI(self.bearer_token, self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret, self.rapidapi_key, self.rapidapi_host)

        self.fetcher = TwitterDataFetcher(self.bearer_token, self.consumer_key, self.consumer_secret, self.access_token, self.access_token_secret, self.rapidapi_key, self.rapidapi_host)

        self.data_processor = TwitterDataProcessor()
```
</details>

_______________________

### Testing TwitterAPI

Test cases for the ``TwitterAPI`` class test the four main functions of the class.

Therefore, the corresponding function is called first so get the cassette response. Then, the fixture is loaded and the results are compared.

The test cases can be found under the ``tests/test_api.py`` file of the repository.

<details>
<summary>Example for testing with cassettes</summary>
```python
@tape.use_cassette("tests/cassettes/tweet_info.yaml")
def test_tweet_info(self):
    cassette_response = self.api.tweet_info(test_tweet_id_1, get_args(self.api.LITERALS_TWEET_INFO))
    with open("tests/fixtures/tweet_info.pickle", "rb") as handle:
        expected_response = pickle.load(handle)
    self.assertDictEqual(cassette_response, expected_response)
```
</details>

_______________________
### Testing TwitterDataFetcher

For the ``TwitterDataFetcher`` class, unit testing was performed more granularly. Each function was tested with the help of cassettes and fixtures. The results were compared but also the instances and return types of each function were tested.

The test cases can be found under the ``tests/test_fetch.py`` file of the repository.

<details>
<summary>Example for testing with cassettes</summary>
```python
@tape.use_cassette("tests/cassettes/manual_request.yaml")
def test_manual_request(self):
    url = f"https://api.twitter.com/2/users/{test_user_id_1}"
    cassette_response = self.fetcher._manual_request(url, "GET", additional_fields={"user.fields": ["username"]})
    self.assertIsInstance(cassette_response, dict)
    self.assertEqual(cassette_response["data"]["username"], test_username_1)
    with open("tests/fixtures/manual_request.pickle", "rb") as handle:
        expected_response = pickle.load(handle)
    self.assertDictEqual(cassette_response, expected_response)
```
</details>



Here, some functions were tested for different inputs and check for the exact same output (i.e., Twitter user ID vs. screen name).

_______________________
### Testing TwitterDataProcessor

Both classes, ``BaseDataProcessor`` and ``TwitterDataProcessor``, were tested. Each function of the ```BaseDataProcessor`` class was tested with predefined unit tests without using cassettes. Results as well as instances were checked.

The test cases can be found under the ``tests/test_process.py`` file of the repository.

<details>
<summary>Example for unit testing without cassettes</summary>
```python
test_sets = {test_user_id_1: set([1, 3, 5, 7]), test_user_id_2: set([3, 6, 7, 9]), test_user_id_3: set([0, 3, 7])}

def test_intersection(self):
    # calc intersection
    results = self.data_processor.intersection(test_sets.values())
    # assert instances
    self.assertIsInstance(results, list)
    assert all(isinstance(item, Number) for item in results)
    # assert results to be equal
    self.assertListEqual(results, [3, 7])
```
</details>


For the functions of the ``TwitterDataProcessor`` class, unit tests were also defined previously. Some functions, however, required recently fetcher Twitter user or tweet objects to be tested. Therefore, cassettes and fixtures were created like for the functions of the ``TwitterAPI`` class.

<details>
<summary>Example for unit testing with cassettes</summary>
```python
@tape.use_cassette("tests/cassettes/user_obj.yaml")
def test_extract_followers(self):
    cassette_user = self.api.fetcher.get_user_object(test_user_id_1)
    results = self.data_processor.extract_followers(cassette_user)
    # ensure instances
    self.assertIsInstance(results, dict)
    # compare with fixture
    with open("tests/fixtures/extract_followers.pickle", "rb") as handle:
        test_results = pickle.load(handle)
    self.assertDictEqual(results, test_results)
```
</details>

_______________________
### Testing Utility Functions

Only the internal utility functions [``_tuples_to_string``](./utils.md#internal-utility-functions) and [``_string_to_tuple``](./utils.md#internal-utility-functions) are tested. Cassettes and fixture were not used as they does not rely on external data from a third-party service. These test cases were designed beforehand. The results as well as the instances were tested.

The test cases can be found under the ``tests/test_utils.py`` file of the repository.

_______________________
