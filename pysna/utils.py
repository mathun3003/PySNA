# -*- coding: utf-8 -*-
import json
import re
from datetime import datetime
from typing import Any, Dict


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
        data = serialize_tuples(data)
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
        f = json.load(input_file)
    # existing file should have a "data"-key and a list to append to
    if "data" not in f.keys():
        raise KeyError("The file to be extended must contain the key 'data'.")
    else:
        try:
            # append new dict to file
            f["data"].append(input_dict)
            with open(filepath, "w", encoding=encoding) as jsonfile:
                json.dump(f, jsonfile, indent=4)
        except IOError as e:
            raise e
        # usually when tuple cannot be serialized
        except TypeError:
            # serialize tuples
            input_dict = serialize_tuples(input_dict)
            # retry
            append_to_json(input_dict=input_dict, filepath=filepath, encoding=encoding, **kwargs)
    pass


def load_from_json(filepath: str, encoding: str = "utf-8") -> dict:
    """Load Python Dictionary from JSON file. Tuples are recovered.

    Args:
        filepath (str): Path to JSON file.
        encoding (str, optional): Encoding of file. Defaults to "utf-8".

    Returns:
        dict: Python Dictionary containing (deserialized) data from JSON file.
    """
    # read from filepath
    with open(filepath, "r", encoding=encoding) as jsonfile:
        f = json.load(jsonfile)

    # try to deserialize if any tuples were found in the file
    f = deserialize_tuples(f)
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


def serialize_tuples(data: dict):
    # if "data" key exists
    if "data" in data:
        # iterate over every value
        for key, value in data["data"][0].items():
            # if dict was detected having tuples as keys
            if (isinstance(value, dict)) and all(isinstance(k, tuple) for k in list(value.keys())):
                # serialize tuples
                data["data"][0][key] = {str(k).replace("'", ""): v for k, v in value.items()}
    else:
        # iterate over every value
        for key, value in data.items():
            # if dict was detected having tuples as keys
            if (isinstance(value, dict)) and all(isinstance(k, tuple) for k in list(value.keys())):
                # serialize tuples
                data[key] = {str(k).replace("'", ""): v for k, v in data.items()}
    return data


def deserialize_tuples(data: dict):
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
    else:
        # iterate over every value
        for entry_num, entry in enumerate(data):
            for key in entry.keys():
                # if a serialized tuple was detected
                if isinstance(entry[key], dict):
                    sub_dict = entry[key]
                    if all([re.match(r"^\([^)]+\)$", k) for k in sub_dict.keys()]):
                        for sub_key in sub_dict.keys():
                            # deserialize tuples in sub dict
                            sub_dict[tuple(re.sub(r"[\(\)\']", "", sub_key).split(", "))] = sub_dict.pop(sub_key)
                            # set to input dict
                            data[entry_num][key] = sub_dict
    return data
