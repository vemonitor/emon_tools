# emon_tools

![CI](https://github.com/vemonitor/emon_tools/actions/workflows/python-package.yml/badge.svg?branch=main)
[![PyPI package](https://img.shields.io/pypi/v/emon_tools.svg)](https://pypi.org/project/emon_tools/)
[![codecov](https://codecov.io/gh/vemonitor/emon_tools/graph/badge.svg?token=M7VgGzkApi)](https://codecov.io/gh/vemonitor/emon_tools)
[![Downloads](https://static.pepy.tech/badge/emon_tools)](https://pepy.tech/project/emon_tools)

`emon-tools` is a Python library that provides tools and APIs for interacting with [EmonCMS](https://emoncms.org/) and processing time-series data. It is designed to simplify data retrieval, analysis, and validation, making it easier to work with energy monitoring data.

## Table of Contents

1. [Installation](https://github.com/vemonitor/emon_tools/blob/main/README.md#installation)

    - [Best Practices for Installation](https://github.com/vemonitor/emon_tools/blob/main/README.md#installation)

    - [Global Installation](https://github.com/vemonitor/emon_tools/blob/main/README.md#global-installation)

    - [Module-Specific Installation](https://github.com/vemonitor/emon_tools/blob/main/README.md#installation)

2. [Modules](https://github.com/vemonitor/emon_tools/blob/main/README.md#modules)

    - [emon_fina](https://github.com/vemonitor/emon_tools/blob/main/README.md#emon_fina)

    - [emon_api](https://github.com/vemonitor/emon_tools/blob/main/README.md#emon_api)

3. [Running Tests](https://github.com/vemonitor/emon_tools/blob/main/README.md#running-tests)

4. [Contributing](https://github.com/vemonitor/emon_tools/blob/main/README.md#contributing)

5. [License](https://github.com/vemonitor/emon_tools/blob/main/README.md#license)

## Installation

The `emon-tools` package offers flexible installation options tailored to various use cases. Depending on your requirements, you can choose to install the complete package or specific subsets of dependencies.

### Best Practices for Installation

1. **Environment Management**: Always use a virtual environment (e.g., `venv` or `conda`) to isolate your dependencies and prevent conflicts with other projects.

2. **Upgrading Dependencies**: Keep your dependencies up to date by running `pip install --upgrade emon-tools` periodically.

3. **Check Requirements**: Review the module's requirements in the `setup.cfg` file or on the PyPI page to ensure compatibility with your system.

### Global Installation
To install the entire emon-tools package along with all dependencies, run the following command:

```
pip install emon-tools["all"]
```

Included Dependencies:
- aiohttp
- numpy
- pandas
- matplotlib

**Tip**: This is the best option if you plan to use all features, including data manipulation and visualization.

### Module-Specific Installation

You can install specific modules and their dependencies as needed. For example:  
- To enable `emon_fina` module:

```
pip install emon-tools["fina"]
```

- To enable pandas time-series output functionality:

```
pip install emon-tools["fina, time_series"]
```

- To include graph plotting capabilities:

```
pip install emon-tools["fina, plot"]
```

- To enable `emon_api` module:

```
pip install emon-tools["api"]
```

- To enable `emon_fina` and `emon_api` modules:

```
pip install emon-tools["api, fina"]
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

#### Usage Example

```python
from emon_tools.fina_time_series import FinaDataFrame
from emon_tools.fina_plot import PlotData

fdf = FinaDataFrame(
    feed_id=1,
    data_dir="/path/to/phpfina/files"
)
# Access metadata of the .meta file:
print("Meta: ", fdf.meta)

# get height days of data points from meta start_time
ts = fdf.get_fina_df_time_series(
    start=fdf.meta.start_time,
    step=10,
    window=8 * 24 * 3600
)

PlotData.plot(data=ts)

```

<img src="https://github.com/vemonitor/emon_tools/blob/main/img/1_data_8_days.png" with="100%">

- **Wiki**: See `emon_fina` module [wiki](https://github.com/vemonitor/emon_tools/wiki/emon_fina) section.

- **Jupiter NoteBook**: See `emon_fina` [NoteBook](https://github.com/vemonitor/emon_tools/blob/main/notebook/emon_fina.ipynb)

### 2. emon_api

The `emon_api` module is Emoncms python api module, used to interract with an EmonCMS instance via its JSON API.

#### Features

- Communicate with EmonCMS using RESTful JSON APIs.
- Retrieve and manage feeds, inputs, and other data structures.

#### Usage Example

```python


```

- **Wiki**: See `emon_api` module [wiki](https://github.com/vemonitor/emon_tools/wiki/emon_api) section.

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
This project is licensed under the MIT License. See [LICENSE](https://github.com/vemonitor/emon_tools/blob/main/LICENSE) for more details.
