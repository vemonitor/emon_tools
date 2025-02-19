"""
Unit tests for the FinaDataFrame and FinaDfStats classes.

This module contains pytest-based tests
for the FinaDataFrame and FinaDfStats classes,
which provide methods to represent results
as a pandas DataFrame or plot them using
matplotlib.
"""
# pylint: disable=unused-argument,protected-access,unused-import
from unittest.mock import MagicMock
import numpy as np
import pandas as pd
import pytest
from emon_tools.emon_fina.fina_services import FileReaderProps, FinaMeta
from emon_tools.emon_fina.fina_time_series import FinaDataFrame
from emon_tools.emon_fina.fina_utils import Utils
from emon_tools.emon_fina.fina_models import FinaByDateParamsModel
from emon_tools.emon_fina.fina_models import FinaByDateRangeParamsModel
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel
from emon_tools.emon_fina.fina_models import OutputType
from tests.emon_fina.fina_data_test import EmonFinaDataTest


class TestFinaDataFrame:
    """
    Unit tests for the FinaDataFrame class.
    """
    @pytest.fixture
    def mock_reader_meta(self):
        """Fixture to mock the FinaReader."""
        mock_reader = MagicMock()
        # Two days of data at 10-second intervals
        mock_reader.read_meta.return_value = FinaMeta(
            **EmonFinaDataTest.get_fina_meta_slim()
        )
        mock_reader.DEFAULT_CHUNK_SIZE = 1024
        mock_reader.CHUNK_SIZE_LIMIT = 4096
        return mock_reader

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
    def test_get_df_data(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test get_fina_time_series method.
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
        fdtm = FinaDataFrame(feed_id=1, data_dir="mock_dir")

        # Run the read_file method
        data = fdtm.get_df_data(search)
        assert isinstance(data, pd.DataFrame)
        assert data['values'].shape[0] == expected

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
    def test_get_df_data_by_date(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test get_fina_values_by_date method.
        """
        start, _ = Utils.get_dates_interval_from_timestamp(
            start=kwargs['start_time'],
            window=kwargs['time_window']
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
        fdtm = FinaDataFrame(feed_id=1, data_dir="mock_dir")
        data = fdtm.get_df_data_by_date(search)

        assert isinstance(data, pd.DataFrame)
        assert data['values'].shape[0] == expected

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
    def test_get_df_data_by_date_range(
        self,
        kwargs,
        expected,
        mock_reader_meta
    ):
        """
        Test get_fina_values_by_date method.
        """
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
        fdtm = FinaDataFrame(feed_id=1, data_dir="mock_dir")
        data = fdtm.get_df_data_by_date_range(search)

        assert isinstance(data, pd.DataFrame)
        assert data['values'].shape[0] == expected

    @pytest.mark.parametrize(
        "times, values, expected_exception, error_msg",
        [
            (
                "invalid", np.array([3600]), ValueError,
                'data must be a numpy ndarray.'
            ),
            (
                np.array([3600]), 'invalid', ValueError,
                'output_type must be an OutputType instance.'
            ),
            (
                np.array([3600]), OutputType.TIME_SERIES, ValueError,
                'Invalid data columns. Data missing or corrupted.'
            ),
        ],
    )
    def test_set_data_frame_exceptions(
        self,
        times,
        values,
        expected_exception,
        error_msg
    ):
        """Test exceptions for set_data_frame."""
        with pytest.raises(expected_exception, match=error_msg):
            FinaDataFrame.set_data_frame(times, values)
