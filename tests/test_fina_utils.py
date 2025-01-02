"""Fina Utils unit tests module"""
import pytest
import numpy as np
from emon_tools.fina_utils import Utils


class TestUtils:
    """Unit tests for the Utils class."""

    def test_filter_values_by_range_valid(self):
        """Test filter_values_by_range with valid inputs."""
        values = np.array([1, 2, 3, 4, 5])
        result = Utils.filter_values_by_range(values, min_value=2, max_value=4)
        expected = np.array([np.nan, 2, 3, 4, np.nan])
        np.testing.assert_array_equal(result, expected)

    def test_filter_values_by_range_no_min_value(self):
        """Test filter_values_by_range with no min_value."""
        values = np.array([1, 2, 3, 4, 5])
        result = Utils.filter_values_by_range(values, max_value=4)
        expected = np.array([1, 2, 3, 4, np.nan])
        np.testing.assert_array_equal(result, expected)

    def test_filter_values_by_range_no_max_value(self):
        """Test filter_values_by_range with no max_value."""
        values = np.array([1, 2, 3, 4, 5])
        result = Utils.filter_values_by_range(values, min_value=2)
        expected = np.array([np.nan, 2, 3, 4, 5])
        np.testing.assert_array_equal(result, expected)

    def test_filter_values_by_range_no_min_max_value(self):
        """Test filter_values_by_range with no min_value and max_value."""
        values = np.array([1, 2, 3, 4, 5])
        result = Utils.filter_values_by_range(values)
        expected = np.array([1, 2, 3, 4, 5])
        np.testing.assert_array_equal(result, expected)

    def test_filter_values_by_range_invalid_values_type(self):
        """
        Test filter_values_by_range raises ValueError
        for invalid values type.
        """
        with pytest.raises(
                ValueError, match="Values must be a numpy ndarray."):
            Utils.filter_values_by_range(
                [1, 2, 3, 4, 5], min_value=2, max_value=4)

    def test_filter_values_by_range_invalid_min_max_value(self):
        """
        Test filter_values_by_range raises ValueError
        for invalid min_value and max_value.
        """
        values = np.array([1, 2, 3, 4, 5])
        with pytest.raises(
                ValueError,
                match="`min_value` must be less than `max_value`."):
            Utils.filter_values_by_range(values, min_value=4, max_value=2)
