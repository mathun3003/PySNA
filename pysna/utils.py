# -*- coding: utf-8 -*-
import csv
import json
import logging
from datetime import datetime
from typing import Literal

import pandas as pd

log = logging.getLogger(__name__)


def export_to_file(data: dict, filename: str, type: Literal['json', 'csv', 'xlsx'] | None, export_path: str | None):
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
                with open(export_path + filename + '.json', 'w', encoding='utf-8') as jsonfile:
                    json.dump(data, jsonfile)
            except IOError as e:
                log.error("I/O error: %s", e)
        case 'csv':
            try:
                with open(export_path + filename + '.csv', 'w', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=data.keys())
                    writer.writeheader()
                    for entry in data:
                        writer.writerow(entry)
            except IOError as e:
                log.error("I/O error: %s" % e)
        case 'xlsx':
            try:
                df = pd.DataFrame(data=data, index=[0])
                df.to_excel(export_path + filename + '.xlsx')
            except IOError as e:
                log.error("I/O error: %s" % e)
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
