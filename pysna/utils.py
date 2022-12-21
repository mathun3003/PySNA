# -*- coding: utf-8 -*-
import csv


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
        # ?: use a logger instead?
        raise ValueError(f"'type' needs to be either json, csv, or xlsx, not {type}.")
    else:
        # TODO: continue
        match type:
            case 'json':
                pass
            case 'csv':
                try:
                    with open(export_path + filename, 'w') as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
                        writer.writeheader()
                        for entry in data:
                            writer.writerow(entry)
                except IOError:
                    print("I/O error")
            case 'xlsx':
                pass
    pass
