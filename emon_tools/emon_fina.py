"""
Common utilities for Fina Files processing.
"""
from os.path import isdir, isfile, getsize
from os.path import join as path_join
from struct import unpack
from typing import List, Tuple
from typing import Optional
from typing import Union
from typing import Generator
import logging
import mmap
import math
import datetime as dt
import numpy as np
from emon_tools.fina_utils import Utils

logging.basicConfig()
et_logger = logging.getLogger(__name__)


class MetaData:
    """
    Class to manage metadata with validation, serialization,
    and string representation.

    Attributes:
        interval (int): Interval between data points in seconds.
        start_time (int): Start time as a UNIX timestamp.
        npoints (int): Total number of data points.
        end_time (int): End time as a UNIX timestamp.
    """

    def __init__(self,
                 interval: int,
                 start_time: int,
                 npoints: int,
                 end_time: int
                 ):
        """
        Initialize the MetaData instance.

        Parameters:
            interval (int): Interval between data points in seconds.
            start_time (int): Start time as a UNIX timestamp.
            npoints (int): Total number of data points.
            end_time (int): End time as a UNIX timestamp.

        Raises:
            ValueError:
                If any parameter is invalid or start_time is not less than end_time.
        """
        self.interval = interval
        self.start_time = start_time
        self.npoints = npoints
        self.end_time = end_time

    def _validate_date_order(self):
        """
        Ensure that start_time precedes end_time.

        Raises:
            ValueError: If start_time is not less than end_time.
        """
        if self._start_time >= self._end_time:
            raise ValueError("start_time must be less than end_time.")

    @property
    def interval(self) -> int:
        """
        Get the interval between data points in seconds.

        Returns:
            int: Interval in seconds.
        """
        return self._interval

    @interval.setter
    def interval(self, value: int):
        """
        Set the interval between data points in seconds.

        Parameters:
            value (int): Interval in seconds.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        self._interval = Utils.validate_positive_integer(value, "interval")

    @property
    def start_time(self) -> int:
        """
        Get the start time as a UNIX timestamp.

        Returns:
            int: Start time in seconds since the epoch.
        """
        return self._start_time

    @start_time.setter
    def start_time(self, value: int):
        """
        Set the start time as a UNIX timestamp.

        Parameters:
            value (int): Start time in seconds since the epoch.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        self._start_time = Utils.validate_timestamp(value, "start_time")
        if hasattr(self, "_end_time"):
            self._validate_date_order()

    @property
    def npoints(self) -> int:
        """
        Get the total number of data points.

        Returns:
            int: Number of data points.
        """
        return self._npoints

    @npoints.setter
    def npoints(self, value: int):
        """
        Set the total number of data points.

        Parameters:
            value (int): Number of data points.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        self._npoints = Utils.validate_positive_integer(value, "npoints")

    @property
    def end_time(self) -> int:
        """
        Get the end time as a UNIX timestamp.

        Returns:
            int: End time in seconds since the epoch.
        """
        return self._end_time

    @end_time.setter
    def end_time(self, value: int):
        """
        Set the end time as a UNIX timestamp.

        Parameters:
            value (int): End time in seconds since the epoch.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        self._end_time = Utils.validate_timestamp(value, "end_time")
        if hasattr(self, "_start_time"):
            self._validate_date_order()

    def calculate_nb_days(self) -> int:
        """
        Calculate the number of days covered by the data.

        Returns:
            int: Number of days.
        """
        start = dt.datetime.fromtimestamp(self._start_time, dt.timezone.utc)
        end = dt.datetime.fromtimestamp(self._end_time, dt.timezone.utc)
        delta = (end - start).total_seconds() / (3600 * 24)
        return math.ceil(delta)

    def serialize(self) -> dict:
        """
        Serialize the metadata into a dictionary.

        Returns:
            dict: Serialized metadata.
        """
        return {
            "interval": self._interval,
            "start_time": self._start_time,
            "npoints": self._npoints,
            "end_time": self._end_time,
        }

    def __str__(self) -> str:
        return f"{self.serialize()}"


class FinaReader:
    """
    Class to handle the reading of Fina data files and associated metadata.

    Attributes:
        feed_id (int): Identifier for the data feed.
        data_dir (str): Directory containing the Fina data files.
        pos (int): Current read position in the data file.
    """

    def __init__(self, feed_id: int, data_dir: str):
        """
        Initialize the FinaReader instance.

        Parameters:
            feed_id (int): Identifier for the data feed.
            data_dir (str): Directory containing the Fina data files.

        Raises:
            ValueError: If feed_id is not positive or data_dir is invalid.
        """
        if feed_id <= 0:
            raise ValueError("feed_id must be a positive integer.")
        if not isdir(data_dir):
            raise ValueError(f"{data_dir} is not a valid directory.")

        self._feed_id = feed_id
        self._data_dir = data_dir
        self._pos = 0
        self._chunk_size = 0

    @property
    def feed_id(self) -> int:
        """
        Get the identifier for the data feed.

        Returns:
            int: Data feed identifier.
        """
        return self._feed_id

    @feed_id.setter
    def feed_id(self, value: int):
        """
        Set the identifier for the data feed.

        Parameters:
            value (int): Data feed identifier.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        if value <= 0:
            raise ValueError("feed_id must be a positive integer.")
        self._feed_id = value

    @property
    def data_dir(self) -> str:
        """
        Get the directory containing the Fina data files.

        Returns:
            str: Directory path.
        """
        return self._data_dir

    @data_dir.setter
    def data_dir(self, value: str):
        """
        Set the directory containing the Fina data files.

        Parameters:
            value (str): Directory path.

        Raises:
            ValueError: If the directory is invalid.
        """
        if not isdir(value):
            raise ValueError("data_dir must be a valid directory.")
        self._data_dir = value

    @property
    def pos(self) -> str:
        """
        Get the current read position in the data file.

        Returns:
            int: Current read position.
        """
        return self._pos

    @pos.setter
    def pos(self, value: str):
        """
        Set the current read position in the data file.

        Parameters:
            value (int): Read position.

        Raises:
            ValueError: If the position is negative.
        """
        if value < 0:
            raise ValueError("pos must be a positive integer.")
        self._pos = value

    @property
    def chunk_size(self) -> str:
        """
        Get the current read chunk_size in the data file.

        Returns:
            int: Current read chunk_size.
        """
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: str):
        """
        Set the current read chunk_size in the data file.

        Parameters:
            value (int): Read chunk_size.

        Raises:
            ValueError: If the chunk_size is negative.
        """
        if value < 0:
            raise ValueError("chunk_size must be a positive integer.")
        self._chunk_size = value

    def read_meta(self) -> MetaData:
        """
        Read metadata from the .meta file.

        Returns:
            MetaData: Metadata object.

        Raises:
            IOError: If there is an issue reading the meta file.
        """
        try:
            with open(self._get_meta_path(), "rb") as file:
                file.seek(8)
                hexa = file.read(8)
                if len(hexa) != 8:
                    raise ValueError("Meta file is corrupted.")
                interval, start_time = unpack("<2I", hexa)

            data_size = getsize(self._get_data_path())
            npoints = data_size // 4
            end_time = start_time + npoints * interval - interval

            return MetaData(interval, start_time, npoints, end_time)
        except Exception as e:
            raise IOError(
                f"Error reading meta file: {e}"
            ) from e

    def is_ready(self) -> bool:
        """
        Check if the reader is ready based on the metadata.

        Returns:
            bool: True if metadata is valid, False otherwise.
        """
        meta = self.read_meta()
        return meta is not None and self.is_meta_valid(meta.serialize())

    def read_file(self,
                  set_pos: bool = True
                  ) -> Generator[Tuple[int, float], None, None]:
        """
        Read data values from the .dat file.

        Parameters:
            set_pos (bool): Whether to automatically increment the position after reading.

        Yields:
            Tuple[int, float]: Position and data value.

        Raises:
            ValueError: If metadata is invalid or data reading fails.
        """
        meta = self.read_meta()
        if not self.is_ready():
            raise ValueError("Metadata is invalid or incomplete.")

        data_path = self._get_data_path()
        self._pos = 0
        with open(data_path, "rb") as file:
            with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                while 0 <= self._pos < meta.npoints:
                    offset = self._pos * 4
                    hexa = mm[offset:offset + 4]
                    if len(hexa) == 4:
                        value = unpack("<f", hexa)[0]
                        yield self._pos, value
                    else:
                        raise ValueError(
                            f"Error reading data at position {self._pos}."
                        )
                    if set_pos:
                        self._pos += 1

    @staticmethod
    def is_meta_valid(meta: Dict[str, int]) -> bool:
        required_keys = {"interval", "start_time", "npoints", "end_time"}
        return (
            isinstance(meta, dict)
            and required_keys <= meta.keys()
            and all(isinstance(meta[k], int) for k in required_keys)
        )


class FinaDataResult:
    """
    Wrapper for FinaData results providing methods to get results as a DataFrame or plot them.
    """
    def __init__(self, times: np.ndarray, values: np.ndarray):
        self.times = times
        self.values = values

    def df(self) -> Optional[pd.DataFrame]:
        """
        Return the results as a pandas DataFrame with a time index.

        Returns:
            Optional[pd.DataFrame]: A DataFrame with time as the index and values as a column if pandas is available.
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas is not available. Install it to use this feature.")
        return pd.DataFrame({"values": self.values}, index=pd.to_datetime(self.times, unit="s", utc=True))

    def plot(self):
        """
        Plot the results using matplotlib or pandas (if available).

        Raises:
            ImportError: If matplotlib is not available.
        """
        if MATPLOTLIB_AVAILABLE and PANDAS_AVAILABLE:
            df = self.df()
            plt.figure(figsize=(18, 6))
            plt.subplot(1, 1, 1)
            plt.plot(df.index, df['values'], label="Fina Values")
            plt.title("Fina Values")
            plt.xlabel("Time")
            plt.ylabel("Values")
            plt.grid(True)
            plt.show()
        elif MATPLOTLIB_AVAILABLE:
            plt.figure(figsize=(18, 6))
            plt.subplot(1, 1, 1)
            plt.plot(self.times, self.values)
            plt.title("Fina Values")
            plt.xlabel("Time (s)")
            plt.ylabel("Values")
            plt.grid(True)
            plt.show()
        else:
            raise ImportError("Matplotlib is not available. Install it to use this feature.")


class FinaData:
    """
    A class to handle data retrieval and processing from a Fina data file.
    """
    def __init__(self, feed_id: int, data_dir: str):
        """
        Initialize the FinaData object with a FinaReader instance.

        Parameters:
            feed_id (int): Unique identifier for the feed.
            data_dir (str): Directory path to the Fina data files.
        """
        self.reader = FinaReader(feed_id=feed_id, data_dir=data_dir)
        self.meta = self.reader.read_meta()
        self.length = self.meta.npoints * self.meta.interval
        self.lines: int = 0
        self.start: Optional[int] = None
        self.end: Optional[int] = None
        self.step: Optional[int] = None

    def timescale(self) -> np.ndarray:
        """
        Generate the time scale of the feed as a NumPy array.

        Returns:
            np.ndarray: Array of time values in seconds.
        """
        if self.step is None or self.lines == 0:
            raise ValueError("Step size and line count must be set before generating a timescale.")
        return np.arange(0, self.step * self.lines, self.step)

    def read_fina_values(self, start: int, step: int, window: int, set_pos: bool = True) -> np.ndarray:
        """
        Read values from the Fina data file. If the step value is greater than the meta interval,
        calculate the average of the values within each step interval.

        Parameters:
            start (int): Start time in seconds.
            step (int): Step interval in seconds.
            npts (int): Number of points to read.
            set_pos (bool): If True, update the reader's position.

        Returns:
            np.ndarray: Array of read values or averages, with NaNs for missing data.

        Raises:
            ValueError: If the start time is beyond the feed's end time.
        """
        if start >= self.meta.end_time:
            raise ValueError(
                "Invalid start value. Start must be less than the feed's end time "
                "defined by start_time + (npoints * interval) from metadata."
            )
        npts = window // step
        result = np.full(npts, np.nan)
        interval = self.meta.interval

        if step <= interval:
            self.end = start + (npts - 1) * step
            self.reader.pos = (start - self.meta.start_time) // interval

            for i, value in self.reader.read_file(set_pos=set_pos):
                if i < npts:
                    result[i] = value
                else:
                    break

                if not set_pos:
                    time = start + step * (i + 1)
                    self.reader.pos = (time - self.meta.start_time) // interval

        else:
            npts = window // self.meta.interval
            step_sec = step // self.meta.interval
            self.end = start + (npts - 1) * step
            self.reader.pos = (start - self.meta.start_time) // interval
            tmp = np.full(npts, np.nan)
            j, k = 0, 0
            for i, value in self.reader.read_file(set_pos=set_pos):
                if i < npts:
                    if j < step_sec:
                        tmp[i] = value
                        j += 1
                    else:
                        result[k] = np.nanmean(tmp)
                        tmp = np.full(npts, np.nan)
                        j = 0
                        k += 1
                else:
                    break

        self.start, self.step, self.lines = start, step, result.size
        return result

    def get_fina_values(
        self, start: int, step: int, window: int
    ) -> FinaDataResult:
        """
        Retrieve values from the Fina data file within a specific window.

        Parameters:
            start (int): Start time in seconds.
            step (int): Step interval in seconds.
            window (int): Window size in seconds.

        Returns:
            FinaDataResult: An object containing the results with methods for DataFrame and plotting.
        """
        window_min = min(window, self.length)

        values = self.read_fina_values(start=start, step=step, window=window_min)
        times = self.timescale() + start
        return FinaDataResult(times, values)

    def get_fina_values_by_date(
        self, start_date: str, end_date: str, step: int, date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> FinaDataResult:
        """
        Retrieve values from the Fina data file based on date range.

        Parameters:
            start_date (str): Start date as a string.
            end_date (str): End date as a string.
            step (int): Step interval in seconds.
            date_format (str): Format of the date strings.

        Returns:
            FinaDataResult: An object containing the results with methods for DataFrame and plotting.
        """
        start_dt = self.get_utc_datetime_from_string(start_date, date_format)
        end_dt = self.get_utc_datetime_from_string(end_date, date_format)

        start = int(start_dt.timestamp())
        window = math.ceil(end_dt.timestamp() - start)

        return self.get_fina_values(start=start, step=step, window=window)

    @staticmethod
    def get_utc_datetime_from_string(dt_value: str, date_format: str = "%Y-%m-%d %H:%M:%S") -> dt.datetime:
        """
        Convert a date string to a UTC datetime object.

        Parameters:
            dt_value (str): The date-time string to parse.
            date_format (str): Format of the date-time string (default: "%Y-%m-%d %H:%M:%S").

        Returns:
            dt.datetime: A timezone-aware datetime object in UTC.

        Raises:
            ValueError: If parsing fails.
            TypeError: If the input is not a string.
        """
        if not isinstance(dt_value, str):
            raise TypeError("Input must be a string.")

        try:
            naive_datetime = dt.datetime.strptime(dt_value, date_format)
            return naive_datetime.replace(tzinfo=dt.timezone.utc)
        except ValueError as e:
            raise ValueError(
                f"Error parsing date '{dt_value}' with format '{date_format}': {e}"
            ) from e


class FinaStats:
    """FinaStats class for analyzing FinaReader data efficiently."""

    def __init__(self, feed_id: int, data_dir: str):
        self.reader = FinaReader(feed_id, data_dir)
        self.meta = self.reader.read_meta()

    def get_pos(self) -> int:
        """Retrieve the current reader position."""
        return self.reader.pos

    def get_stats(self,
                  min_value: Optional[Union[int, float]] = None,
                  max_value: Optional[Union[int, float]] = None
                  ) -> List[List[Union[float, int]]]:
        """
        Compute daily statistics from PhpFina file data.

        Parameters:
            min_value (Optional[Union[int, float]]): Minimum valid value for filtering.
            max_value (Optional[Union[int, float]]): Maximum valid value for filtering.

        Returns:
            List[List[Union[float, int]]]: Daily grouped statistics.
        """
        # Cache frequently accessed meta values
        start_time = self.meta.start_time
        interval = self.meta.interval

        if start_time is None or interval is None:
            raise ValueError("Meta data is incomplete or invalid.")

        result = []
        raw_data = []
        current_day_start = self.get_start_day(start_time)

        # Process the data in chunks
        for i, value in self.reader.read_file():
            timestamp = start_time + i * interval
            value = self.validate_value(value, min_value, max_value)
            day_start = self.get_start_day(timestamp)

            if day_start == current_day_start:
                raw_data.append([timestamp, value])
            else:
                # Process and append stats for the current day
                if raw_data:
                    result.append(self.get_grouped_stats(np.array(raw_data), current_day_start))
                # Reset for the new day
                raw_data = [[timestamp, value]]
                current_day_start = day_start

        # Process the last chunk of data
        if raw_data:
            result.append(self.get_grouped_stats(np.array(raw_data), current_day_start))

        return result

    @staticmethod
    def validate_value(
        value: Union[int, float],
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None
    ) -> float:
        """
        Validate a value based on thresholds.

        Parameters:
            value (Union[int, float]): The value to validate.
            min_value (Optional[Union[int, float]]): Minimum valid value.
            max_value (Optional[Union[int, float]]): Maximum valid value.

        Returns:
            float: The validated value, or NaN if invalid.
        """
        if not Ut.is_numeric(value):
            return float("nan")
        if min_value is not None and value < min_value:
            return float("nan")
        if max_value is not None and value > max_value:
            return float("nan")
        return value

    @staticmethod
    def get_start_day(timestamp: float) -> float:
        """
        Get the start-of-day timestamp for a given timestamp in UTC.

        Parameters:
            timestamp (float): The input timestamp.

        Returns:
            float: The start-of-day timestamp in UTC.
        """
        dt_point = dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc)
        return dt.datetime(dt_point.year, dt_point.month, dt_point.day, tzinfo=dt.timezone.utc).timestamp()

    @staticmethod
    def get_grouped_stats(raw_data: np.ndarray, day_start: float) -> List[Union[float, int]]:
        """
        Compute statistics for a single day's data.

        Parameters:
            raw_data (np.ndarray): Array of timestamps and values for the day.
            day_start (float): Start-of-day timestamp.

        Returns:
            List[Union[float, int]]: Computed statistics for the day.
        """
        if raw_data.size == 0:
            return [day_start, np.nan, np.nan, np.nan, 0, 0, 0, np.nan]

        values = raw_data[:, 1]
        time_deltas = np.diff(raw_data[:, 0]) if len(raw_data) > 1 else [np.nan]

        nb_nan = np.isnan(values).sum()
        nb_total = len(values)
        nb_finite = np.isfinite(values).sum()

        stats = [
            np.nanmin(values) if nb_finite > 0 else np.nan,
            np.nanmean(values) if nb_finite > 0 else np.nan,
            np.nanmax(values) if nb_finite > 0 else np.nan,
            nb_finite,
            nb_nan,
            nb_total,
            np.nanmean(time_deltas),
        ]
        return [day_start] + stats
