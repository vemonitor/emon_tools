"""FinaData Unit Tests"""
# pylint: disable=unused-argument,protected-access

from unittest.mock import MagicMock
from datetime import datetime, timezone
import numpy as np
import pytest
from emon_tools.emon_fina import FinaStats  # Adjust the import path as necessary
from emon_tools.fina_reader import MetaData
from emon_tools.fina_utils import Utils

class TestFinaStats:
    """Test suite for the FinaStats class."""

    @pytest.fixture
    def mock_reader(self):
        """Fixture to mock the FinaReader."""
        mock_reader = MagicMock()
        # Two days of data at 10-second intervals
        npoints = (3600 * 24 * 2)
        start_time = Utils.get_start_day(1575981140)
        mock_reader.read_meta.return_value = MetaData(
            start_time=start_time,
            interval=10,
            npoints=npoints,
            end_time=start_time + npoints * 10 - 10,
        )
        mock_reader.read_file.return_value = [
            (
                np.arange(0, 8640, 1),  # Positions
                np.arange(20, 20 + 8640, dtype=float),     # Values
            )
        ]  # Mocked data
        mock_reader.chunk_size = 8640
        mock_reader.CHUNK_SIZE_LIMIT = 4096  # Set CHUNK_SIZE_LIMIT to an integer value
        return mock_reader


    @pytest.fixture
    def fina_stats(self, mock_reader):
        """Fixture to create a FinaStats instance with a mocked FinaReader."""
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr("emon_tools.emon_fina.FinaReader", lambda *args, **kwargs: mock_reader)
        return FinaStats(feed_id=1, data_dir="mock_dir")


    @pytest.mark.parametrize(
        "min_value, max_value, expected_stats",
        [
            (
                None,
                None,
                [1575936000.0, 20.0, 4339.5, 8659.0],
            ),
            (
                21,
                None,
                [1575936000.0, 21.0, 4340.0, 8659.0],
            ),
            (
                None,
                23,
                [1575936000.0, 20.0, 21.5, 23.0],
            ),
            (
                21,
                23,
                [1575936000.0, 21.0, 22.0, 23.0],
            ),
        ],
    )
    def test_get_stats(self, min_value, max_value, expected_stats, fina_stats):
        """
        Test get_stats computes correct statistics with and without filters.

        Args:
            fina_stats: Mocked FinaStats instance.
            min_value: Minimum value for filtering.
            max_value: Maximum value for filtering.
            expected_stats: Expected statistics array for comparison.
        """
        stats = fina_stats.get_stats(
            max_size=172800,  # Max size for data processing
            min_value=min_value,
            max_value=max_value,
        )
        # Validate output
        assert len(stats) == 1  # Expecting stats for three days
        # Allow for floating-point precision errors
        assert stats[0] == expected_stats

    @pytest.mark.parametrize(
        "value, min_value, max_value, expected",
        [
            (np.array([25, 26, 27, 22]), 20, 30, np.array([25, 26, 27, 22])),
            (np.array([15, 20, 30, 2]), 20, 30, np.array([float("nan"), 20, 30, float("nan")])),
            (np.array([22, 2, 40, 27]), 20, 30, np.array([22, float("nan"), float("nan"), 27])),
            (
                np.array([22, float("nan"), 40, 27]),
                20,
                30,
                np.array([22, float("nan"), float("nan"), 27])
            ),
        ],
    )
    def test_filter_values_by_range(self, value, min_value, max_value, expected):
        """Test filter_values_by_range correctly filters invalid values."""
        result = Utils.filter_values_by_range(value, min_value=min_value, max_value=max_value)
        nb_expected = np.isnan(expected).sum()
        if nb_expected > 0:
            assert np.isnan(result).sum() == nb_expected
        else:
            assert np.array_equal(result, expected)

    def test_get_start_day(self):
        """Test get_start_day correctly computes the start of the day."""
        timestamp = 1700000000  # "2023-11-14 02:13:20" in UTC
        expected = datetime(2023, 11, 14, tzinfo=timezone.utc).timestamp()
        assert Utils.get_start_day(timestamp) == expected

    @pytest.mark.parametrize(
        "meta, expected_exception, error_msg",
        [
            (
                {"start_time": None, "interval": 60, "npoints": 10, "end_time": 1700099000},
                ValueError,
                "start_time timestamp must be a number.",
            ),
            (
                {"start_time": 1700000000, "interval": None, "npoints": 10, "end_time": 1700099000},
                ValueError,
                "interval must be an integer.",
            ),
            (
                {"start_time": 1700000000, "interval": 60, "npoints": None, "end_time": 1700099000},
                ValueError,
                "npoints must be an integer.",
            ),
            (
                {"start_time": 1700000000, "interval": 60, "npoints": 10, "end_time": None},
                ValueError,
                "end_time timestamp must be a number.",
            )
        ],
    )
    def test_get_stats_invalid_meta(self, fina_stats, meta, expected_exception, error_msg):
        """Test get_stats raises an exception for invalid meta data."""
        with pytest.raises(expected_exception, match=error_msg):
            fina_stats.meta = MetaData(**meta)

    @pytest.mark.parametrize(
        "raw_data, day_start, expected_output",
        [
            # Test Case 1: Empty raw_data
            (np.array([]), 1609459200.0, [1609459200.0, np.nan, np.nan, np.nan, np.nan, np.nan]),

            # Test Case 2: Valid raw_data
            (
                np.array([1.0, 2.0, 3.0]),
                1609459200.0,
                [1609459200.0, 1.0, 2.0, 3.0, 3, 3],
            ),

            # Test Case 3: Single entry in raw_data
            (
                np.array([42.0]),
                1609459200.0,
                [1609459200.0, 42.0, 42.0, 42.0, 1, 1],
            ),

            # Test Case 4: All NaN values in raw_data
            (
                np.array([np.nan, np.nan]),
                1609459200.0,
                [1609459200.0, np.nan, np.nan, np.nan, 0, 2],
            ),
        ],
    )
    def test_get_grouped_stats(self, raw_data, day_start, expected_output):
        """
        Test FinaStats.get_grouped_stats for various input scenarios.
        """
        result = FinaStats.get_values_stats(raw_data, day_start)

        # Check if all values match within acceptable precision
        for r, e in zip(result, expected_output):
            if np.isnan(e):
                assert np.isnan(r), f"Expected NaN but got {r}"
            else:
                assert pytest.approx(r, rel=1e-6) == e, f"Expected {e} but got {r}"
