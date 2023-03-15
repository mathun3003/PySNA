# -*- coding: utf-8 -*-
import copy
import json
import warnings
from datetime import datetime
from typing import Any, Dict

import pandas as pd

warnings.simplefilter(action="ignore", category=FutureWarning)


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

    References:
        - https://mathun3003.github.io/PySNA/user-guide/overview/Utilities/#export-to-csv
        - https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
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


def append_to_csv(data: dict, filepath: str, encoding: str = "utf-8", sep: str = ","):
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
        - https://mathun3003.github.io/PySNA/user-guide/overview/Utilities/#append-to-csv
        - https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html
        - https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
    """
    # catch nested dict
    if any(isinstance(data[key], dict) for key in data.keys()):
        raise ValueError("'data' dictionary must not contain nested dictionaries. Use JSON export instead.")
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


def export_to_json(data: dict, export_path: str, encoding: str = "utf-8", ensure_ascii: bool = False, *args):
    """Export dictionary data to JSON file. Tuple-keys are encoded to strings.

    Args:
        data (dict): Data dictionary
        export_path (str): Export path including file name and extension.
        encoding (str, optional): Encoding of JSON file. Defaults to "utf-8".
        ensure_ascii (bool): Wheather to convert characters to ASCII. Defaults to False.

    References: https://mathun3003.github.io/PySNA/user-guide/overview/Utilities/#export-to-json
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


def append_to_json(input_dict: Dict[str, Any], filepath: str, encoding: str = "utf-8", **kwargs):
    """Append a dictionary to an existing JSON file. Tuple-keys are encoded to strings.

    Args:
        input_dict (Dict[str, Any]): Dictionary containing new data that should be added to file.
        filepath (str): Absolute or relative filepath including the file extension. Depending on the current working directory.
        encoding (str, optional): The encoding of the file. Defaults to "utf-8".

    NOTE: Existing JSON file needs a 'data' key.

    Raises:
        ValueError: If input dict and file do not have the same keys or columns, respectively.

    References: https://mathun3003.github.io/PySNA/user-guide/overview/Utilities/#append-to-json
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


def load_from_json(filepath: str, encoding: str = "utf-8", **kwargs) -> dict:
    """Load Python Dictionary from JSON file. Tuples are recovered.

    Args:
        filepath (str): Path to JSON file.
        encoding (str, optional): Encoding of file. Defaults to "utf-8".

    Returns:
        dict: Python Dictionary containing (deserialized) data from JSON file.

    References: https://mathun3003.github.io/PySNA/user-guide/overview/Utilities/#load-from-json
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


def strf_datetime(date: datetime, format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Convert datetime object to string representation.

    Args:
        date (datetime): Input datetime object
        format (str, optional): Datetime string format. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: string representation of input datetime in given format.
    """
    return date.strftime(format)


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
