"""Fina Utils unit tests module"""
from unittest.mock import patch
import datetime as dt
import pytest
from emon_tools.utils import Utils


class TestUtils:
    """Unit tests for the Utils class."""

    def test_is_str(self):
        """Test is_str method."""
        assert Utils.is_str("hello") is True
        assert Utils.is_str("") is True
        assert Utils.is_str("", not_empty=True) is False
        assert Utils.is_str(123) is False

    def test_is_list(self):
        """Test is_list method."""
        assert Utils.is_list(["hello"]) is True
        assert Utils.is_list([]) is True
        assert Utils.is_list([], not_empty=True) is False
        assert Utils.is_list("not a list") is False

    def test_is_dict(self):
        """Test is_dict method."""
        assert Utils.is_dict({"key": "value"}) is True
        assert Utils.is_dict({}) is True
        assert Utils.is_dict({}, not_empty=True) is False
        assert Utils.is_dict("not a dict") is False

    def test_is_set(self):
        """Test is_set method."""
        assert Utils.is_set({"key", "value"}) is True
        assert Utils.is_set(set()) is True
        assert Utils.is_set(set(), not_empty=True) is False
        assert Utils.is_set("not a dict") is False

    def test_is_tuple(self):
        """Test is_tuple method."""
        assert Utils.is_tuple(("key", "value")) is True
        assert Utils.is_tuple(tuple()) is True
        assert Utils.is_tuple((1, )) is True
        assert Utils.is_tuple(tuple(), not_empty=True) is False
        assert Utils.is_tuple("not a dict") is False

    def test_validate_number_valid(self):
        """Test validate_number with valid input."""
        assert Utils.validate_number(10, "test_field", positive=True) == 10
        assert Utils.validate_number(10.2, "test_field", positive=True) == 10.2
        assert Utils.validate_number(0, "test_field", non_neg=True) == 0

    @pytest.mark.parametrize("value", ["string", None])
    def test_validate_number_invalid(self, value):
        """Test validate_number raises ValueError for invalid input."""
        with pytest.raises(ValueError, match="test_field must be a number."):
            Utils.validate_number(value, "test_field")

    @pytest.mark.parametrize("value", [-1, 0, -1.1])
    def test_validate_number_positive_invalid(self, value):
        """Test validate_number raises ValueError for invalid input."""
        match_error = "test_field must be a positive number."
        with pytest.raises(ValueError, match=match_error):
            Utils.validate_number(value, "test_field", positive=True)

    @pytest.mark.parametrize("value", [-1, -1.1])
    def test_validate_number_non_neg_invalid(self, value):
        """Test validate_number raises ValueError for invalid input."""
        match_error = "test_field must be a non-negative number."
        with pytest.raises(ValueError, match=match_error):
            Utils.validate_number(value, "test_field", non_neg=True)

    def test_validate_integer_valid(self):
        """Test validate_integer with valid input."""
        assert Utils.validate_integer(10, "test_field", positive=True) == 10
        assert Utils.validate_integer(1, "test_field", positive=True) == 1

    @pytest.mark.parametrize("value", ["string", None])
    def test_validate_integer_invalid(self, value):
        """Test validate_integer raises ValueError for invalid input."""
        with pytest.raises(ValueError, match="test_field must be an integer."):
            Utils.validate_integer(value, "test_field")

    @pytest.mark.parametrize("value", [-1, 0, -10])
    def test_validate_integer_positive_invalid(self, value):
        """Test validate_integer raises ValueError for invalid input."""
        match_error = "test_field must be a positive integer."
        with pytest.raises(ValueError, match=match_error):
            Utils.validate_integer(value, "test_field", positive=True)

    @pytest.mark.parametrize("value", [-1, -10])
    def test_validate_integer_non_neg_invalid(self, value):
        """Test validate_integer raises ValueError for invalid input."""
        match_error = "test_field must be a non-negative integer."
        with pytest.raises(ValueError, match=match_error):
            Utils.validate_integer(value, "test_field", non_neg=True)

    def test_validate_timestamp_valid(self):
        """Test validate_timestamp with valid input."""
        assert Utils.validate_timestamp(0, "test_field") == 0

    @pytest.mark.parametrize("value", [-1])
    def test_validate_timestamp_invalid(self, value):
        """Test validate_timestamp raises ValueError for invalid input."""
        match_error = "test_field timestamp must be a non-negative number."
        with pytest.raises(ValueError, match=match_error):
            Utils.validate_timestamp(value, "test_field")

    @pytest.mark.parametrize("value", ["string", None])
    def test_validate_timestamp_type_invalid(self, value):
        """Test validate_timestamp raises ValueError for invalid input."""
        match_error = "test_field timestamp must be a number."
        with pytest.raises(ValueError, match=match_error):
            Utils.validate_timestamp(value, "test_field")

    @pytest.mark.parametrize("value", [2147480001, 9999999999])
    def test_validate_timestamp_invalid_value(self, value):
        """Test validate_timestamp raises ValueError for invalid input."""
        match_error = ("test_field must be a valid UNIX timestamp "
                       "between 0 and 2147480000.")
        with pytest.raises(ValueError, match=match_error):
            Utils.validate_timestamp(value, "test_field")

    @patch("emon_tools.utils.dt.datetime")
    def test_validate_timestamp_conversion_error(self, mock_datetime):
        """
        Test validate_timestamp raises ValueError
        when conversion to datetime fails.
        """
        # Configure the mock to raise a ValueError when fromtimestamp is called
        mock_datetime.fromtimestamp.side_effect = ValueError(
            "Invalid timestamp")

        match_error = "test_field must be a valid UNIX timestamp."
        with pytest.raises(ValueError, match=match_error):
            Utils.validate_timestamp(1000000000, "test_field")

    def test_get_start_day_valid(self):
        """Test get_start_day with a valid timestamp."""
        timestamp = 1700000000  # Corresponds to a known date
        result = Utils.get_start_day(timestamp)
        expected = dt.datetime(
            2023, 11, 14, tzinfo=dt.timezone.utc).timestamp()
        result = Utils.get_start_day(timestamp, timezone=None)
        expected = dt.datetime(
            2023, 11, 14).timestamp()
        assert result == expected

    def test_get_start_day_edge_case(self):
        """Test get_start_day with epoch timestamp."""
        timestamp = 0  # Epoch time
        result = Utils.get_start_day(timestamp)
        expected = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc).timestamp()
        assert result == expected

    def test_get_string_datetime_from_timestamp_valid(self):
        """Test get_string_datetime_from_timestamp with valid input."""
        # Corresponds to "2023-11-14 02:13:20"
        result = Utils.get_string_datetime_from_timestamp(1700000000)
        assert result == '2023-11-14 22:13:20'

        # Corresponds to "2023-11-14 02:13:20"
        result = Utils.get_string_datetime_from_timestamp(1700000000 + 3600)
        assert result == '2023-11-14 23:13:20'

    def test_get_string_datetime_from_timestamp_invalid_timestamp(self):
        """Test get_string_datetime_from_timestamp with invalid  timestamp."""
        match_error = "timestamp timestamp must be a non-negative number."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_string_datetime_from_timestamp(-1)

    def test_get_utc_datetime_from_string_valid(self):
        """Test get_utc_datetime_from_string with valid input."""
        date_str = "2023-11-14 10:00:00"
        result = Utils.get_utc_datetime_from_string(date_str)
        expected = dt.datetime(2023, 11, 14, 10, 0, 0, tzinfo=dt.timezone.utc)
        assert result == expected

    def test_get_utc_datetime_from_string_invalid_format(self):
        """Test get_utc_datetime_from_string with invalid date format."""
        date_str = "14/11/2023 10:00:00"
        match_error = "Error parsing date '14/11/2023 10:00:00'"
        with pytest.raises(ValueError, match=match_error):
            Utils.get_utc_datetime_from_string(date_str)

    def test_get_utc_datetime_from_string_invalid_type(self):
        """Test get_utc_datetime_from_string with non-string input."""
        match_error = "The input date-time value must be a string."
        with pytest.raises(TypeError, match=match_error):
            Utils.get_utc_datetime_from_string(12345)

    def test_get_dates_interval_from_timestamp_valid(self):
        """Test get_dates_interval_from_timestamp with valid inputs."""
        start = 1700000000  # Corresponds to "2023-11-14 02:13:20"
        window = 3600  # 1 hour
        date_format = "%Y-%m-%d %H:%M:%S"
        result = Utils.get_dates_interval_from_timestamp(
            start, window, date_format)
        expected = ("2023-11-14 22:13:20", "2023-11-14 23:13:20")
        assert result == expected

    def test_get_dates_interval_from_timestamp_invalid_start(self):
        """
        Test get_dates_interval_from_timestamp
        raises ValueError for invalid start.
        """
        match_error = "'start' and 'window' must be integers."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_dates_interval_from_timestamp("invalid", 3600)

    def test_get_dates_interval_from_timestamp_negative_start(self):
        """
        Test get_dates_interval_from_timestamp
        raises ValueError for negative start.
        """
        match_error = "'start' and 'window' must be non-negative."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_dates_interval_from_timestamp(-1, 3600)

    def test_get_dates_interval_from_timestamp_negative_window(self):
        """
        Test get_dates_interval_from_timestamp
        raises ValueError for negative window.
        """
        match_error = "'start' and 'window' must be non-negative."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_dates_interval_from_timestamp(1700000000, -3600)

    def test_get_dates_interval_from_timestamp_invalid_window(self):
        """
        Test get_dates_interval_from_timestamp
        raises ValueError for invalid window.
        """
        match_error = "'start' and 'window' must be integers."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_dates_interval_from_timestamp(1700000000, "invalid")

    def test_get_window_by_dates_valid(self):
        """Test get_window_by_dates with valid inputs."""
        start_date = "2023-11-14 10:00:00"
        end_date = "2023-11-14 12:00:00"
        interval = 3600  # 1 hour
        result = Utils.get_window_by_dates(start_date, end_date, interval)
        expected_start_timestamp = int(
            dt.datetime(
                2023, 11, 14, 10, 0, 0, tzinfo=dt.timezone.utc).timestamp())
        expected_window_size = 7200  # 2 hours in seconds
        assert result == (expected_start_timestamp, expected_window_size)

    def test_get_window_by_dates_invalid_date_range(self):
        """
        Test get_window_by_dates raises ValueError for invalid date range.
        """
        start_date = "2023-11-14 12:00:00"
        end_date = "2023-11-14 10:00:00"
        interval = 3600  # 1 hour
        match_error = "The start date must be earlier than the end date."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_window_by_dates(start_date, end_date, interval)

    def test_get_window_by_dates_invalid_interval(self):
        """Test get_window_by_dates raises ValueError for invalid interval."""
        start_date = "2023-11-14 10:00:00"
        end_date = "2023-11-14 12:00:00"
        interval = -3600  # Negative interval
        match_error = "interval must be a positive integer."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_window_by_dates(start_date, end_date, interval)

    def test_get_window_by_dates_invalid_start_date_format(self):
        """
        Test get_window_by_dates raises ValueError
        for invalid start date format.
        """
        start_date = "14/11/2023 10:00:00"
        end_date = "2023-11-14 12:00:00"
        interval = 3600  # 1 hour
        match_error = "Error parsing date '14/11/2023 10:00:00'"
        with pytest.raises(ValueError, match=match_error):
            Utils.get_window_by_dates(start_date, end_date, interval)

    def test_get_window_by_dates_invalid_end_date_format(self):
        """
        Test get_window_by_dates raises ValueError
        for invalid end date format.
        """
        start_date = "2023-11-14 10:00:00"
        end_date = "14/11/2023 12:00:00"
        interval = 3600  # 1 hour
        match_error = "Error parsing date '14/11/2023 12:00:00'"
        with pytest.raises(ValueError, match=match_error):
            Utils.get_window_by_dates(start_date, end_date, interval)

    def test_get_window_by_dates_invalid_interval_type(self):
        """
        Test get_window_by_dates raises ValueError for non-integer interval.
        """
        start_date = "2023-11-14 10:00:00"
        end_date = "2023-11-14 12:00:00"
        interval = "3600"  # Interval as string
        match_error = "interval must be an integer."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_window_by_dates(start_date, end_date, interval)

    def test_get_dates_by_window_valid(self):
        """Test get_dates_by_window with valid inputs."""
        start = 1700000000  # Corresponds to "2023-11-14 22:13:20"
        window = 3600  # 1 hour
        result = Utils.get_dates_by_window(start, window)
        expected_start = dt.datetime(
            2023, 11, 14, 22, 13, 20, tzinfo=dt.timezone.utc)
        expected_end = dt.datetime(
            2023, 11, 14, 23, 13, 20, tzinfo=dt.timezone.utc)
        assert result == (expected_start, expected_end)

    def test_get_dates_by_window_invalid_start(self):
        """Test get_dates_by_window raises ValueError for invalid start."""
        match_error = "'start' and 'window' must be integers."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_dates_by_window("invalid", 3600)

    def test_get_dates_by_window_negative_start(self):
        """Test get_dates_by_window raises ValueError for negative start."""
        match_error = "'start' and 'window' must be non-negative."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_dates_by_window(-1, 3600)

    def test_get_dates_by_window_negative_window(self):
        """Test get_dates_by_window raises ValueError for negative window."""
        match_error = "'start' and 'window' must be non-negative."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_dates_by_window(1700000000, -3600)

    def test_get_dates_by_window_invalid_window(self):
        """Test get_dates_by_window raises ValueError for invalid window."""
        match_error = "'start' and 'window' must be integers."
        with pytest.raises(ValueError, match=match_error):
            Utils.get_dates_by_window(1700000000, "invalid")
