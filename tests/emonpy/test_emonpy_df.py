"""Test Suite for EmonPy class."""
from unittest.mock import MagicMock
import pytest
from emon_tools.emon_api.api_utils import SUCCESS_KEY
from emon_tools.emonpy.emonpy_df import EmonDfPy
from tests.emonpy.emonpy_test_data import EmonpyDataTest as dtest


class TestEmonDfPy:
    """Unit tests for the EmonDfPy class."""

    @pytest.fixture
    def api(self):
        """Fixture to provide an EmonDfPy instance."""
        emon = EmonDfPy(url="http://example.com", api_key="123")
        emon.list_inputs_fields = MagicMock()
        emon.list_feeds = MagicMock()
        emon.create_feed = MagicMock()
        emon.post_inputs = MagicMock()
        emon.set_input_fields = MagicMock()
        emon.set_input_process_list = MagicMock()
        return emon

    def test_init(self):
        """Test initialization of EmonPy."""
        emon = EmonDfPy(url="http://example.com", api_key="123")
        assert emon.api_key == "123"
        assert emon.url == "http://example.com"
