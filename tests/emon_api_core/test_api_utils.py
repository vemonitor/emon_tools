"""Tests for emon_tools.api_utils module."""
import pytest
from emon_tools.api_utils import Utils


class TestApiUtils:
    """Tests for Utils class."""

    def test_is_valid_node(self):
        """Test is_valid_node method."""
        assert Utils.is_valid_node("Node1") is True
        assert Utils.is_valid_node("") is False
        assert Utils.is_valid_node(123) is False
        assert Utils.is_valid_node("Node@1") is False

    @pytest.mark.parametrize(
        "node, expected_exception, error_msg",
        [
            (
                123, TypeError,
                "node must be a not empty string."
            ),
            (
                " ", TypeError,
                "node must be a not empty string."
            ),
            (
                "Node@1", ValueError,
                "node must be a valid string."
            ),
        ],
    )
    def test_validate_node(
        self,
        node,
        expected_exception,
        error_msg
    ):
        """Test validate_node method."""
        with pytest.raises(expected_exception, match=error_msg):
            Utils.validate_node(node, "node")

    def test_is_request_success(self):
        """Test is_request_success method."""
        assert Utils.is_request_success({"success": "true"}) is True
        assert Utils.is_request_success({"success": "false"}) is False
        assert Utils.is_request_success("not a dict") is False

    @pytest.mark.parametrize(
        "input_data, filter_data, filter_in, expected",
        [
            (
                {
                    "name": "I1", "nodeid": "emon_tools_ex1",
                    "description": "Managed Input"
                },
                ["name", "nodeid"],
                True,
                {
                    "name": "I1", "nodeid": "emon_tools_ex1"
                }
            ),
            (
                {
                    "name": "I1", "nodeid": "emon_tools_ex1",
                    "description": "Managed Input"
                },
                ["description"],
                True,
                {
                    "description": "Managed Input"
                }
            ),
            # Test: Negate match (filter_in=False)
            (
                {
                    "name": "I1", "nodeid": "emon_tools_ex1",
                    "description": "Managed Input"
                },
                ["description"],
                False,
                {
                    "name": "I1", "nodeid": "emon_tools_ex1"
                }
            ),
        ],
    )
    def test_filter_dict_by_keys(
        self,
        input_data,
        filter_data,
        filter_in, expected
    ):
        """
        Test the filter_list_of_dicts method with various scenarios.

        Args:
            input_data (list): The input list of dictionaries to filter.
            filter_data (dict): The dictionary of filter conditions.
            filter_in (bool): Whether to include or exclude matching items.
            expected (list): The expected result after filtering.
        """
        result = Utils.filter_dict_by_keys(
            input_data=input_data, filter_data=filter_data, filter_in=filter_in
        )
        assert result == expected, f"Expected {expected}, got {result}"

    @pytest.mark.parametrize(
        "input_data, filter_data, filter_in, expected",
        [
            # Test: Exact match (filter_in=True)
            (
                [
                    {
                        "name": "I1", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                    {
                        "name": "I2", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                    {
                        "name": "I3", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                ],
                {"name": "I1", "nodeid": "emon_tools_ex1"},
                True,
                [{
                    "name": "I1", "nodeid": "emon_tools_ex1",
                    "description": "Managed Input"}],
            ),
            (
                [
                    {
                        "name": "I1", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"
                    },
                    {
                        "name": "I2", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"
                    },
                    {
                        "name": "I3", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"
                    },
                ],
                {"name": ["I1", "I2"], "nodeid": "emon_tools_ex1"},
                True,
                [
                    {
                        "name": "I1", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"
                    },
                    {
                        "name": "I2", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"
                    },
                ],
            ),
            # Test: No match (filter_in=True)
            (
                [
                    {
                        "name": "I2", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                    {
                        "name": "I3", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                ],
                {"name": "I1", "nodeid": "emon_tools_ex1"},
                True,
                [],
            ),
            # Test: Negate match (filter_in=False)
            (
                [
                    {
                        "name": "I1", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                    {
                        "name": "I2", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                    {
                        "name": "I3", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                ],
                {"name": "I1", "nodeid": "emon_tools_ex1"},
                False,
                [
                    {
                        "name": "I2", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                    {
                        "name": "I3", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                ],
            ),
            # Test: Empty filter data
            (
                [
                    {
                        "name": "I1", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                    {
                        "name": "I2", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                ],
                {},
                True,
                [],
            ),
            # Test: Empty input data
            (
                [],
                {"name": "I1", "nodeid": "emon_tools_ex1"},
                True,
                [],
            ),
            # Test: Partial key-value match
            (
                [
                    {
                        "name": "I1", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                    {
                        "name": "I2", "nodeid": "emon_tools_ex2",
                        "description": "Managed Input"},
                    {
                        "name": "I3", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                ],
                {"nodeid": "emon_tools_ex1"},
                True,
                [
                    {
                        "name": "I1", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                    {
                        "name": "I3", "nodeid": "emon_tools_ex1",
                        "description": "Managed Input"},
                ],
            ),
        ],
    )
    def test_filter_list_of_dicts(
        self,
        input_data,
        filter_data,
        filter_in, expected
    ):
        """
        Test the filter_list_of_dicts method with various scenarios.

        Args:
            input_data (list): The input list of dictionaries to filter.
            filter_data (dict): The dictionary of filter conditions.
            filter_in (bool): Whether to include or exclude matching items.
            expected (list): The expected result after filtering.
        """
        result = Utils.filter_list_of_dicts(
            input_data=input_data, filter_data=filter_data, filter_in=filter_in
        )
        assert result == expected, f"Expected {expected}, got {result}"

    def test_compute_input_list_to_string(self):
        """Test the compute_input_list_to_string method."""
        process_list = [(1, 10), (2, 20)]
        result = Utils.compute_input_list_to_string(process_list)
        assert result == "1:102:20"

        assert Utils.compute_input_list_to_string([]) == []
        assert Utils.compute_input_list_to_string(None) == []

    def test_compute_input_list_processes(self):
        """Test the compute_input_list_processes method."""
        process_list = "1:10,2:20"
        result = Utils.compute_input_list_processes(process_list)
        assert result == [(1, 10), (2, 20)]

        assert Utils.compute_input_list_processes("") == []
        assert Utils.compute_input_list_processes(None) == []

    def test_get_formatted_feed_name(self):
        """Test the get_formatted_feed_name method."""
        assert Utils.get_formatted_feed_name(
            "Node1", "Feed1") == "node:Node1:Feed1"
        assert Utils.get_formatted_feed_name("", "Feed1") is None
        assert Utils.get_formatted_feed_name("Node1", None) is None
        assert Utils.get_formatted_feed_name(None, None) is None

    def test_is_process_feed(self):
        """Test the is_process_feed method."""
        process_list = [(1, 10), (2, 20)]
        assert Utils.is_process_feed(process_list, 10) is True
        assert Utils.is_process_feed(process_list, 30) is False
        assert Utils.is_process_feed("1:10,2:20", 10) is True
        assert Utils.is_process_feed(None, 10) is False

    def test_remove_feed_from_process(self):
        """Test the remove_feed_from_process method."""
        process_list = [(1, 10), (2, 20)]
        result = Utils.remove_feed_from_process(process_list, 10)
        assert result == "2:20"

        result = Utils.remove_feed_from_process("1:10,2:20", 10)
        assert result == "2:20"

        result = Utils.remove_feed_from_process(None, 10)
        assert result == ""

    @pytest.mark.parametrize(
        (
            "feed, is_create, expected_result, "
            "is_error, expected_error, error_msg"),
        [
            (
                {
                    "tag": "Tag1",
                    "name": "Feed1",
                    "datatype": 1,
                    "engine": 1,
                    "interval": 10,
                    "public": 1,
                },
                True,
                True,
                False, None, None
            ),
            (
                {
                    "datatype": 1,
                    "engine": 1,
                    "interval": 10,
                    "public": 1,
                },
                True,
                True,
                True, ValueError,
                "Field 'name' is required"
            ),
            (
                [],
                True,
                True,
                True, ValueError,
                "Input data must be a dictionary."
            ),
            (
                {
                    "tag": "",
                    "name": "",
                    "datatype": -1,
                    "engine": -1,
                    "interval": -1,
                    "public": 2,
                },
                True,
                True,
                True, ValueError,
                "Invalid value for 'tag'"
            ),
        ],
    )
    def test_validate_feed_fields(
        self,
        feed,
        is_create,
        expected_result,
        is_error,
        expected_error,
        error_msg
    ):
        """Test the validate_feed_fields method."""
        if is_error:
            with pytest.raises(expected_error, match=error_msg):
                Utils.validate_feed_fields(
                    data=feed,
                    is_create=is_create
                )
        else:
            assert Utils.validate_feed_fields(
                data=feed,
                is_create=is_create
            ) is expected_result

    def test_validate_time_series_data_point(self):
        """Test the validate_time_series_data_point method."""
        assert Utils.validate_time_series_data_point(1672531200, 42.5) is True

        with pytest.raises(
                ValueError, match="time must be a positive integer"):
            Utils.validate_time_series_data_point(-1, 42.5)

        with pytest.raises(ValueError, match="value must be a number"):
            Utils.validate_time_series_data_point(1672531200, "not a number")
