"""Fina Utils Module"""

from enum import Enum
from typing import Optional
from typing import Union
import numpy as np
from emon_tools.utils import Utils as Ut


class FillNanMethod(Enum):
    """Remove Nan Method Enum"""
    FORWARD = "forward"
    INTERPOLATE = "interpolate"


class Utils(Ut):
    """Utility class providing validation and other methods."""

    @staticmethod
    def filter_values_by_range(
        values: np.ndarray,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None
    ) -> np.ndarray:
        """
        Filter an array of values by replacing
        those outside a specified range with NaN.

        Parameters:
            values (np.ndarray): The ndarray of values to filter.
            min_value (Optional[Union[int, float]]):
                Minimum valid value. Values below this will be set to NaN.
            max_value (Optional[Union[int, float]]):
                Maximum valid value. Values above this will be set to NaN.

        Returns:
            np.ndarray:
                The filtered array with values outside
                the specified range replaced by NaN.

        Raises:
            ValueError: If `values` is not a numpy ndarray.
            ValueError: If `min_value` is greater than or equal to `max_value`.

        Example:
            >>> values = np.array([1, 2, 3, 4, 5])
            >>> filter_values_by_range(values, min_value=2, max_value=4)
            array([nan,  2.,  3.,  4., nan])
        """
        if not isinstance(values, np.ndarray):
            raise ValueError("Values must be a numpy ndarray.")

        if min_value is not None and max_value is not None:
            if min_value >= max_value:
                raise ValueError("`min_value` must be less than `max_value`.")

        mask = np.zeros_like(values, dtype=bool)
        if min_value is not None:
            mask |= values < min_value
        if max_value is not None:
            mask |= values > max_value

        values = values.astype(float)  # Ensure NaN compatibility
        values[mask] = np.nan

        return values


class NpFillNan:
    """Class for cleaning and filling NaN values in NumPy arrays."""

    @staticmethod
    def forward_fill_nan(raw_array: np.ndarray) -> np.ndarray:
        """
        Forward fill NaN values in a 1D array using the previous non-NaN value.

        Parameters:
            raw_array (np.ndarray): Input array with NaN values.

        Returns:
            np.ndarray: Array with NaN values forward-filled.
        """
        if raw_array.size > 0:
            valid_indices = np.arange(len(raw_array))
            valid_indices[np.isnan(raw_array)] = 0
            valid_indices = np.maximum.accumulate(valid_indices)
            raw_array = raw_array[valid_indices]

        return raw_array

    @staticmethod
    def interpolate_fill_nan(raw_array: np.ndarray) -> np.ndarray:
        """
        Interpolate to fill NaN values in a 1D array.

        Parameters:
            raw_array (np.ndarray): Input array with NaN values.

        Returns:
            np.ndarray: Array with NaN values interpolated.
        """
        if raw_array.size > 0:
            mask = np.isnan(raw_array)
            if mask.any():
                raw_array[mask] = np.interp(
                    np.flatnonzero(mask),
                    np.flatnonzero(~mask),
                    raw_array[~mask]
                )

        return raw_array

    @staticmethod
    def fill_nan_values(
        raw_array: np.ndarray,
        method: FillNanMethod = FillNanMethod.INTERPOLATE,
        fill_before: bool = True,
        fill_between: bool = True,
        fill_after: bool = True
    ) -> np.ndarray:
        """
        Handle NaN values in an array based on specified regions and method.

        Parameters:
            raw_array (np.ndarray):
                Input array with NaN values.
            method (FillNanMethod):
                Method to handle NaN values (INTERPOLATE or FORWARD).
            fill_before (bool):
                Whether to fill NaN values before the first non-NaN value.
            fill_between (bool):
                Whether to fill NaN values between
                the first and last non-NaN values.
            fill_after (bool):
                Whether to fill NaN values after the last non-NaN value.

        Returns:
            np.ndarray: A copy of the input array with NaN values handled.
        """
        if raw_array.size == 0:
            return raw_array.copy()

        # Create a copy of the input array to avoid modifying the original
        result_array = raw_array.copy()

        # Identify finite (non-NaN) values
        finite_mask = np.isfinite(result_array)

        # If no non-NaN values, return the array as is
        if not finite_mask.any():
            return result_array

        # Index of the first non-NaN value
        first_valid_index = np.argmax(finite_mask)
        # Index of the last non-NaN value
        last_valid_index = len(result_array) - np.argmax(finite_mask[::-1]) - 1

        # Fill before the first non-NaN value
        if fill_before and first_valid_index > 0:
            result_array[:first_valid_index] = result_array[first_valid_index]

        # Fill between the first and last non-NaN values
        if fill_between:
            between_slice = result_array[first_valid_index:last_valid_index + 1]
            if method == FillNanMethod.FORWARD:
                result_array[first_valid_index:last_valid_index + 1] = NpFillNan.forward_fill_nan(
                    between_slice)
            elif method == FillNanMethod.INTERPOLATE:
                result_array[first_valid_index:last_valid_index + 1] = NpFillNan.interpolate_fill_nan(
                    between_slice)

        # Fill after the last non-NaN value
        if fill_after and last_valid_index < len(result_array) - 1:
            result_array[last_valid_index + 1:] = result_array[last_valid_index]

        return result_array
