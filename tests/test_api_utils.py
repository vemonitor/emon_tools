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

    def test_compute_response(self):
        """Test compute_response method."""
        assert Utils.compute_response(
            {"success": True, "message": "ok"}) == (True, "ok")
        assert Utils.compute_response(
            {"success": False, "message": "error"}) == (False, "error")
        assert Utils.compute_response(
            "simple message") == (True, "simple message")
        assert Utils.compute_response(
            123) == (False, "Invalid response")

    def test_filter_list_of_dicts(self):
        """Test the filter_list_of_dicts method."""
        input_data = [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value3", "key2": "value4"},
        ]
        filter_data = {"key1": "value1"}

        result = Utils.filter_list_of_dicts(
            input_data, filter_data, filter_in=True)
        assert result == [{"key1": "value1", "key2": "value2"}]

        result = Utils.filter_list_of_dicts(
            input_data, filter_data, filter_in=False)
        assert result == [{"key1": "value3", "key2": "value4"}]

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
        assert Utils.get_formatted_feed_name("Node1", "Feed1") == "node:Node1:Feed1"
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

    def test_validate_feed_fields(self):
        """Test the validate_feed_fields method."""
        valid_data = {
            "tag": "Tag1",
            "name": "Feed1",
            "datatype": 1,
            "engine": 1,
            "interval": 10,
            "public": 1,
        }

        assert Utils.validate_feed_fields(valid_data) is True

        invalid_data = {
            "tag": "",
            "name": "",
            "datatype": -1,
            "engine": -1,
            "interval": -1,
            "public": 2,
        }

        with pytest.raises(ValueError, match="Invalid value for 'tag'"):
            Utils.validate_feed_fields(invalid_data)

    def test_validate_time_series_data_point(self):
        """Test the validate_time_series_data_point method."""
        assert Utils.validate_time_series_data_point(1672531200, 42.5) is True

        with pytest.raises(ValueError, match="time must be a positive integer"):
            Utils.validate_time_series_data_point(-1, 42.5)

        with pytest.raises(ValueError, match="value must be a number"):
            Utils.validate_time_series_data_point(1672531200, "not a number")
