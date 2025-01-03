# emon_tools

![CI](https://github.com/vemonitor/emon_tools/actions/workflows/python-package.yml/badge.svg?branch=main)
[![PyPI package](https://img.shields.io/pypi/v/emon_tools.svg)](https://pypi.org/project/emon_tools/)
[![codecov](https://codecov.io/gh/vemonitor/emon_tools/graph/badge.svg?token=M7VgGzkApi)](https://codecov.io/gh/vemonitor/emon_tools)
[![Downloads](https://static.pepy.tech/badge/emon_tools)](https://pepy.tech/project/emon_tools)

`emon-tools` is a Python library that provides tools and APIs for interacting with [EmonCMS](https://emoncms.org/) and processing time-series data. It is designed to simplify data retrieval, analysis, and validation, making it easier to work with energy monitoring data.

## Installation

### Global Installation
To install all modules and dependencies globally:
1. Via Pip
```
pip install emon-tools
```

### Module-Specific Installation

You can install specific modules and their dependencies as needed. For example:   
- To enable pandas time-series output functionality:

```
pip install emon-tools[time_series]
```

- To include graph plotting capabilities:

```
pip install emon-tools[plot]
```

## Modules
`emon_tools` is modular, allowing you to install and use individual components as needed.

### 1. emon_fina

The `emon_fina` module facilitates the analysis and processing of time-series data, particularly from PhpFina file formats.

#### Features

- Data Reading: Efficiently read data from PhpFina file formats.
- Time-Series Analysis: Compute daily statistics such as min, max, mean, and more.
- Filtering: Validate and filter data based on custom thresholds.
- Utilities: Timestamp manipulation and interval computation tools.

#### PhpFina File Structure

PhpFina is a lightweight binary file format used by EmonCMS for storing time-series data. Each PhpFina feed consists of two files:

1. `.dat` File: Contains the actual time-series data values, stored as binary floats. Each value corresponds to a specific timestamp based on the feed's start time and interval.

2. `.meta` File: Contains metadata about the feed. Its structure includes:  
  - **Offset 0-7**: Reserved for future use or ignored by the library.
  - **Offset 8-15**: Contains two 4-byte little-endian integers:
    - `interval`: The time interval (in seconds) between consecutive data points.
    - `start_time`: The Unix timestamp of the first data point.
  - Computed Values:
    - `npoints`: The total number of data points, calculated as `data_size // 4` (where each data point is 4 bytes).
    - `end_tim`e: Computed as `start_time + npoints * interval - interval`.

#### Usage Examples:

The examples below demonstrate how to retrieve and analyze data from PhpFina timeseries .dat files. For additional examples, refer to the [`emon_fina`](https://github.com/vemonitor/emon_tools/blob/main/notebook/emon_fina.ipynb) Jupiter NoteBook.


##### Retrieving data

###### 1. Initialize `FinaData`:

This initializes the `FinaData` class, allowing you to interact with the time-series data files:

```python
from emon_tools.emon_fina import FinaData

fdf = FinaData(
    feed_id=1,
    data_dir="/path/to/phpfina/files
)
```

Access metadata of the .meta file:

```python
print(fdf.meta)
# Example Output:
# {
#     "interval": 10,
#     "start_time": 1575981140,
#     "npoints": 4551863,
#     "end_time": 1621499760
# }
```

##### 2. Retrieve Values:

Retrieve specific ranges of data values from the `.dat` file based on time intervals or date ranges.

1. 1D NumPy Array by time window:

Extract values starting from a specific timestamp and within a time window:

```python
values = fdf.get_fina_values(
    start=fr.meta.start_time,
    step=10,
    window=8 * 24 * 3600
)
```

2. 1D NumPy Array by datetime interval:

Extract values within a specific date range:

```python
ts = fdf.get_fina_values_by_date(
    start_date='2019-12-12 00:00:00',
    end_date='2019-12-13 00:00:00',
    step=10
)
```

3. 2D Time-Series NumPy Array by time window:

Retrieve a 2D array containing timestamps and corresponding values:

```python
ts = fdf.get_fina_time_series(
    start=fr.meta.start_time,
    step=10,
    window=8 * 24 * 3600
)
```

4. 2D Time-Series NumPy Array by datetime interval:

Retrieve a 2D array of timestamps and values for a specific date range:

```python
ts = fdf.get_fina_time_series_by_date(
    start_date='2019-12-12 00:00:00',
    end_date='2019-12-13 00:00:00',
    step=10
)
```

5. Pandas DataFrame Time-Series:

Convert time-series data into a Pandas DataFrame for easier manipulation:

`FinaDataFrame` initialization:

```python
from emon_tools.fina_time_series import FinaDataFrame

fdf = FinaDataFrame(
    feed_id=1,
    data_dir="/path/to/phpfina/files
)

ts = fdf.get_fina_df_time_series(
    start=fdf.meta.start_time,
    step=10,
    window=8 * 24 * 3600
)

# Or by date_range

ts = fdf.get_fina_time_series_by_date(
    start_date='2019-12-12 00:00:00',
    end_date='2019-12-13 00:00:00',
    step=10
)
```

Access metadata of the `.meta` file:

```python
print(fdf.meta)
# Example Output:
# {
#     "interval": 10,
#     "start_time": 1575981140,
#     "npoints": 4551863,
#     "end_time": 1621499760
# }
```

##### 3. Plotting Data:

Visualize the retrieved time-series data:

```python
from emon_tools.fina_plot import PlotData

PlotData.plot(data=ts)
```

##### Compute Daily Statistics

###### 1. Initialize `FinaStats`:

This initializes the  `FinaStats` class for statistical computations:

```python
from emon_tools.emon_fina import FinaStats
from emon_tools.emon_fina import StatsType

stats = FinaStats(
    feed_id=1,
    data_dir="/path/to/phpfina/files
)
```

Access metadata of the .meta file:

```python
print(stats.meta)
# Example Output:
# {
#     "interval": 10,
#     "start_time": 1575981140,
#     "npoints": 4551863,
#     "end_time": 1621499760
# }
```

###### 2. Integrity Statistics:

Analyze the integrity of the .dat file by computing the presence of valid and missing data:

```python
# Compute daily statistics
daily_stats = stats.get_stats(stats_type=StatsType.INTEGRITY)
```

<img src="https://github.com/vemonitor/emon_tools/blob/main/img/integrity_stats.png" with="100%">

###### 3. Value Statistics:

Compute daily statistics (e.g., min, max, mean) for data values:

```python
# Compute daily statistics
daily_stats = stats.get_stats(stats_type=StatsType.VALUES)
```

<img src="https://github.com/vemonitor/emon_tools/blob/main/img/values_stats.png" with="100%">

###### 4. Filtered Value Statistics:

Restrict statistical calculations to a specific value range:

```python
# Compute daily statistics
daily_stats = stats.get_stats(
    stats_type=StatsType.VALUES,
    min_value=-50,
    max_value=50
)
```

<img src="https://github.com/vemonitor/emon_tools/blob/main/img/values_stats_limited.png" with="100%">

###### 5. Windowed Statistics:
Limit statistics to a specific time window:

```python
# Compute daily statistics
daily_stats = stats.get_stats(
    start_time=1575981140,
    steps_window=8 * 24 * 3600,
    stats_type=StatsType.VALUES,
    min_value=-50,
    max_value=50
)
```

### 2. emon_api

The `emon_api` module is Emoncms python api module, used to interract with Emoncms server instance.

#### Features

- Data Reading: Efficiently read data from Emoncms.
- Data Writing: Set Inputs, feeds or values

### Usage Examples:

...

## Running Tests

To ensure everything is functioning correctly, run the test suite:

```
pytest -v
```

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a feature branch.
3. Submit a pull request with a clear description.

## License
This project is licensed under the MIT License. See LICENSE for more details.
