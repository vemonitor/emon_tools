"""
Unit tests for the FinaDataResult class.

This module contains pytest-based tests for the FinaDataResult class, which
provides methods to represent results as a pandas DataFrame or plot them using
matplotlib.
"""
# pylint: disable=unused-argument,protected-access,unused-import
from unittest.mock import patch, mock_open, MagicMock
from struct import pack
import numpy as np
import pandas as pd
import pytest
from emon_tools.fina_time_series import FinaDataFrame
from emon_tools.fina_time_series import FinaDfStats
from emon_tools.fina_plot import FinaPlot
from emon_tools.fina_plot import PlotData
from emon_tools.fina_plot import PlotStats


class TestPlotData:
    """
    Unit tests for the PlotData class.
    """

    @pytest.fixture
    def sample_data(self):
        """
        Provide a fixture for sample time and value data.
        """
        times = np.array([1640995200, 1640995300, 1640995400])  # Example timestamps
        values = np.array([1.5, 2.3, 3.7])  # Example values
        return np.vstack((times, values)).T

    @pytest.fixture
    def sample_data_frame(self):
        """
        Provide a fixture for sample time and value data.
        """
        times = np.array([1640995200, 1640995300, 1640995400])  # Example timestamps
        values = np.array([1.5, 2.3, 3.7])  # Example values
        return FinaDataFrame.set_data_frame(times, values)

    @patch("emon_tools.fina_plot.plt.show")
    def test_plot_with_pandas(self, mock_show, sample_data_frame):
        """
        Test the plot method when pandas and matplotlib are available.
        """
        PlotData.plot(sample_data_frame)
        mock_show.assert_called_once()

    @patch("emon_tools.fina_plot.plt.show")
    def test_plot_without_pandas(self, mock_show, sample_data):
        """
        Test the plot method when only matplotlib is available.
        """
        PlotData.plot(sample_data)
        mock_show.assert_called_once()


class TestPlotStats:
    """
    Unit tests for the PlotStats class.
    """

    @pytest.fixture
    def sample_data_integrity(self):
        """
        Provide a fixture for sample time and integrity data.
        """
        # Example timestamps
        times = np.array([1640995200, 1640995300, 1640995400])
        # Example values
        nb_finite = np.array([1.5, 2.3, 3.7])
        nb_total = np.array([2, 3.3, 4.7])
        return np.vstack((times, nb_finite, nb_total)).T

    @pytest.fixture
    def sample_df_integrity(self):
        """
        Provide a fixture for sample time and integrity data.
        """
        df = pd.DataFrame({
            "time": [1640995200, 1640995300, 1640995400],
            "nb_finite": [1.5, 2.3, 3.7],
            "nb_total": [2, 3.3, 4.7]
        })
        return df.set_index(pd.to_datetime(df['time'], unit='s', utc=True))

    @pytest.fixture
    def sample_data_values(self):
        """
        Provide a fixture for sample time and value data.
        """
        # Example timestamps
        times = np.array([1640995200, 1640995300, 1640995400])
        # Example values
        mins = np.array([1.5, 2.3, 3.7])
        means = np.array([2, 3.3, 4.7])
        maxs = np.array([3, 4.3, 5.7])
        return np.vstack((times, mins, means, maxs)).T

    @pytest.fixture
    def sample_df_values(self):
        """
        Provide a fixture for sample time and value data.
        """
        times = np.array([1640995200, 1640995300, 1640995400])  # Example timestamps
        mins = np.array([1.5, 2.3, 3.7])
        means = np.array([2, 3.3, 4.7])
        maxs = np.array([3, 4.3, 5.7])
        df = pd.DataFrame({
            "time": times,
            "min": mins,
            "mean": means,
            "max": maxs
        })
        return df.set_index(pd.to_datetime(df['time'], unit='s', utc=True))

    @patch("emon_tools.fina_plot.plt.show")
    def test_plot_values_with_pandas(self, mock_show, sample_df_values):
        """
        Test the plot method when pandas and matplotlib are available.
        """
        PlotStats.plot_values(sample_df_values)
        mock_show.assert_called_once()

    @patch("emon_tools.fina_plot.plt.show")
    def test_plot_values_without_pandas(self, mock_show, sample_data_values):
        """
        Test the plot method when only matplotlib is available.
        """
        PlotStats.plot_values(sample_data_values)
        mock_show.assert_called_once()

    @patch("emon_tools.fina_plot.plt.show")
    def test_plot_integrity_with_pandas(self, mock_show, sample_data_integrity):
        """
        Test the plot method when pandas and matplotlib are available.
        """
        PlotStats.plot_integrity(sample_data_integrity)
        mock_show.assert_called_once()

    @patch("emon_tools.fina_plot.plt.show")
    def test_plot_integrity_without_pandas(self, mock_show, sample_df_integrity):
        """
        Test the plot method when only matplotlib is available.
        """
        PlotStats.plot_integrity(sample_df_integrity)
        mock_show.assert_called_once()
