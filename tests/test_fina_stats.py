"""FinaData Unit Tests"""
# pylint: disable=unused-argument,protected-access

from unittest.mock import MagicMock
from datetime import datetime, timezone
import numpy as np
import pytest
from emon_tools.emon_fina import StatsType
from emon_tools.emon_fina import FinaStats
from emon_tools.fina_reader import MetaData
from emon_tools.fina_utils import Utils


class TestFinaStats:
    """Test suite for the FinaStats class."""

    @pytest.fixture
    def mock_reader(self):
        """Fixture to mock the FinaReader."""
        mock_reader = MagicMock()
        # Two days of data at 10-second intervals
        npoints = 3600 * 24 * 2
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
        mock_reader.CHUNK_SIZE_LIMIT = 4096
        return mock_reader

    @pytest.fixture
    def fina_stats(self, mock_reader):
        """Fixture to create a FinaStats instance with a mocked FinaReader."""
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader
        )
        return FinaStats(feed_id=1, data_dir="mock_dir")

    def test_validate_and_prepare_params_valid(self, fina_stats):
        """Test _validate_and_prepare_params with valid parameters."""
        start_time = 0
        steps_window = 100
        max_size = 1000
        result = fina_stats._validate_and_prepare_params(
            start_time,
            steps_window,
            max_size
        )
        assert result is not None

    @pytest.mark.parametrize(
        "params, expected_exception, error_msg",
        [
            (
                {
                    "start_time": -1,
                    "steps_window": 100,
                    "max_size": 1000
                },
                ValueError,
                'Start time must be a non-negative integer.'
            ),
            (
                {
                    "start_time": 0,
                    "steps_window": -100,
                    "max_size": 1000
                },
                ValueError,
                'Window steps must be a positive integer.'
            ),
            (
                {
                    "start_time": 0,
                    "steps_window": 100,
                    "max_size": -1
                },
                ValueError,
                'Max size must be a positive integer.'
            ),
        ],
    )
    def test_validate_and_prepare_params_invalid(
        self,
        params,
        expected_exception,
        error_msg,
        fina_stats
    ):
        """Test _validate_and_prepare_params with invalid start_time."""
        with pytest.raises(expected_exception, match=error_msg):
            fina_stats._validate_and_prepare_params(
                **params)

    def test_validate_chunk_within_day_boundary(self, fina_stats):
        """Test _validate_chunk with positions within the day boundary."""
        positions = np.array([0, 1, 2, 3, 4])
        next_day_start = fina_stats.meta.start_time + 86400
        try:
            fina_stats._validate_chunk(positions, next_day_start)
        except ValueError:
            pytest.fail("Unexpected ValueError raised.")

    def test_validate_chunk_exceeds_day_boundary(self, fina_stats):
        """Test _validate_chunk with positions exceeding the day boundary."""
        positions = np.array([0, 1, 2, 3, 8641])
        next_day_start = fina_stats.meta.start_time + 86400
        match_error = (
            "Reader Error: Last timestamp 1576022410.0 "
            "exceeds day boundary 1576022400.0.")
        with pytest.raises(
                ValueError, match=match_error):
            fina_stats._validate_chunk(positions, next_day_start)

    def test_trim_results_empty(self, fina_stats):
        """Test _trim_results with empty data."""
        result = fina_stats._trim_results(np.full([1, 2], np.nan))
        assert np.isnan(result).sum() == 2

    @pytest.mark.parametrize(
        "stats_props, expected_stats",
        [
            (
                {
                    "min_value": None
                },
                [1575936000.0, 20.0, 4339.5, 8659.0],
            ),
            (
                {
                    "min_value": 21
                },
                [1575936000.0, 21.0, 4340.0, 8659.0],
            ),
            (
                {
                    "max_value": 23
                },
                [1575936000.0, 20.0, 21.5, 23.0],
            ),
            (
                {
                    "min_value": 21,
                    "max_value": 23
                },
                [1575936000.0, 21.0, 22.0, 23.0],
            ),
            (
                {
                    "min_value": 21,
                    "max_value": 23
                },
                [1575936000.0, 21.0, 22.0, 23.0],
            ),
            (
                {
                    "stats_type": StatsType.INTEGRITY
                },
                [1575936000.0, 8640.0, 8640.0],
            ),
        ],
    )
    def test_get_stats(self, stats_props, expected_stats, fina_stats):
        """
        Test get_stats computes correct statistics with and without filters.

        Args:
            fina_stats: Mocked FinaStats instance.
            min_value: Minimum value for filtering.
            max_value: Maximum value for filtering.
            expected_stats: Expected statistics array for comparison.
        """
        stats = fina_stats.get_stats(**stats_props)
        # Validate output
        assert len(stats) == 1  # Expecting stats for three days
        # Allow for floating-point precision errors
        assert stats[0] == expected_stats

    @pytest.mark.parametrize(
        "stats_props, expected_stats",
        [
            (
                {
                    "start_date": None
                },
                [1575936000.0, 20.0, 4339.5, 8659.0],
            ),
            (
                {
                    "start_date": "2019-12-10 00:00:00"
                },
                [1575936000.0, 20.0, 4339.5, 8659.0],
            ),
            (
                {
                    "end_date": "2019-12-11 00:00:00"
                },
                [1575936000.0, 20.0, 4339.5, 8659.0],
            ),
            (
                {
                    "start_date": "2019-12-10 00:00:00",
                    "end_date": "2019-12-11 00:00:00"
                },
                [1575936000.0, 20.0, 4339.5, 8659.0],
            ),
        ],
    )
    def test_get_stats_by_date(self, stats_props, expected_stats, fina_stats):
        """
        Test get_stats_by_date computes correct statistics
        with and without filters.

        Args:
            fina_stats: Mocked FinaStats instance.
            min_value: Minimum value for filtering.
            max_value: Maximum value for filtering.
            expected_stats: Expected statistics array for comparison.
        """
        stats = fina_stats.get_stats_by_date(**stats_props)
        # Validate output
        assert len(stats) == 1  # Expecting stats for three days
        # Allow for floating-point precision errors
        assert stats[0] == expected_stats

    @pytest.mark.parametrize(
        "value, min_value, max_value, expected",
        [
            (np.array([25, 26, 27, 22]), 20, 30, np.array([25, 26, 27, 22])),
            (
                np.array([15, 20, 30, 2]),
                20,
                30,
                np.array([float("nan"), 20, 30, float("nan")])
            ),
            (
                np.array([22, 2, 40, 27]),
                20,
                30,
                np.array([22, float("nan"), float("nan"), 27])
            ),
            (
                np.array([22, float("nan"), 40, 27]),
                20,
                30,
                np.array([22, float("nan"), float("nan"), 27])
            ),
        ],
    )
    def test_filter_values_by_range(
        self,
        value,
        min_value,
        max_value,
        expected
    ):
        """Test filter_values_by_range correctly filters invalid values."""
        result = Utils.filter_values_by_range(
            value, min_value=min_value, max_value=max_value)
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
                {
                    "start_time": None,
                    "interval": 60,
                    "npoints": 10,
                    "end_time": 1700099000
                },
                ValueError,
                "start_time timestamp must be a number.",
            ),
            (
                {
                    "start_time": 1700000000,
                    "interval": None,
                    "npoints": 10,
                    "end_time": 1700099000
                },
                ValueError,
                "interval must be an integer.",
            ),
            (
                {
                    "start_time": 1700000000,
                    "interval": 60,
                    "npoints": None,
                    "end_time": 1700099000
                },
                ValueError,
                "npoints must be an integer.",
            ),
            (
                {
                    "start_time": 1700000000,
                    "interval": 60,
                    "npoints": 10,
                    "end_time": None
                },
                ValueError,
                "end_time timestamp must be a number.",
            )
        ],
    )
    def test_get_stats_invalid_meta(
        self,
        fina_stats,
        meta,
        expected_exception,
        error_msg
    ):
        """Test get_stats raises an exception for invalid meta data."""
        with pytest.raises(expected_exception, match=error_msg):
            fina_stats.meta = MetaData(**meta)

    @pytest.mark.parametrize(
        "raw_data, day_start, expected_output",
        [
            # Test Case 1: Empty raw_data
            (
                np.array([]),
                1609459200.0,
                [1609459200.0, np.nan, np.nan, np.nan, np.nan, np.nan]
            ),
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
                assert pytest.approx(
                    r, rel=1e-6) == e, f"Expected {e} but got {r}"
