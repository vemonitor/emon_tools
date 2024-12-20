"""NpFillNan Unit Tests"""
import numpy as np
from emon_tools.fina_utils  import FillNanMethod
from emon_tools.fina_utils import NpFillNan


# Unit tests
class TestNpFillNan:
    """
    Unit tests for the NpFillNan class.

    Tests cover forward filling, interpolation, and handling of special
    cases such as empty arrays and arrays with no finite values.
    """

    def test_forward_fill_nan(self):
        """
        Test forward filling NaN values in a 1D array.
        """
        raw_array = np.array([1.0, np.nan, np.nan, 2.0, np.nan])
        expected = np.array([1.0, 1.0, 1.0, 2.0, 2.0])
        result = NpFillNan.forward_fill_nan(raw_array)
        np.testing.assert_array_equal(result, expected)

    def test_interpolate_fill_nan(self):
        """
        Test interpolation for filling NaN values in a 1D array.
        """
        raw_array = np.array([1.0, np.nan, np.nan, 4.0])
        expected = np.array([1.0, 2.0, 3.0, 4.0])
        result = NpFillNan.interpolate_fill_nan(raw_array)
        np.testing.assert_array_almost_equal(result, expected)

    def test_fill_nan_values_interpolate(self):
        """
        Test handling NaN values with interpolation in specific regions.
        """
        raw_array = np.array([np.nan, 1.0, np.nan, np.nan, 5.0, np.nan])
        expected = np.array([1.0, 1.0, 2.333333, 3.666667, 5.0, 5.0])
        result = NpFillNan.fill_nan_values(raw_array, FillNanMethod.INTERPOLATE)
        np.testing.assert_array_almost_equal(result, expected)

    def test_fill_nan_values_forward(self):
        """
        Test handling NaN values with forward filling in specific regions.
        """
        raw_array = np.array([np.nan, 1.0, np.nan, 3.0, np.nan, np.nan])
        expected = np.array([1.0, 1.0, 1.0, 3.0, 3.0, 3.0])
        result = NpFillNan.fill_nan_values(raw_array, FillNanMethod.FORWARD)
        np.testing.assert_array_equal(result, expected)

    def test_fill_nan_no_finite_values(self):
        """
        Test behavior when there are no finite values in the array.
        """
        raw_array = np.array([np.nan, np.nan, np.nan])
        expected = raw_array.copy()
        result = NpFillNan.fill_nan_values(raw_array, FillNanMethod.INTERPOLATE)
        np.testing.assert_array_equal(result, expected)

    def test_fill_nan_empty_array(self):
        """
        Test behavior with an empty array input.
        """
        raw_array = np.array([])
        expected = raw_array.copy()
        result = NpFillNan.fill_nan_values(raw_array, FillNanMethod.INTERPOLATE)
        np.testing.assert_array_equal(result, expected)

    def test_fill_nan_partial_regions(self):
        """
        Test handling NaN values in partially valid regions.
        """
        raw_array = np.array([np.nan, 2.0, np.nan, np.nan, 5.0, np.nan, np.nan])
        expected = np.array([2.0, 2.0, 3.0, 4.0, 5.0, 5.0, 5.0])
        result = NpFillNan.fill_nan_values(
            raw_array,
            method=FillNanMethod.INTERPOLATE,
            fill_before=True,
            fill_between=True,
            fill_after=True
        )
        np.testing.assert_array_almost_equal(result, expected)
