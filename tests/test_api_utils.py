"""Tests for emon_tools.api_utils module."""
from emon_tools.api_utils import Utils


class TestApiUtils:
    """Tests for Utils class."""

    def test_is_str(self):
        """Test is_str method."""
        assert Utils.is_str("hello") is True
        assert Utils.is_str("") is True
        assert Utils.is_str("", not_empty=True) is False
        assert Utils.is_str(123) is False

    def test_is_list(self):
        """Test is_list method."""
        assert Utils.is_list(["hello"]) is True
        assert Utils.is_list([]) is True
        assert Utils.is_list([], not_empty=True) is False
        assert Utils.is_list("not a list") is False

    def test_is_dict(self):
        """Test is_dict method."""
        assert Utils.is_dict({"key": "value"}) is True
        assert Utils.is_dict({}) is True
        assert Utils.is_dict({}, not_empty=True) is False
        assert Utils.is_dict("not a dict") is False

    def test_is_valid_node(self):
        """Test is_valid_node method."""
        assert Utils.is_valid_node("Node1") is True
        assert Utils.is_valid_node("") is False
        assert Utils.is_valid_node(123) is False
        assert Utils.is_valid_node("Node@1") is True

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
