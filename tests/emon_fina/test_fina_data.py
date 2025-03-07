"""FinaData Unit Tests"""
# pylint: disable=unused-argument,protected-access
from unittest.mock import MagicMock
from unittest.mock import patch, mock_open
from struct import pack
import datetime as dt
import numpy as np
import pytest
from emon_tools.emon_fina.emon_fina import FinaData
from emon_tools.emon_fina.fina_models import FinaByDateParamsModel
from emon_tools.emon_fina.fina_models import FinaByDateRangeParamsModel
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel
from emon_tools.emon_fina.fina_models import OutputAverageEnum
from emon_tools.emon_fina.fina_models import OutputType
from emon_tools.emon_fina.fina_models import TimeRefEnum
from emon_tools.emon_fina.fina_services import FileReaderProps, FinaMeta
from emon_tools.emon_fina.fina_utils import Utils
from tests.emon_fina.fina_data_test import EmonFinaDataTest


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
    @patch("emon_tools.emon_fina.fina_reader.isfile", return_value=True)
    @patch("emon_tools.emon_fina.fina_reader.getsize", return_value=400)
    def fdt(self,
            mock_open_file,
            mock_isfile,
            mock_getsize,
            tmp_path_override):
        """
        Fixture to provide a valid FinaData instance for testing.
        """
        file_name = "1"
        return FinaData(
            file_name=file_name,
            data_dir=tmp_path_override
        )

    @pytest.fixture
    def mock_reader_base(self):
        """Fixture to mock the FinaReader."""
        mock_reader = MagicMock()
        # Two days of data at 10-second intervals
        return mock_reader

    @pytest.fixture
    def mock_reader_meta(self):
        """Fixture to mock the FinaReader."""
        mock_reader = MagicMock()
        # Two days of data at 10-second intervals
        mock_reader.read_meta.return_value = FinaMeta(
            **EmonFinaDataTest.get_fina_meta()
        )
        mock_reader.DEFAULT_CHUNK_SIZE = 1024
        mock_reader.CHUNK_SIZE_LIMIT = 4096
        return mock_reader

    @pytest.fixture
    def mock_reader(self):
        """Fixture to mock the FinaReader."""
        mock_reader = MagicMock()
        # Two days of data at 10-second intervals
        mock_reader.read_meta.return_value = FinaMeta(
            **EmonFinaDataTest.get_fina_meta()
        )
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta()
            ),
            search=FinaByTimeParamsModel(
                start_time=EmonFinaDataTest.get_time_start(),
                time_interval=10,
                time_window=3600
            )
        )
        reader_props.initialise_reader()
        mock_reader.props = reader_props
        mock_reader.DEFAULT_CHUNK_SIZE = 1024
        mock_reader.CHUNK_SIZE_LIMIT = 4096
        return mock_reader

    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<2I", 10, 1575981140))
    @patch("emon_tools.emon_fina.fina_reader.isfile", return_value=True)
    @patch("emon_tools.emon_fina.fina_reader.getsize", return_value=400)
    def test_initialization_valid(self,
                                  mock_open_file,
                                  mock_isfile,
                                  mock_getsize,
                                  tmp_path_override):
        """
        Test initializing FinaData with valid parameters.
        """
        data = FinaData(file_name="1", data_dir=tmp_path_override)
        assert data.reader.params.file_name == "1"
        assert data.reader.params.data_dir == tmp_path_override
        assert data.meta.interval == 10
        assert data.meta.start_time == 1575981140
        assert data.meta.npoints == 100
        assert data.meta.end_time == 1575982130

    def test_initialization_invalid(self, tmp_path_override):
        """
        Test FinaData initialization with invalid parameters.
        """
        with pytest.raises(
                ValueError,
                match=r"1 validation error for FinaReaderParamsModel.*"):
            FinaData(file_name=-1, data_dir=tmp_path_override)

        with pytest.raises(
                OSError,
                match=r"Error reading meta file: Directory do not exist.*"):
            FinaData(file_name="1", data_dir="/invalid_dir")

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 3600,
                    "time_interval": 60
                },
                60
            ),
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 3600,
                    "time_interval": 30
                },
                120
            ),
        ],
    )
    def test_get_averaged_values(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test FinaData _get_averaged_values method.
        """
        search = FinaByTimeParamsModel(**kwargs)
        mock_reader_meta.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.arange(20, 20 + 360, dtype=float),  # Values
            )
        ]  # Mocked data
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta()
            ),
            search=search
        )
        reader_props.initialise_reader()
        mock_reader_meta.props = reader_props
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader_meta
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")
        result = fdtm._get_averaged_values(search)
        assert result.shape[0] == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 3600,
                    "time_interval": 10
                },
                360
            ),
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 100,
                    "time_interval": 10
                },
                10
            ),
        ],
    )
    def test_read_direct_values_no_remaining(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test _read_direct_values when remaining points become zero.
        """
        search = FinaByTimeParamsModel(**kwargs)
        mock_reader_meta.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.arange(20, 20 + 360, dtype=float),  # Values
            )
        ]  # Mocked data
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta()
            ),
            search=search
        )
        reader_props.initialise_reader()
        mock_reader_meta.props = reader_props
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader_meta
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")
        result = fdtm._read_direct_values(search)
        assert result.shape[0] == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 3600,
                    "time_interval": 60
                },
                60
            ),
        ],
    )
    def test_get_averaged_values_empty_values(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test _read_averaged_values when a chunk of values is empty.
        """
        # start, step, npts, interval, window = 0, 20, 3, 10, 60
        search = FinaByTimeParamsModel(**kwargs)
        mock_reader_meta.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.full((360, 1), np.nan, dtype=float),  # Values
            )
        ]  # Mocked data
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta()
            ),
            search=search
        )
        reader_props.initialise_reader()
        mock_reader_meta.props = reader_props
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader_meta
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")
        result = fdtm._get_averaged_values(search)
        assert result.shape[0] == expected
        assert np.isnan(result[:, 1]).size == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_type": OutputType.VALUES
                },
                (60, 1)
            ),
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_type": OutputType.VALUES_MIN_MAX
                },
                (60, 3)
            ),
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_type": OutputType.TIME_SERIES
                },
                (60, 2)
            ),
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_type": OutputType.TIME_SERIES_MIN_MAX
                },
                (60, 4)
            ),
            (
                {
                    "start_time": int(Utils.get_start_day(1575981140)),
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_type": OutputType.INTEGRITY
                },
                (60, 3)
            ),
        ],
    )
    def test_get_averaged_output_type(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test _read_averaged_values when remaining points become zero.
        """
        # start, step, npts, interval, window = 0, 20, 2, 10, 40
        search = FinaByTimeParamsModel(**kwargs)
        mock_reader_meta.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.arange(20, 20 + 360, dtype=float),  # Values
            )
        ]  # Mocked data
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta()
            ),
            search=search
        )
        reader_props.initialise_reader()
        mock_reader_meta.props = reader_props
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader_meta
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")
        result = fdtm._get_averaged_values(search)
        assert result.shape == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (  # 0
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_average": OutputAverageEnum.COMPLETE,
                    "time_ref_start": TimeRefEnum.BY_TIME
                },
                59
            ),
            (  # 1
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_average": OutputAverageEnum.COMPLETE,
                    "time_ref_start": TimeRefEnum.BY_SEARCH
                },
                59
            ),
            (  # 2
                {
                    "start_time": EmonFinaDataTest.get_time_start_2() - 142,
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_average": OutputAverageEnum.COMPLETE,
                    "time_ref_start": TimeRefEnum.BY_TIME
                },
                57
            ),
            (  # 3
                {
                    "start_time": EmonFinaDataTest.get_time_start_2() - 142,
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_average": OutputAverageEnum.COMPLETE,
                    "time_ref_start": TimeRefEnum.BY_SEARCH
                },
                57
            ),
            (  # 4
                {
                    "start_time": EmonFinaDataTest.get_time_start_2() - 120,
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_average": OutputAverageEnum.COMPLETE,
                    "time_ref_start": TimeRefEnum.BY_SEARCH
                },
                58
            ),
            (  # 5
                {
                    "start_time": EmonFinaDataTest.get_time_start_2() - 142,
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_average": OutputAverageEnum.PARTIAL,
                    "time_ref_start": TimeRefEnum.BY_TIME
                },
                57
            ),
            (  # 6
                {
                    "start_time": EmonFinaDataTest.get_time_start_2() - 142,
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_average": OutputAverageEnum.PARTIAL,
                    "time_ref_start": TimeRefEnum.BY_SEARCH
                },
                57
            ),
            (  # 7
                {
                    "start_time": EmonFinaDataTest.get_time_start_2() - 142,
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_average": OutputAverageEnum.AS_IS,
                    "time_ref_start": TimeRefEnum.BY_TIME
                },
                59
            ),
            (  # 8
                {
                    "start_time": EmonFinaDataTest.get_time_start_2() - 142,
                    "time_window": 3600,
                    "time_interval": 60,
                    "output_average": OutputAverageEnum.AS_IS,
                    "time_ref_start": TimeRefEnum.BY_SEARCH
                },
                59
            ),
        ],
    )
    def test_get_averaged_values_output_average(
        self,
        kwargs,
        expected,
        mock_reader_base
    ):
        """
        Test _read_averaged_values when reshaped_values is empty.
        """
        # start, step, npts, interval, window = 0, 20, 3, 10, 60
        search = FinaByTimeParamsModel(**kwargs)
        mock_reader_base.read_meta.return_value = FinaMeta(
            **EmonFinaDataTest.get_fina_meta_slim()
        )

        mock_reader_base.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.arange(20, 20 + 360, dtype=float),  # Values
            )
        ]  # Mocked data
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta_slim()
            ),
            search=search
        )
        reader_props.initialise_reader()
        mock_reader_base.props = reader_props
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader_base
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")
        result = fdtm._get_averaged_values(search)
        assert result.shape[0] == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": 1575936012,
                    "time_window": 3600,
                    "time_interval": 60,
                    "time_ref_start": TimeRefEnum.BY_TIME
                },
                (60, [1575936010.0, 1575936070.0, 1575936130.0])
            ),
            (
                {
                    "start_time": 1575936012,
                    "time_window": 3600,
                    "time_interval": 60,
                    "time_ref_start": TimeRefEnum.BY_SEARCH
                },
                (60, [1575936010.0, 1575936070.0, 1575936130.0])
            ),
        ],
    )
    def test_get_averaged_values_time_ref_start(
        self,
        kwargs,
        expected,
        mock_reader
    ):
        """
        Test _read_averaged_values when reshaped_values is empty.
        """
        search = FinaByTimeParamsModel(**kwargs)
        mock_reader.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.arange(20, 20 + 360, dtype=float),  # Values
            )
        ]  # Mocked data
        mock_reader.props.search = search
        mock_reader.props.initialise_reader()
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")
        result = fdtm._get_averaged_values(search)
        assert result.shape[0] == expected[0]
        assert result[0: 3, 0].tolist() == expected[1]

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

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 10
                },
                359
            ),
            (
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 20
                },
                179
            ),
        ],
    )
    def test_read_fina_values(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test the read_fina_values method for reading raw data values.
        """
        search = FinaByTimeParamsModel(**kwargs)
        mock_reader_meta.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.arange(20, 20 + 360, dtype=float),  # Values
            )
        ]  # Mocked data
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta_slim()
            ),
            search=search
        )
        reader_props.initialise_reader()
        mock_reader_meta.props = reader_props
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader_meta
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")
        # Run the read_file method
        data = fdtm.read_fina_values(search)

        assert data.shape[0] == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 10
                },
                359
            ),
            (
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 20
                },
                179
            ),
        ],
    )
    def test_get_fina_values(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test get_fina_values method.
        """
        search = FinaByTimeParamsModel(**kwargs)
        mock_reader_meta.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.arange(20, 20 + 360, dtype=float),  # Values
            )
        ]  # Mocked data
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta_slim()
            ),
            search=search
        )
        reader_props.initialise_reader()
        mock_reader_meta.props = reader_props
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader_meta
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")
        # Run the read_file method
        data = fdtm.get_fina_values(search)

        assert data.shape[0] == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 10
                },
                359
            ),
            (
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 20
                },
                179
            ),
        ],
    )
    def test_get_data_by_date(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test get_fina_values_by_date method.
        """
        start, _ = Utils.get_dates_interval_from_timestamp(
            start=kwargs.get('start_time'),
            window=kwargs.get('time_window')
        )
        search_t = FinaByTimeParamsModel(**kwargs)
        del kwargs['start_time']
        kwargs['start_date'] = start
        search = FinaByDateParamsModel(**kwargs)
        mock_reader_meta.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.arange(20, 20 + 360, dtype=float),  # Values
            )
        ]  # Mocked data
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta_slim()
            ),
            search=search_t
        )
        reader_props.initialise_reader()
        mock_reader_meta.props = reader_props
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader_meta
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")

        data = fdtm.get_data_by_date(search)

        assert isinstance(data, np.ndarray)
        assert data.shape[0] == expected

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 10
                },
                359
            ),
            (
                {
                    "start_time": EmonFinaDataTest.get_time_start_2(),
                    "time_window": 3600,
                    "time_interval": 20
                },
                179
            ),
        ],
    )
    def test_get_data_by_date_range(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test get_data_by_date_range method.
        """        
        # Run the read_file method
        start, end = Utils.get_dates_interval_from_timestamp(
            start=kwargs.get('start_time'),
            window=kwargs.get('time_window')
        )
        search_t = FinaByTimeParamsModel(**kwargs)
        del kwargs['start_time']
        del kwargs['time_window']
        kwargs['start_date'] = start
        kwargs['end_date'] = end
        search = FinaByDateRangeParamsModel(**kwargs)
        mock_reader_meta.read_file.return_value = [
            (
                np.arange(0, 360, 1),  # Positions
                np.arange(20, 20 + 360, dtype=float),  # Values
            )
        ]  # Mocked data
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta_slim()
            ),
            search=search_t
        )
        reader_props.initialise_reader()
        mock_reader_meta.props = reader_props
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(
            "emon_tools.emon_fina.emon_fina.FinaReader",
            lambda *args,
            **kwargs: mock_reader_meta
        )
        fdtm = FinaData(file_name="1", data_dir="mock_dir")
        data = fdtm.get_data_by_date_range(search)

        assert data.shape[0] == expected

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
        result = Utils.get_utc_datetime_from_string(
            dt_value=dt_value,
            date_format=date_format,
            timezone=dt.timezone.utc
        )
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
