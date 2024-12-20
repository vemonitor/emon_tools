"""Fina Utils unit tests module"""
import datetime as dt
import pytest
from emon_tools.fina_utils import Utils

class TestUtils:
    """Unit tests for the Utils class."""

    def test_validate_positive_number_valid(self):
        """Test validate_positive_number with valid input."""
        assert Utils.validate_positive_number(10, "test_field") == 10
        assert Utils.validate_positive_number(10.2, "test_field") == 10.2

    @pytest.mark.parametrize("value", [-1, 0, "string", None])
    def test_validate_positive_number_invalid(self, value):
        """Test validate_positive_number raises ValueError for invalid input."""
        with pytest.raises(ValueError, match="test_field must be a positive number."):
            Utils.validate_positive_number(value, "test_field")

    def test_validate_positive_integer_valid(self):
        """Test validate_positive_integer with valid input."""
        assert Utils.validate_positive_integer(10, "test_field") == 10

    @pytest.mark.parametrize("value", [-1, 0, "string", 5.5, None])
    def test_validate_positive_integer_invalid(self, value):
        """Test validate_positive_integer raises ValueError for invalid input."""
        with pytest.raises(ValueError, match="test_field must be a positive integer."):
            Utils.validate_positive_integer(value, "test_field")

    def test_validate_timestamp_valid(self):
        """Test validate_timestamp with valid input."""
        assert Utils.validate_timestamp(0, "test_field") == 0

    @pytest.mark.parametrize("value", [-1, "string", None])
    def test_validate_timestamp_invalid(self, value):
        """Test validate_timestamp raises ValueError for invalid input."""
        with pytest.raises(ValueError, match="test_field timestamp must be a positive number."):
            Utils.validate_timestamp(value, "test_field")

    @pytest.mark.parametrize("value", [2147480001, 9999999999])
    def test_validate_timestamp_invalid_value(self, value):
        """Test validate_timestamp raises ValueError for invalid input."""
        with pytest.raises(ValueError, match=" must be a valid timestamp."):
            Utils.validate_timestamp(value, "test_field")

    def test_get_start_day_valid(self):
        """Test get_start_day with a valid timestamp."""
        timestamp = 1700000000  # Corresponds to a known date
        result = Utils.get_start_day(timestamp)
        expected = dt.datetime(2023, 11, 14, tzinfo=dt.timezone.utc).timestamp()
        assert result == expected

    def test_get_start_day_edge_case(self):
        """Test get_start_day with epoch timestamp."""
        timestamp = 0  # Epoch time
        result = Utils.get_start_day(timestamp)
        expected = dt.datetime(1970, 1, 1, tzinfo=dt.timezone.utc).timestamp()
        assert result == expected

    def test_get_utc_datetime_from_string_valid(self):
        """Test get_utc_datetime_from_string with valid input."""
        date_str = "2023-11-14 10:00:00"
        result = Utils.get_utc_datetime_from_string(date_str)
        expected = dt.datetime(2023, 11, 14, 10, 0, 0, tzinfo=dt.timezone.utc)
        assert result == expected

    def test_get_utc_datetime_from_string_invalid_format(self):
        """Test get_utc_datetime_from_string with invalid date format."""
        date_str = "14/11/2023 10:00:00"
        with pytest.raises(ValueError, match="Error parsing date '14/11/2023 10:00:00'"):
            Utils.get_utc_datetime_from_string(date_str)

    def test_get_utc_datetime_from_string_invalid_type(self):
        """Test get_utc_datetime_from_string with non-string input."""
        with pytest.raises(TypeError, match="Input must be a string."):
            Utils.get_utc_datetime_from_string(12345)

    def test_get_dates_interval_from_timestamp_valid(self):
        """Test get_dates_interval_from_timestamp with valid inputs."""
        start = 1700000000  # Corresponds to "2023-11-14 02:13:20"
        window = 3600  # 1 hour
        date_format = "%Y-%m-%d %H:%M:%S"
        result = Utils.get_dates_interval_from_timestamp(start, window, date_format)
        expected = ("2023-11-14 22:13:20", "2023-11-14 23:13:20")
        assert result == expected

    def test_get_dates_interval_from_timestamp_invalid_start(self):
        """Test get_dates_interval_from_timestamp raises ValueError for invalid start."""
        with pytest.raises(ValueError, match="Both 'timestamp' and 'window' must be integers."):
            Utils.get_dates_interval_from_timestamp("invalid", 3600)

    def test_get_dates_interval_from_timestamp_negative_start(self):
        """Test get_dates_interval_from_timestamp raises ValueError for negative start."""
        with pytest.raises(ValueError, match="'timestamp' must be a non-negative integer."):
            Utils.get_dates_interval_from_timestamp(-1, 3600)

    def test_get_dates_interval_from_timestamp_negative_window(self):
        """Test get_dates_interval_from_timestamp raises ValueError for negative window."""
        with pytest.raises(ValueError, match="'interval' must be a non-negative integer."):
            Utils.get_dates_interval_from_timestamp(1700000000, -3600)

    def test_get_dates_interval_from_timestamp_invalid_window(self):
        """Test get_dates_interval_from_timestamp raises ValueError for invalid window."""
        with pytest.raises(ValueError, match="Both 'timestamp' and 'window' must be integers."):
            Utils.get_dates_interval_from_timestamp(1700000000, "invalid")
