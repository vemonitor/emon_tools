"""
fina_time_series

This module extends the functionality of `emon_tools.emon_fina` by introducing
classes to work with Pandas DataFrames for Fina data results.

Classes:
    - FinaDataFrame:
        Extends FinaData with methods to convert time-series data
        into Pandas DataFrames.
    - FinaDfStats:
        Extends FinaStats to compute and return statistics
        as Pandas DataFrames.

Dependencies:
    - Requires Pandas (`pip install pandas`).

Usage Example:
    >>> from fina_time_series import FinaDataFrame
    >>> fina_data = FinaDataFrame("path_to_data_file")
    >>> fina_result = fina_data.get_fina_time_series(
        start=0, step=60, window=3600)
    >>> df = fina_result.df()
    >>> print(df)

Raises:
    - ImportError: If Pandas is not installed.

Author:
    Your Name

License:
    MIT License
"""
from typing import Optional
import numpy as np
import pandas as pd
from emon_tools.emon_fina.fina_services import FinaOutputData
from emon_tools.emon_fina.emon_fina import FinaData
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel
from emon_tools.emon_fina.fina_models import FinaByDateParamsModel
from emon_tools.emon_fina.fina_models import FinaByDateRangeParamsModel
from emon_tools.emon_fina.fina_models import OutputType


class FinaDataFrame(FinaData):
    """
    Extension of FinaData with additional methods to retrieve
    and handle time-series data as Pandas DataFrames.

    Methods:
        - get_fina_time_series:
            Retrieve time-series data and convert it into a Pandas DataFrame.
        - get_fina_time_series_by_date:
            Retrieve time-series data by date range and return as a DataFrame.
        - set_data_frame:
            Static method to convert arrays of time and values
            into a Pandas DataFrame.
    """

    def get_df_data(
        self,
        props: FinaByTimeParamsModel
    ) -> pd.DataFrame:
        """
        Retrieve time series data within a specified time window
        and return it as a Pandas DataFrame.

        Parameters:
            start (int): The start time in seconds (Unix timestamp).
            step (int): The interval between data points in seconds.
            window (int): The total duration of the time window in seconds.

        Returns:
            pd.DataFrame:
                A DataFrame with time as the index and data values as a column.

        Raises:
            ValueError:
                If the shape of the times and values arrays do not match.

        Example:
            >>> fina_data.get_fina_time_series(start=0, step=60, window=3600)
        """
        data = self.read_fina_values(
            props=props
        )
        return self.set_data_frame(data, props.output_type)

    def get_df_data_by_date(
        self,
        props: FinaByDateParamsModel
    ) -> pd.DataFrame:
        """
        Retrieve time series data by specifying a date range
        and convert it to a Pandas DataFrame.

        Parameters:
            start_date (str): The start date as a string.
            end_date (str): The end date as a string.
            step (int): The interval between data points in seconds.
            date_format (str, optional):
                The format of the input date strings.
                Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            pd.DataFrame:
                A DataFrame with time as the index and data values as a column.

        Raises:
            ValueError: If the parsed start or end date is invalid.

        Example:
            >>> fina_data.get_fina_time_series_by_date(
                "2023-01-01 00:00:00",
                "2023-01-02 00:00:00",
                step=60)
        """
        data = self.get_data_by_date(
            props=props
        )

        return self.set_data_frame(data, props.output_type)

    def get_df_data_by_date_range(
        self,
        props: FinaByDateRangeParamsModel
    ) -> pd.DataFrame:
        """
        Retrieve time series data by specifying a date range
        and convert it to a Pandas DataFrame.

        Parameters:
            start_date (str): The start date as a string.
            end_date (str): The end date as a string.
            step (int): The interval between data points in seconds.
            date_format (str, optional):
                The format of the input date strings.
                Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            pd.DataFrame:
                A DataFrame with time as the index and data values as a column.

        Raises:
            ValueError: If the parsed start or end date is invalid.

        Example:
            >>> fina_data.get_fina_time_series_by_date(
                "2023-01-01 00:00:00",
                "2023-01-02 00:00:00",
                step=60)
        """
        data = self.get_data_by_date_range(
            props=props
        )

        return self.set_data_frame(data, props.output_type)

    @staticmethod
    def set_data_frame(
        data: np.ndarray,
        output_type: OutputType
    ) -> Optional["pd.DataFrame"]:
        """
        Convert arrays of time and values into a Pandas DataFrame.

        Parameters:
            times (np.ndarray): Array of time values (Unix timestamps).
            values (np.ndarray):
                Array of data values corresponding to the times.

        Returns:
            Optional[pd.DataFrame]:
                A DataFrame with time as the index and data values as a column.

        Raises:
            ValueError:
                If the input arrays are not of the same shape
                or not instances of np.ndarray.

        Example:
            >>> times = np.array([1672531199, 1672531259, 1672531319])
            >>> values = np.array([1.0, 2.0, 3.0])
            >>> FinaDataFrame.set_data_frame(times, values)
        """
        if not isinstance(data, np.ndarray):
            raise ValueError("data must be a numpy ndarray.")

        if not isinstance(output_type, OutputType):
            raise ValueError("output_type must be an OutputType instance.")

        # Get columns labels for current output_type
        cols = FinaOutputData.get_columns(output_type)
        is_defined_cols = len(data.shape) == 2\
            and data.shape[1] == len(cols)
        is_one_col = len(data.shape) == 1\
            and len(cols) == 1
        if not is_defined_cols and not is_one_col:
            raise ValueError(
                "Invalid data columns. Data missing or corrupted."
            )
        if data.shape[0] > 0:
            if 'time' in cols:
                df = pd.DataFrame(
                    data,
                    columns=cols,
                    index=pd.to_datetime(data[:, 0], unit="s", utc=False)
                )
                df.index.name = "time"
            else:
                df = pd.DataFrame(
                    data,
                    columns=cols
                )
        else:
            df = pd.DataFrame(
                [],
                columns=cols
            )
        return df
