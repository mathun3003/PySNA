Utility Functions
----------------

Utility functions are defined to read and write to specific files.

The files can be imported via

```python
from pysna.utils import export_to_json, export_to_csv, append_to_json, append_to_csv, load_from_json
```

or are included in the import-all-statement:

```python
from pysna import *
```

________

### Export to JSON

Function:

```python
export_to_json(data: dict, export_path: str, encoding: str = 'utf-8', ensure_ascii: bool = False, *args)
```
Export dictionary data to JSON file.
Function will add a ```data``` key for the JSON file and store the provided dictionary inside the ```data``` field.

Args:

- ```data``` (dict): Data dictionary.
- ```export_path``` (str): Export path including file name and extension.
- ```encoding``` (str, optional): Encoding of JSON file. Defaults to UTF-8.
- ```args``` (optional): Further arguments to be passed to ```json.dump()```.

References: [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)

**NOTE:** When trying to export a dictionary containing tuples as keys, the function will try to serialize them by converting tuples to strings. For recovering the original dictionary after JSON export, use the [```load_from_json```](#load-from-json) function.

Example:
```python
# request results for Tweet comparison, return timestamp
results = api.compare_tweets([1612443577447026689, 1611301422364082180, 1612823288723476480],
                             compare=["common_liking_users"],
                             return_timestamp=True)
# export to JSON file
export_to_json(results, export_path="compare_tweets.json")
```
The exported ```compare_tweets.json``` file will the look like:
```json
{
    "data": [
        {
            "common_liking_users": [
                3862364523
            ],
            "utc_timestamp": "2023-01-31 09:22:11.996652"
        }
}
```

________

### Append to JSON

Function:

```python
append_to_json(input_dict: Dict[str, Any], filepath: str, encoding: str = "utf-8", **kwargs)
```

Append a dictionary to an existing JSON file.  
Existing JSON file needs a 'data' key.

Args:

- ```input_dict```: Dictionary containing new data that should be added to file.
- ```filepath```: Absolute or relative filepath including the file extension. Depending on the current working directory.
- ```encoding```: The encoding of the file. Defaults to UTF-8.
- ```kwargs```: Additional keyword arguments to be passed to ```json.dump()``` and ```json.load()```

References: [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)

**Note:** When trying to append a dictionary containing tuples as keys, the function will try to serialize them by converting tuples to strings. For recovering the original dictionary after JSON export, use the [```load_from_json```](#load-from-json) function.

Example:

```python
# generate new results that should be appended in the next step
new_results = api.compare_tweets([1612443577447026689, 1611301422364082180, 1612823288723476480],
                                 compare=["common_liking_users"],
                                 return_timestamp=True)

# append to an existing file.
append_to_json(new_results, "compare_tweets.json")
```

The extended ```compare_tweets.json``` file will be supplemented with one further entry within the ```data``` field. An example output could look like:

```json
{
    "data": [
        {
            "common_liking_users": [
                3862364523
            ],
            "utc_timestamp": "2023-01-31 09:22:11.996652"
        },
        {
            "common_liking_users": [
                3862364523
            ],
            "utc_timestamp": "2023-01-31 09:23:05.848485"
        }
    ]
}

```
________

### Load from JSON

Function:
```python
load_from_json(filepath: str, encoding: str = "utf-8", **kwargs) -> dict
```
Load Python Dictionary from JSON file. Tuples are recovered.

Args:

- ```filepath``` (str): Path to JSON file.
- ```encoding``` (str, optional): Encoding of file. Defaults to UTF-8.
- ```kwargs``` (optional): Keyword arguments to be passed to ```json.load()```.

Returns:
Python Dictionary containing (deserialized) data from JSON file.


References: [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)

Example:
Suppose an ```example.json``` file containing one entry with a serialized tuple key:
```json
{
    "data": [
        {
            "(WWU_Muenster, goetheuni)": 0.578077
        }
    ]
}
```
By calling:
```python
from pysna.utils import load_from_json

data = load_from_json("example.json")
print(data)
```
the tuple will be recovered and a conventional Python Dictionary will be returned:
```
{("WWU_Muenster", "goetheuni"): 0.578077}
```

________

### Export to CSV

Function:

```python
export_to_csv(data: dict, export_path: str, encoding: str = "utf-8", sep: str = ",", **kwargs)
```

Export dictionary data to CSV file.  
Will raise an exception if ```data``` dictionary contains nested dictionaries.

Args:

- ```data``` (dict): Data dictionary
- ```export_path``` (str): Exportpath including file name and extension.
- ```encoding``` (str, optional): Encoding of CSV file. Defaults to UTF-8.
- ```sep``` (str, optional): Value separator for CSV file. Defaults to ```','```.
- ```kwargs``` (optional): Keyword arguments for ```pandas.DataFrame.to_csv```.

References: [https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)

Example:

```python
# request results for user information, return timestamp
results = api.user_info("WWU_Muenster",
                        ["id", "location", "friends_count", "followers_count", "last_active", "statuses_count"],
                        return_timestamp=True)
# export to CSV file
export_to_csv(results, export_path="user_info.csv")
```

________

### Append to CSV

Function:

```python
append_to_csv(data: dict, filepath: str, encoding: str = "utf-8", sep: str = ",", *args)
```

Append a dictionary to an existing CSV file.  
Will raise an exception if ```data``` dictionary contains nested dictionaries.


Args:

- ```data``` (dict): Dictionary containing new data that should be added to file.
- ```filepath``` (str): Absolute or relative filepath including the file extension. Depending on the current working directory.
- ```encoding``` (str, optional): Encoding of CSV file. Defaults to UTF-8.
- ```sep``` (str, optional): Value separator for CSV file. Defaults to ",".
- ```args```: Keyword Arguments for reading and writing from/to CSV file from pandas. Pass in: ```*[read_kwargs, write_kwargs]```, whereas both are dictionaries (i.e., provide a list of two dictionaries).

References:  

- [https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)  
- [https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)


Example:
```python
# request results for user information, return timestamp
results = api.user_info("WWU_Muenster",
                        ["id", "location", "friends_count", "followers_count", "last_active", "statuses_count"],
                        return_timestamp=True)
# export to CSV file
append_to_csv(results, filepath="user_info.csv")
```

________

Notes
----------------
- Only JSON and CSV file formats are supported, yet.
