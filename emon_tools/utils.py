"""Fina Utils Module"""
from typing import Any, Optional
from typing import Tuple
from typing import Union
import datetime as dt


class Utils:
    """Utility class providing validation and other methods."""

    @staticmethod
    def is_str(text: str, not_empty=False) -> bool:
        """
        Test if text is a string.

        :Example :
            >>> Utils.is_str(text='hello')
            >>> True
        :param text: str: Value to test.
        :return: bool: True if value is valid string object.
        """
        result = isinstance(text, str)
        if not_empty:
            result = result is True and len(text.strip()) > 0
        return result

    @staticmethod
    def is_list(data: Any, not_empty: bool = False) -> bool:
        """
        Test if data is a list.

        :Example :
            >>> Utils.is_list(data=['hello'])
            >>> True
        :param data: Any: Value to test.
        :return: bool: True if value is valid list object.
        """
        result = isinstance(data, list)
        if not_empty:
            result = result is True and len(data) > 0
        return result

    @staticmethod
    def is_dict(data: Any, not_empty: bool = False) -> bool:
        """
        Test if data is a dict.

        :Example :
            >>> Utils.is_dict(data=['hello'])
            >>> True
        :param data: Any: Value to test.
        :return: bool: True if value is valid dict object.
        """
        result = isinstance(data, dict)
        if not_empty:
            result = result is True and len(data) > 0
        return result

    @staticmethod
    def is_set(data: Any, not_empty: bool = False) -> bool:
        """
        Test if data is a set.

        :Example :
            >>> Utils.is_set(data=['hello'])
            >>> True
        :param data: Any: Value to test.
        :return: bool: True if value is valid set object.
        """
        result = isinstance(data, set)
        if not_empty:
            result = result is True and len(data) > 0
        return result

    @staticmethod
    def is_tuple(data: Any, not_empty: bool = False) -> bool:
        """
        Test if data is a set.

        :Example :
            >>> Utils.is_set(data=['hello'])
            >>> True
        :param data: Any: Value to test.
        :return: bool: True if value is valid set object.
        """
        result = isinstance(data, tuple)
        if not_empty:
            result = result is True and len(data) > 0
        return result

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
                If True, ensures the value is strictly positive.
                Defaults to False.
            non_neg (bool, optional):
                If True, ensures the value is non-negative. Defaults to False.

        Returns:
            Union[int, float]: The validated value.

        Raises:
            ValueError: If the value is not a number
            or does not meet the specified constraints.
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
                If True, ensures the value is strictly positive.
                Defaults to False.
            non_neg (bool, optional):
                If True, ensures the value is non-negative. Defaults to False.

        Returns:
            int: The validated integer.

        Raises:
            ValueError: If the value is not an integer
            or does not meet the specified constraints.
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
                If the input is not a positive number
                or exceeds the valid UNIX timestamp range.
        """
        # Validate the timestamp is a number and non-negative
        Utils.validate_number(
            timestamp, f"{field_name} timestamp", non_neg=True)

        # Validate the timestamp is within
        # a reasonable range for UNIX timestamps
        max_timestamp = 2147480000  # Near the year 2038 problem threshold
        if not 0 <= timestamp <= max_timestamp:
            raise ValueError(
                f"{field_name} must be a valid UNIX timestamp "
                f"between 0 and {max_timestamp}."
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
    def get_utc_timestamp(timestamp: Union[int, float]) -> float:
        """
        Get the start-of-day timestamp for a given timestamp in UTC.

        Parameters:
            timestamp (Union[int, float]): The input UNIX timestamp.

        Returns:
            float: The start-of-day timestamp in UTC.
        """
        dt_point = dt.datetime.fromtimestamp(timestamp)
        dt_point = dt_point.replace(tzinfo=dt.timezone.utc)
        return dt_point.timestamp()

    @staticmethod
    def get_start_day(
        timestamp: Union[int, float],
        timezone: Optional[dt.timezone] = dt.timezone.utc
    ) -> float:
        """
        Get the start-of-day timestamp for a given timestamp in UTC.

        Parameters:
            timestamp (Union[int, float]): The input UNIX timestamp.

        Returns:
            float: The start-of-day timestamp in UTC.
        """
        dt_point = dt.datetime.fromtimestamp(timestamp)
        start_of_day = dt.datetime(
            dt_point.year, dt_point.month, dt_point.day
        )
        if isinstance(timezone, dt.timezone):
            return Utils.get_utc_timestamp(start_of_day.timestamp())
        return start_of_day.timestamp()

    @staticmethod
    def get_string_datetime_from_timestamp(
        timestamp: str,
        timezone: Optional[dt.timezone] = dt.timezone.utc,
        date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> dt.datetime:
        """Get string representation of UTC timestamp."""
        timestamp = Utils.validate_timestamp(timestamp, "timestamp")

        if isinstance(timezone, dt.timezone):
            result = dt.datetime.fromtimestamp(
                timestamp,
                tz=timezone
            )
        else:
            result = dt.datetime.fromtimestamp(timestamp)
        return result.strftime(date_format)

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
                f"Error parsing date '{dt_value}' "
                f"with the format '{date_format}': {e}"
            ) from e

    @staticmethod
    def get_dates_interval_from_timestamp(
        start: int,
        window: int,
        date_format: str = "%Y-%m-%d %H:%M:%S"
    ) -> Tuple[str, str]:
        """
        Generate formatted start and end date strings
        based on a start timestamp and window size.

        Parameters:
            start (int): The starting UNIX timestamp in seconds.
            window (int): The duration of the interval in seconds.
            date_format (str):
                Format string for the output datetime.
                Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            Tuple[str, str]:
                A tuple containing the formatted
                start and end dates as strings.

        Raises:
            ValueError: If `start` or `window`
            are not integers or are negative.
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
                The format of the input date strings.
                Defaults to "%Y-%m-%d %H:%M:%S".

        Returns:
            Tuple[int, int]:
                - Start timestamp (in seconds since the Unix epoch).
                - Window size as the number of intervals.

        Raises:
            ValueError:
                If the `start_date` is later than or equal to `end_date`.
            ValueError:
                If the `interval` is not a positive integer.
        """
        # Convert date strings to UTC datetime objects
        start_dt = Utils.get_utc_datetime_from_string(start_date, date_format)
        end_dt = Utils.get_utc_datetime_from_string(end_date, date_format)

        # Validate date range
        if start_dt >= end_dt:
            raise ValueError(
                "The start date must be earlier than the end date.")

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
        Calculate start and end UTC datetimes
        based on a start timestamp and window size.

        Parameters:
            start (int): Start timestamp in seconds since epoch.
            window (int): Duration of the window in seconds.

        Returns:
            Tuple[dt.datetime, dt.datetime]:
                Start and end datetimes as UTC datetime objects.

        Raises:
            ValueError: If `start` or `window` is invalid.
        """
        if not isinstance(start, int) or not isinstance(window, int):
            raise ValueError("'start' and 'window' must be integers.")
        if start < 0 or window < 0:
            raise ValueError("'start' and 'window' must be non-negative.")

        # Convert start timestamp to a datetime object in UTC
        start_dt = dt.datetime.fromtimestamp(start, tz=dt.timezone.utc)
        start_dt.replace(tzinfo=dt.timezone.utc)
        # Calculate end datetime by adding the window size
        end_dt = start_dt + dt.timedelta(seconds=window)

        return start_dt, end_dt
