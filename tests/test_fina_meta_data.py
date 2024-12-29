"""
Unit tests for the MetaData class.

This module tests the functionality of the MetaData class, including validation,
serialization, and computation of derived attributes.
"""
import datetime as dt
import pytest
from emon_tools.fina_reader import MetaData

class TestMetaData:
    """
    Unit tests for the MetaData class.

    Tests cover validation of parameters, serialization, and derived computations.
    """

    def test_initialization_valid(self):
        """
        Test initializing MetaData with valid parameters.
        """
        metadata = MetaData(interval=10, start_time=1000000, npoints=100, end_time=2000000)
        assert metadata.interval == 10
        assert metadata.start_time == 1000000
        assert metadata.npoints == 100
        assert metadata.end_time == 2000000
        metadata.start_time = 1500000
        assert metadata.start_time == 1500000

    def test_initialization_invalid_date_order(self):
        """
        Test initialization raises ValueError if start_time is not less than end_time.
        """
        with pytest.raises(ValueError, match="start_time must be less than end_time"):
            MetaData(interval=10, start_time=2000000, npoints=100, end_time=1000000)

    def test_initialization_invalid_interval(self):
        """
        Test initialization raises ValueError for invalid interval parameter.
        """
        with pytest.raises(ValueError, match="interval must be a positive integer"):
            MetaData(interval=-10, start_time=1000000, npoints=100, end_time=2000000)

    def test_initialization_invalid_start_time(self):
        """
        Test initialization raises ValueError for invalid start_time parameter.
        """
        with pytest.raises(
                ValueError,
                match="start_time timestamp must be a non-negative number."):
            MetaData(interval=10, start_time=-1000000, npoints=100, end_time=2000000)

    def test_calculate_nb_days(self):
        """
        Test calculation of the number of days covered by the metadata.
        """
        start_time = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp())
        end_time = int(dt.datetime(2023, 1, 3, tzinfo=dt.timezone.utc).timestamp())
        metadata = MetaData(interval=10, start_time=start_time, npoints=100, end_time=end_time)
        assert metadata.calculate_nb_days() == 2

    def test_calculate_nb_days_fractional(self):
        """
        Test calculation of the number of days when duration includes fractional days.
        """
        start_time = int(dt.datetime(2023, 1, 1, tzinfo=dt.timezone.utc).timestamp())
        end_time = int(dt.datetime(2023, 1, 2, 12, tzinfo=dt.timezone.utc).timestamp())
        metadata = MetaData(interval=10, start_time=start_time, npoints=100, end_time=end_time)
        assert metadata.calculate_nb_days() == 2

    def test_serialize(self):
        """
        Test serialization of metadata into a dictionary.
        """
        metadata = MetaData(interval=10, start_time=1000000, npoints=100, end_time=2000000)
        expected = {
            "interval": 10,
            "start_time": 1000000,
            "npoints": 100,
            "end_time": 2000000
        }
        assert metadata.serialize() == expected

    def test_string_representation(self):
        """
        Test the string representation of the metadata.
        """
        metadata = MetaData(interval=10, start_time=1000000, npoints=100, end_time=2000000)
        assert str(
            metadata
        ) == "{'interval': 10, 'start_time': 1000000, 'npoints': 100, 'end_time': 2000000}"
