# emon_tools

![CI](https://github.com/vemonitor/emon_tools/actions/workflows/python-package.yml/badge.svg?branch=main)
[![PyPI package](https://img.shields.io/pypi/v/emon_tools.svg)](https://pypi.org/project/emon_tools/)
[![codecov](https://codecov.io/gh/vemonitor/emon_tools/graph/badge.svg?token=M7VgGzkApi)](https://codecov.io/gh/vemonitor/emon_tools)
[![Downloads](https://static.pepy.tech/badge/emon_tools)](https://pepy.tech/project/emon_tools)

`emon-tools` is a Python library that provides a streamlined API interface for seamless interactions with [EmonCMS](https://emoncms.org/), along with tools designed to analyze and visualize PhpFina files.

Explore the project Wiki for detailed documentation and guides: [emon_tools Wiki](https://github.com/vemonitor/emon_tools/wiki).

## Table of Contents

1. [Installation](https://github.com/vemonitor/emon_tools/blob/main/README.md#installation)

    - [Best Practices for Installation](https://github.com/vemonitor/emon_tools/blob/main/README.md#installation)

    - [Global Installation](https://github.com/vemonitor/emon_tools/blob/main/README.md#global-installation)

    - [Module-Specific Installation](https://github.com/vemonitor/emon_tools/blob/main/README.md#installation)

2. [Modules](https://github.com/vemonitor/emon_tools/blob/main/README.md#modules)

    - [emon_fina](https://github.com/vemonitor/emon_tools/blob/main/README.md#emon_fina)

    - [emon_api](https://github.com/vemonitor/emon_tools/blob/main/README.md#emon_api)

3. [Optional Full-Stack Visualization App](#optional-full-stack-visualization-app)
    - [Overview](#overview)
    - [Local Development Setup](#local-development-setup)
    - [Docker Compose Deployment](#docker-compose-deployment)
4. [Running Tests](#running-tests)
5. [Contributing](#contributing)
6. [License](#license)

## Installation

The `emon-tools` package offers flexible installation options tailored to various use cases. Depending on your requirements, you can choose to install the complete package or specific subsets of dependencies.

### Best Practices for Installation

1. **Environment Management**: Always use a virtual environment (e.g., `venv` or `conda`) to isolate your dependencies and prevent conflicts with other projects.

2. **Upgrading Dependencies**: Keep your dependencies up to date by running `pip install --upgrade emon-tools` periodically.

3. **Check Requirements**: Review the module's requirements in the `setup.cfg` file or on the PyPI page to ensure compatibility with your system.

### Global Installation
To install the entire emon-tools package along with all dependencies—and to ensure you get the latest version—run:

```
pip install emon-tools["all"] --upgrade
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
pip install emon-tools["fina"] --upgrade
```

- To enable pandas time-series output functionality:

```
pip install emon-tools["fina, time_series"] --upgrade
```

- To include graph plotting capabilities:

```
pip install emon-tools["fina, plot"] --upgrade
```

- To enable `emon_api` module:

```
pip install emon-tools["api"] --upgrade
```

- To enable `emon_fina` and `emon_api` modules:

```
pip install emon-tools["api, fina"] --upgrade
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
from emon_tools.emon_fina.fina_plot import PlotData
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel

fdf = FinaDataFrame(
    file_name="1",
    data_dir="/path/to/phpfina/files"
)
# Access metadata of the .meta file:
print("Meta: ", fdf.meta)

# get height days of data points from meta start_time
ts = fdf.get_df_data(
    props=FinaByTimeParamsModel(
        start_time=fr.meta.start_time,
        time_window=8 * 24 * 3600,
        time_interval=10
    )
)

PlotData.plot(data=ts)

```

<img src="https://github.com/vemonitor/emon_tools/blob/main/img/1_data_8_days.png" with="100%">

- **Wiki**: See `emon_fina` module [wiki](https://github.com/vemonitor/emon_tools/wiki/emon_fina) section.

- **Jupiter NoteBook**: See `emon_fina` [NoteBook](https://github.com/vemonitor/emon_tools/blob/main/notebook/emon_fina.ipynb)

### 2. emon_api

The `emon_api` module is Emoncms python api interface, used to easy interract with an EmonCMS instance via its JSON API.

#### Features

- **Streamlined Interface**: A user-friendly Python API for EmonCMS.
- **RESTful Communication**: Perform seamless data exchanges with EmonCMS through JSON APIs.
- **Data Management**: Retrieve and manage feeds, inputs, and other EmonCMS structures with ease.

#### Usage Example

```python
from emon_tools.emon_api.emon_api import EmonFeedsApi
cli = EmonApi(
    url="http://127.0.0.1:8080",
    api_key="MyAPIKey123"
)
# Get current inputs and feeds on Emoncms server
inputs = cli.list_inputs()
print("Inputs: ", inputs)
feeds = cli.list_feeds()
print("Feeds: ", feeds)
```

- **Wiki**: See `emon_api` module [wiki](https://github.com/vemonitor/emon_tools/wiki/emon_api) section.
- **Examples**: Explore [api_bulk_structure](https://github.com/vemonitor/emon_tools/blob/main/examples/emon_api.py) for input and feed supervision, as well as posting bulk dummy data.

## 🚀 Full-Stack Visualization App Deployment

This optional full-stack application offers a graphical interface to visualize data from any EmonCMS instance and explore archived PhpFina file backups. It comprises:

- FastAPI Backend: Exposes the `emon-tools` functionalities via a RESTful API.
- Vite React Frontend: A modern dashboard built using React, TypeScript, and Tailwind CSS.

### Overview

The full-stack app enables users to:

- Interactively browse and monitor live data from EmonCMS instances.
- Visualize historical time-series data from archived PhpFina files.
- Manage EmonCMS feeds and inputs via an intuitive web interface.

### 🧰 Prerequisites

Ensure the following are installed on your system:
- Docker
- Docker Compose

### 📦 Deployment Steps
This repository now includes a Docker Compose example that leverages the provided Dockerfiles for both backend and frontend. This approach is ideal for quickly deploying the full-stack app in a containerized environment.

1. Clone the Repository

```bash
git clone https://github.com/vemonitor/emon_tools.git
cd emon_tools
```

2. Set Up Environment Variables

Navigate to the Docker Compose development directory and create a `.env` file by copying the provided example:

```bash
cd docker-compose\dev
copy .example_env .env
```

Edit the .env file to replace placeholder values (changethis) with your actual configuration:

```env
MYSQL_HOST=your_mysql_host
MYSQL_PORT=3306
MYSQL_DB=your_database_name
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_ROOT_PASSWORD=your_root_password
```

> Note: The `.env` file is utilized by Docker Compose for variable substitution in the `docker-compose.yml` file. Ensure all required variables are defined to prevent runtime errors. 

3. Build containers and start the containers:

From the `docker-compose/dev` directory, execute:

```bash
docker-compose up --build
```

This command builds the Docker images and starts the containers as defined in the `docker-compose.yml` file.

4. Access the Application

Once the containers are running:

- Frontend: Access the React dashboard at http://localhost:3000
- Backend: Access the FastAPI backend at http://localhost:8000
    - Swagger UI: http://localhost:8000/docs
    - ReDoc: http://localhost:8000/redoc

### 🪟 Accessing from Windows Host (WSL2 Users)

If you're running Docker within WSL2 and need to access the application from your Windows host:

 1. Determine the IP address of your WSL2 instance:

    ```bash
    ip addr show eth0 | grep inet
    ```

    Look for an output similar to:

    ```ccp
    inet 172.20.39.89/20 brd 172.20.47.255 scope global eth0
    ```

 2. Use the extracted IP address to access the application from your Windows browser:

 - Frontend: http://172.20.39.89:3000​

 - Backend: http://172.20.39.89:8000

 > Note: WSL2 has a separate network interface, so `localhost` on Windows does not directly map to `localhost` within WSL2. Using the WSL2 IP address bridges this gap. ​

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
