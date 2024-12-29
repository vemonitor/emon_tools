"""FinaReader Unit Tests"""
# pylint: disable=unused-argument,protected-access

from unittest.mock import patch, mock_open
from os.path import join as path_join
from struct import pack
import numpy as np
import pytest
from emon_tools.fina_reader import FinaReader
from emon_tools.fina_reader import MetaData


class TestFinaReader:
    """
    Unit tests for the FinaReader class.

    This test suite validates the functionality of FinaReader, including
    metadata reading, file operations, and edge case handling.
    """

    @pytest.fixture
    def tmp_path_override(self, tmp_path):
        """
        Provide a fixture for a valid temporary path to simulate data directory.
        """
        data_dir = tmp_path / "test_data"
        data_dir.mkdir()
        return str(data_dir)

    @pytest.fixture
    def valid_fina_reader(self, tmp_path_override):
        """
        Provide a fixture for a valid FinaReader instance.
        """
        feed_id = 1
        return FinaReader(feed_id=feed_id, data_dir=tmp_path_override)

    def test_initialization_valid(self, tmp_path_override):
        """
        Test initializing FinaReader with valid parameters.
        """
        reader = FinaReader(feed_id=1, data_dir=tmp_path_override)
        assert reader.feed_id == 1
        assert reader.data_dir == tmp_path_override

    @pytest.mark.parametrize("feed_id", [0, -1])
    def test_initialization_invalid_feed_id(self, tmp_path_override, feed_id):
        """
        Test initializing FinaReader with invalid feed_id values.
        """
        with pytest.raises(ValueError, match="feed_id must be a positive integer."):
            FinaReader(feed_id=feed_id, data_dir=tmp_path_override)

    def test_initialization_invalid_data_dir(self):
        """
        Test initializing FinaReader with an invalid data_dir.
        """
        with pytest.raises(ValueError, match="is not a valid directory."):
            FinaReader(feed_id=1, data_dir="invalid_dir")

    def test_setters(self, valid_fina_reader, tmp_path_override):
        """
        Test setter methods for feed_id, data_dir, and pos attributes.
        """
        # feed_id setter
        valid_fina_reader.feed_id = 2
        assert valid_fina_reader.feed_id == 2

        with pytest.raises(ValueError, match="feed_id must be a positive integer."):
            valid_fina_reader.feed_id = -1

        # data_dir setter
        valid_fina_reader.data_dir = tmp_path_override
        assert valid_fina_reader.data_dir == tmp_path_override

        with pytest.raises(ValueError, match="data_dir must be a valid directory."):
            valid_fina_reader.data_dir = "invalid_dir"

        # pos setter
        valid_fina_reader.pos = 10
        assert valid_fina_reader.pos == 10

        with pytest.raises(ValueError, match="pos must be a positive integer."):
            valid_fina_reader.pos = -1

    @patch("emon_tools.fina_reader.isfile", return_value=False)
    def test_get_meta_path_invalid(self, mock_isfile, valid_fina_reader):
        """
        Test that _get_meta_path raises FileNotFoundError when the meta file does not exist.
        """
        # Simulate accessing the meta file path
        with pytest.raises(FileNotFoundError, match="Meta file does not exist"):
            valid_fina_reader._get_meta_path()

        # Assert that os.path.isfile was called with the expected file path
        expected_path = path_join(
            valid_fina_reader.data_dir,
            f"{valid_fina_reader.feed_id}.meta"
        )
        mock_isfile.assert_called_once_with(expected_path)

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<2I", 10, 1000000))
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    def test_read_meta(self,
                       mock_getsize,
                       mock_isfile,
                       mock_open_file,
                       valid_fina_reader):
        """
        Test reading metadata from the meta file.
        """
        meta = valid_fina_reader.read_meta()
        assert isinstance(meta, MetaData)
        assert meta.interval == 10
        assert meta.start_time == 1000000
        assert meta.npoints == 100
        assert meta.end_time == 1000990

    # Invalid interval
    @patch("builtins.open", new_callable=mock_open, read_data=pack("<2I", 0, 1000000))
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    def test_read_meta_invalid(self,
                               mock_getsize,
                               mock_isfile,
                               mock_open_file,
                               valid_fina_reader):
        """
        Test reading invalid metadata from the meta file.
        """
        with pytest.raises(
            OSError,
            match="Error reading meta file: interval must be a positive integer."):
            valid_fina_reader.read_meta()

    # Less than 8 bytes
    @patch("builtins.open", new_callable=mock_open, read_data=b"1234")
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    def test_read_meta_corrupted_meta_file(
        self,
        mock_getsize,
        mock_isfile,
        mock_open_file,
        valid_fina_reader
    ):
        """
        Test that ValueError is raised when the meta file is corrupted
        (i.e., insufficient bytes are read).
        """
        with pytest.raises(IOError, match=r"Error reading meta file: .*"):
            valid_fina_reader.read_meta()

        # Ensure the correct file was attempted to open
        mock_open_file.assert_called_once_with(
            valid_fina_reader._get_meta_path(),
            "rb"
        )

    @patch("builtins.open", new_callable=mock_open, read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_read_file(
        self,
        mock_mmap,
        mock_open_file,
        mock_isfile,
        mock_getsize,
        valid_fina_reader
    ):
        """
        Test reading data values from the .dat file.
        """
        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs to mimic actual mmap slicing behavior
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                # Calculate the position based on the slice start
                size = (slice_obj.stop - slice_obj.start) // 4  # Number of floats
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method
        results = list(valid_fina_reader.read_file(
            npoints=10,
            start_pos=0,
            chunk_size=5
        ))

        # Assert the results
        assert len(results) == 1  # Two chunks of 5 points each
        for chunk in results:
            positions, values = chunk
            assert len(positions) == len(values) == 10
            for pos, value in zip(positions, values):
                assert 0 <= pos < 10
                assert isinstance(value, np.float32)
                assert value == 42.0

    @patch("emon_tools.fina_reader.isfile", return_value=False)
    def test_read_file_missing_data(self, mock_isfile, valid_fina_reader):
        """
        Test error when the data file does not exist.
        """
        with pytest.raises(FileNotFoundError, match="Data file does not exist"):
            list(valid_fina_reader.read_file(npoints=10))

    @patch("emon_tools.fina_reader.isfile", return_value=True)
    def test_read_file_invalid_npoints(self, mock_isfile, valid_fina_reader):
        """
        Test that ValueError is raised when npoints is invalid.
        """
        with pytest.raises(ValueError, match="npoints must be a positive integer."):
            list(valid_fina_reader.read_file(npoints=-1))

    @patch("builtins.open", new_callable=mock_open, read_data=b"\x00\x00\x00")  # Less than 4 bytes
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_read_file_corrupted_data(
        self,
        mock_mmap,
        mock_getsize,
        mock_isfile,
        mock_open_file,
        valid_fina_reader
    ):
        """
        Test that ValueError is raised when the data file is corrupted
        (i.e., insufficient bytes are read for a float).
        """
        # Mock mmap object behavior
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value
        # Return less than 4 bytes
        mock_mmap_instance.__getitem__.side_effect = lambda s: b"\x00\x00\x00"

        with pytest.raises(ValueError, match="Failed to read expected chunk at position 0."):
            list(valid_fina_reader.read_file(npoints=1))

        # Ensure the file was opened
        mock_open_file.assert_called_once_with(valid_fina_reader._get_data_path(), "rb")


    @patch("builtins.open", new_callable=mock_open, read_data=pack("<f", 42.0) * 10)
    @patch("emon_tools.fina_reader.getsize", return_value=400)
    @patch("emon_tools.fina_reader.isfile", return_value=True)
    @patch("emon_tools.fina_reader.mmap.mmap", autospec=True)
    def test_read_file_with_window(
        self,
        mock_mmap,
        mock_getsize,
        mock_isfile,
        mock_open_file,
        valid_fina_reader
    ):
        """
        Test reading data with a specified window size.
        """
        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                size = (slice_obj.stop - slice_obj.start) // 4  # Number of floats
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method with a window size
        results = list(valid_fina_reader.read_file(
            npoints=10,
            start_pos=0,
            chunk_size=5,
            window=7
        ))

        # Assert the results
        assert len(results) == 1  # Two chunks: 5 and 2 points
        assert sum(len(chunk[0]) for chunk in results) == 7  # Total 7 points

    def test_sanitize_path_invalid_extension(self, valid_fina_reader):
        """
        Test _sanitize_path with an invalid file extension.
        """
        filename = "invalid_file.txt"
        with pytest.raises(ValueError, match="Invalid file extension."):
            valid_fina_reader._sanitize_path(filename)

    def test_sanitize_path_outside_directory(self, valid_fina_reader):
        """
        Test _sanitize_path with a filename that attempts to access outside the allowed directory.
        """
        filename = "../outside_file.dat"
        with pytest.raises(ValueError, match="Attempt to access files outside the allowed directory."):
            valid_fina_reader._sanitize_path(filename)
