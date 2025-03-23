"""Fina Models Unit Tests"""
from pydantic import ValidationError
import pytest
from emon_tools.emon_fina.fina_models import OutputType
from emon_tools.emon_fina.fina_models import OutputAverageEnum
from emon_tools.emon_fina.fina_models import TimeRefEnum
from emon_tools.emon_fina.fina_models import FinaMetaModel
from emon_tools.emon_fina.fina_models import FileReaderPropsModel
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel


class TestFinaByTimeParamsModel:
    """
    Unit tests for the FinaData Models class.

    This test suite validates the functionality of FinaData Models Validators
    """
    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "start_time": 1700000009,
                    "time_window": 3600,
                    "time_interval": 10,
                    "output_type": OutputType.VALUES
                },
                {
                    'start_time': 1700000009,
                    'time_window': 3600,
                    'time_interval': 10,
                    'n_decimals': 3,
                    'min_value': None, 'max_value': None,
                    'output_type': OutputType.VALUES,
                    'output_average': OutputAverageEnum.COMPLETE,
                    'time_ref_start': TimeRefEnum.BY_TIME
                }
            ),
            (
                {
                    "start_time": 1700000009,
                    "time_window": 3600,
                    "time_interval": 10,
                    'min_value': -50,
                    'max_value': 50,
                    "output_type": OutputType.VALUES
                },
                {
                    'start_time': 1700000009,
                    'time_window': 3600,
                    'time_interval': 10,
                    'n_decimals': 3,
                    'min_value': -50, 'max_value': 50,
                    'output_type': OutputType.VALUES,
                    'output_average': OutputAverageEnum.COMPLETE,
                    'time_ref_start': TimeRefEnum.BY_TIME
                }
            ),
            (
                {
                    "start_time": 1700000009,
                    "time_window": 3600,
                    "time_interval": 10,
                    'min_value': -50.5,
                    'max_value': 50.5,
                    "output_type": OutputType.VALUES
                },
                {
                    "start_time": 1700000009,
                    "time_window": 3600,
                    'time_interval': 10,
                    'n_decimals': 3,
                    'min_value': -50.5, 'max_value': 50.5,
                    'output_type': OutputType.VALUES,
                    'output_average': OutputAverageEnum.COMPLETE,
                    'time_ref_start': TimeRefEnum.BY_TIME
                }
            ),
            (
                {
                    "start_time": 0,
                    "time_window": 0,
                    "time_interval": 0,
                    "output_type": OutputType.VALUES
                },
                {
                    "start_time": 0,
                    "time_window": 0,
                    'time_interval': 0,
                    'n_decimals': 3,
                    'min_value': None, 'max_value': None,
                    'output_type': OutputType.VALUES,
                    'output_average': OutputAverageEnum.COMPLETE,
                    'time_ref_start': TimeRefEnum.BY_TIME
                }
            ),
            (
                {},
                {
                    "start_time": 0,
                    "time_window": 0,
                    'time_interval': 0,
                    'n_decimals': 3,
                    'min_value': None, 'max_value': None,
                    'output_type': OutputType.TIME_SERIES,
                    'output_average': OutputAverageEnum.COMPLETE,
                    'time_ref_start': TimeRefEnum.BY_TIME
                }
            ),
        ],
    )
    def test_valid(
        self,
        kwargs,
        expected
    ):
        """
        Test FinaData initialization with invalid parameters.
        """
        result = FinaByTimeParamsModel(**kwargs)
        assert dict(result) == expected

    @pytest.mark.parametrize(
        "kwargs, expected_exception, error_msg",
        [
            (
                {
                    "start_time": -1,
                    "time_window": -1,
                    "time_interval": -1,
                },
                ValidationError,
                "3 validation errors for FinaByTimeParamsModel\n.*"
            ),
            (
                {
                    "start_time": "0",
                    "time_window": "0",
                    "time_interval": "0",
                    "min_value": "0",
                    "max_value": "0",
                },
                ValidationError,
                "7 validation errors for FinaByTimeParamsModel\n.*"
            ),
            (
                {
                    "start_time": 1.1,
                    "time_window": 1.1,
                    "time_interval": 1.1,
                },
                ValidationError,
                "3 validation errors for FinaByTimeParamsModel\n.*"
            ),

        ],
    )
    def test_invalid(
        self,
        kwargs,
        expected_exception,
        error_msg
    ):
        """
        Test FinaData initialization with invalid parameters.
        """
        with pytest.raises(
                expected_exception, match=error_msg):
            FinaByTimeParamsModel(**kwargs)


class TestFinaMetaModel:
    """
    Unit tests for the FinaMetaModel class.

    This test suite validates the functionality of FinaMetaModel Validators
    """
    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "interval": 10,
                    "start_time": 1700000009,
                    "end_time": 1700003609,
                    "npoints": 100,
                    "size": 4096
                },
                {
                    "interval": 10,
                    "start_time": 1700000009,
                    "end_time": 1700003609,
                    "npoints": 100,
                    "size": 4096
                }
            ),
            (
                {
                    "interval": 0,
                    "start_time": 0,
                    "end_time": 0,
                    "npoints": 0,
                    "size": 0
                },
                {
                    "interval": 0,
                    "start_time": 0,
                    "end_time": 0,
                    "npoints": 0,
                    "size": 0
                }
            ),
        ],
    )
    def test_valid(self, kwargs, expected):
        """
        Test FinaMetaModel initialization with valid parameters.
        """
        result = FinaMetaModel(**kwargs)
        assert dict(result) == expected

    @pytest.mark.parametrize(
        "kwargs, expected_exception, error_msg",
        [
            (
                {
                    "interval": -1,
                    "start_time": -1,
                    "end_time": -1,
                    "npoints": -1,
                    "size": -1
                },
                ValidationError,
                "5 validation errors for FinaMetaModel\n.*"
            ),
            (
                {
                    "interval": 10,
                    "start_time": 1700003609,
                    "end_time": 1700000009,
                    "npoints": 100,
                    "size": 4096
                },
                ValidationError,
                "start_time must be less than end_time."
            ),
            (
                {
                    "interval": 10,
                    "start_time": "1700000009",
                    "end_time": "1700003609",
                    "npoints": "100",
                    "size": "4096"
                },
                ValidationError,
                "4 validation errors for FinaMetaModel\n.*"
            ),
        ],
    )
    def test_invalid(self, kwargs, expected_exception, error_msg):
        """
        Test FinaMetaModel initialization with invalid parameters.
        """
        with pytest.raises(expected_exception, match=error_msg):
            FinaMetaModel(**kwargs)


class TestFileReaderPropsModel:
    """
    Unit tests for the FileReaderPropsModel class.

    This test suite validates the functionality
    of FileReaderPropsModel Validators
    """
    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            (
                {
                    "meta": {
                        "interval": 10,
                        "start_time": 1700000009,
                        "end_time": 1700003609,
                        "npoints": 100,
                        "size": 4096
                    },
                    "search": {
                        "start_time": 1700000009,
                        "time_window": 3600,
                        "time_interval": 10,
                        "output_type": OutputType.VALUES
                    },
                    "current_pos": 0,
                    "start_pos": 0,
                    "chunk_size": 1024,
                    "remaining_points": 0,
                    "start_search": 0,
                    "window_search": 0,
                    "block_size": 0,
                    "current_window": 0,
                    "window_max": 0,
                    "current_start": 0,
                    "next_start": 0,
                    "auto_pos": True
                },
                {
                    "meta": {
                        "interval": 10,
                        "start_time": 1700000009,
                        "end_time": 1700003609,
                        "npoints": 100,
                        "size": 4096
                    },
                    "search": {
                        "start_time": 1700000009,
                        "time_window": 3600,
                        "time_interval": 10,
                        'n_decimals': 3,
                        "min_value": None,
                        "max_value": None,
                        "output_type": OutputType.VALUES,
                        "output_average": OutputAverageEnum.COMPLETE,
                        "time_ref_start": TimeRefEnum.BY_TIME
                    },
                    "current_pos": 0,
                    "start_pos": 0,
                    "chunk_size": 1024,
                    "remaining_points": 0,
                    "start_search": 0,
                    "window_search": 0,
                    "block_size": 0,
                    "current_window": 0,
                    "window_max": 0,
                    "current_start": 0,
                    "next_start": 0,
                    "auto_pos": True
                }
            ),
            (
                {
                    "meta": {
                        "interval": 0,
                        "start_time": 0,
                        "end_time": 0,
                        "npoints": 0,
                        "size": 0
                    },
                    "search": {
                        "start_time": 0,
                        "time_window": 0,
                        "time_interval": 0,
                        "output_type": OutputType.VALUES
                    },
                    "current_pos": 0,
                    "start_pos": 0,
                    "chunk_size": 0,
                    "remaining_points": 0,
                    "start_search": 0,
                    "window_search": 0,
                    "block_size": 0,
                    "current_window": 0,
                    "window_max": 0,
                    "current_start": 0,
                    "next_start": 0,
                    "auto_pos": True
                },
                {
                    "meta": {
                        "interval": 0,
                        "start_time": 0,
                        "end_time": 0,
                        "npoints": 0,
                        "size": 0
                    },
                    "search": {
                        "start_time": 0,
                        "time_window": 0,
                        "time_interval": 0,
                        'n_decimals': 3,
                        "min_value": None,
                        "max_value": None,
                        "output_type": OutputType.VALUES,
                        "output_average": OutputAverageEnum.COMPLETE,
                        "time_ref_start": TimeRefEnum.BY_TIME
                    },
                    "current_pos": 0,
                    "start_pos": 0,
                    "chunk_size": 0,
                    "remaining_points": 0,
                    "start_search": 0,
                    "window_search": 0,
                    "block_size": 0,
                    "current_window": 0,
                    "window_max": 0,
                    "current_start": 0,
                    "next_start": 0,
                    "auto_pos": True
                }
            ),
        ],
    )
    def test_valid(self, kwargs, expected):
        """
        Test FileReaderPropsModel initialization with valid parameters.
        """
        result = FileReaderPropsModel(**kwargs)
        assert result.model_dump() == expected

    @pytest.mark.parametrize(
        "kwargs, expected_exception, error_msg",
        [
            (
                {
                    "meta": {
                        "interval": -1,
                        "start_time": -1,
                        "end_time": -1,
                        "npoints": -1,
                        "size": -1
                    },
                    "search": {
                        "start_time": -1,
                        "time_window": -1,
                        "time_interval": -1,
                        "output_type": OutputType.VALUES
                    },
                    "current_pos": -1,
                    "start_pos": -1,
                    "chunk_size": -1,
                    "remaining_points": -1,
                    "start_search": -1,
                    "window_search": -1,
                    "block_size": -1,
                    "current_window": -1,
                    "window_max": -1,
                    "current_start": -1,
                    "next_start": -1,
                    "auto_pos": True
                },
                ValidationError,
                "19 validation errors for FileReaderPropsModel\n.*"
            )
        ],
    )
    def test_invalid(self, kwargs, expected_exception, error_msg):
        """
        Test FileReaderPropsModel initialization with invalid parameters.
        """
        if expected_exception:
            with pytest.raises(expected_exception, match=error_msg):
                FileReaderPropsModel(**kwargs)
        else:
            result = FileReaderPropsModel(**kwargs)
            assert result.chunk_size == FileReaderPropsModel.CHUNK_SIZE_LIMIT
