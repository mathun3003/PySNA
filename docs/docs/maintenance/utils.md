Utility Functions
----------------

Some utility functions were implemented to support export and import of collected data to different formats. With the help of these functions, a comparison over time is made possible as they can be used in combination with specific arguments from the main functions of the ``TwitterAPI`` class.

Besides the class-linked methods from the ``TwitterAPI``, ``TwitterDataFetcher``, and ``TwitterDataProcessor`` classes, utility functions were developed which are part of the ``utils`` module of the package. These are, by not being part of a class, not only usable for Twitter data exclusively, but also for data from other social media platforms and are not linked to classes or the corresponding platforms, therefore. Methods for export to CSV and JSON files were designed as well as appending new observations to existing files.

All functions can be imported by running:
```python
from pysna.utils import *
```
or name the desired functions in the import statement.

In the following, functions for internal usage as well as user functions are presented.

# Internal Utility Functions

The following functions are used internally at different places in the code. They are not intended to be used directly by users. Often, they are designed to be helper functions for contributing developers.

_____________

### strf_datetime

Converts datetime objects to string representation. Default format is ``%Y-%m-%d %H:%M:%S`` and will return a datetime string like ``2023-03-10 09:16:12.662320``.

Function:
```python
strf_datetime(date: datetime, format: str = "%Y-%m-%d %H:%M:%S")
```

This function takes in a date format string. Any other format different to the default one can be passed in using the ``format`` argument.

This function is used internally to convert a Unix timestamp to a readable format. This is the case, for the ``return_timestamp`` argument of the four main functions from the ``TwitterAPI`` class`.

<details>
<summary>Source Code</summary>
```python
def strf_datetime(date: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Convert datetime object to string representation.

    Args:
        date (datetime): Input datetime object
        format (str, optional): Datetime string format. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: string representation of input datetime in given format.
    """
    return date.strftime(format)
```
</details>

_____________

### tuple_to_string (private)

This function serializes tuples-keys from dictionaries to string representation. A tuple-key wil obtain a leading ``__tuple__`` string and decomposed in list representation. This function is private as it is not intended for external usage by the package user.

The reason why this function was implemented is that an export to JSON format is not possible with tuples as keys. Some of the four main functions from the ``TwitterAPI`` class will generate tuples as dictionary keys (e.g., when a relationship of two Twitter users or twees is investigated). The JSON format does not support tuples for serialization and, thus, needs a list representation of Python tuples. This function will iterate recursively through the entire dictionary that is provided to the function and will exchange the dictionary tuple-keys to a string representation. Thus, even for nested dictionaries, this function will find and convert all tuple-keys inside the dictionary.

Function:
```python
_tuple_to_string(obj: Any)
```

For instance, a tuple-key like ```("WWU_Muenster", "goetheuni")``` will be encoded to ``__tuple__["WWU_Muenster", "goetheuni"]``. Then, the ``JSONEncoder`` class from the ``json`` Python module can convert this key as string.

This function is used within the [``export_to_json``](./utils.md#export_to_json) function to serialize tuples inside the data dictionary.

In order to avoid a manipulation of the object passed in, a deep copy of the object is performed at the beginning before conversion.

<details>
<summary>Source Code</summary>
```python
def _tuple_to_string(obj: Any) -> Any:
    """Serialize tuple-keys to string representation. A tuple wil obtain a leading '__tuple__' string and decomposed in list representation.

    Args:
        obj (Any): Typically a dict, tuple, list, int, or string.

    Returns:
        Any: Input object with serialized tuples.

    Example:
        A tuple ("WWU_Muenster", "goetheuni") will be encoded to "__tuple__["WWU_Muenster", "goetheuni"].
    """
    # deep copy object to avoid manipulation during iteration
    obj_copy = copy.deepcopy(obj)
    # if the object is a dictionary
    if isinstance(obj, dict):
        # iterate over every key
        for key in obj:
            # set for later to avoid modification in later iterations when this var does not get overwritten
            serialized_key = None
            # if key is tuple
            if isinstance(key, tuple):
                # stringify the key
                serialized_key = f"__tuple__{list(key)}"
                # replace old key with encoded key
                obj_copy[serialized_key] = obj_copy.pop(key)
            # if the key was modified
            if serialized_key is not None:
                # do it again for the next nested dictionary
                obj_copy[serialized_key] = _tuple_to_string(obj[key])
            # else, just do it for the next dictionary
            else:
                obj_copy[key] = _tuple_to_string(obj[key])
    return obj_copy
```
</details>

_____________

### string_to_tuple (private)

This function converts serialized tuples back to original representation. Serialized tuples need to have a leading ``__tuple__`` string. This function is private as no external usage by the package user is intended.

This function does the opposite of what the [``_tuple_to_string``](./utils.md#tuple_to_string) function does. Since any tuple-keys were decomposed into a string representation through the [``export_to_json``](./utils.md#export_to_json) function, these tuples need to be recovered when the data is to be imported again. Therefore, this function is used internally within the [```load_from_json```](./utils.md#load_from_json) function. This function iterates recursively through the entire JSON data that is being loaded and decodes any serialized tuple with a leading ``__tuple__`` string to the corresponding Python tuple representation, so that serialized tuples are recovered.

Function:
```python
_string_to_tuple(obj: Any)
```

In order to avoid a manipulation of the object passed in, a deep copy of the object is performed at the beginning before conversion.

<details>
<summary>Source Code</summary>
```python
def _string_to_tuple(obj: Any) -> Any:
    """Convert serialized tuples back to original representation. Tuples need to have a leading "__tuple__" string.

    Args:
        obj (Any): Typically a dict, tuple, list, int, or string.

    Returns:
        Any: Input object with recovered tuples.

    Example:
        A encoded tuple "__tuple__["WWU_Muenster", "goetheuni"] will be decoded to ("WWU_Muenster", "goetheuni").
    """
    # deep copy object to avoid manipulation during iteration
    obj_copy = copy.deepcopy(obj)
    # if the object is a dictionary
    if isinstance(obj, dict):
        # iterate over every key
        for key in obj:
            # set for later to avoid modification in later iterations when this var does not get overwritten
            serialized_key = None
            # if key is a serialized tuple starting with the "__tuple__" affix
            if isinstance(key, str) and key.startswith("__tuple__"):
                # decode it so tuple
                serialized_key = tuple(key.split("__tuple__")[1].strip("[]").replace("'", "").split(", "))
                # if key is number in string representation
                if all(entry.isdigit() for entry in serialized_key):
                    # convert to integer, recover ID
                    serialized_key = tuple(map(int, serialized_key))
                # replace old key with encoded key
                obj_copy[serialized_key] = obj_copy.pop(key)
            # if the key was modified
            if serialized_key is not None:
                # do it again for the next nested dictionary
                obj_copy[serialized_key] = _string_to_tuple(obj[key])
            # else, just do it for the next dictionary
            else:
                obj_copy[key] = _string_to_tuple(obj[key])
    # if another instance was found
    elif isinstance(obj, list):
        for item in obj:
            _string_to_tuple(item)
    return obj_copy
```
</details>

_____________

# User Utility Functions

These functions are designed for external usage by the package user. They allow export to JSON or CSV formats as well as appending new observations to existing files. For the JSON format specifically, a function was designed to load and recover a saved Python dictionary from a JSON file.

All user utility function can be imported by running
```python
from pysna import *
```
as they are part of the import-all shortcut.

_____________

### export_to_json

Export dictionary data to JSON file. Tuple-keys are encoded to strings.

Function:
```python
export_to_json(data: dict, export_path: str, encoding: str = "utf-8", ensure_ascii: bool = False, *args)
```

Args:

- ``data`` (dict): Data dictionary that should be exported.
- ``export_path`` (str): Export path including file name and extension.
- ``encoding`` (str, optional): Encoding of JSON file. Defaults to "utf-8".
- ``ensure_ascii`` (bool): Wheather to convert characters to ASCII. Defaults to False.

Other encodings could be specified by overwriting the default for the ``encoding`` argument. The ``ensure_ascii`` argument is used for the ``json.dump`` function from the ``json`` Python module. Additional arguments can be passed to the ``json.dump`` function by the ```*args`` argument of this function.

In case a tuple was detected in the input data dictionary, an error will be raised during the serialization since JSON does not support tuple encoding. Therefore, the ``TypeError`` or ``json.JSONDecodeError`` are caught and the data dictionary will be preprocessed by the internal [``_tuple_to_string``](./utils.md#tuple_to_string) function. Then, all tuple-keys inside the data dictionary will be converted to a string representation and the export will be repeated with the serialized tuples.

Any exported dictionary will be exported to a JSON file of the form:
```json
{
    "data": [
        ...
    ]
}
```

Thus, the dictionary will be stored inside the list of the ``data`` key. This allows appending new entries to the same file (for more information, see the [``append_to_json``](./utils.md#append_to_json) function).

Reference: [https://docs.python.org/3/library/json.html](https://docs.python.org/3/library/json.html)


<details>
<summary>Source Code</summary>
```python
def export_to_json(data: dict, export_path: str, encoding: str = "utf-8", ensure_ascii: bool = False, *args):
    """Export dictionary data to JSON file. Tuple-keys are encoded to strings.

    Args:
        data (dict): Data dictionary
        export_path (str): Export path including file name and extension.
        encoding (str, optional): Encoding of JSON file. Defaults to "utf-8".
        ensure_ascii (bool): Wheather to convert characters to ASCII. Defaults to False.
    """

    try:
        with open(export_path, "w", encoding=encoding) as jsonfile:
            # add 'data' key in order to append additional dicts to same file, if not already exist
            if "data" not in data:
                serialized_data = {"data": [data]}
            # dump to json
            json.dump(serialized_data, jsonfile, indent=4, ensure_ascii=ensure_ascii, *args)
    except IOError as e:
        raise e
    # usually when tuple cannot be serialized
    except TypeError or json.JSONDecodeError:
        # serialize tuples
        data = _tuple_to_string(data)
        # retry
        export_to_json(data=data, export_path=export_path, encoding=encoding, ensure_ascii=ensure_ascii)
    pass
```
</details>

_____________

### append_to_json

Append a dictionary to an existing JSON file. Tuple-keys are encoded to strings.

Function:
```python
append_to_json(input_dict: Dict[str, Any], filepath: str, encoding: str = "utf-8", **kwargs)
```

Args:  

- ``input_dict`` (Dict[str, Any]): Dictionary containing new data that should be added to file.
- ``filepath`` (str): Absolute or relative filepath including the file extension. Depending on the current working directory.
- ``encoding`` (str, optional): The encoding of the file. Defaults to "utf-8".

The function takes in a data dictionary containing the data that should be added to an existing file. Tuple-keys will be encoded to strings using the [``_tuples_to_strings``](./utils.md#tuples_to_strings) function. If any tuple-key inside the dictionary is detected during the serialization, the corresponding ``TypeError`` and/or ``json.JSONDecodeError`` will be caught and the [``_tuples_to_strings``](./utils.md#tuples_to_strings) will be invoked. After that, the export will be repeated. The filepath of the existing JSON file must be provided including the file extension. Other encodings different to UTF-8 can also be specified. Keyword arguments can also be passed to the ``json.dumps`` function by the ``**kwargs`` argument.

The provided input data dictionary will be appended to the ``data`` key of the JSON file. Hence, the existing file must be of the form:

```json
{
    "data": [
        ...
    ]
}
```

<details>
<summary>Source Code</summary>
```python
def append_to_json(input_dict: Dict[str, Any], filepath: str, encoding: str = "utf-8", **kwargs):
    """Append a dictionary to an existing JSON file. Tuple-keys are encoded to strings.

    Args:
        input_dict (Dict[str, Any]): Dictionary containing new data that should be added to file.
        filepath (str): Absolute or relative filepath including the file extension. Depending on the current working directory.
        encoding (str, optional): The encoding of the file. Defaults to "utf-8".

    NOTE: Existing JSON file needs a 'data' key.

    Raises:
        ValueError: If input dict and file do not have the same keys or columns, respectively.
    """

    # load file from path
    with open(filepath, "r", encoding=encoding) as input_file:
        f = json.load(input_file, **kwargs)
    # existing file should have a "data"-key and a list to append to
    if "data" not in f.keys():
        raise KeyError("The file to be extended must contain the key 'data'.")
    else:
        try:
            # serialize tuples if any exist
            input_dict = _tuple_to_string(input_dict)
            # append new dict to file
            f["data"].append(input_dict)
            with open(filepath, "w", encoding=encoding) as jsonfile:
                json.dump(f, jsonfile, indent=4, **kwargs)
        except IOError as e:
            raise e
        # usually when tuple cannot be serialized
        except TypeError or json.JSONDecodeError:
            # serialize tuples
            input_dict = _tuple_to_string(input_dict)
            # retry
            append_to_json(input_dict=input_dict, filepath=filepath, encoding=encoding, **kwargs)
    pass
```
</details>

________________

### load_from_json

Load Python dictionary from JSON file. Tuples are recovered.

Function:
```python
load_from_json(filepath: str, encoding: str = "utf-8", **kwargs)
```

Args:  

- ``filepath`` (str): Path to JSON file.
- ``encoding`` (str, optional): Encoding of file. Defaults to "utf-8".


The function allows to recover a JSON serialized dictionary containing tuple-keys. Therefore, the interncal [``_strings_to_tuples``](./utils.md#strings_to_tuples) is used. The user will get a full Python dictionary like before the export to JSON of it.

<details>
<summary>Source Code</summary>
```python
def load_from_json(filepath: str, encoding: str = "utf-8", **kwargs) -> dict:
    """Load Python Dictionary from JSON file. Tuples are recovered.

    Args:
        filepath (str): Path to JSON file.
        encoding (str, optional): Encoding of file. Defaults to "utf-8".

    Returns:
        dict: Python Dictionary containing (deserialized) data from JSON file.
    """
    # read from filepath
    with open(filepath, "r", encoding=encoding) as jsonfile:
        f = json.load(jsonfile, **kwargs)

    if "data" in f:
        entries = [_string_to_tuple(entry) for entry in f["data"]]
        f = {"data": entries}
    else:
        # try to deserialize if any tuples were found in the file
        f = _string_to_tuple(f)
    return f
```
</details>

_____________

### export_to_csv

Besides the JSON export, a CSV export option is provided by this function. Dictionary data is exported to CSV files using the [Pandas](https://pandas.pydata.org/) package.

Function:
```python
export_to_csv(data: dict, export_path: str, encoding: str = "utf-8", sep: str = ",", **kwargs)
```

Args:  

- ``data`` (dict): Data dictionary (nested dictionaries are not allowed)
- ``export_path`` (str): Export path including file name and extension.
- ``encoding`` (str, optional): Encoding of CSV file. Defaults to 'utf-8'.
- ``sep`` (str, optional): Value separator for CSV file. Defaults to ",".
- ``kwargs``: Keyword arguments for pd.DataFrame.to_csv. See references below for further details.

The function will raise a ``ValueError`` if a nested dictionary was provided.

This function was designed to allow an export of a simple one-level dictionary to a more readable format compared to JSON. However, it is highly recommended to use the JSON export function instead.


Reference: [https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)

<details>
<summary>Source Code</summary>
```python
def export_to_csv(data: dict, export_path: str, encoding: str = "utf-8", sep: str = ",", **kwargs):
    """Export dictionary data to CSV file.

    Args:
        data (dict): Data dictionary (nested dictionaries are not allowed)
        export_path (str): Export path including file name and extension.
        encoding (str, optional): Encoding of CSV file. Defaults to 'utf-8'.
        sep (str, optional): Value separator for CSV file. Defaults to ",".
        kwargs: Keyword arguments for pd.DataFrame.to_csv. See references below for further details.

    Raises:
        ValueError: If nested dictionary was provided.
        IOError: If export fails due to bad input.

    References: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
    """
    # catch nested dict
    if any(isinstance(data[key], dict) for key in data.keys()):
        raise ValueError("'data' dictionary must not contain nested dictionaries. Use JSON export instead.")
    try:
        # convert to pandas dataframe from dict
        f = pd.DataFrame(data, index=[0])
        # export data frame
        f.to_csv(export_path, encoding=encoding, sep=sep, index=False, **kwargs)
    except IOError as e:
        raise e
```
</details>

_____________

### append_to_csv

Append a dictionary to an existing CSV file.

Function:
```python
append_to_csv(data: dict, filepath: str, encoding: str = "utf-8", sep: str = ",", *args)
```

Args:  

- ``data`` (dict): Dictionary containing new data that should be added to file.
- ``filepath`` (str): Absolute or relative filepath including the file extension. Depending on the current working directory.
- ``encoding`` (str, optional): Encoding of CSV file.. Defaults to 'utf-8'.
- ``sep`` (str, optional): Value separator for CSV file. Defaults to ",".
- ``args``: Keyword Arguments for reading and writing from/to CSV file from pandas. Pass in: *[read_kwargs, write_kwargs]. See references below for further details on possible read/write arguments.

The ``args`` argument allows to specify additional read and write options. Therefore, the user can pass in a list containing keyword arguments for read and write. Thus, the ``args`` argument has to be of the form:

```python
[{"doublequote": False},    # read keywords arguments
{"prefix": "foo_"}]         # write keywords argument
```

Read keyword arguments will be passed to the p``andas.read_csv`` function whereas write keyword arguments will be passed to the ``pandas.DataFrame.to_csv`` function.

The function will raise a ``ValueError`` if a nested dictionary was provided.

This function was designed to allow an append of a simple one-level dictionary to an existing CSV file. However, it is highly recommended to use the JSON export function instead.

References:  

- [Pandas to CSV](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)
- [Pandas read CSV](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)

<details>
<summary>Source Code</summary>
```python
def append_to_csv(data: dict, filepath: str, encoding: str = "utf-8", sep: str = ",", *args):
    """Append a dictionary to an existing CSV file.

    Args:
        data (dict): Dictionary containing new data that should be added to file.
        filepath (str): Absolute or relative filepath including the file extension. Depending on the current working directory.
        encoding (str, optional): Encoding of CSV file.. Defaults to 'utf-8'.
        sep (str, optional): Value separator for CSV file. Defaults to ",".
        args: Keyword Arguments for reading and writing from/to CSV file from pandas. Pass in: *[read_kwargs, write_kwargs]. See references below for further details on possible read/write arguments.

    Raises:
        ValueError: If nested dictionary was provided.
        ValueError: If 'args' does not contain a dictionaries for read and write.
        IOError: If export fails due to bad input.

    References:
        - https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
        - https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    """
    # catch nested dict
    if any(isinstance(data[key], dict) for key in data.keys()):
        raise ValueError("'data' dictionary must not contain nested dictionaries. Use JSON export instead.")
    if args:
        if any(not isinstance(kwargs, dict) for kwargs in args):
            raise ValueError("'args' must be of type list containing dictionaries.")
    try:
        # read existing file
        f = pd.read_csv(filepath, sep=sep, encoding=encoding)
        # convert data dict to df
        input_df = pd.DataFrame(data, index=[0])
        # concat dfs
        f = pd.concat([f, input_df], axis=0)
        # export to CSV
        f.to_csv(filepath, sep=sep, encoding=encoding, index=False)
    except IOError as e:
        raise e
```
</details>
_____________

A function for CSV import was not designed as this was already implemented by the ``csv`` Python package or the ``Pandas`` package. Thus, a comparable function seemed unreasonable and redundant.
_____________
