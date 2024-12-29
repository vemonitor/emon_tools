"""Fina Utils Module"""

from enum import Enum
from typing import Tuple
from typing import Optional
from typing import Union
import datetime as dt
import numpy as np


class FillNanMethod(Enum):
    """Remove Nan Method Enum"""
    FORWARD = "forward"
    INTERPOLATE = "interpolate"


class Utils:
    """Utility class providing validation and other methods."""

    @staticmethod
    def validate_number(
        value: Union[int, float],
        field_name: str,
        positive: bool = False,
        non_neg: bool = False
    ) -> int:
        """
        Validate that a value is a number, with optional constraints.

        Parameters:
            value (Union[int, float]): The value to validate.
            field_name (str): The name of the field for error messages.
            positive (bool, optional):
                If True, ensures the value is strictly positive. Defaults to False.
            non_neg (bool, optional):
                If True, ensures the value is non-negative. Defaults to False.

        Returns:
            Union[int, float]: The validated value.

        Raises:
            ValueError: If the value is not a number or does not meet the specified constraints.
        """
        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_name} must be a number.")
        if positive and value <= 0:
            raise ValueError(f"{field_name} must be a positive number.")
        if non_neg and value < 0:
            raise ValueError(f"{field_name} must be a non-negative number.")
        return value

    @staticmethod
    def validate_integer(
        value: int,
        field_name: str,
        positive: bool = False,
        non_neg: bool = False
    ) -> int:
        """
        Validate that a value is an integer, with optional constraints.

        Parameters:
            value (int): The value to validate.
            field_name (str): The name of the field for error messages.
            positive (bool, optional):
                If True, ensures the value is strictly positive. Defaults to False.
            non_neg (bool, optional):
                If True, ensures the value is non-negative. Defaults to False.

        Returns:
            int: The validated integer.

        Raises:
            ValueError: If the value is not an integer or does not meet the specified constraints.
        """
        if not isinstance(value, int):
            raise ValueError(f"{field_name} must be an integer.")
        if positive and value <= 0:
            raise ValueError(f"{field_name} must be a positive integer.")
        if non_neg and value < 0:
            raise ValueError(f"{field_name} must be a non-negative integer.")
        return value

    @staticmethod
    def validate_timestamp(
        timestamp: Union[int, float],
        field_name: str
    ) -> Union[int, float]:
        """
        Validate whether a given value is a valid UNIX timestamp.

        Parameters:
            timestamp (Union[int, float]): The input to validate.
            field_name (str): The name of the field for error messages.

        Returns:
            Union[int, float]: The validated timestamp.

        Raises:
            ValueError:
                If the input is not a positive number or exceeds the valid UNIX timestamp range.
        """
        # Validate the timestamp is a number and non-negative
        Utils.validate_number(timestamp, f"{field_name} timestamp", non_neg=True)

        # Validate the timestamp is within a reasonable range for UNIX timestamps
        max_timestamp = 2147480000  # Near the year 2038 problem threshold
        if not 0 <= timestamp <= max_timestamp:
            raise ValueError(
                f"{field_name} must be a valid UNIX timestamp between 0 and {max_timestamp}."
            )

        # Attempt conversion to datetime to ensure validity
        try:
            dt.datetime.fromtimestamp(timestamp)
        except (ValueError, OSError) as e:
            raise ValueError(
                f"{field_name} must be a valid UNIX timestamp."
            ) from e

        return timestamp

    @staticmethod
    def get_start_day(timestamp: Union[int, float]) -> float:
        """
        Get the start-of-day timestamp for a given timestamp in UTC.

        Parameters:
            timestamp (Union[int, float]): The input UNIX timestamp.

        Returns:
            float: The start-of-day timestamp in UTC.
        """
        dt_point = dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc)
        start_of_day = dt.datetime(
            dt_point.year, dt_point.month, dt_point.day, tzinfo=dt.timezone.utc
        )
        return start_of_day.timestamp()

    @staticmethod
    def get_utc_datetime_from_string(dt_value: str,
                                     date_format: str = "%Y-%m-%d %H:%M:%S"
                                     ) -> dt.datetime:
        """
        Convert a date string to a UTC datetime object.

        Parameters:
            dt_value (str): The date-time string to parse.
            date_format (str): The format of the date-time string.
                Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            dt.datetime: A timezone-aware datetime object in UTC.

        Raises:
            TypeError: If the input is not a string.
            ValueError: If parsing fails due to an invalid format or value.
        """
        if not isinstance(dt_value, str):
            raise TypeError("The input date-time value must be a string.")

        try:
            naive_datetime = dt.datetime.strptime(dt_value, date_format)
            return naive_datetime.replace(tzinfo=dt.timezone.utc)
        except ValueError as e:
            raise ValueError(
                f"Error parsing date '{dt_value}' with the format '{date_format}': {e}"
            ) from e

    @staticmethod
    def get_dates_interval_from_timestamp(
        start: int,
        window: int,
        date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> Tuple[str, str]:
        """
        Generate formatted start and end date strings based on a start timestamp and window size.

        Parameters:
            start (int): The starting UNIX timestamp in seconds.
            window (int): The duration of the interval in seconds.
            date_format (str):
                Format string for the output datetime. Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            Tuple[str, str]: A tuple containing the formatted start and end dates as strings.

        Raises:
            ValueError: If `start` or `window` are not integers or are negative.
        """
        if not isinstance(start, int) or not isinstance(window, int):
            raise ValueError("'start' and 'window' must be integers.")
        if start < 0 or window < 0:
            raise ValueError("'start' and 'window' must be non-negative.")

        start_dt = dt.datetime.fromtimestamp(start, tz=dt.timezone.utc)
        end_dt = start_dt + dt.timedelta(seconds=window)

        return start_dt.strftime(date_format), end_dt.strftime(date_format)

    @staticmethod
    def get_window_by_dates(start_date: str,
                            end_date: str,
                            interval: int,
                            date_format: str = "%Y-%m-%d %H:%M:%S"
                            ) -> Tuple[int, int]:
        """
        Calculate the start timestamp and the number
        of intervals (window size) based on a date range.

        Parameters:
            start_date (str): The start date as a string.
            end_date (str): The end date as a string.
            interval (int): The time interval in seconds for each data point.
            date_format (str):
                The format of the input date strings. Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            Tuple[int, int]:
                - Start timestamp (in seconds since the Unix epoch).
                - Window size as the number of intervals.

        Raises:
            ValueError: If the `start_date` is later than or equal to `end_date`.
            ValueError: If the `interval` is not a positive integer.
        """
        # Convert date strings to UTC datetime objects
        start_dt = Utils.get_utc_datetime_from_string(start_date, date_format)
        end_dt = Utils.get_utc_datetime_from_string(end_date, date_format)

        # Validate date range
        if start_dt >= end_dt:
            raise ValueError("The start date must be earlier than the end date.")

        # Validate interval
        interval = Utils.validate_integer(interval, 'interval', positive=True)

        # Calculate start timestamp and window size
        start_timestamp = int(start_dt.timestamp())
        # ( / interval)
        window_size = int(end_dt.timestamp() - start_timestamp)

        return start_timestamp, window_size

    @staticmethod
    def get_dates_by_window(start: int,
                            window: int
                            ) -> Tuple[dt.datetime, dt.datetime]:
        """
        Calculate start and end UTC datetimes based on a start timestamp and window size.

        Parameters:
            start (int): Start timestamp in seconds since epoch.
            window (int): Duration of the window in seconds.

        Returns:
            Tuple[dt.datetime, dt.datetime]: Start and end datetimes as UTC datetime objects.

        Raises:
            ValueError: If `start` or `window` is invalid.
        """
        if not isinstance(start, int) or not isinstance(window, int):
            raise ValueError("'start' and 'window' must be integers.")
        if start < 0 or window < 0:
            raise ValueError("'start' and 'window' must be non-negative.")

        # Convert start timestamp to a datetime object in UTC
        start_dt = dt.datetime.fromtimestamp(start, tz=dt.timezone.utc)
        # Calculate end datetime by adding the window size
        end_dt = start_dt + dt.timedelta(seconds=window)

        return start_dt, end_dt

    @staticmethod
    def filter_values_by_range(
        values: np.ndarray,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None
    ) -> np.ndarray:
        """
        Filter an array of values by replacing those outside a specified range with NaN.

        Parameters:
            values (np.ndarray): The ndarray of values to filter.
            min_value (Optional[Union[int, float]]):
                Minimum valid value. Values below this will be set to NaN.
            max_value (Optional[Union[int, float]]):
                Maximum valid value. Values above this will be set to NaN.

        Returns:
            np.ndarray: The filtered array with values outside the specified range replaced by NaN.

        Raises:
            ValueError: If `values` is not a numpy ndarray.
            ValueError: If `min_value` is greater than or equal to `max_value`.

        Example:
            >>> values = np.array([1, 2, 3, 4, 5])
            >>> filter_values_by_range(values, min_value=2, max_value=4)
            array([nan,  2.,  3.,  4., nan])
        """
        if not isinstance(values, np.ndarray):
            raise ValueError("Values must be a numpy ndarray.")

        if min_value is not None and max_value is not None:
            if min_value >= max_value:
                raise ValueError("`min_value` must be less than `max_value`.")

        mask = np.zeros_like(values, dtype=bool)
        if min_value is not None:
            mask |= values < min_value
        if max_value is not None:
            mask |= values > max_value

        values = values.astype(float)  # Ensure NaN compatibility
        values[mask] = np.nan

        return values


class NpFillNan:
    """Class for cleaning and filling NaN values in NumPy arrays."""

    @staticmethod
    def forward_fill_nan(raw_array: np.ndarray) -> np.ndarray:
        """
        Forward fill NaN values in a 1D array using the previous non-NaN value.

        Parameters:
            raw_array (np.ndarray): Input array with NaN values.

        Returns:
            np.ndarray: Array with NaN values forward-filled.
        """
        if raw_array.size > 0:
            valid_indices = np.arange(len(raw_array))
            valid_indices[np.isnan(raw_array)] = 0
            valid_indices = np.maximum.accumulate(valid_indices)
            raw_array = raw_array[valid_indices]

        return raw_array

    @staticmethod
    def interpolate_fill_nan(raw_array: np.ndarray) -> np.ndarray:
        """
        Interpolate to fill NaN values in a 1D array.

        Parameters:
            raw_array (np.ndarray): Input array with NaN values.

        Returns:
            np.ndarray: Array with NaN values interpolated.
        """
        if raw_array.size > 0:
            mask = np.isnan(raw_array)
            if mask.any():
                raw_array[mask] = np.interp(
                    np.flatnonzero(mask),
                    np.flatnonzero(~mask),
                    raw_array[~mask]
                )

        return raw_array

    @staticmethod
    def fill_nan_values(
        raw_array: np.ndarray,
        method: FillNanMethod = FillNanMethod.INTERPOLATE,
        fill_before: bool = True,
        fill_between: bool = True,
        fill_after: bool = True
    ) -> np.ndarray:
        """
        Handle NaN values in an array based on specified regions and method.

        Parameters:
            raw_array (np.ndarray):
                Input array with NaN values.
            method (FillNanMethod):
                Method to handle NaN values (INTERPOLATE or FORWARD).
            fill_before (bool):
                Whether to fill NaN values before the first non-NaN value.
            fill_between (bool):
                Whether to fill NaN values between
                the first and last non-NaN values.
            fill_after (bool):
                Whether to fill NaN values after the last non-NaN value.

        Returns:
            np.ndarray: A copy of the input array with NaN values handled.
        """
        if raw_array.size == 0:
            return raw_array.copy()

        # Create a copy of the input array to avoid modifying the original
        result_array = raw_array.copy()

        # Identify finite (non-NaN) values
        finite_mask = np.isfinite(result_array)

        # If no non-NaN values, return the array as is
        if not finite_mask.any():
            return result_array

        # Index of the first non-NaN value
        first_valid_index = np.argmax(finite_mask)
        # Index of the last non-NaN value
        last_valid_index = len(result_array) - np.argmax(finite_mask[::-1]) - 1

        # Fill before the first non-NaN value
        if fill_before and first_valid_index > 0:
            result_array[:first_valid_index] = result_array[first_valid_index]

        # Fill between the first and last non-NaN values
        if fill_between:
            between_slice = result_array[first_valid_index:last_valid_index + 1]
            if method == FillNanMethod.FORWARD:
                result_array[first_valid_index:last_valid_index + 1] = NpFillNan.forward_fill_nan(
                    between_slice)
            elif method == FillNanMethod.INTERPOLATE:
                result_array[first_valid_index:last_valid_index + 1] = NpFillNan.interpolate_fill_nan(
                    between_slice)

        # Fill after the last non-NaN value
        if fill_after and last_valid_index < len(result_array) - 1:
            result_array[last_valid_index + 1:] = result_array[last_valid_index]

        return result_array
