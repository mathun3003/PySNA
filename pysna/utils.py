# -*- coding: utf-8 -*-
import csv
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Literal

import pandas as pd

# create logger instance
log = logging.getLogger(__name__)
# set logging level
log.setLevel(logging.ERROR)
# log to stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


def export_to_file(data: dict, export_path: str, type: Literal['json', 'csv', 'xlsx'] | None, encoding: str = "utf-8"):
    """_summary_

    Args:
        data (dict): _description_
        filename (str): _description_
        type (Literal[&#39;json&#39;, &#39;csv&#39;, &#39;xlsx&#39;]): _description_
        export_path (str, optional): _description_.

    Raises:
        ValueError: _description_
    """

    # TODO: test
    match type:
        case 'json':
            try:
                with open(export_path, 'w', encoding=encoding) as jsonfile:
                    json.dump(data, jsonfile)
            except IOError as e:
                log.error("I/O error: %s", e)
        case 'csv':
            try:
                with open(export_path, 'w', encoding=encoding) as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=data.keys())
                    writer.writeheader()
                    for entry in data:
                        writer.writerow(entry)
            except IOError as e:
                log.error("I/O error: %s" % e)
        case 'xlsx':
            try:
                df = pd.DataFrame(data=data, index=[0])
                df.to_excel(export_path)
            except IOError as e:
                log.error("I/O error: %s" % e)
    pass


def append_to_file(input_dict: Dict[str, Any], filepath: str, file_type: str = "json", timestamp_column: str | None = None, encoding: str = "utf-8", **kwargs):
    """Append a dictionary to an existing CSV or JSON file.

    Args:
        input_dict (Dict[str, Any]): Dictionary containing new data that should be added to file.
        filepath (str): Absolute or relative filepath including the file extension. Depending on the current working directory.
        file_type (str, optional): Whether to extend a CSV or JSON file. Defaults to "json".
        timestamp_column (str | None, optional): The timestamp column of the CSV file that should be parsed during read-in. Defaults to None.
        encoding (str, optional): The encoding of the file. Defaults to "utf-8".

    NOTE: Input dict and file need the same keys or columns, respectively.

    Raises:
        ValueError: If input dict and file do not have the same keys or columns, respectively.
    """

    match file_type:
        case "json":
            # load file from path
            with open(filepath, 'r', encoding=encoding) as input_file:
                f = json.loads(input_file)
            # check if both dicts have the same keys. If not, raise an exception.
            if not set(list(input_dict.keys())) == set(list(f.keys())):
                raise ValueError("Unknown key(s). Make sure that the input dictionary and the JSON file have the same keys.")
            else:
                #? really necessary? The same timestamp is unlikely to occur twice in a file.
                # check if timestamp already exist in input file
                # if input_dict["timestamp"] in f.keys():
                #     # check if ID already exists in input file
                #     input_dict["id"] in ...

                # delete utc_timestamp entry from input dict
                input_dict.pop("utc_timestamp")
                # insert new entries to existing file from input dict
                f[input_dict["utc_timestamp"]] = input_dict
                # write to file, overwrite
                with open(filepath, 'w', encoding=encoding) as jsonfile:
                    json.dump(f, jsonfile)
        case "csv":
            # read CSV file from path
            f = pd.read_csv(filepath, encoding=encoding, **kwargs, parse_dates=timestamp_column)
            # raise an error, if the file header and the input dict has not the same columns or keys, respectively.
            if not set(list(input_dict.keys())) == set(f.columns):
                raise ValueError("Unknown key(s) or column(s). Make sure that the input dictionary and the CSV file header have the same keys or columns, respectively.")
            else:
                # append to input file
                f = f.append(input_dict, ignore_index=True)
                # export file, overwrite
                f.to_csv(filepath, encoding=encoding, index=False)
        case _:
            log.error("I/O error: %s" % IOError("Invalid file type provided for {}".format(file_type)))
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
