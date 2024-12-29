"""
fina_time_series

This module extends the functionality of `emon_tools.emon_fina` by introducing
classes to work with Pandas DataFrames for Fina data results.

Classes:
    - FinaDataFrame: Extends FinaData with methods to convert time-series data into Pandas DataFrames.
    - FinaDfStats: Extends FinaStats to compute and return statistics as Pandas DataFrames.

Dependencies:
    - Requires Pandas (`pip install pandas`).

Usage Example:
    >>> from fina_time_series import FinaDataFrame
    >>> fina_data = FinaDataFrame("path_to_data_file")
    >>> fina_result = fina_data.get_fina_time_series(start=0, step=60, window=3600)
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
from typing import List
from typing import Union
import numpy as np
from emon_tools.emon_fina import Utils
from emon_tools.emon_fina import FinaData
from emon_tools.emon_fina import FinaStats
from emon_tools.emon_fina import StatsType

try:
    import pandas as pd
except ImportError as e:
    raise ImportError(
        "Pandas is required for this module. Install it with `pip install pandas`."
    ) from e



class FinaDataFrame(FinaData):
    """
    Extension of FinaData with additional methods to retrieve and handle time-series data
    as Pandas DataFrames.

    Methods:
        - get_fina_time_series:
            Retrieve time-series data and convert it into a Pandas DataFrame.
        - get_fina_time_series_by_date:
            Retrieve time-series data by date range and return as a DataFrame.
        - set_data_frame:
            Static method to convert arrays of time and values into a Pandas DataFrame.
    """
    def __init__(self, feed_id: int, data_dir: str):
        """
        Initialize the FinaDataFrame object with a FinaReader instance.

        Parameters:
            feed_id (int): Unique identifier for the feed.
            data_dir (str): Directory path to the Fina data files.
        """
        FinaData.__init__(self, feed_id=feed_id, data_dir=data_dir)

    def get_fina_df_time_series(
        self,
        start: int,
        step: int,
        window: int
    ) -> pd.DataFrame:
        """
        Retrieve time series data within a specified time window
        and return it as a Pandas DataFrame.

        Parameters:
            start (int): The start time in seconds (Unix timestamp).
            step (int): The interval between data points in seconds.
            window (int): The total duration of the time window in seconds.

        Returns:
            pd.DataFrame: A DataFrame with time as the index and data values as a column.

        Raises:
            ValueError: If the shape of the times and values arrays do not match.
        
        Example:
            >>> fina_data.get_fina_time_series(start=0, step=60, window=3600)
        """
        values = self.read_fina_values(start=start, step=step, window=window)
        return self.set_data_frame(self.timestamps(), values)

    def get_fina_time_series_by_date(
        self,
        start_date: str,
        end_date: str,
        step: int,
        date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> pd.DataFrame:
        """
        Retrieve time series data by specifying a date range and convert it to a Pandas DataFrame.

        Parameters:
            start_date (str): The start date as a string.
            end_date (str): The end date as a string.
            step (int): The interval between data points in seconds.
            date_format (str, optional):
                The format of the input date strings. Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            pd.DataFrame: A DataFrame with time as the index and data values as a column.

        Raises:
            ValueError: If the parsed start or end date is invalid.
        
        Example:
            >>> fina_data.get_fina_time_series_by_date(
                "2023-01-01 00:00:00",
                "2023-01-02 00:00:00",
                step=60)
        """
        start_dt = Utils.get_utc_datetime_from_string(start_date, date_format)
        end_dt = Utils.get_utc_datetime_from_string(end_date, date_format)

        start = int(start_dt.timestamp())
        window = int(end_dt.timestamp() - start)

        values = self.get_fina_values(start=start, step=step, window=window)

        return self.set_data_frame(self.timestamps(), values)

    @staticmethod
    def set_data_frame(times: np.ndarray,
                       values: np.ndarray
                       ) -> Optional["pd.DataFrame"]:
        """
        Convert arrays of time and values into a Pandas DataFrame.

        Parameters:
            times (np.ndarray): Array of time values (Unix timestamps).
            values (np.ndarray): Array of data values corresponding to the times.

        Returns:
            Optional[pd.DataFrame]: A DataFrame with time as the index and data values as a column.

        Raises:
            ValueError:
                If the input arrays are not of the same shape or not instances of np.ndarray.
        
        Example:
            >>> times = np.array([1672531199, 1672531259, 1672531319])
            >>> values = np.array([1.0, 2.0, 3.0])
            >>> FinaDataFrame.set_data_frame(times, values)
        """
        if not isinstance(times, np.ndarray)\
                or not isinstance(values, np.ndarray):
            raise ValueError("Times and Values must be a numpy ndarray.")

        if not times.shape == values.shape:
            raise ValueError("Times and Values must have same shape.")

        df = pd.DataFrame(
            {"values": values},
            index=pd.to_datetime(times, unit="s", utc=True)
        )
        df.index.name = "times"
        return df


class FinaDfStats(FinaStats):
    """
    Extension of FinaStats with methods to compute and return statistics as Pandas DataFrames.

    Methods:
        - get_df_stats: Compute daily statistics and return them as a Pandas DataFrame.
        - get_df_stats_by_date:
            Compute statistics for a specific date range and return as a DataFrame.
        - get_stats_labels: Get column labels for the statistics DataFrame.
        - get_integrity_labels: Get column labels for integrity stats.
        - get_values_labels: Get column labels for value stats.
    """
    def get_df_stats(
        self,
        start_time: Optional[int] = 0,
        steps_window: int = -1,
        max_size: int = 10_000,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        stats_type: StatsType = StatsType.VALUES
    ) -> List[List[Union[float, int]]]:
        """
        Compute statistics for data within a specified range and return them as a Pandas DataFrame.

        Parameters:
            start_time (Optional[int]): The start time in seconds (Unix timestamp). Defaults to 0.
            steps_window (int): The number of steps in the window. Defaults to -1 (all data).
            max_size (int): Maximum size of the dataset. Defaults to 10,000.
            min_value (Optional[Union[int, float]]):
                Minimum valid value for filtering. Defaults to None.
            max_value (Optional[Union[int, float]]):
                Maximum valid value for filtering. Defaults to None.
            stats_type (StatsType): Type of statistics to compute. Defaults to StatsType.VALUES.

        Returns:
            pd.DataFrame: A DataFrame containing computed statistics with time as the index.
        
        Example:
            >>> stats_df = fina_stats.get_df_stats(
                start_time=0,
                steps_window=3600,
                stats_type=StatsType.VALUES)
        """
        df = pd.DataFrame(
            self.get_stats(
                start_time=start_time,
                steps_window=steps_window,
                max_size=max_size,
                min_value=min_value,
                max_value=max_value,
                stats_type=stats_type
            ),
            columns=self.get_stats_labels(stats_type=stats_type)
        )
        return df.set_index(pd.to_datetime(df['time'], unit='s', utc=True))

    def get_df_stats_by_date(self,
        start_date: str,
        end_date: str,
        date_format: str = "%Y-%m-%d %H:%M:%S",
        max_size: int = 10_000,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        stats_type: StatsType = StatsType.VALUES
    ) -> List[List[Union[float, int]]]:
        """
        Compute statistics for data within a specified date range
        and return them as a Pandas DataFrame.

        Parameters:
            start_date (str): The start date as a string.
            end_date (str): The end date as a string.
            date_format (str, optional):
                The format of the input date strings. Defaults to "%Y-%m-%d %H:%M:%S".
            max_size (int): Maximum size of the dataset. Defaults to 10,000.
            min_value (Optional[Union[int, float]]):
                Minimum valid value for filtering. Defaults to None.
            max_value (Optional[Union[int, float]]):
                Maximum valid value for filtering. Defaults to None.
            stats_type (StatsType): Type of statistics to compute. Defaults to StatsType.VALUES.

        Returns:
            pd.DataFrame: A DataFrame containing computed statistics with time as the index.
        
        Example:
            >>> stats_df = fina_stats.get_df_stats_by_date(
                "2023-01-01 00:00:00",
                "2023-01-02 00:00:00")
        """
        df = pd.DataFrame(
            self.get_stats_by_date(
                start_date=start_date,
                end_date=end_date,
                date_format=date_format,
                max_size=max_size,
                min_value=min_value,
                max_value=max_value
            ),
            columns=self.get_stats_labels(stats_type=stats_type)
        )
        return df.set_index(pd.to_datetime(df['time'], unit='s', utc=True))

    @staticmethod
    def get_stats_labels(stats_type: StatsType = StatsType.VALUES) -> List[str]:
        """
        Get the column labels for the statistics DataFrame based on the type of statistics.

        Parameters:
            stats_type (StatsType): The type of statistics (VALUES or INTEGRITY).

        Returns:
            List[str]: A list of column labels for the DataFrame.
        
        Example:
            >>> FinaDfStats.get_stats_labels(stats_type=StatsType.VALUES)
        """
        if stats_type == StatsType.VALUES:
            return FinaDfStats.get_values_labels()
        return FinaDfStats.get_integrity_labels()

    @staticmethod
    def get_integrity_labels():
        """
        Get column labels for integrity statistics DataFrame.

        Returns:
            List[str]: A list of column labels for integrity stats.
        
        Example:
            >>> FinaDfStats.get_integrity_labels()
        """
        return [
            'time', 'nb_finite', 'nb_total'
        ]

    @staticmethod
    def get_values_labels():
        """
        Get column labels for value statistics DataFrame.

        Returns:
            List[str]: A list of column labels for value stats.
        
        Example:
            >>> FinaDfStats.get_values_labels()
        """
        return [
            'time', 'min', 'mean', 'max'
        ]
