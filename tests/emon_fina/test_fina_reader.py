"""
Unit tests for the FinaReader class.

Ensures full coverage, including security, file validation,
and edge cases. Uses pytest best practices with TestClass
and @pytest.mark.parametrize.
"""
from struct import pack
from unittest.mock import patch, mock_open
import pytest
from emon_tools.emon_fina.fina_reader import FinaReader
from emon_tools.emon_fina.fina_services import FileReaderProps, FinaMeta
from emon_tools.emon_fina.fina_models import (
    FinaByTimeParamsModel, FinaMetaModel
)
from tests.emon_fina.fina_data_test import EmonFinaDataTest


class TestFinaReader:
    """
    Test suite for FinaReader class.
    Ensures correct initialization, file handling, and data security.
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
    def valid_fina_reader(self, tmp_path_override):
        """Fixture for initializing FinaReader with valid parameters."""
        return FinaReader(file_name="testfile", data_dir=tmp_path_override)

    @pytest.mark.parametrize(
        "file_name, data_dir, expected_exception",
        [
            ("", "/valid/path", ValueError),
            ("testfile", "", ValueError),
            ("testfile", "/invalid/path?", ValueError),
        ]
    )
    def test_init_invalid_params(
        self,
        file_name,
        data_dir,
        expected_exception
    ):
        """
        Test initialization with invalid parameters.
        Ensures directory existence validation.
        """
        with pytest.raises(expected_exception):
            FinaReader(file_name, data_dir)

    @pytest.mark.parametrize(
        "filename, expected_exception",
        [
            ("../outside/meta.meta", ValueError),
            ("invalid.exe", ValueError),
        ]
    )
    def test_sanitize_path_invalid(
        self,
        valid_fina_reader,
        filename,
        expected_exception
    ):
        """
        Test _sanitize_path for invalid paths and extensions.
        Ensures security against directory traversal attacks.
        """
        with pytest.raises(expected_exception):
            valid_fina_reader._sanitize_path(filename)

    def test_sanitize_path_valid(self, valid_fina_reader):
        """Test _sanitize_path for valid file paths."""
        with patch(
                "emon_tools.emon_fina.fina_reader.isdir", return_value=True):
            result = valid_fina_reader._sanitize_path("testfile.meta")
            assert result.endswith("testfile.meta")

    @pytest.mark.parametrize(
        "file_size, limit, expected_exception",
        [
            (2048, 1024, ValueError),
            (512, 1024, None),
        ]
    )
    def test_validate_file_size(self, valid_fina_reader, file_size, limit,
                                expected_exception):
        """
        Test _validate_file_size for valid and invalid sizes.
        Ensures files do not exceed set limits.
        """
        with patch(
            "emon_tools.emon_fina.fina_reader.getsize",
            return_value=file_size
        ):
            if expected_exception:
                with pytest.raises(expected_exception):
                    valid_fina_reader._validate_file_size("testfile", limit)
            else:
                valid_fina_reader._validate_file_size("testfile", limit)

    def test_get_meta_path_not_found(self, valid_fina_reader):
        """Test _get_meta_path when meta file is missing."""
        with patch(
            "emon_tools.emon_fina.fina_reader.isfile",
            return_value=False
        ):
            with pytest.raises(FileNotFoundError):
                valid_fina_reader._get_meta_path()

    def test_get_data_path_not_found(self, valid_fina_reader):
        """Test _get_data_path when data file is missing."""
        with patch(
            "emon_tools.emon_fina.fina_reader.isfile",
            return_value=False
        ):
            with pytest.raises(FileNotFoundError):
                valid_fina_reader._get_data_path()

    def test_read_meta_invalid_content(self, valid_fina_reader):
        """Test read_meta for corrupted meta file."""
        mock_file = mock_open(read_data=b"\x00" * 7)
        with patch("builtins.open", mock_file), \
             patch(
                 "emon_tools.emon_fina.fina_reader.getsize",
                 return_value=512), \
             patch(
                 "emon_tools.emon_fina.fina_reader.isfile",
                 return_value=True):
            with pytest.raises(OSError):
                valid_fina_reader.read_meta()

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<2I", 10, 1000000))
    @patch("emon_tools.emon_fina.fina_reader.isfile", return_value=True)
    @patch("emon_tools.emon_fina.fina_reader.getsize", return_value=400)
    def test_read_meta(self,
                       mock_getsize,
                       mock_isfile,
                       mock_open_file,
                       valid_fina_reader):
        """
        Test reading metadata from the meta file.
        """
        meta = valid_fina_reader.read_meta()
        assert isinstance(meta, FinaMeta)
        assert meta.interval == 10
        assert meta.start_time == 1000000
        assert meta.npoints == 100
        assert meta.end_time == 1000990

    # Invalid interval
    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<2I", 0, 1000000))
    @patch("emon_tools.emon_fina.fina_reader.isfile", return_value=True)
    @patch("emon_tools.emon_fina.fina_reader.getsize", return_value=400)
    def test_read_meta_invalid(self,
                               mock_getsize,
                               mock_isfile,
                               mock_open_file,
                               valid_fina_reader):
        """
        Test reading invalid metadata from the meta file.
        """
        match_error = r"Error reading meta file: 1 .*"
        with pytest.raises(
                OSError,
                match=match_error):
            valid_fina_reader.read_meta()

    # Less than 8 bytes
    @patch("builtins.open", new_callable=mock_open, read_data=b"1234")
    @patch("emon_tools.emon_fina.fina_reader.isfile", return_value=True)
    @patch("emon_tools.emon_fina.fina_reader.getsize", return_value=400)
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

    def test_initialise_reader(self, valid_fina_reader):
        """Test initialise_reader sets props correctly."""
        meta = FinaMeta(
            interval=10,
            start_time=1575981140,
            end_time=1575981140 + 100,
            npoints=10,
            size=40
        )
        props = FinaByTimeParamsModel(
            start_time=1575981140,
            time_window=100,
            time_interval=10
        )
        valid_fina_reader.initialise_reader(meta, props)
        assert isinstance(valid_fina_reader.props, FileReaderProps)

    def test_read_file_empty(self, valid_fina_reader):
        """Test read_file handles empty files correctly."""
        with patch(
            "emon_tools.emon_fina.fina_reader.getsize",
            return_value=0), \
                patch("builtins.open", mock_open(read_data=b"")), \
                patch(
                 "emon_tools.emon_fina.fina_reader.isfile",
                 return_value=True
                ):
            valid_fina_reader.initialise_reader(
                FinaMetaModel(
                    interval=1,
                    start_time=0,
                    end_time=1,
                    npoints=0,
                    size=0
                ),
                FinaByTimeParamsModel(
                    start_time=1575981140,
                    time_window=100,
                    time_interval=10
                )
            )
            with pytest.raises(ValueError):
                list(valid_fina_reader.read_file())

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data=pack("<f", 42.0) * 360
    )
    @patch("emon_tools.emon_fina.fina_reader.isfile", return_value=True)
    @patch("emon_tools.emon_fina.fina_reader.getsize", return_value=1440)
    @patch("emon_tools.emon_fina.fina_reader.mmap.mmap", autospec=True)
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
        # Get meta information from the test data.
        meta_dict = EmonFinaDataTest.get_fina_meta_slim()
        # Set search.start_time to meta["start_time"]
        # so it falls within the meta range.
        search = FinaByTimeParamsModel(**{
            "start_time": meta_dict["start_time"],
            "time_window": 3600,
            "time_interval": 10
        })
        reader_props = FileReaderProps(
            meta=FinaMeta(**meta_dict),
            search=search
        )
        reader_props.initialise_reader()
        valid_fina_reader.props = reader_props

        # Mock the mmap object
        mock_mmap_instance = mock_mmap.return_value.__enter__.return_value

        # Handle slice inputs to mimic actual mmap slicing behavior.
        def mock_getitem(slice_obj):
            if isinstance(slice_obj, slice):
                size = (slice_obj.stop - slice_obj.start) // 4
                return pack("<f", 42.0) * size
            raise ValueError("Invalid slice input")

        mock_mmap_instance.__getitem__.side_effect = mock_getitem

        # Run the read_file method
        results = list(valid_fina_reader.read_file())

        assert len(results) == 2
