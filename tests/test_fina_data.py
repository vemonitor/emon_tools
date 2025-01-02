"""FinaData Unit Tests"""
# pylint: disable=unused-argument,protected-access

from unittest.mock import patch, mock_open
from struct import pack
import datetime as dt
import numpy as np
import pytest
from emon_tools.emon_fina import FinaData
from emon_tools.fina_utils import Utils


class TestFinaData:
    """
    Unit tests for the FinaData class.

    This test suite validates the functionality of FinaData, including
    metadata reading, file operations, and edge case handling.
    """

    @pytest.fixture
    def tmp_path_override(self, tmp_path):
        """
        Provide a fixture for a valid temporary path
        to simulate data directory.
        """
        data_dir = tmp_path / "test_data"
        data_dir.mkdir()
        return str(data_dir)

    @pytest.fixture
    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<2I", 10, 1575981140))
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    def fdt(self,
            mock_open_file,
            mock_isfile,
            mock_getsize,
            tmp_path_override):
        """
        Fixture to provide a valid FinaData instance for testing.
        """
        feed_id = 1
        return FinaData(
            feed_id=feed_id,
            data_dir=tmp_path_override
        )

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<2I", 10, 1575981140))
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    def test_initialization_valid(self,
                                  mock_open_file,
                                  mock_isfile,
                                  mock_getsize,
                                  tmp_path_override):
        """
        Test initializing FinaData with valid parameters.
        """
        data = FinaData(feed_id=1, data_dir=tmp_path_override)
        assert data.reader.feed_id == 1
        assert data.reader.data_dir == tmp_path_override
        assert data.meta.interval == 10
        assert data.meta.start_time == 1575981140
        assert data.meta.npoints == 100
        assert data.meta.end_time == 1575982130

    def test_initialization_invalid(self, tmp_path_override):
        """
        Test FinaData initialization with invalid parameters.
        """
        with pytest.raises(
                ValueError, match="feed_id must be a positive integer."):
            FinaData(feed_id=-1, data_dir=tmp_path_override)

        with pytest.raises(
                ValueError, match="/invalid_dir is not a valid directory."):
            FinaData(feed_id=1, data_dir="/invalid_dir")

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_read_direct_values_no_remaining(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test _read_direct_values when remaining points become zero.
        """
        start, step, npts, interval, window = 0, 10, 5, 10, 50
        fdt.meta = type("Meta", (), {"start_time": 0, "npoints": 10})
        fdt.reader = type("Reader", (), {
            "read_file": lambda **kwargs: iter([
                (0, np.array([1, 2, 3, 4, 5])),
                (5, np.array([6, 7, 8, 9, 10]))
            ])
        })

        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        def mock_getitem(slice_obj):
            size = (slice_obj.stop - slice_obj.start) // 4
            return pack("<f", 42.0) * size

        mock_mmap_instance.__getitem__.side_effect = mock_getitem
        fdt.reader.CHUNK_SIZE_LIMIT = 4096
        result = fdt._read_direct_values(
            start, step, npts, interval, window, set_pos=True)
        assert result.tolist() == [1, 2, 3, 4, 5]

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_read_averaged_values_empty_values(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test _read_averaged_values when a chunk of values is empty.
        """
        start, step, npts, interval, window = 0, 20, 3, 10, 60
        fdt.meta = type("Meta", (), {"start_time": 0, "npoints": 10})
        fdt.reader = type("Reader", (), {
            "read_file": lambda **kwargs: iter([
                (0, np.array([])),  # Empty chunk
                (10, np.array([1, 2, 3, 4, 5, 6]))
            ])
        })

        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        def mock_getitem(slice_obj):
            size = (slice_obj.stop - slice_obj.start) // 4
            return pack("<f", 42.0) * size

        mock_mmap_instance.__getitem__.side_effect = mock_getitem
        fdt.reader.CHUNK_SIZE_LIMIT = 4096
        result = fdt._read_averaged_values(start, step, npts, interval, window)
        assert result.tolist() == [1.5, 3.5, 5.5]

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_read_averaged_values_no_remaining(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test _read_averaged_values when remaining points become zero.
        """
        start, step, npts, interval, window = 0, 20, 2, 10, 40
        fdt.meta = type("Meta", (), {"start_time": 0, "npoints": 10})
        fdt.reader = type("Reader", (), {
            "read_file": lambda **kwargs: iter([
                (0, np.array([1, 2, 3, 4, 5, 6])),
                (10, np.array([7, 8, 9, 10, 11, 12]))
            ])
        })

        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        def mock_getitem(slice_obj):
            size = (slice_obj.stop - slice_obj.start) // 4
            return pack("<f", 42.0) * size

        mock_mmap_instance.__getitem__.side_effect = mock_getitem
        fdt.reader.CHUNK_SIZE_LIMIT = 4096
        result = fdt._read_averaged_values(start, step, npts, interval, window)
        assert result.tolist() == [1.5, 3.5]

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_read_averaged_values_nan_fallback(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test _read_averaged_values when reshaped_values is empty.
        """
        start, step, npts, interval, window = 0, 20, 3, 10, 60
        fdt.meta = type("Meta", (), {"start_time": 0, "npoints": 10})
        fdt.reader = type("Reader", (), {
            "read_file": lambda **kwargs: iter([
                (0, np.array([np.nan] * 6))  # All NaN values
            ])
        })

        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        def mock_getitem(slice_obj):
            size = (slice_obj.stop - slice_obj.start) // 4
            return pack("<f", 42.0) * size

        mock_mmap_instance.__getitem__.side_effect = mock_getitem
        fdt.reader.CHUNK_SIZE_LIMIT = 4096
        result = fdt._read_averaged_values(start, step, npts, interval, window)
        assert np.isnan(result).all()

    def test_reset(self, fdt):
        """Test the reset method for FinaData."""
        fdt.lines = 100
        fdt.start = 1000
        fdt.end = 2000
        fdt.step = 10

        # Call the reset method
        fdt.reset()

        # Check if all attributes are reset to their default values
        assert fdt.lines == 0
        assert fdt.start is None
        assert fdt.end is None
        assert fdt.step is None

    def test_timescale(self, fdt):
        """
        Test the timescale method for generating time values.
        """
        match_error = (
            "Step size and line count must be set "
            "before generating a timescale.")
        with pytest.raises(
                ValueError,
                match=match_error):
            ts = fdt.timescale()
        fdt.step = 10
        fdt.lines = 10
        ts = fdt.timescale()
        assert isinstance(ts, np.ndarray)
        assert len(ts) == 10
        assert ts.min() == 0
        assert ts.max() == 90
        assert ts.mean() == 45

    def test_timestamps(self, fdt):
        """
        Test the timescale method for generating time values.
        """
        with pytest.raises(
                ValueError,
                match="win_start timestamp must be a number."):
            ts = fdt.timestamps()
        fdt.step = 10
        fdt.lines = 10
        fdt.start = 1700000000
        ts = fdt.timestamps()
        assert isinstance(ts, np.ndarray)
        assert len(ts) == 10
        assert ts.min() == 1700000000
        assert ts.max() == 1700000090
        assert ts.mean() == 1700000045

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_read_fina_values(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test the read_fina_values method for reading raw data values.
        """
        with pytest.raises(ValueError, match=r"^Invalid start value.*"):
            fdt.read_fina_values(
                start=1575983130,
                step=10,
                window=100
            )
        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs to mimic actual mmap slicing behavior
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                # Calculate the position based on the slice start
                # Number of floats
                size = (slice_obj.stop - slice_obj.start) // 4
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method
        data = fdt.read_fina_values(
            start=1575981140,
            step=10,
            window=100
        )

        assert data.shape[0] == 10

        # Run the read_file method
        data = fdt.read_fina_values(
            start=1575981140,
            step=20,
            window=100
        )

        assert data.shape[0] == 5

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_get_fina_values(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test get_fina_values method.
        """
        with pytest.raises(ValueError, match=r"^Invalid start value.*"):
            fdt.read_fina_values(
                start=1575983130,
                step=10,
                window=400
            )
        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs to mimic actual mmap slicing behavior
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                # Calculate the position based on the slice start
                # Number of floats
                size = (slice_obj.stop - slice_obj.start) // 4
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method
        data = fdt.get_fina_values(
            start=1575981140,
            step=10,
            window=100
        )

        assert data.shape[0] == 10

        # Run the read_file method
        data = fdt.get_fina_values(
            start=1575981140,
            step=20,
            window=100
        )

        assert data.shape[0] == 5

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_get_fina_time_series(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test get_fina_time_series method.
        """
        with pytest.raises(ValueError, match=r"^Invalid start value.*"):
            fdt.get_fina_time_series(
                start=1575983130,
                step=10,
                window=400
            )
        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs to mimic actual mmap slicing behavior
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                # Calculate the position based on the slice start
                # Number of floats
                size = (slice_obj.stop - slice_obj.start) // 4
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method
        data = fdt.get_fina_time_series(
            start=1575981140,
            step=10,
            window=100
        )
        assert isinstance(data, np.ndarray)
        assert data.shape[0] == 10

        # Run the read_file method
        data = fdt.get_fina_time_series(
            start=1575981140,
            step=20,
            window=100
        )

        assert isinstance(data, np.ndarray)
        assert data.shape[0] == 5

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_get_fina_values_by_date(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test get_fina_values_by_date method.
        """
        start, end = Utils.get_dates_interval_from_timestamp(
            start=1575983130,
            window=400
        )
        with pytest.raises(ValueError, match=r"^Invalid start value.*"):
            fdt.get_fina_values_by_date(
                start_date=start,
                end_date=end,
                step=10
            )
        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs to mimic actual mmap slicing behavior
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                # Calculate the position based on the slice start
                # Number of floats
                size = (slice_obj.stop - slice_obj.start) // 4
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method
        start, end = Utils.get_dates_interval_from_timestamp(
            start=1575981140,
            window=100
        )
        data = fdt.get_fina_values_by_date(
            start_date=start,
            end_date=end,
            step=10
        )

        assert isinstance(data, np.ndarray)
        assert data.shape[0] == 10

        # Run the read_file method
        data = fdt.get_fina_values_by_date(
            start_date=start,
            end_date=end,
            step=20
        )

        assert isinstance(data, np.ndarray)
        assert data.shape[0] == 5

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_get_fina_time_series_by_date(
        self,
        mock_mmap,
        mock_isfile,
        mock_getsize,
        mock_open_file,
        fdt
    ):
        """
        Test get_fina_values_by_date method.
        """
        start, end = Utils.get_dates_interval_from_timestamp(
            start=1575983130,
            window=400
        )
        with pytest.raises(
                ValueError,
                match=r"Invalid start value. Start must be less than .*"):
            fdt.get_fina_time_series_by_date(
                start_date=start,
                end_date=end,
                step=10
            )
        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs to mimic actual mmap slicing behavior
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                # Calculate the position based on the slice start
                # Number of floats
                size = (slice_obj.stop - slice_obj.start) // 4
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method
        start, end = Utils.get_dates_interval_from_timestamp(
            start=1575981140,
            window=100
        )
        data = fdt.get_fina_time_series_by_date(
            start_date=start,
            end_date=end,
            step=10
        )

        assert isinstance(data, np.ndarray)
        assert data.shape[0] == 10

        # Run the read_file method
        data = fdt.get_fina_time_series_by_date(
            start_date=start,
            end_date=end,
            step=20
        )

        assert isinstance(data, np.ndarray)
        assert data.shape[0] == 5

    def test_calculate_optimal_chunk_size(self, fdt):
        """Test the calculate_optimal_chunk_size method."""
        fdt.CHUNK_SIZE_LIMIT = 1024

        # Test with valid parameters
        assert fdt.calculate_optimal_chunk_size(
            window=10000) == 256
        assert fdt.calculate_optimal_chunk_size(
            window=10000, min_chunk_size=512) == 512
        assert fdt.calculate_optimal_chunk_size(
            window=10000, scale_factor=2.0) == 256
        assert fdt.calculate_optimal_chunk_size(
            window=10000, divisor=128) == 256

        # Test with invalid parameters
        with pytest.raises(
                ValueError, match="window size must be a positive integer."):
            fdt.calculate_optimal_chunk_size(window=-1)
        with pytest.raises(
                ValueError,
                match="Minimum chunk size must be a positive integer."):
            fdt.calculate_optimal_chunk_size(window=10000, min_chunk_size=-1)
        with pytest.raises(
                ValueError, match="Scale factor must be a positive number."):
            fdt.calculate_optimal_chunk_size(window=10000, scale_factor=-1.0)
        with pytest.raises(
                ValueError, match="divisor must be a positive integer."):
            fdt.calculate_optimal_chunk_size(window=10000, divisor=-1)

    def test_calculate_nearest_divisible(self):
        """Test the calculate_nearest_divisible method."""
        # Test with valid parameters
        assert FinaData.calculate_nearest_divisible(
            250, 128, 256, 1024) == 256
        assert FinaData.calculate_nearest_divisible(
            500, 128, 256, 1024) == 512
        assert FinaData.calculate_nearest_divisible(
            1000, 128, 256, 1024) == 1024
        assert FinaData.calculate_nearest_divisible(
            100, 128, 256, 1024) == 256

        # Test with edge cases
        assert FinaData.calculate_nearest_divisible(
            1025, 128, 256, 1024) == 1024
        assert FinaData.calculate_nearest_divisible(
            255, 128, 256, 1024) == 256
        assert FinaData.calculate_nearest_divisible(
            0, 128, 256, 1024) == 256

    @pytest.mark.parametrize(
        "dt_value, date_format, expected",
        [
            (
                "2024-12-14 15:30:00", "%Y-%m-%d %H:%M:%S",
                dt.datetime(2024, 12, 14, 15, 30, tzinfo=dt.timezone.utc)),
            (
                "01/01/2000 00:00:00", "%d/%m/%Y %H:%M:%S",
                dt.datetime(2000, 1, 1, 0, 0, tzinfo=dt.timezone.utc)),
        ],
    )
    def test_get_utc_datetime_from_string(
        self,
        dt_value,
        date_format,
        expected
    ):
        """Test valid inputs for get_utc_datetime_from_string."""
        result = Utils.get_utc_datetime_from_string(dt_value, date_format)
        assert result == expected

    @pytest.mark.parametrize(
        "dt_value, date_format, expected_exception, error_msg",
        [
            (
                123, "%Y-%m-%d %H:%M:%S", TypeError,
                "The input date-time value must be a string."),
            (
                "invalid-date", "%Y-%m-%d %H:%M:%S", ValueError,
                "Error parsing date 'invalid-date'"),
            (
                "2024-12-14", "%d/%m/%Y", ValueError,
                (
                    "Error parsing date '2024-12-14' with the format "
                    "'%d/%m/%Y': time data '2024-12-14' does not match format "
                )
            ),
        ],
    )
    def test_get_utc_datetime_from_string_exceptions(
        self,
        dt_value,
        date_format,
        expected_exception,
        error_msg
    ):
        """Test exceptions for get_utc_datetime_from_string."""
        with pytest.raises(expected_exception, match=error_msg):
            Utils.get_utc_datetime_from_string(dt_value, date_format)

    @pytest.mark.parametrize(
        "start, window, date_format, expected",
        [
            (
                1700000000, 3600, "%Y-%m-%d %H:%M:%S",
                (
                    "2023-11-14 22:13:20",
                    "2023-11-14 23:13:20",
                ),
            ),
            (
                0, 60, "%d/%m/%Y %H:%M:%S",
                (
                    "01/01/1970 00:00:00",
                    "01/01/1970 00:01:00",
                ),
            ),
        ],
    )
    def test_get_dates_interval_from_timestamp(
        self,
        start,
        window,
        date_format,
        expected
    ):
        """Test valid inputs for get_dates_interval_from_timestamp."""
        # Act
        result = Utils.get_dates_interval_from_timestamp(
            start, window, date_format)

        # Assert
        assert result == expected

    @pytest.mark.parametrize(
        "start, window, expected_exception, error_msg",
        [
            (
                "invalid",
                3600,
                ValueError,
                "'start' and 'window' must be integers."),
            (
                1700000000,
                "invalid",
                ValueError,
                "'start' and 'window' must be integers."
            ),
            (
                -1,
                3600,
                ValueError,
                "'start' and 'window' must be non-negative."
            ),
            (
                1700000000,
                -3600,
                ValueError,
                "'start' and 'window' must be non-negative."
            ),
        ],
    )
    def test_get_dates_interval_from_timestamp_exceptions(
        self,
        start,
        window,
        expected_exception,
        error_msg
    ):
        """Test exceptions for get_dates_interval_from_timestamp."""
        with pytest.raises(expected_exception, match=error_msg):
            Utils.get_dates_interval_from_timestamp(start, window)
