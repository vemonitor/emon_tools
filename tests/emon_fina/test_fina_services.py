"""
Test suite for the emon_fina.fina_services module.
"""
from pydantic import ValidationError
import pytest
from emon_tools.emon_fina.fina_services import FinaMeta
from emon_tools.emon_fina.fina_services import FileReaderProps
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel


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
