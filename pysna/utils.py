# -*- coding: utf-8 -*-
import copy
import json
import re
import warnings
from datetime import datetime
from typing import Any, Dict

import pandas as pd

warnings.simplefilter(action="ignore", category=FutureWarning)


def export_to_csv(data: dict, export_path: str, encoding: str = "utf-8", sep: str = ",", **kwargs):
    """Export dictionary data to CSV file.

    Args:
        data (dict): Data dictionary
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


def export_to_json(data: dict, export_path: str, encoding: str = "utf-8", ensure_ascii: bool = False, *args):
    """Export dictionary data to JSON file.

    Args:
        data (dict): Data dictionary
        export_path (str): Export path including file name and extension.
        encoding (str, optional): Encoding of JSON file. Defaults to "utf-8".
    """

    try:
        with open(export_path, "w", encoding=encoding) as jsonfile:
            # add 'data' key in order to append additional dicts to same file, if not already exist
            if "data" not in data:
                data = {"data": [data]}
            # dump to json
            json.dump(data, jsonfile, indent=4, ensure_ascii=ensure_ascii, *args)
    except IOError as e:
        raise e
    # usually when tuple cannot be serialized
    except TypeError:
        # serialize tuples
        data = _encode_json(data)
        # retry
        export_to_json(data=data, export_path=export_path, encoding=encoding, ensure_ascii=ensure_ascii)
    pass


def append_to_json(input_dict: Dict[str, Any], filepath: str, encoding: str = "utf-8", **kwargs):
    """Append a dictionary to an existing JSON file.

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
            # append new dict to file
            f["data"].append(input_dict)
            with open(filepath, "w", encoding=encoding) as jsonfile:
                json.dump(f, jsonfile, indent=4, **kwargs)
        except IOError as e:
            raise e
        # usually when tuple cannot be serialized
        except TypeError:
            # serialize tuples
            input_dict = _encode_json(input_dict)
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
    """
    # read from filepath
    with open(filepath, "r", encoding=encoding) as jsonfile:
        f = json.load(jsonfile, **kwargs)

    # try to deserialize if any tuples were found in the file
    f = _decode_json(f)
    return f


def strf_datetime(date: datetime, format="%Y-%m-%d %H:%M:%S") -> str:
    """Convert datetime object to string representation.

    Args:
        date (datetime): Input datetime object
        format (str, optional): Datetime string format. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: string representation of input datetime in given format.
    """
    return date.strftime(format)


def _encode_json(data: dict):
    # if "data" key exists
    if "data" in data:
        # iterate over every value
        for key, value in data["data"][0].items():
            # if dict was detected having tuples as keys
            if (isinstance(value, dict)) and all(isinstance(k, tuple) for k in list(value.keys())):
                # serialize tuples
                data["data"][0][key] = {str(k).replace("'", ""): v for k, v in value.items()}
        # if any top-level tuple was detected
        if any(isinstance(key, tuple) for key in data["data"][0].keys()):
            # serialize tuples
            data["data"][0] = {(str(key).replace("'", "") if isinstance(key, tuple) else key): dct for key, dct in data["data"][0].items()}
    else:
        # iterate over every value
        for key, value in data.items():
            # if dict was detected having tuples as keys
            if (isinstance(value, dict)) and all(isinstance(k, tuple) for k in list(value.keys())):
                # serialize tuples
                data[key] = {str(k).replace("'", ""): v for k, v in data.items()}
        # if any top-level tuple was detected
        if any(isinstance(key, tuple) for key in data.keys()):
            # serialize tuples
            data = {(str(key).replace("'", "") if isinstance(key, tuple) else key): dct for key, dct in data.items()}

    return data


def _decode_json(data: dict):
    if "data" in data:
        # iterate over every value
        for entry_num, entry in enumerate(data["data"]):
            for key in entry.keys():
                # if a serialized tuple was detected
                if isinstance(entry[key], dict):
                    sub_dict = entry[key]
                    if all([re.match(r"^\([^)]+\)$", k) for k in sub_dict.keys()]):
                        for sub_key in sub_dict.keys():
                            # deserialize tuples in sub dict
                            sub_dict[tuple(re.sub(r"[\(\)\']", "", sub_key).split(", "))] = sub_dict.pop(sub_key)
                            # set to input dict
                            data["data"][entry_num][key] = sub_dict
        # if any serialized top-level tuple was detected
        for key in copy.deepcopy(data["data"][0]).keys():
            if re.match(r"^\([^)]+\)$", key):
                # deserialize tuples
                data["data"][0][tuple(re.sub(r"[\(\)\']", "", key).split(", "))] = data["data"][0].pop(key)
    else:
        for key in data.keys():
            # if a serialized tuple was detected
            if isinstance(data[key], dict):
                sub_dict = data[key]
                if all([re.match(r"^\([^)]+\)$", k) for k in sub_dict.keys()]):
                    for sub_key in sub_dict.keys():
                        # deserialize tuples in sub dict
                        sub_dict[tuple(re.sub(r"[\(\)\']", "", sub_key).split(", "))] = sub_dict.pop(sub_key)
                        # set to input dict
                        data[key] = sub_dict
                # if int was changed to str, cast to int
                elif any([key.isdigit() for key in sub_dict.keys()]):
                    for sub_key in [k for k in sub_dict.keys() if k.isdigit()]:
                        sub_dict[int(sub_key)] = sub_dict.pop(sub_key)
                    for sub_key in [k for k in sub_dict.keys() if isinstance(k, str)]:
                        for k in sub_dict[sub_key].keys():
                            if k.isdigit():
                                sub_dict[sub_key][int(k)] = sub_dict.pop(sub_dict[sub_key][k])
            # cast to int if key is a digit
            if key.isdigit():
                data[int(key)] = data.pop(key)
        # if any serialized top-level tuple was detected
        for key in copy.deepcopy(data).keys():
            if isinstance(key, tuple):
                # deserialize tuples
                data[tuple(re.sub(r"[\(\)\']", "", key).split(", "))] = data.pop(key)
    return data
