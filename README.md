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

#### Usage Example:

The examples below demonstrate how to retrieve and analyze data from PhpFina timeseries .dat files. For additional examples, refer to the [`emon_fina` Jupiter NoteBook](https://github.com/vemonitor/emon_tools/blob/main/notebook/emon_fina.ipynb).

Every PhpFina timeseries feed engine is acompagned with `.meta` file who contain meta values of actual status of `.dat` file. Meta data is readed on initialize objects

##### Retrieving data

`FinaData` initialization:

```python
from emon_tools.emon_fina import FinaData

fdf = FinaData(
    feed_id=1,
    data_dir="/path/to/phpfina/files
)
```

Values output can be set as:
> In above example we get 8 days (8 * 24 * 3600) from meta `time_start` value.

1. 1D numpy array by timestamp

Retrieve data values from the Fina data file for a specified time window.

```python
values = fdf.get_fina_values(
    start=fr.meta.start_time,
    step=10,
    window=8 * 24 * 3600
)
```

2. 1D numpy array by srting datetime

Retrieve values from the Fina data file based on a specified date range.

```python
ts = fdf.get_fina_values_by_date(
    start_date='2019-12-12 00:00:00',
    end_date='2019-12-13 00:00:00',
    step=10
)
```

3. 2D TimeSeries numpy array by timestamp

Retrieve a 2D time series array of timestamps and values from the Fina data file.

```python
ts = fdf.get_fina_time_series(
    start=fr.meta.start_time,
    step=10,
    window=8 * 24 * 3600
)
```



4. 2D TimeSeries numpy array by srting datetime

Retrieve a 2D time series array of timestamps and values for a specific date range.

```python
ts = fdf.get_fina_time_series_by_date(
    start_date='2019-12-12 00:00:00',
    end_date='2019-12-13 00:00:00',
    step=10
)
```

5. pandas DataFrame TimeSeries

`FinaDataFrame` initialization:

```python
from emon_tools.fina_time_series import FinaDataFrame

fdf = FinaDataFrame(
    feed_id=1,
    data_dir="/path/to/phpfina/files
)
```

Retrieve time series data within a specified time window
and return it as a Pandas DataFrame.

```python
ts = fdf.get_fina_df_time_series(
    start=fr.meta.start_time,
    step=10,
    window=8 * 24 * 3600
)
```

Retrieve time series data by specifying a date range and convert it to a Pandas DataFrame.

```python
ts = fdf.get_fina_time_series_by_date(
    start_date='2019-12-12 00:00:00',
    end_date='2019-12-13 00:00:00',
    step=10
)
```
And optionaly ploted dirrectly.

`FinaDataFrame` initialization:

```python
from emon_tools.fina_plot import PlotData

PlotData.plot(data=ts)
```

##### Compute Daily Statistics

`FinaDataFrame` initialization:

```python
from emon_tools.emon_fina import FinaStats
from emon_tools.emon_fina import StatsType

stats = FinaStats(
    feed_id=1,
    data_dir="/path/to/phpfina/files
)
```

Once initialized, you can access the metadata of the PhpFina `.meta` file. For example, a file with `feed_id=1` might return:

```python
stats.meta
    {
        "interval": 10,
        "start_time": 1575981140,
        "npoints": 4551863,
        "end_time": 1621499760
    }
```

On grabing phpfina timeseries feed engine, missed data points are set as Nan values,
We can get file integrity daily statistics to compute real and total values of phpfina `.dat` file

```python
# Compute daily statistics
daily_stats = stats.get_stats(stats_type=StatsType.INTEGRITY)
```

<img src="https://github.com/vemonitor/emon_tools/blob/main/img/integrity_stats.png" with="100%">

Or we can get daily values statistics from your phpfina timeseries feed engine file

```python
# Compute daily statistics
daily_stats = stats.get_stats(stats_type=StatsType.VALUES)
```

<img src="https://github.com/vemonitor/emon_tools/blob/main/img/values_stats.png" with="100%">

Phpfina timeseries feed engine file can contain bad data, in this case we can limit values from statistics without bad values.
Here statistics are calculated only with values between -50 and 50.

```python
# Compute daily statistics
daily_stats = stats.get_stats(
    stats_type=StatsType.VALUES,
    min_value=-50,
    max_value=50
)
```

<img src="https://github.com/vemonitor/emon_tools/blob/main/img/values_stats_limited.png" with="100%">

You can limit daily statistics from desired window, by setting `start_time` and/or `steps_window` properties.
In above example we get daily stats values for 8 days from timestamp value 1575981140
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

....