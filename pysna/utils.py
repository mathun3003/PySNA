# -*- coding: utf-8 -*-
import json
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
            # add 'data' key in order to append additional dicts to same file
            data = {"data": [data]}
            # dump to json
            json.dump(data, jsonfile, indent=4, ensure_ascii=ensure_ascii, *args)
    except IOError as e:
        raise e
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
    pass


def strf_datetime(date: datetime, format="%Y-%m-%d %H:%M:%S") -> str:
    """Convert datetime object to string representation.

    Args:
        date (datetime): Input datetime object
        format (str, optional): Datetime string format. Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        str: string representation of input datetime in given format.
    """
    return date.strftime(format)
