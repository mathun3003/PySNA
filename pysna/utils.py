# -*- coding: utf-8 -*-
import csv
import json
import logging

import pandas as pd

log = logging.getLogger(__name__)

def export_to_file(data: dict, filename: str, type: str, export_path='./'):
    """_summary_
    # TODO: fill me
    Args:
        data (dict): _description_
        filename (str): _description_
        type (str): _description_
        export_path (str): _description_

    Raises:
        ValueError: _description_
    """
    # catch Value Errors for 'type'
    if not type in ['json', 'csv', 'xlsx']:
        raise ValueError(f"'type' needs to be either json, csv, or xlsx, not {type}.")
    else:
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
