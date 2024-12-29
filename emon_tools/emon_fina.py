"""
Common utilities for Fina Files processing.
"""
from enum import Enum
from typing import List
from typing import Optional
from typing import Union
import logging
import math
import numpy as np
from emon_tools.fina_utils import Utils
from emon_tools.fina_reader import FinaReader


logging.basicConfig()
et_logger = logging.getLogger(__name__)


class StatsType(Enum):
    """Remove Nan Method Enum"""
    VALUES = "values"
    INTEGRITY = "integrity"


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

    def _read_direct_values(
        self,
        start: int,
        step: int,
        npts: int,
        interval: int,
        window: int,
        set_pos: bool
    ) -> np.ndarray:
        """
        Read raw values when the step interval is less than or equal to the metadata interval.

        This method retrieves data points directly from the file, filling the result array
        sequentially up to the required number of points (`npts`).

        Parameters:
            start (int): Start time in seconds from the feed's start time.
            step (int): Step interval in seconds for the data retrieval.
            npts (int): Number of data points to read.
            interval (int): Metadata interval in seconds.
            window (int): Total time window in seconds.
            set_pos (bool): If True, updates the reader's position after reading.

        Returns:
            np.ndarray: A NumPy array containing the retrieved values, with NaNs for missing data.

        Notes:
            - This method assumes the `step` interval is small enough for direct reading.
            - Values are read in chunks determined by `calculate_optimal_chunk_size`.
        """
        result = np.full(npts, np.nan)
        self.end = start + (npts - 1) * step
        start_pos = (start - self.meta.start_time) // interval

        reader_props = {
            "npoints": self.meta.npoints,
            "start_pos": start_pos,
            "chunk_size": self.calculate_optimal_chunk_size(window=window),
            "window": window,
            "set_pos": set_pos,
        }

        nb_filled = 0
        for _, values in self.reader.read_file(**reader_props):
            available = values.shape[0]
            remaining = npts - nb_filled

            if remaining <= 0:
                break

            to_copy = min(available, remaining)
            result[nb_filled : nb_filled + to_copy] = values[:to_copy]
            nb_filled += to_copy

        self.start, self.step, self.lines = start, step, result.size
        return result

    def _read_averaged_values(
        self,
        start: int,
        step: int,
        npts: int,
        interval: int,
        window: int
    ) -> np.ndarray:
        """
        Read and average values when the step interval is greater than the metadata interval.

        This method aggregates values within each `step` interval, computing their mean to 
        produce a reduced and meaningful representation of the data.

        Parameters:
            start (int): Start time in seconds from the feed's start time.
            step (int): Step interval in seconds for the data aggregation.
            npts (int): Number of data points to produce after averaging.
            interval (int): Metadata interval in seconds.
            window (int): Total time window in seconds.

        Returns:
            np.ndarray: A NumPy array containing the averaged values, with NaNs for missing data.

        Notes:
            - The averaging process ensures the result matches
              the expected number of points (`npts`).
            - Chunk size is adjusted to be divisible by the step factor for precise reshaping.
            - Empty or partially filled chunks are handled gracefully to avoid runtime errors.
        """
        step_factor = step // interval
        self.end = start + (npts - 1) * step
        start_pos = (start - self.meta.start_time) // interval
        chunk_size = self.calculate_optimal_chunk_size(window=window, divisor=step_factor)
        result = np.full(npts, np.nan)

        reader_props = {
            "npoints": self.meta.npoints,
            "start_pos": start_pos,
            "chunk_size": chunk_size,
            "window": window,
            "set_pos": True,
        }

        nb_filled = 0
        for _, values in self.reader.read_file(**reader_props):
            if values.size == 0:
                continue  # Skip empty reads

            available = values.shape[0]
            remaining = npts - nb_filled

            if remaining <= 0:
                break

            # Ensure the values array can be reshaped without remainder
            usable_size = (available // step_factor) * step_factor
            reshaped_values = values[:usable_size].reshape(-1, step_factor)

            # Avoid computing mean on empty arrays
            if reshaped_values.size > 0:
                averaged_values = np.nanmean(reshaped_values, axis=1)
            else:
                averaged_values = np.full(reshaped_values.shape[0], np.nan)

            to_copy = min(len(averaged_values), remaining)
            result[nb_filled : nb_filled + to_copy] = averaged_values[:to_copy]
            nb_filled += to_copy

        self.start, self.step, self.lines = start, step, result.size
        return result

    def reset(self):
        """
        Reset the object's state to its default values.

        This method reinitializes the core properties of the object, 
        ensuring that it is in a clean and consistent state for reuse. 
        Useful for scenarios where the object's attributes need to 
        be cleared and set to their default states.

        Attributes Reset:
            - `lines` (int): Resets to 0, representing no data points processed.
            - `start` (Optional[int]): Resets to None, indicating no defined start time.
            - `end` (Optional[int]): Resets to None, indicating no defined end time.
            - `step` (Optional[int]): Resets to None, indicating no defined step interval.

        Usage:
            Call this method whenever you need to clear the object's state, 
            typically before reusing it for new operations.
        """
        self.lines: int = 0
        self.start: Optional[int] = None
        self.end: Optional[int] = None
        self.step: Optional[int] = None

    def timescale(self) -> np.ndarray:
        """
        Generate a time scale for the feed as a NumPy array.

        This method creates an evenly spaced array of time values in seconds,
        based on the configured step size and number of lines. It represents 
        the time intervals associated with the data feed.

        Returns:
            np.ndarray: A 1D array of time values in seconds, starting at 0 and 
                        incrementing by `self.step` for `self.lines` intervals.

        Raises:
            ValueError: If `step` is not set or `lines` is zero, indicating 
                        that the necessary properties for generating a time 
                        scale are not properly initialized.

        Example:
            If `step` is 10 and `lines` is 5, this method returns:
            `[0, 10, 20, 30, 40]`
        """
        if self.step is None or self.lines == 0:
            raise ValueError("Step size and line count must be set before generating a timescale.")
        return np.arange(0, self.step * self.lines, self.step)

    def timestamps(self) -> np.ndarray:
        """
        Generate an array of timestamps for the feed as a NumPy array.

        This method calculates the timestamps by adding the `start` time to the 
        generated time scale, providing absolute time values in seconds for each 
        interval of the feed.

        Returns:
            np.ndarray: A 1D array of absolute time values in seconds, starting 
                        from `self.start` and incrementing by `self.step` for 
                        `self.lines` intervals.

        Raises:
            ValueError: If `self.start` is invalid or not properly initialized. 
                        Validation is performed by `Utils.validate_timestamp`.

        Example:
            If `self.start` is 1700000000 and the time scale is `[0, 10, 20, 30]`, 
            this method returns:
            `[1700000000, 1700000010, 1700000020, 1700000030]`
        """
        Utils.validate_timestamp(self.start, 'win_start')
        return self.timescale() + self.start

    def read_fina_values(
        self,
        start: int,
        step: int,
        window: int,
        set_pos: bool = True
    ) -> np.ndarray:
        """
        Read values from the Fina data file, either directly or averaged,
        based on the step interval.

        This method retrieves values from the Fina data file
        for a specified time range and step interval.
        If the `step` is less than or equal to the metadata interval, values are read directly.
        Otherwise, values within each `step` interval are averaged.

        Parameters:
            start (int): Start time in seconds from the feed's start time.
            step (int): Step interval in seconds for the data retrieval.
            window (int): Total time window to read in seconds.
            set_pos (bool): If True, updates the reader's position after reading.

        Returns:
            np.ndarray: 
                A NumPy array containing either the raw values or averaged values.
                Missing data is represented by NaNs.

        Raises:
            ValueError: If the `start` time exceeds the feed's end time.

        Notes:
            - This method adapts its approach based on the relation
              between `step` and the feed's metadata interval.
            - For large `step` values,
              averaging within step intervals is performed for efficiency and clarity.
        """
        if start >= self.meta.end_time:
            raise ValueError(
                "Invalid start value. "
                "Start must be less than the feed's end time "
                "defined by start_time + (npoints * interval) from metadata."
            )

        interval = self.meta.interval
        window = min(window, self.length)
        step = max(step, interval)
        npts = window // step

        if step <= interval:
            return self._read_direct_values(start, step, npts, interval, window, set_pos)

        return self._read_averaged_values(start, step, npts, interval, window)

    def get_fina_values(self,
                        start: int,
                        step: int,
                        window: int
                        ) -> np.ndarray:
        """
        Retrieve data values from the Fina data file for a specified time window.

        This method accesses the Fina data file to extract values within a given 
        time window, starting from a specific time point and using a defined step 
        interval. The method delegates the actual data reading to `read_fina_values`.

        Parameters:
            start (int): Start time in seconds, relative to the feed's start time.
            step (int): Step interval in seconds for sampling the data.
            window (int): Total time window in seconds to retrieve data.

        Returns:
            np.ndarray: A 1D NumPy array containing the retrieved values. Missing 
                        data points are represented by NaNs.

        Notes:
            - The method ensures that the requested time window and step size are 
            handled appropriately, including averaging if the step size exceeds 
            the feed's interval.
            - It is essential to validate the `start`, `step`, and `window` parameters 
            against the metadata to avoid errors.
            - The data extraction aligns with the metadata's time configuration 
            (e.g., interval and start time).

        Raises:
            ValueError: If the `start` time is invalid or exceeds the feed's end time.
        """
        return self.read_fina_values(start=start, step=step, window=window)

    def get_fina_time_series(self,
                             start: int,
                             step: int,
                             window: int
                             ) -> np.ndarray:
        """
        Retrieve a 2D time series array of timestamps and values from the Fina data file.

        This method combines the calculated timestamps and corresponding data values into a 
        2D array where each row represents a [timestamp, value] pair.

        Parameters:
            start (int): Start time in seconds from the feed's start time.
            step (int): Step interval in seconds for data retrieval.
            window (int): Total time window in seconds to retrieve data.

        Returns:
            np.ndarray: A 2D NumPy array with shape (n, 2), where the first column contains 
                        timestamps and the second contains corresponding values.

        Notes:
            - Missing values in the data are represented by NaNs.
            - The timestamps are based on the `start` parameter and the step size.
        """
        values = self.get_fina_values(start=start, step=step, window=window)
        return np.vstack((self.timestamps(), values)).T

    def get_fina_values_by_date(self,
                                start_date: str,
                                end_date: str,
                                step: int,
                                date_format: str = "%Y-%m-%d %H:%M:%S"
                                ) -> np.ndarray:
        """
        Retrieve values from the Fina data file based on a specified date range.

        This method converts the given date range into a time window and retrieves the 
        corresponding values from the data file.

        Parameters:
            start_date (str): Start date in string format.
            end_date (str): End date in string format.
            step (int): Step interval in seconds for data retrieval.
            date_format (str): Format of the input date strings. Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            np.ndarray: 
                A 1D NumPy array containing the retrieved values, with NaNs for missing data.

        Notes:
            - The `Utils.get_window_by_dates` method is used to compute the time range.
            - This method is useful for aligning data retrieval with specific time periods.
        """
        start, window = Utils.get_window_by_dates(
            start_date=start_date,
            end_date=end_date,
            interval=self.meta.interval,
            date_format=date_format,
        )

        return self.get_fina_values(start=start, step=step, window=window)

    def get_fina_time_series_by_date(self,
                                     start_date: str,
                                     end_date: str,
                                     step: int,
                                     date_format: str = "%Y-%m-%d %H:%M:%S"
                                    ) -> np.ndarray:
        """
        Retrieve a 2D time series array of timestamps and values for a specific date range.

        This method combines timestamps and corresponding values within the specified date range 
        into a 2D array where each row represents a [timestamp, value] pair.

        Parameters:
            start_date (str): Start date in string format.
            end_date (str): End date in string format.
            step (int): Step interval in seconds for data retrieval.
            date_format (str): Format of the input date strings. Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            np.ndarray: A 2D NumPy array with shape (n, 2), where the first column contains 
                        timestamps and the second contains corresponding values.

        Notes:
            - Combines `get_fina_values_by_date` and `timestamps` to create the time series.
            - Useful for generating aligned time series data for specific date ranges.
        """
        values = self.get_fina_values_by_date(
            start_date=start_date,
            end_date=end_date,
            step=step,
            date_format=date_format
        )
        return np.vstack((
            self.timestamps(),
            values
        )).T

    def calculate_optimal_chunk_size(
        self,
        window: int,
        min_chunk_size: int = 256,
        scale_factor: float = 1.5,
        divisor: Optional[int] = None
    ) -> int:
        """
        Compute the optimal chunk size for processing data within the given constraints.

        This method determines the best chunk size based on the total window size, scaling factors, 
        and optional divisors while ensuring it remains within the provided limits.

        Parameters:
            window (int): The total size of the data window to process.
            min_chunk_size (int): Minimum allowable chunk size. Defaults to 256.
            scale_factor (float): Factor used to compute the initial division. Defaults to 1.5.
            divisor (Optional[int]):
                Optional divisor to ensure the chunk size is a multiple of this value.

        Returns:
            int: The computed optimal chunk size.

        Raises:
            ValueError:
                If any input parameter is invalid, such as negative values or invalid ranges.

        Notes:
            - If `divisor` is provided,
              the chunk size is adjusted to the nearest multiple of `divisor`.
            - The method ensures that the chunk size respects both minimum and maximum constraints.
        """
        max_chunk_size: int = self.reader.CHUNK_SIZE_LIMIT
        if window <= 0:
            raise ValueError("Window size must be a positive integer.")
        if min_chunk_size <= 0 or max_chunk_size <= 0:
            raise ValueError("Chunk size limits must be positive integers.")
        if min_chunk_size > max_chunk_size:
            raise ValueError("min_chunk_size must be less than or equal to max_chunk_size.")

        # Calculate the base optimal chunk size
        division_factor = int(scale_factor * (window ** 0.5))
        chunk_size = max(min(window // division_factor, max_chunk_size), min_chunk_size)

        # Adjust chunk size for small remainders
        remaining_points = window % chunk_size
        if remaining_points > 0 and remaining_points <= chunk_size // 2:
            chunk_size = max(min_chunk_size, remaining_points)

        # Ensure chunk size is divisible by divisor and within limits
        if divisor is not None:
            chunk_size = FinaData.calculate_nearest_divisible(
                value=chunk_size,
                divisor=divisor,
                min_value=min_chunk_size,
                max_value=max_chunk_size
            )
        return chunk_size

    @staticmethod
    def calculate_nearest_divisible(
        value: int,
        divisor: int,
        min_value: int,
        max_value: int
    ) -> int:
        """
        Adjust a value to the nearest multiple of a divisor within given limits.

        This method ensures that the adjusted value is divisible by the specified divisor while 
        remaining within the provided minimum and maximum limits.

        Parameters:
            value (int): The initial value to adjust.
            divisor (int): The divisor to make the value divisible by.
            min_value (int): Minimum allowable value.
            max_value (int): Maximum allowable value.

        Returns:
            int: The adjusted value, guaranteed to be divisible by `divisor` and within limits.

        Notes:
            - The method prioritizes adherence to limits over exact divisibility if conflicts arise.
            - Useful for ensuring efficient chunking in data processing.
        """
        remainder = value % divisor
        if remainder > 0:
            value += divisor - remainder

        # Ensure the adjusted value is within limits
        if value > max_value:
            value = max_value - (max_value % divisor)
        elif value < min_value:
            value = min_value + (
                divisor - (min_value % divisor)
            ) if min_value % divisor != 0 else min_value

        return value


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

    def _initialize_result(
            self,
            selected_points: int,
            stats_type: StatsType = StatsType.VALUES
        ):
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
        array = FinaStats.init_stats(
            stats_type=stats_type
        )
        result = np.full((npts_total, len(array)), array)
        return result

    def _get_initial_day_boundaries(self, start_point: int):
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
            chunk_size = int((next_day_start - init_start) / self.meta.interval)
        else:
            chunk_size = int((next_day_start - current_day_start) / self.meta.interval)
        return max(chunk_size, self.reader.CHUNK_SIZE_LIMIT)

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

    def _process_day(self,
        values: np.ndarray,
        current_day_start: int,
        min_value: Optional[Union[int, float]],
        max_value: Optional[Union[int, float]],
        stats_type: StatsType = StatsType.VALUES
    ) -> np.ndarray:
        """
        Process data for a single day by filtering and computing statistics.

        Parameters:
            values (np.ndarray): Array of data values for the current day.
            current_day_start (int): Start time of the current day.
            min_value (Optional[Union[int, float]]): Minimum valid value for filtering.
            max_value (Optional[Union[int, float]]): Maximum valid value for filtering.
            stats_type (StatsType): Type of statistics to compute. Defaults to StatsType.VALUES.

        Returns:
            np.ndarray: Computed statistics for the current day.
        """
        filtered_values = Utils.filter_values_by_range(values.copy(), min_value, max_value)
        if stats_type == StatsType.INTEGRITY:
            return self.get_integrity_stats(filtered_values, current_day_start)
        return self.get_values_stats(filtered_values, current_day_start)

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
        max_value: Optional[Union[int, float]] = None,
        stats_type: StatsType = StatsType.VALUES
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
            stats_type (StatsType): Type of statistics to compute. Defaults to StatsType.VALUES.

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
        result = self._initialize_result(
            selected_points=selected_points,
            stats_type=stats_type
        )
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
            result[days] = self._process_day(
                values=values,
                current_day_start=current_day_start,
                min_value=min_value,
                max_value=max_value,
                stats_type=stats_type
            )

            # Update day boundaries for next iteration
            days += 1
            current_day_start, next_day_start = self._update_day_boundaries(next_day_start)
            self.reader.chunk_size = self._get_chunk_size(current_day_start, next_day_start)
        # Trim and return results
        return self._trim_results(result)

    def get_stats_by_date(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        date_format: str = "%Y-%m-%d %H:%M:%S",
        max_size: int = 10_000,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
        stats_type: StatsType = StatsType.VALUES
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
            stats_type (StatsType): Type of statistics to compute. Defaults to StatsType.VALUES.

        Returns:
            List[List[Union[float, int]]]: 
                A list of daily statistics where each entry contains:
                [day_start, min_value, mean_value, max_value, finite_count, total_count].

        Raises:
            ValueError: If the start or end date cannot be converted to valid timestamps.
            ValueError: If the computed steps for the date range exceed max_size.
        """
        start, window = 0, -1
        if start_date is not None and end_date is not None:
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
            max_value=max_value,
            stats_type=stats_type
        )

    @staticmethod
    def init_stats(
        day_start: Union[float, int] = np.nan,
        stats_type: StatsType = StatsType.VALUES
    ) -> List[Union[float, int]]:
        """Initialyse stats array values."""
        if stats_type == StatsType.INTEGRITY:
            return [day_start, np.nan, np.nan]
        return [day_start, np.nan, np.nan, np.nan]

    @staticmethod
    def get_integrity_stats(values: np.ndarray, day_start: float) -> List[Union[float, int]]:
        """
        Compute statistics for a single day's data.

        Parameters:
            values (np.ndarray): Array of values for the day.
            day_start (float): Start-of-day timestamp.

        Returns:
            List[Union[float, int]]: Computed statistics for the day.
        """
        if values.shape[0] == 0:
            return FinaStats.init_stats(
                day_start=day_start,
                stats_type=StatsType.INTEGRITY
            )

        nb_total = values.shape[0]
        nb_finite = np.isfinite(values).sum()

        stats = [
            nb_finite,
            nb_total,
        ]
        return [day_start] + stats

    @staticmethod
    def get_values_stats(values: np.ndarray, day_start: float) -> List[Union[float, int]]:
        """
        Compute statistics for a single day's data.

        Parameters:
            values (np.ndarray): Array of values for the day.
            day_start (float): Start-of-day timestamp.

        Returns:
            List[Union[float, int]]: Computed statistics for the day.
        """
        if values.shape[0] == 0:
            return FinaStats.init_stats(
                day_start=day_start,
                stats_type=StatsType.VALUES
            )

        nb_finite = np.isfinite(values).sum()

        stats = [
            np.nanmin(values) if nb_finite > 0 else np.nan,
            np.nanmean(values) if nb_finite > 0 else np.nan,
            np.nanmax(values) if nb_finite > 0 else np.nan
        ]
        return [day_start] + stats
