"""
Common Services for Fina Files processing.
"""
import logging
import math
import datetime as dt
from typing import List, Tuple, Union

import numpy as np
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel, OutputType
from emon_tools.emon_fina.fina_models import FinaMetaModel
from emon_tools.emon_fina.fina_models import OutputAverageEnum
from emon_tools.emon_fina.fina_models import TimeRefEnum
from emon_tools.emon_fina.fina_models import FileReaderPropsModel
from emon_tools.emon_fina.fina_utils import Utils as Ut


logging.basicConfig()
et_logger = logging.getLogger(__name__)


class FinaMeta(FinaMetaModel):
    """
    Service class to handle file-reading logic using FinaMetaModel.

    Attributes:
        meta (FinaMetaModel): Metadata describing the data file.
    """

    def calculate_nb_days(self) -> int:
        """
        Calculate the number of days covered by the data.

        Returns:
            int: Number of days.
        """
        start = dt.datetime.fromtimestamp(self.start_time, dt.timezone.utc)
        end = dt.datetime.fromtimestamp(self.end_time, dt.timezone.utc)
        delta_days = (end - start).total_seconds() / (3600 * 24)
        return math.ceil(delta_days)

    def serialize(self) -> dict:
        """
        Serialize the metadata into a dictionary.

        Returns:
            dict: Serialized metadata.
        """
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "interval": self.interval,
            "npoints": self.npoints,
            "size": self.size,
        }


class FinaOutputData:
    """Used to unify fina data result format"""
    @staticmethod
    def init_stats(
        block_size: int,
        step_start: Union[float, int] = np.nan,
        output_type: OutputType = OutputType.VALUES
    ) -> List[Union[float, int]]:
        """Initialyse stats array values."""
        result = [np.nan]
        if block_size == 1:
            return result

        if output_type == OutputType.VALUES_MIN_MAX:
            result = [np.nan, np.nan, np.nan]
        elif output_type == OutputType.TIME_SERIES:
            result = [step_start, np.nan]
        elif output_type == OutputType.TIME_SERIES_MIN_MAX:
            result = [step_start, np.nan, np.nan, np.nan]
        elif output_type == OutputType.INTEGRITY:
            result = [step_start, np.nan, np.nan]
        return result

    @staticmethod
    def get_columns(
        output_type: OutputType = OutputType.VALUES
    ) -> List[Union[float, int]]:
        """Initialyse stats array values."""
        result = ["values"]
        if output_type == OutputType.VALUES_MIN_MAX:
            result = ["min", "values", "max"]
        elif output_type == OutputType.TIME_SERIES:
            result = ["time", "values"]
        elif output_type == OutputType.TIME_SERIES_MIN_MAX:
            result = ["time", "min", "values", "max"]
        elif output_type == OutputType.INTEGRITY:
            result = ["time", "nb_finite", "nb_total"]
        return result

    @staticmethod
    def get_integrity_stats(
        values: np.ndarray,
        day_start: float
    ) -> List[Union[float, int]]:
        """
        Compute statistics for a single day's data.

        Parameters:
            values (np.ndarray): Array of values for the day.
            day_start (float): Start-of-day timestamp.

        Returns:
            List[Union[float, int]]: Computed statistics for the day.
        """
        nb_total = values.shape[0]
        nb_finite = np.isfinite(values).sum()

        stats = [
            nb_finite,
            nb_total,
        ]
        return [day_start] + stats

    @staticmethod
    def get_values_stats(
        values: np.ndarray,
        day_start: float,
        with_stats: bool = True,
        with_time: bool = True
    ) -> List[Union[float, int]]:
        """
        Compute statistics for a single day's data.

        Parameters:
            values (np.ndarray): Array of values for the day.
            day_start (float): Start-of-day timestamp.

        Returns:
            List[Union[float, int]]: Computed statistics for the day.
        """
        if values.shape[0] == 1:
            return [values]
        nb_finite = np.isfinite(values).sum()
        if with_stats:
            stats = [
                np.nanmin(values) if nb_finite > 0 else np.nan,
                np.nanmean(values) if nb_finite > 0 else np.nan,
                np.nanmax(values) if nb_finite > 0 else np.nan
            ]
        else:
            stats = [np.nanmean(values) if nb_finite > 0 else np.nan]
        if with_time:
            return [day_start] + stats
        return stats


class FileReaderProps(FileReaderPropsModel):
    """
    File reader properties for efficient reading of PHPPina data files.

    Attributes:
      - meta: FinaMetaModel instance containing file metadata.
      - search:
        FinaByTimeParamsModel instance containing user search parameters.
      - current_pos: The current read position in file points.
      - start_pos: The starting file read position.
      - window_max: Maximum valid position for current search.
      - chunk_size: Number of points to read per I/O operation.
      - remaining_points: Remaining points available in the current loop.
      - start_search: Translated search.start_time (in points).
      - window_search: Translated search.time_window (in points).
      - block_size: Ratio between search.time_interval and meta.interval.
      - current_window: Current block size for aggregation.
      - current_start/next_start: Current and next time boundaries.
    """

    def has_remaining_points(self) -> bool:
        """
        Check if there are remaining points to read.

        Returns:
            bool: True if remaining_points > 0, else False.
        """
        return self.remaining_points > 0

    def get_initial_output_step(self) -> bool:
        """
        Calculate the initial output step based on the start search value
        and interval.
        Returns:
            bool:
                The absolute value of the product of start_search and interval.
        """
        i_step = 0
        if self.start_search < 0\
                and abs(self.start_search) >= self.block_size:
            i_step = abs(round(self.start_search / self.block_size))
        return i_step

    def update_remaining_points(self) -> int:
        """
        Update the remaining points based on window_max and current_pos.

        Returns:
            int: The updated number of remaining points.
        """
        self.remaining_points = self.calc_remaining_points(
            window_max=self.window_max,
            start_pos=self.start_pos,
            current_pos=self.current_pos
        )
        return self.remaining_points

    def init_read_props(self):
        """
        Initialize reading properties:
         - Calculate start_pos and start_search.
         - Determine the search window (window_search)
         and its maximum (window_max).
         - Calculate block_size if search.time_interval > meta.interval.
        """
        # Calculate block_size: number of meta intervals
        # in one search time_interval.
        self.block_size = math.ceil(
            self.search.time_interval / self.meta.interval
        )
        # Calculate the starting file position based on search.start_time.
        self.start_pos = self.calc_start_pos(
            start_time=self.search.start_time,
            meta_npoints=self.meta.npoints,
            meta_start_time=self.meta.start_time,
            meta_interval=self.meta.interval,
        )
        self.current_pos = self.start_pos

        # Translate user search.start_time into file points.
        self.start_search = self.calc_start_search(
            start_time=self.search.start_time,
            time_interval=self.search.time_interval,
            start_pos=self.start_pos,
            meta_start_time=self.meta.start_time,
            meta_interval=self.meta.interval,
            time_ref_start=self.search.time_ref_start,
            output_average=self.search.output_average,
        )

        # Align start_pos based on start_search if needed.
        self.start_pos = self.align_start_search_and_pos(
            start_pos=self.start_pos,
            start_search=self.start_search,
            block_size=self.block_size,
            output_average=self.search.output_average,
        )
        self.current_pos = self.start_pos
        # Calculate the effective window search size.
        self.window_search = self.calc_window_search(
            time_window=self.search.time_window,
            start_search=self.start_search,
            start_pos=self.start_pos,
            meta=self.meta,
        )

        # Calculate the maximum points available in the window.
        self.window_max = self.calc_window_max(
            window_search=self.window_search,
            npoints=self.meta.npoints,
            start_pos=self.start_pos,
            start_search=self.start_search
        )

        self.remaining_points = self.calc_remaining_points(
            window_max=self.window_max,
            start_pos=self.start_pos,
            current_pos=self.current_pos
        )

    def init_step_boundaries(self):
        """
        Compute initial time boundaries for processing data.
        Uses the calculated start_pos and start_search to determine
        the current timestamp and the next available timestamp
        (in file points).
        """
        current_start, next_start = self.calc_initial_step_boundaries(
            start_pos=self.start_pos,
            start_search=self.start_search,
            meta=self.meta,
            search=self.search,
        )
        self.current_start = current_start
        self.next_start = next_start

    def update_step_boundaries(self) -> Tuple[int, int]:
        """
        Update the time boundaries for the next iteration.

        Returns:
            Tuple[int, int]: Updated (current_start, next_start).
        """
        self.current_start = self.next_start
        self.next_start = self.next_start + self.search.time_interval
        return self.current_start, self.next_start

    def calc_current_window_size(self) -> int:
        """
        Calculate the number of file points in the current window.

        Returns:
            int: Current window size (at least 1).
        """
        # Ensure the limits are within the file's time boundaries.
        limit_start = max(self.meta.start_time, self.current_start)
        limit_end = min(self.meta.end_time, self.next_start)
        self.current_window = min(
            self.block_size,
            max(
                1,
                math.ceil((limit_end - limit_start) / self.meta.interval)
            )
        )
        return self.current_window

    # --- Chunk Size Calculation Helpers ---

    @staticmethod
    def _round_up(value: int, base: int) -> int:
        return math.ceil(value / base) * base

    @staticmethod
    def _round_down(value: int, base: int) -> int:
        return max(base, math.floor(value / base) * base)

    def get_chunk_size(
        self, bypass_min: bool = False, optimized: bool = True
    ) -> int:
        """
        Compute the optimal chunk size (number of file points to read)
        for efficient I/O. The chunk size is adjusted to be a multiple of
        the current window size while respecting limits (CHUNK_SIZE_LIMIT,
        remaining_points) and an efficient minimum.

        Parameters:
            bypass_min (bool):
                If True, bypass the efficient minimum constraint.
            optimized (bool):
                If False, return exactly current_window.

        Returns:
            int: The computed chunk size.
        """
        if self.remaining_points <= 0:
            self.chunk_size = 0
            return 0

        max_allowed = min(self.CHUNK_SIZE_LIMIT, self.remaining_points)
        # Efficient minimum: round up window_max to a multiple of block_size.
        efficient_min = self._round_up(self.window_max, self.block_size)

        default_candidate = self._round_up(
            self.DEFAULT_CHUNK_SIZE, self.current_window
        )
        if not bypass_min and default_candidate < efficient_min:
            default_candidate = self._round_up(
                efficient_min,
                self.current_window
            )

        if default_candidate > max_allowed:
            default_candidate = self._round_down(
                max_allowed,
                self.current_window
            )

        fallback_candidate = self._round_down(max_allowed, self.current_window)
        if not bypass_min and fallback_candidate < efficient_min:
            fallback_candidate = min(
                self._round_up(efficient_min, self.current_window),
                fallback_candidate
            )

        # Choose candidate.
        if efficient_min <= default_candidate <= max_allowed:
            self.chunk_size = default_candidate
        else:
            self.chunk_size = fallback_candidate

        if not optimized:
            self.chunk_size = self.current_window

        return self.chunk_size

    def initialise_reader(self):
        """
        Initialize the reader properties and boundaries.
        """
        self.init_read_props()
        self.init_step_boundaries()
        self.calc_current_window_size()
        self.get_chunk_size(bypass_min=True)
        # Ensure invariants: start_pos <= current_pos <= npoints.
        assert self.start_pos <= self.current_pos <= self.meta.npoints, (
            f"Invariant violated: start_pos({self.start_pos}) <= "
            f"current_pos({self.current_pos}) <= npoints({self.meta.npoints})"
        )

    def iter_update_before(self) -> int:
        """
        Update reader properties before a read iteration.

        Returns:
            int: The chunk size to use for the current iteration.
        """
        self.update_remaining_points()
        return self.calc_current_chunk_size(
            chunk_size=self.chunk_size, remaining_points=self.remaining_points
        )

    def iter_update_after(self):
        """
        Update reader properties after a read iteration.
        Increments the current position by the size of the current chunk,
        updates step boundaries, and recalculates the window size.
        """
        # self.update_step_boundaries()
        self.calc_current_window_size()
        increment = self.calc_current_chunk_size(
            chunk_size=self.chunk_size, remaining_points=self.remaining_points
        )
        if increment == 0:
            et_logger.warning(
                "Chunk size computed as zero; terminating iteration to avoid "
                "infinite loop."
            )
            return
        self.current_pos += increment
        # Reassert state invariant.
        assert self.start_pos <= self.current_pos <= self.meta.npoints, (
            f"Invariant violated after update: start_pos({self.start_pos}) <= "
            f"current_pos({self.current_pos}) <= npoints({self.meta.npoints})"
        )

    @staticmethod
    def calc_current_chunk_size(chunk_size: int, remaining_points: int) -> int:
        """
        Calculate the effective chunk size for the current iteration.

        Returns:
            int: The minimum of the desired chunk_size
            and the remaining_points.
        """
        return min(chunk_size, remaining_points)

    # --- Utility Calculations Converting Time to File Points ---

    @staticmethod
    def calc_start_pos(
        start_time: int,
        meta_npoints: int,
        meta_start_time: int,
        meta_interval: int,
    ) -> int:
        """
        Convert a timestamp (start_time) into a file position (point index).
        """
        return max(
            0,
            min(
                meta_npoints,
                (start_time - meta_start_time) // meta_interval
            )
        )

    @staticmethod
    def get_nearest_aligned_timestamp(
        base_time: int,
        timestamp: int,
        interval: int
    ) -> int:
        """
        Calculate the nearest timestamp that is an integer
        multiple of 'interval' away from 'base_time',
        such that the result is as close as possible to 'timestamp'.

        Args:
            base_time (int):
            The reference timestamp from which valid timestamps are offset.
            timestamp (int): The timestamp that should be aligned.
            interval (int): The interval between valid timestamps (in seconds).

        Returns:
            int:
                The nearest aligned timestamp to `timestamp`
                that is computed as base_time + (n * interval),
                where n is an integer.

        Raises:
            ValueError: If interval is zero.
        """
        if interval == 0:
            raise ValueError(
                "Unable to calculate nearest aligned timestamp. "
                "Interval must be non-zero"
            )
        n = round((timestamp - base_time) / interval)
        return base_time + n * interval

    @staticmethod
    def calculate_nb_points(
        base_time: int,
        timestamp: int,
        interval: int,
        base_interval: int
    ) -> Tuple[int]:
        """
        Calculate the number of base points offset from base_time.
        """
        if interval == 0:
            raise ValueError(
                "Unable to calculate nb points from start. "
                "Interval must be non-zero"
            )
        nearest_time = FileReaderProps.get_nearest_aligned_timestamp(
            base_time=base_time,
            timestamp=timestamp,
            interval=base_interval)
        diff = nearest_time - base_time
        n = round(diff / interval)
        remainder = diff - (n * interval)
        nb_points = remainder // base_interval
        return nb_points, round(diff / base_interval)

    @staticmethod
    def calc_start_search(
        start_time: int,
        time_interval: int,
        start_pos: int,
        meta_start_time: int,
        meta_interval: int,
        time_ref_start: TimeRefEnum,
        output_average: OutputAverageEnum,
    ) -> int:
        """
        Calculate a valid search start position (in file points)
        based on the user's search start_time.
        If start_pos > 0, then start_search is simply set to start_pos.

        For time_ref_start BY_TIME, the search start is aligned using the
        utility function get_start_of_interval with start_time as reference.
        For time_ref_start BY_SEARCH:
        - If output_average is PARTIAL, the base position is used.
        - If output_average is COMPLETE, the base position is adjusted upward
            to the next complete block boundary.

        Returns:
            int: The computed search start position in file points.
        """
        block_size = math.ceil(time_interval / meta_interval)
        # If a valid starting position already exists, use it.
        if start_pos > 0:
            if output_average == OutputAverageEnum.COMPLETE:
                return (start_pos * -1) % block_size
            if output_average in (
                OutputAverageEnum.PARTIAL, OutputAverageEnum.AS_IS
            ):
                return start_pos

        # Otherwise, compute the base file position
        # corresponding to search.start_time.
        if time_ref_start == TimeRefEnum.BY_TIME:
            # Align to the start of the interval using the user's start_time.
            time_ref = Ut.get_start_of_interval(
                timestamp=start_time,
                interval=time_interval
            )
            start_search, points_ref = FileReaderProps.calculate_nb_points(
                base_time=meta_start_time,
                timestamp=time_ref,
                interval=time_interval,
                base_interval=meta_interval
            )
            # if output_average == OutputAverageEnum.COMPLETE:
            #    start_search = start_search % block_size
            if output_average == OutputAverageEnum.AS_IS:
                start_search = points_ref
        elif time_ref_start == TimeRefEnum.BY_SEARCH:
            start_search, points_ref = FileReaderProps.calculate_nb_points(
                base_time=meta_start_time,
                timestamp=start_time,
                interval=time_interval,
                base_interval=meta_interval
            )
            # if output_average == OutputAverageEnum.COMPLETE:
            #    start_search = start_search % block_size
            if output_average == OutputAverageEnum.AS_IS:
                start_search = points_ref
        else:
            raise ValueError(
                "Unable to calculate start_search. "
                "Invalid time_ref_start value."
            )

        return start_search

    @staticmethod
    def align_start_search_and_pos(
        start_pos: int,
        start_search: int,
        block_size: int,
        output_average: OutputAverageEnum
    ) -> int:
        """
        Adjust start_pos if the search start is earlier than expected.
        (The original condition was rarely met; adjust as needed.)
        """
        if start_search < 0\
                and output_average == OutputAverageEnum.COMPLETE:
            start_pos = max(
                0,
                start_search % block_size
            )
        return start_pos

    @staticmethod
    def calc_window_search(
        time_window: int,
        start_search: int,
        start_pos: int,
        meta: FinaMetaModel,
    ) -> int:
        """
        Convert the user-defined time window into a number of file points.
        """
        if time_window == 0:
            window_search = meta.npoints - start_pos
        else:
            window_search = (start_search // meta.interval) + (time_window //
                                                               meta.interval)
        return window_search

    @staticmethod
    def calc_window_max(
        window_search: int,
        npoints: int,
        start_pos: int,
        start_search: int
    ) -> int:
        """
        Calculate the maximum file points available for the current search.
        """
        if window_search > 0:
            window_max = window_search - abs(start_search)
        else:
            window_max = max(0, npoints - start_pos)
        return window_max

    @staticmethod
    def calc_remaining_points(
        window_max: int,
        start_pos: int,
        current_pos: int
    ) -> int:
        """
        Calculate the number of remaining file points in the current window.
        """
        return max(0, window_max - (current_pos - start_pos))

    @staticmethod
    def calc_time_correction(
        time_ref: int,
        start_pos: int,
        meta_start_time: int,
        meta_interval: int,
        window_max: int,
    ) -> int:
        """
        Calculate a correction value for aligning the time boundaries.
        This correction is based on the difference between the reference time
        and the meta start time.
        """
        ref_low = (time_ref - meta_start_time) % meta_interval
        ref_high = meta_interval - ref_low
        if ref_low == 0:
            correction = start_pos
        elif ref_low > ref_high:
            if time_ref <= meta_start_time:
                correction = min(start_pos, (time_ref - meta_start_time) +
                                 ref_high)
            else:
                correction = min(window_max, (time_ref - meta_start_time) +
                                 ref_high)
        else:
            if time_ref <= meta_start_time:
                correction = min(start_pos, (time_ref - meta_start_time) -
                                 ref_low)
            else:
                correction = min(window_max, (time_ref - meta_start_time) -
                                 ref_low)
        return correction

    @staticmethod
    def calc_initial_step_boundaries(
        start_pos: int,
        start_search: int,
        meta: FinaMetaModel,
        search: FinaByTimeParamsModel,
    ) -> Tuple[int, int]:
        """
        Compute the initial time boundaries (in file points)
        for the first read step.

        Returns:
            Tuple[int, int]: (current_start, next_start)
        """
        if search.start_time >= meta.start_time:
            current_start = meta.start_time + (start_pos * meta.interval)
        else:
            current_start = meta.start_time + (start_search * meta.interval)
        next_start = current_start + search.time_interval
        return current_start, next_start
