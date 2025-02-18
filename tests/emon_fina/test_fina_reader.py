from struct import pack
from unittest.mock import MagicMock, patch, mock_open
import pytest

from emon_tools.emon_fina.fina_services import FileReaderProps, FinaMeta
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel, FinaMetaModel
from emon_tools.emon_fina.fina_utils import Utils as Ut
from emon_tools.emon_fina.fina_reader import FinaReader
from tests.emon_fina.fina_data_test import EmonFinaDataTest



class TestFinaReader:
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
        """
        Provide a fixture for a valid FinaReader instance.
        """
        feed_id = 1
        return FinaReader(feed_id=feed_id, data_dir=tmp_path_override)
    
    def test_init_invalid_feed_id(self):
        with pytest.raises(ValueError, match="feed_id must be a positive integer"):
            FinaReader(-1, "/valid/path")

    def test_init_invalid_data_dir(self):
        with patch("emon_tools.emon_fina.fina_reader.isdir", return_value=False):
            with pytest.raises(ValueError, match="Invalid PhpFina directory path"):
                FinaReader(1, "/invalid/path")

    @patch("emon_tools.emon_fina.fina_reader.isdir", return_value=True)
    def test_sanitize_path(self, mock_isdir):
        reader = FinaReader(1, "/data")
        valid_file = "valid.dat"
        invalid_file = "../invalid.dat"
        
        assert reader._sanitize_path(valid_file).startswith("/data")
        
        with pytest.raises(ValueError, match="Attempt to access files outside"):
            reader._sanitize_path(invalid_file)

    @patch("emon_tools.emon_fina.fina_reader.isdir", return_value=True)
    def test_validate_file_size(self, mock_isdir):
        reader = FinaReader(1, "/data")
        with patch("emon_tools.emon_fina.fina_reader.getsize", return_value=2048):
            reader._validate_file_size("/data/file", 4096)
        with patch("emon_tools.emon_fina.fina_reader.getsize", return_value=8192):
            with pytest.raises(ValueError, match="File size exceeds the limit"):
                reader._validate_file_size("/data/file", 4096)

    @patch("emon_tools.emon_fina.fina_reader.isdir", return_value=True)
    def test_get_meta_path(self, mock_isdir):
        reader = FinaReader(1, "/data")
        with patch("emon_tools.emon_fina.fina_reader.isfile", return_value=True), \
             patch("emon_tools.emon_fina.fina_reader.getsize", return_value=512):
            assert reader._get_meta_path().endswith(".meta")
        
        with patch("emon_tools.emon_fina.fina_reader.isfile", return_value=False):
            with pytest.raises(FileNotFoundError, match="Meta file does not exist"):
                reader._get_meta_path()

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
        match_error = (r"Error reading meta file: 1 .*")
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
        # Set search.start_time to meta["start_time"] so it falls within the meta range.
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
