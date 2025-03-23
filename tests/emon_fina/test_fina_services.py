"""
Test suite for the emon_fina.fina_services module.
"""
import numpy as np
from pydantic import ValidationError
import pytest
from emon_tools.emon_fina.fina_services import FinaMeta, FinaOutputData
from emon_tools.emon_fina.fina_services import FileReaderProps
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel, OutputType


class TestFinaMeta:
    """
    Test suite for the FinaMeta class.

    This test suite includes the following tests:
    - test_calculate_nb_days:
        Tests the calculate_nb_days method of FinaMeta class.
    - test_serialize: Tests the serialize method of FinaMeta class.
    - test_str: Tests the __str__ method of FinaMeta class.
    - test_validation_error: Tests that FinaMeta raises ValidationError for
      invalid inputs.

    Each test uses pytest.mark.parametrize to run multiple test cases with
    different inputs and expected outputs.
    """
    @pytest.fixture
    def valid_fina_meta_params(self):
        """Get valid FinaMeta init params"""
        return {
            "interval": 10,
            "start_time": 1609459200,
            "npoints": 100,
            "end_time": 1609462800,
            "size": 400,
        }

    @pytest.mark.parametrize(
        "start_time, end_time, expected_days",
        [
            (1609459200, 1609545600, 1),  # 1 day
            (1609459200, 1609632000, 2),  # 2 days
            (1609459200, 1609718400, 3),  # 3 days
            (1609459200, 1609545599, 1),  # Just under 1 day
        ]
    )
    def test_calculate_nb_days(
        self, start_time, end_time, expected_days, valid_fina_meta_params
    ):
        """
        Test the calculate_nb_days method of FinaMeta class.
        """
        params = valid_fina_meta_params.copy()
        params.update({
            "start_time": start_time,
            "end_time": end_time,
        })
        meta = FinaMeta(**params)
        assert meta.calculate_nb_days() == expected_days

    @pytest.mark.parametrize(
        "interval, start_time, npoints, end_time, expected_dict",
        [
            (10, 1609459200, 100, 1609462800, {
                "interval": 10,
                "start_time": 1609459200,
                "npoints": 100,
                "end_time": 1609462800,
                "size": 400,
            }),
            (5, 1609459200, 200, 1609462800, {
                "interval": 5,
                "start_time": 1609459200,
                "npoints": 200,
                "end_time": 1609462800,
                "size": 400,
            }),
        ]
    )
    def test_serialize(
        self, interval, start_time, npoints, end_time, expected_dict,
        valid_fina_meta_params
    ):
        """
        Test the serialize method of FinaMeta class.
        """
        params = valid_fina_meta_params.copy()
        params.update({
            "interval": interval,
            "start_time": start_time,
            "npoints": npoints,
            "end_time": end_time,
        })
        meta = FinaMeta(**params)
        assert meta.serialize() == expected_dict

    @pytest.mark.parametrize(
        "interval, start_time, npoints, end_time, expected_exception",
        [
            (None, 1609459200, 100, 1609462800, ValidationError),
            (10, None, 100, 1609462800, ValidationError),
            (10, 1609459200, None, 1609462800, ValidationError),
            (10, 1609459200, 100, None, ValidationError),
        ]
    )
    def test_validation_error(
        self,
        interval,
        start_time,
        npoints,
        end_time,
        expected_exception,
        valid_fina_meta_params
    ):
        """
        Test that FinaMeta raises ValidationError for invalid inputs.
        """
        params = valid_fina_meta_params.copy()
        params.update({
            "interval": interval,
            "start_time": start_time,
            "npoints": npoints,
            "end_time": end_time,
        })
        with pytest.raises(expected_exception):
            FinaMeta(**params)


class TestFileReaderProps:
    """
    Test suite for the FileReaderProps class.

    This test suite includes the following tests:
    - test_has_remaining_points: Tests the has_remaining_points method.
    - test_update_remaining_points: Tests the update_remaining_points method.
    - test_init_read_props: Tests the init_read_props method.
    - test_init_step_boundaries: Tests the init_step_boundaries method.
    - test_update_step_boundaries: Tests the update_step_boundaries method.
    - test_calc_current_window_size: Tests the calc_current_window_size method.
    - test_get_chunk_size: Tests the get_chunk_size method.
    - test_initialise_reader: Tests the initialise_reader method.
    - test_iter_update_before: Tests the iter_update_before method.
    - test_iter_update_after: Tests the iter_update_after method.
    """

    @pytest.fixture
    def valid_file_reader_props_params(self):
        """
        Get valid FileReaderProps init
        """
        return {
            "meta": FinaMeta(
                interval=10,
                start_time=1609459200,
                npoints=100,
                end_time=1609462800,
                size=400,
            ),
            "search": FinaByTimeParamsModel(
                start_time=1609459200,
                time_window=3600,
                time_interval=86400,
            ),
            "remaining_points": 100,
            "current_pos": 0,
            "window_max": 100,
            "chunk_size": 10,
            "current_window": 10,
            "start_pos": 0,
            "start_search": 0,
            "window_search": 0,
            "current_start": 1609459200,
            "next_start": 1609545600,
            "block_size": 1,
            "DEFAULT_CHUNK_SIZE": 10,
            "CHUNK_SIZE_LIMIT": 100,
        }

    def test_has_remaining_points(self, valid_file_reader_props_params):
        """
        Test the has_remaining_points method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        assert props.has_remaining_points() is True

    def test_update_remaining_points(self, valid_file_reader_props_params):
        """
        Test the update_remaining_points method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        props.update_remaining_points()
        assert props.remaining_points == 100

    def test_init_read_props(self, valid_file_reader_props_params):
        """
        Test the init_read_props method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        props.init_read_props()
        assert props.start_pos == 0
        assert props.current_pos == 0
        assert props.start_search == 0
        assert props.window_search == 360
        assert props.window_max == 360
        assert props.remaining_points == 360
        assert props.block_size == 8640

    def test_init_step_boundaries(self, valid_file_reader_props_params):
        """
        Test the init_step_boundaries method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        props.init_step_boundaries()
        assert props.current_start == 1609459200
        assert props.next_start == 1609545600

    def test_update_step_boundaries(self, valid_file_reader_props_params):
        """
        Test the update_step_boundaries method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        props.update_step_boundaries()
        assert props.current_start == 1609545600
        assert props.next_start == 1609632000

    def test_calc_current_window_size(self, valid_file_reader_props_params):
        """
        Test the calc_current_window_size method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        props.calc_current_window_size()
        assert props.current_window == 1

    def test_get_chunk_size(self, valid_file_reader_props_params):
        """
        Test the get_chunk_size method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        chunk_size = props.get_chunk_size()
        assert chunk_size == 100

    def test_initialise_reader(self, valid_file_reader_props_params):
        """
        Test the initialise_reader method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        props.initialise_reader()
        assert props.start_pos == 0
        assert props.current_start == 1609459200
        assert props.next_start == 1609545600
        assert props.current_window == 360
        assert props.chunk_size == 360

    def test_iter_update_before(self, valid_file_reader_props_params):
        """
        Test the iter_update_before method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        chunk_size = props.iter_update_before()
        assert chunk_size == 10

    def test_iter_update_after(self, valid_file_reader_props_params):
        """
        Test the iter_update_after method.
        """
        props = FileReaderProps(**valid_file_reader_props_params)
        props.iter_update_after()
        assert props.current_start == 1609459200
        assert props.next_start == 1609545600
        assert props.current_pos == 10

    @pytest.mark.parametrize(
        "kwargs, expected_result",
        [
            # ref_low >= ref_high
            (
                {
                    "time_ref": 1609459200,
                    "start_pos": 100,
                    "meta_start_time": 1609455600,
                    "meta_interval": 3600,
                    "window_max": 7200
                },
                100
            ),
            # ref_low < ref_high
            (
                {
                    "time_ref": 1609459200,
                    "start_pos": 50,
                    "meta_start_time": 1609455600,
                    "meta_interval": 7200,
                    "window_max": 10400
                },
                0
            ),
            # ref_low == ref_high
            (
                {
                    "time_ref": 1609459200,
                    "start_pos": 0,
                    "meta_start_time": 1609455600,
                    "meta_interval": 3600,
                    "window_max": 7200
                },
                0
            ),
            # ref_low < ref_high with different values
            (
                {
                    "time_ref": 1609459200,
                    "start_pos": 200,
                    "meta_start_time": 1609455600,
                    "meta_interval": 1800,
                    "window_max": 3600
                },
                200
            ),
            # ref_low >= ref_high with different values
            (
                {
                    "time_ref": 1609459200,
                    "start_pos": 300,
                    "meta_start_time": 1609455600,
                    "meta_interval": 900,
                    "window_max": 3600
                },
                300
            ),
            (
                {
                    "time_ref": 1609455600 - 8,
                    "start_pos": 0,
                    "meta_start_time": 1609455600,
                    "meta_interval": 10,
                    "window_max": 3600
                },
                -10
            ),
            (
                {
                    "time_ref": 1609455600 - 11,
                    "start_pos": 0,
                    "meta_start_time": 1609455600,
                    "meta_interval": 10,
                    "window_max": 3600
                },
                -10
            ),
            (
                {
                    "time_ref": 1609455600 - 8,
                    "start_pos": 0,
                    "meta_start_time": 1609455600,
                    "meta_interval": 20,
                    "window_max": 3600
                },
                0
            ),
            (
                {
                    "time_ref": 1609455600 - 11,
                    "start_pos": 0,
                    "meta_start_time": 1609455600,
                    "meta_interval": 20,
                    "window_max": 3600
                },
                -20
            ),
            (
                {
                    "time_ref": 1609455600 + 8,
                    "start_pos": 0,
                    "meta_start_time": 1609455600,
                    "meta_interval": 10,
                    "window_max": 3600
                },
                10
            ),
            (
                {
                    "time_ref": 1609455600 + 11,
                    "start_pos": 0,
                    "meta_start_time": 1609455600,
                    "meta_interval": 10,
                    "window_max": 3600
                },
                10
            ),
            (
                {
                    "time_ref": 1609455600 + 8,
                    "start_pos": 0,
                    "meta_start_time": 1609455600,
                    "meta_interval": 20,
                    "window_max": 3600
                },
                0
            ),
            (
                {
                    "time_ref": 1609455600 + 11,
                    "start_pos": 0,
                    "meta_start_time": 1609455600,
                    "meta_interval": 20,
                    "window_max": 3600
                },
                20
            ),
        ]
    )
    def test_calc_time_correction(
        self,
        kwargs,
        expected_result
    ):
        """
        Test the calc_time_correction method.
        """
        result = FileReaderProps.calc_time_correction(
            **kwargs
        )
        assert result == expected_result

    @pytest.mark.parametrize(
        (
            "time_interval, start_time, time_window, "
            "expected_time_interval, expected_start_time, expected_time_window"
        ),
        [
            # Case 1: start_time and time_window are 0
            (0, 0, 0, 10, 1609459200, 3600),
            # Case 2: start_time is 0, time_window is non-zero
            (0, 0, 7200, 10, 1609459200, 7200),
            # Case 3: start_time is non-zero, time_window is 0
            (0, 1609462800, 0, 10, 1609462800, 3600),
            # Case 4: start_time and time_window are non-zero
            (0, 1609462800, 7200, 10, 1609462800, 7200),
            # Case 5: time_interval is non-zero and valid
            (20, 0, 0, 20, 1609459200, 3600),
            # Case 6: time_interval is non-zero
            # but not a multiple of base_interval
            (25, 0, 0, 30, 1609459200, 3600),
        ]
    )
    def test_initialise_search(
        self,
        time_interval,
        start_time,
        time_window,
        expected_time_interval,
        expected_start_time,
        expected_time_window,
        valid_file_reader_props_params
    ):
        """
        Test the initialise_search method.
        """
        params = valid_file_reader_props_params.copy()
        params["search"].time_interval = time_interval
        params["search"].start_time = start_time
        params["search"].time_window = time_window

        props = FileReaderProps(**params)
        props.initialise_search()

        assert props.search.time_interval == expected_time_interval
        assert props.search.start_time == expected_start_time
        assert props.search.time_window == expected_time_window

    @pytest.mark.parametrize(
        "base_interval, interval, expected_result",
        [
            (10, 25, 30),  # Interval is not a multiple of base_interval
            (10, 20, 20),  # Interval is a multiple of base_interval
            (10, 10, 10),  # Interval equals base_interval
            (10, 5, 10),   # Interval is less than base_interval
            (10, 0, 10),   # Interval is zero
            (10, 100, 100),  # Interval is much larger than base_interval
        ]
    )
    def test_get_nearest_valid_interval(
        self,
        base_interval,
        interval,
        expected_result
    ):
        """
        Test the get_nearest_valid_interval method.
        """
        result = FileReaderProps.get_nearest_valid_interval(
            base_interval, interval)
        assert result == expected_result

    @pytest.mark.parametrize(
        "base_interval, interval, expected_exception",
        [
            (0, 10, ValueError),  # Base interval is zero
            (-10, 20, ValueError),  # Base interval is negative
        ]
    )
    def test_get_nearest_valid_interval_exceptions(
        self,
        base_interval,
        interval,
        expected_exception
    ):
        """
        Test that get_nearest_valid_interval
        raises exceptions for invalid inputs.
        """
        with pytest.raises(expected_exception):
            FileReaderProps.get_nearest_valid_interval(base_interval, interval)

    @pytest.mark.parametrize(
        "base_time, timestamp, interval, base_interval, expected_result",
        [
            # Case 1: Valid inputs with aligned timestamp
            (1609459200, 1609462800, 3600, 3600, (0, 1)),
            # Case 2: Valid inputs with unaligned timestamp
            (1609459200, 1609462800, 3600, 1800, (0, 2)),
            # Case 3: Interval is larger than base_interval
            (1609459200, 1609462800, 7200, 3600, (1, 1)),
            # Case 4: Timestamp is before base_time
            (1609462800, 1609459200, 3600, 3600, (0, -1)),
            # Case 5: Timestamp is exactly base_time
            (1609459200, 1609459200, 3600, 3600, (0, 0)),
            # Case 6: Interval is not a multiple of base_interval
            (1609459200, 1609461000, 3600, 1800, (1, 1)),
            # Case 7: Timestamp is far ahead of base_time
            (1609459200, 1609470000, 3600, 3600, (0, 3)),
        ]
    )
    def test_calculate_nb_points(
        self,
        base_time,
        timestamp,
        interval,
        base_interval,
        expected_result
    ):
        """
        Test the calculate_nb_points method.
        """
        result = FileReaderProps.calculate_nb_points(
            base_time=base_time,
            timestamp=timestamp,
            interval=interval,
            base_interval=base_interval
        )
        assert result == expected_result

    @pytest.mark.parametrize(
        "base_time, timestamp, interval, base_interval, expected_exception",
        [
            # Case 1: Interval is zero
            (1609459200, 1609462800, 0, 3600, ValueError),
            # Case 2: Base interval is zero
            (1609459200, 1609462800, 3600, 0, ValueError),
        ]
    )
    def test_calculate_nb_points_exceptions(
        self,
        base_time,
        timestamp,
        interval,
        base_interval,
        expected_exception
    ):
        """
        Test that calculate_nb_points raises exceptions for invalid inputs.
        """
        with pytest.raises(expected_exception):
            FileReaderProps.calculate_nb_points(
                base_time=base_time,
                timestamp=timestamp,
                interval=interval,
                base_interval=base_interval
            )

    @pytest.mark.parametrize(
        "value, base, expected_result",
        [
            (10, 3, 12),  # Value is not a multiple of base
            (10, 5, 10),  # Value is already a multiple of base
            (0, 3, 0),    # Value is zero
            (7, 1, 7),    # Base is 1
            (7, 7, 7),    # Value equals base
            (7, 10, 10),  # Base is larger than value
        ]
    )
    def test_round_up(self, value, base, expected_result):
        """
        Test the _round_up method.
        """
        result = FileReaderProps._round_up(value, base)
        assert result == expected_result

    @pytest.mark.parametrize(
        "value, base, expected_result",
        [
            (10, 3, 9),   # Value is not a multiple of base
            (10, 5, 10),  # Value is already a multiple of base
            (0, 3, 3),    # Value is zero
            (7, 1, 7),    # Base is 1
            (7, 7, 7),    # Value equals base
            (7, 10, 10),  # Base is larger than value
        ]
    )
    def test_round_down(self, value, base, expected_result):
        """
        Test the _round_down method.
        """
        result = FileReaderProps._round_down(value, base)
        assert result == expected_result

    @pytest.mark.parametrize(
        "value, base, expected_exception",
        [
            (10, 0, ValueError),  # Base is zero
        ]
    )
    def test_round_up_exceptions(self, value, base, expected_exception):
        """
        Test that _round_up raises exceptions for invalid inputs.
        """
        with pytest.raises(expected_exception):
            FileReaderProps._round_up(value, base)

    @pytest.mark.parametrize(
        "value, base, expected_exception",
        [
            (10, 0, ValueError),  # Base is zero
        ]
    )
    def test_round_down_exceptions(self, value, base, expected_exception):
        """
        Test that _round_down raises exceptions for invalid inputs.
        """
        with pytest.raises(expected_exception):
            FileReaderProps._round_down(value, base)


class TestFinaOutputData:
    """
    Test suite for the FinaOutputData class.
    """

    @pytest.mark.parametrize(
        "output_type, expected_columns",
        [
            (OutputType.VALUES, ["values"]),
            (OutputType.VALUES_MIN_MAX, ["min", "values", "max"]),
            (OutputType.TIME_SERIES, ["time", "values"]),
            (OutputType.TIME_SERIES_MIN_MAX, ["time", "min", "values", "max"]),
            (OutputType.INTEGRITY, ["time", "nb_finite", "nb_total"]),
        ]
    )
    def test_get_columns(self, output_type, expected_columns):
        """
        Test the get_columns method of FinaOutputData class.
        """
        result = FinaOutputData.get_columns(output_type=output_type)
        assert result == expected_columns

    @pytest.mark.parametrize(
        "values, day_start, with_stats, with_time, expected_result",
        [
            # Case 2: Multiple values, with_stats=True, with_time=True
            (
                np.array([1.0, 2.0, 3.0]), 1609459200.0, True, True,
                [1609459200.0, 1.0, 2.0, 3.0]
            ),
            # Case 3: Multiple values, with_stats=False, with_time=True
            (
                np.array([1.0, 2.0, 3.0]), 1609459200.0, False, True,
                [1609459200.0, 2.0]
            ),
            # Case 4: Multiple values, with_stats=True, with_time=False
            (
                np.array([1.0, 2.0, 3.0]), 1609459200.0, True, False,
                [1.0, 2.0, 3.0]
            ),
            # Case 5: Multiple values, with_stats=False, with_time=False
            (
                np.array([1.0, 2.0, 3.0]), 1609459200.0, False, False,
                [2.0]
            ),
            # Case 6: Empty array, with_stats=True, with_time=True
            (
                np.array([]), 1609459200.0, True, True,
                [1609459200.0, np.nan, np.nan, np.nan]
            ),
            # Case 7: Empty array, with_stats=False, with_time=True
            (
                np.array([]), 1609459200.0, False, True,
                [1609459200.0, np.nan]
            ),
            # Case 8: Empty array, with_stats=True, with_time=False
            (
                np.array([]), 1609459200.0, True, False,
                [np.nan, np.nan, np.nan]
            ),
            # Case 9: Empty array, with_stats=False, with_time=False
            (
                np.array([]), 1609459200.0, False, False,
                [np.nan]
            ),
            # Case 10: Array with NaN values, with_stats=True, with_time=True
            (
                np.array([np.nan, np.nan]), 1609459200.0, True, True,
                [1609459200.0, np.nan, np.nan, np.nan]
            ),
            # Case 11: Array with NaN values, with_stats=False, with_time=True
            (
                np.array([np.nan, np.nan]), 1609459200.0, False, True,
                [1609459200.0, np.nan]
            ),
        ]
    )
    def test_get_values_stats(
        self,
        values,
        day_start,
        with_stats,
        with_time,
        expected_result
    ):
        """
        Test the get_values_stats method of FinaOutputData class.
        """
        result = FinaOutputData.get_values_stats(
            values=values,
            day_start=day_start,
            with_stats=with_stats,
            with_time=with_time
        )
        assert result == expected_result
