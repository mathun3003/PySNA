BaseDataProcessor
----------------

The ```BaseDataProcessor``` class contains general operations for data processing. It forms the basis for the ```TwitterDataProcessor``` class. The ```BaseDataProcessor``` class is used within the ```TwitterAPI``` class for processing data that is not specific to any social media platform. Methods exist for calculating descriptive metrics for numeric and datetime values as well as calculating the intersection and difference of sets.  

This class can also be used to process previously collected data.

# Initialization

If you want to use this class for data processing or other package components, follow the steps below.  

Import the ```BaseDataProcessor``` class from the ```process``` module:

```python
from pysna.process import BaseDataProcessor
# init instance
data_processor = BaseDataProcessor()
```

and start invoking a function:

```python
sets = [set(1,2,4), set(1,3,5), set(1,8,9)]
# calculate intersection of all sets
data_processor.intersection(sets)
```

# Methods

The methods of this class use functions from [Numpy](https://numpy.org/) and default Python operations.  

### calc_descriptive_metrics
Calculates descriptive metrics of a given data set. Returns the given data set with appended statistical metrics. Input data set must be a dictionary containing numeric values.

Function:
```python
BaseDataProcessor.calc_descriptive_metrics(data: Dict[str | int, Number])
```

The following metrics are calculated:

- Max Value
- Min Value
- Mean Value
- Median
- Standard Deviation
- Sample Variance
- Range (Max - Min)
- Interquartiles Range
- Mean Absolute Deviation

These metrics might help to interpret the data more accurately and saves time to evaluate data manually.  

All metrics are calculated and appended to a new key 'metrics' in the input dictionary. This implementation enables to enrich input data with statistical metrics without the need to append the metrics to the dictionary after calculation.

<details>
<summary>Source Code</summary>
```python
import numpy as np

def calc_descriptive_metrics(self, data: Dict[str | int, Number]) -> dict:
    """Calculates descriptive metrics of a given data set.

    Args:
        data (Dict[str  |  int, Number]): Data dictionary containing numeric values.

    Raises:
        ValueError: If non-numeric values are contained in the data dictionary.

    Returns:
        dict: Input data dictionary containing descriptive metrics.

    Metrics:
        - Max Value
        - Min Value
        - Mean Value
        - Median
        - Standard Deviation
        - Sample Variance
        - Range (Max - Min)
        - Interquartiles Range
        - Mean Absolute Deviation
    """
    if not any(isinstance(value, Number) for value in data.values()):
        raise ValueError("Only numeric values are allowed.")
    # extract numeric values by iterating over data dict with iterable items
    numerics = list(data.values())
    # init empty dict to store descriptive metrics
    metrics = dict()
    # calc max
    metrics["max"] = max(numerics)
    # calc min
    metrics["min"] = min(numerics)
    # calc mean
    metrics["mean"] = np.array(numerics).mean()
    # calc median
    metrics["median"] = np.median(numerics)
    # calc standard deviation
    metrics["std"] = np.std(numerics)
    # calc variance
    metrics["var"] = np.var(numerics)
    # calc range
    metrics["range"] = max(numerics) - min(numerics)
    # calc interquarile range
    metrics["IQR"] = np.subtract(*np.percentile(numerics, [75, 25]))
    # calc absolute mean deviation
    metrics["mad"] = np.mean(np.absolute(numerics - np.mean(numerics)))
    # add metrics
    data["metrics"] = metrics
    return data
```
</details>

______________

### calc_datetime_metrics

Calculates descriptive metrics on datetime objects. The function takes in a dictionary with datetime values. The function will return the input dictionary with appended metrics.  

Function:
```python
BaseDataProcessor.calc_datetime_metrics(dates: Dict[str, datetime])
```

The following metrics are calculated:

- Mean
- Median
- Max
- Min
- Time Span (in days, seconds, and microseconds)
- Deviation from mean (in days and seconds). Negative values indicate below average, positive ones above average.
- Deviation from median (in days and seconds). Negative values indicate below median, positive ones above average.


The metrics will help to analyze creation dates of social media accounts or posts. The metrics are choosed based on typical behaviors of social bots as they are often created within a short period. These metrics will help to figure out if it is likely that the investigated account is a social bot.


All metrics are calculated and appended to a new key 'metrics' in the input dictionary. This implementation enables to enrich input data with statistical metrics without the need to append the metrics to the dictionary after calculation.

<details>
<summary>Source Code</summary>
```python
def calc_datetime_metrics(self, dates: Dict[str, datetime]) -> dict():
    """Calculates descriptive metrics on datetime objects.

    Args:
        dates (Dict[str, datetime]): Dictionary containing identifiers as keys and datetime objects as values.

    Returns:
        dict: Input dates with added datetime metrics.

    Metrics:
        - Mean
        - Median
        - Max
        - Min
        - Time Span (in days, seconds, and microseconds)
        - Deviation from mean (in days and seconds). Negative values indicate below average, positive ones above average.
        - Deviation from median (in days and seconds). Negative values indicate below median, positive ones above average.
    """
    # use the datetime's timestamp to make them comparable
    timestamps = [dt.timestamp() for dt in dates.values()]
    # calc mean of creation dates
    total_time = sum(timestamps)
    mean_timestamp = total_time / len(timestamps)
    # convert mean timestamp back to datetime object with timezone information
    mean_datetime = datetime.fromtimestamp(mean_timestamp, tz=timezone.utc)

    # calculate time differences to mean datetime of every creation date
    time_diffs_mean = {key: {"days": (dt - mean_datetime).days, "seconds": (dt - mean_datetime).seconds} for key, dt in dates.items()}

    # find the median of the timestamps
    median_timestamp = np.median(timestamps)
    # Convert median timestamp back to datetime object
    median_datetime = datetime.fromtimestamp(median_timestamp, tz=timezone.utc)

    # calculate time differences to median timestamp of every creation date
    time_diffs_median = {key: {"days": (dt - median_datetime).days, "seconds": (dt - median_datetime).seconds} for key, dt in dates.items()}

    # calc range of creation dates
    max_date, min_date = max(dates.values()), min(dates.values())
    time_span = max_date - min_date

    # convert creation dates to isoformat for readability
    dates = {key: dt.isoformat() for key, dt in dates.items()}

    # add metrics to output
    dates["metrics"] = dict()
    dates["metrics"]["deviation_from_mean"] = time_diffs_mean
    dates["metrics"]["deviation_from_median"] = time_diffs_median
    dates["metrics"]["time_span"] = {"days": time_span.days, "seconds": time_span.seconds, "microseconds": time_span.microseconds}
    dates["metrics"]["mean"] = mean_datetime.isoformat()
    dates["metrics"]["median"] = median_datetime.isoformat()
    dates["metrics"]["max"] = max_date.isoformat()
    dates["metrics"]["min"] = min_date.isoformat()
    return dates
```
</details>
______________

### intersection

Calculates the intersection of multiple sets. This function takes in a list of sets and returns their intersection.

Function:

```python
BaseDataProcessor.intersection(iterable: List[set])
```

This function is used, for example, to get the follower IDs of multiple social media accounts. The sets contain the individual follower IDs of the social media accounts.


<details>
<summary>Source Code</summary>
```python
def intersection(self, iterable: List[set]) -> list:
    """Calculates the intersection of multiple sets.

    Args:
        iterable (List[set]): List containing sets.

    Returns:
        list: intersection set casted to list.
    """
    intersection = set.intersection(*map(set, iterable))
    return list(intersection)
```
</details>
______________

### difference

Calculates the difference of multiple sets. The function takes in a list of dictionaries containing identifiers (e.g., account IDs) as keys and the sets as values. This function will return for each key in the dictionary the individual difference of each set.

Function:

```python
BaseDataProcessor.difference(sets: Dict[int | str, set])
```

This function is used to calculate the difference of followers of the specified social media accounts. In this context, the account IDs are stored as dictionary keys and their follower IDs as values.

<details>
<summary>Source Code</summary>
```python
def difference(self, sets: Dict[int | str, set]) -> dict:
    """Calculates the difference of multiple sets.

    Args:
        sets (Dict[set]): Dictionary containing sets where keys are identifiers.

    Returns:
        dict: Individual difference of each set that was provided.
    """
    # init empty dict to store individual differences for each set
    differences = dict()
    for key, values in sets.items():
        differences[key] = list(set(values))
        for other_key, other_values in sets.items():
            if key != other_key:
                differences[key] = list(set(differences[key]) - set(other_values))
    return differences
```
</details>


______________
