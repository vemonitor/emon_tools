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

    def _get_base_path(self) -> str:
        return path_join(self._data_dir, str(self._feed_id))

    def _get_meta_path(self) -> str:
        file_path = f"{self._get_base_path()}.meta"
        if not isfile(file_path):
            raise FileNotFoundError(f"Meta file does not exist: {file_path}")
        return file_path

    def _get_data_path(self) -> str:
        file_path = f"{self._get_base_path()}.dat"
        if not isfile(file_path):
            raise FileNotFoundError(f"Data file does not exist: {file_path}")
        return file_path

    def _validate_read_params(
        self,
        npoints: int,
        start_pos: int,
        chunk_size: int,
        window: Optional[int],
    ) -> int:
        """
        Validate read parameters and calculate total points to process.

        Parameters:
            npoints (int): Total number of points in the file.
            start_pos (int): Starting position (index) in the file.
            chunk_size (int): Number of values to read per chunk.
            window (Optional[int]): Maximum number of points to read.

        Returns:
            int: Total points to process based on input parameters.

        Raises:
            ValueError: If parameters are invalid.
        """
        npoints = Utils.validate_positive_integer(npoints, "npoints")
        self.chunk_size = Utils.validate_positive_integer(chunk_size, "chunk_size")

        if not isinstance(start_pos, int) or start_pos < 0:
            raise ValueError(f"start_pos ({start_pos}) must be an integer upper or equal to zero.")

        if start_pos >= npoints:
            raise ValueError(f"start_pos ({start_pos}) exceeds total npoints ({npoints}).")

        if window is not None:
            window = Utils.validate_positive_integer(window, "window")
            total_points = min(npoints - start_pos, window)
        else:
            total_points = npoints - start_pos

        return total_points

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

    def read_file(
        self,
        npoints: int,
        start_pos: int = 0,
        chunk_size: int = 1024,
        window: Optional[int] = None,
        set_pos: bool = True,
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Read data values from the .dat file in chunks.

        Parameters:
            npoints (int): Total number of points in the file.
            start_pos (int): Starting position (index) in the file. Defaults to 0.
            chunk_size (int): Number of values to read in each chunk. Defaults to 1024.
            window (Optional[int]): 
                Maximum number of points to read.
                If None, reads all available points.
            set_pos (bool): Whether to automatically increment the position after reading.

        Yields:
            Tuple[np.ndarray, np.ndarray]: 
                - Array of positions (indices).
                - Array of corresponding data values.

        Raises:
            ValueError: If parameters are invalid or data reading fails.
            IOError: If file access fails.
        """
        # Validate inputs and compute total points to read
        total_points = self._validate_read_params(
            npoints=npoints,
            start_pos=start_pos,
            chunk_size=chunk_size,
            window=window
        )

        data_path = self._get_data_path()
        self._pos = start_pos

        try:
            with open(data_path, "rb") as file:
                with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    while self._pos < start_pos + total_points:
                        # Calculate current chunk size
                        remaining_points = start_pos + total_points - self._pos
                        current_chunk_size = min(self.chunk_size, remaining_points)

                        # Compute offsets and read data
                        offset = self._pos * 4
                        end_offset = offset + current_chunk_size * 4
                        chunk_data = mm[offset:end_offset]

                        if len(chunk_data) != current_chunk_size * 4:
                            raise ValueError(
                                f"Failed to read expected chunk at position {self._pos}. "
                                f"Expected {current_chunk_size * 4} bytes, got {len(chunk_data)}."
                            )

                        # Convert to values and yield
                        values = np.frombuffer(chunk_data, dtype='<f4')
                        positions = np.arange(self._pos, self._pos + current_chunk_size)
                        yield positions, values

                        # Increment position
                        if set_pos:
                            self._pos += current_chunk_size

        except IOError as e:
            raise IOError(
                f"Error accessing data file at path {data_path}: {e}"
            ) from e
        except ValueError as e:
            raise ValueError(f"Data reading failed: {e}") from e


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

    def _validate_and_prepare_params(
            self,
            start_time: int,
            steps_window: int,
            max_size: int
        ):
        """
        Validate input parameters and prepare the start point and selected points.

        Parameters:
            start_time (int): The start time in seconds from the beginning of the file.
            steps_window (int): Number of steps to process. Use -1 for all data.
            max_size (int): Maximum allowed number of steps to process.

        Returns:
            Tuple[int, int]: The start point (in steps) and the number of selected points.

        Raises:
            ValueError: 
                If the start time exceeds the file's end time 
                or if the selected points exceed max_size.
        """
        file_start_time = self.meta.start_time
        interval = self.meta.interval
        total_points = self.meta.npoints

        start_point = max(0, (start_time - file_start_time) // interval)
        if steps_window == -1:
            steps_window = total_points - start_point

        if start_point >= total_points:
            raise ValueError(
                f"Start time ({start_time}) exceeds file "
                f"end time ({self.meta.end_time}).")

        selected_points = min(steps_window, total_points - start_point)
        if selected_points > max_size:
            raise ValueError(
                f"Requested steps ({selected_points}) exceed "
                f"max_size ({max_size}).")

        return start_point, selected_points

    def _initialize_result(self, selected_points):
        """
        Initialize the result array and calculate points per day.

        Parameters:
            selected_points (int): Number of selected points to process.

        Returns:
            A numpy array initialized with NaN values to store results.
        """
        interval = self.meta.interval
        npts_day = math.ceil(86400 / interval)  # Points per day
        npts_total = math.ceil(selected_points / npts_day) + 1

        result = np.full((npts_total, 6), [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan])
        return result

    def _get_initial_day_boundaries(self, start_point):
        """
        Compute the initial start and end times of the first day boundary.

        Parameters:
            start_time (int): The start time in seconds from the beginning of the file.

        Returns:
            Tuple[int, int]: The current day start time and the next day start time.
        """
        file_start_time = self.meta.start_time
        interval = self.meta.interval

        current_day_start = Utils.get_start_day(file_start_time + start_point * interval)
        next_day_start = current_day_start + 86400
        return current_day_start, next_day_start

    def _get_chunk_size(
            self,
            current_day_start,
            next_day_start,
            is_first=False
        ):
        """
        Compute the chunk_size of the current day.

        Parameters:
            start_time (int): The start time in seconds from the beginning of the file.

        Returns:
            Tuple[int, int]: The current day start time and the next day start time.
        """
        if is_first:
            init_start = max(self.meta.start_time, current_day_start)
            init_chunk = int((next_day_start - init_start) / self.meta.interval)
        else:
            init_chunk = int((next_day_start - current_day_start) / self.meta.interval)
        return init_chunk

    def _validate_chunk(self, positions, next_day_start):
        """
        Validate the chunk of data to ensure it fits within the current day boundary.

        Parameters:
            positions (np.ndarray): Array of positions for the current chunk.
            next_day_start (int): Start time of the next day.

        Raises:
            ValueError: If the chunk contains data beyond the current day's boundary.
        """
        timestamps = self.meta.start_time + (positions * self.meta.interval)
        if timestamps[-1] >= next_day_start:
            raise ValueError(
                f"Reader Error: Last timestamp {timestamps[-1]} "
                f"exceeds day boundary {next_day_start}."
            )

    def _process_day(self, values, current_day_start, min_value, max_value):
        """
        Process data for a single day by filtering and computing statistics.

        Parameters:
            values (np.ndarray): Array of data values for the current day.
            current_day_start (int): Start time of the current day.
            min_value (Optional[Union[int, float]]): Minimum valid value for filtering.
            max_value (Optional[Union[int, float]]): Maximum valid value for filtering.

        Returns:
            np.ndarray: Computed statistics for the current day.
        """
        filtered_values = Utils.filter_values_by_range(values.copy(), min_value, max_value)
        return self.get_grouped_stats(filtered_values, current_day_start)

    def _update_day_boundaries(self, next_day_start):
        """
        Update the day boundaries for the next iteration.

        Parameters:
            current_day_start (int): Start time of the current day.

        Returns:
            Tuple[int, int]: Updated current day start time and next day start time.
        """
        return next_day_start, next_day_start + 86400

    def _trim_results(self, result):
        """
        Trim the result array to include only processed data.

        Parameters:
            result (np.ndarray): Array of computed results with potential NaN entries.

        Returns:
            List[List[Union[float, int]]]: Trimmed result array as a list of lists.
        """
        finite_mask = np.isfinite(result[:, 0])
        if not finite_mask.any():
            return result.tolist()

        last_valid_index = len(result) - np.argmax(finite_mask[::-1]) - 1
        return result[:last_valid_index + 1].tolist()

    def get_stats(
        self,
        start_time: Optional[int] = 0,
        steps_window: int = -1,
        max_size: int = 10_000,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None
    ) -> List[List[Union[float, int]]]:
        """
        Compute daily statistics from PhpFina file data.

        Parameters:
            start_time (Optional[int]):
                Start time in seconds from the beginning of the file. Defaults to 0.
            steps_window (int):
                Number of steps to process. Use -1 to process all data. Defaults to -1.
            max_size (int):
                Maximum number of data points to process in one call. Defaults to 10,000.
            min_value (Optional[Union[int, float]]): Minimum valid value for filtering.
            max_value (Optional[Union[int, float]]): Maximum valid value for filtering.

        Returns:
            List[List[Union[float, int]]]: 
                A list of daily statistics where each entry contains:
                [day_start, min_value, mean_value, max_value, finite_count, total_count].
        """
        # Prepare metadata and validate parameters
        start_point, selected_points = self._validate_and_prepare_params(
            start_time=start_time,
            steps_window=steps_window,
            max_size=max_size
        )

        # Initialize result storage and day boundaries
        result = self._initialize_result(selected_points)
        current_day_start, next_day_start = self._get_initial_day_boundaries(start_point)
        init_chunk = self._get_chunk_size(current_day_start, next_day_start, True)

        reader_props = {
            "npoints": self.meta.npoints,
            "start_pos": start_point,
            "chunk_size": init_chunk,
            "window": selected_points,
            "set_pos": True
        }

        # Process data in chunks
        days = 0
        for positions, values in self.reader.read_file(**reader_props):
            self._validate_chunk(positions, next_day_start)
            result[days] = self._process_day(values, current_day_start, min_value, max_value)

            # Update day boundaries for next iteration
            days += 1
            current_day_start, next_day_start = self._update_day_boundaries(next_day_start)
            self.reader.chunk_size = self._get_chunk_size(current_day_start, next_day_start)
        # Trim and return results
        return self._trim_results(result)

    def get_stats_by_date(
            self,
            start_date: str,
            end_date: str,
            date_format: str = "%Y-%m-%d %H:%M:%S",
            max_size: int = 10_000,
            min_value: Optional[Union[int, float]] = None,
            max_value: Optional[Union[int, float]] = None
        ) -> List[List[Union[float, int]]]:
        """
        Compute daily statistics from PhpFina file data for a specified date range.

        Parameters:
            start_date (str): Start date in the specified format.
            end_date (str): End date in the specified format.
            date_format (str): Format of the input dates. Defaults to "%Y-%m-%d %H:%M:%S".
            max_size (int):
                Maximum number of data points to process in one call. Defaults to 10,000.
            min_value (Optional[Union[int, float]]): Minimum valid value for filtering. Optional.
            max_value (Optional[Union[int, float]]): Maximum valid value for filtering. Optional.

        Returns:
            List[List[Union[float, int]]]: 
                A list of daily statistics where each entry contains:
                [day_start, min_value, mean_value, max_value, finite_count, total_count].

        Raises:
            ValueError: If the start or end date cannot be converted to valid timestamps.
            ValueError: If the computed steps for the date range exceed max_size.
        """
        # Calculate the start time and number of steps based on the provided date range.
        start, window = Utils.get_window_by_dates(
            start_date=start_date,
            end_date=end_date,
            interval=self.meta.interval,
            date_format=date_format,
        )

        # Use the get_stats method with the computed parameters.
        return self.get_stats(
            start_time=start,
            steps_window=window,
            max_size=max_size,
            min_value=min_value,
            max_value=max_value
        )

    @staticmethod
    def get_grouped_stats(values: np.ndarray, day_start: float) -> List[Union[float, int]]:
        """
        Compute statistics for a single day's data.

        Parameters:
            values (np.ndarray): Array of values for the day.
            day_start (float): Start-of-day timestamp.

        Returns:
            List[Union[float, int]]: Computed statistics for the day.
        """
        if values.shape[0] == 0:
            return [day_start, np.nan, np.nan, np.nan, np.nan, np.nan]

        nb_total = values.shape[0]
        nb_finite = np.isfinite(values).sum()

        stats = [
            np.nanmin(values) if nb_finite > 0 else np.nan,
            np.nanmean(values) if nb_finite > 0 else np.nan,
            np.nanmax(values) if nb_finite > 0 else np.nan,
            nb_finite,
            nb_total,
        ]
        return [day_start] + stats
