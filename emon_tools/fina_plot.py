"""
fina_plot_helper.py

This module provides utility classes and methods for visualizing financial and statistical data 
using matplotlib and pandas. It includes tools for plotting grids, time-series data, and statistical
summaries in a clean and efficient manner.

Dependencies:
- numpy
- pandas
- matplotlib
"""
from typing import Union
import numpy as np

try:
    import pandas as pd
except ImportError as e:
    raise ImportError(
        "Pandas is required for this module. Install it with `pip install pandas`."
    ) from e

try:
    import matplotlib.pyplot as plt
    from matplotlib import ticker
except ImportError as e:
    raise ImportError(
        "Matplotlib is required for this module. "
        "Install it with `pip install matplotlib`."
    ) from e



class FinaPlot:
    """
    A base class for plot helpers, providing utility functions to enhance matplotlib visualizations.

    This class offers methods to set up grid styles and other shared plotting configurations.
    """
    @staticmethod
    def auto_plot_grid(
        x_grid: bool = False,
        x_major: bool = True,
        x_minor: bool = True,
        y_grid: bool = False,
        y_major: bool = True,
        y_minor: bool = True
    ):
        """
        Configure and enable gridlines for the current matplotlib plot.

        Parameters:
            x_grid (bool): Whether to enable gridlines for the x-axis. Defaults to False.
            x_major (bool): Whether to enable major ticks on the x-axis. Defaults to True.
            x_minor (bool): Whether to enable minor ticks on the x-axis. Defaults to True.
            y_grid (bool): Whether to enable gridlines for the y-axis. Defaults to False.
            y_major (bool): Whether to enable major ticks on the y-axis. Defaults to True.
            y_minor (bool): Whether to enable minor ticks on the y-axis. Defaults to True.
        """
        ax=plt.gca()
        ax.grid(True)
        if x_grid:
            if x_major:
                ax.xaxis.set_major_locator(ticker.AutoLocator())
            if x_minor:
                ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
        if y_grid:
            if y_major:
                ax.yaxis.set_major_locator(ticker.AutoLocator())
            if y_minor:
                ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)


class PlotData(FinaPlot):
    """
    A class for plotting time-series data,
    providing utilities for FinaData and FinaDfResult objects.
    """

    @staticmethod
    def plot(data: Union[np.ndarray, pd.DataFrame]):
        """
        Plot a dataset using matplotlib.

        Parameters:
            data (Union[np.ndarray, pd.DataFrame]): The data to be plotted. Can be a NumPy array 
                (with time and values) or a Pandas DataFrame with 'values'.

        Raises:
            ImportError: If matplotlib is not installed.
        """
        plt.figure(figsize=(18, 6))
        plt.subplot(1, 1, 1)
        if isinstance(data, np.ndarray):
            plt.plot(data[:, 0], data[:, 1], label="Fina Values")
        else:
            plt.plot(data.index, data['values'], label="Fina Values")
        plt.title("Fina Values")
        plt.xlabel("Time")
        plt.ylabel("Values")
        FinaPlot.auto_plot_grid(x_grid=True, y_grid=True)
        plt.show()


class PlotStats(FinaPlot):
    """
    A class for visualizing statistical summaries, tailored for FinaStats and FinaDfStats objects.
    """

    @staticmethod
    def plot_values(data: Union[np.ndarray, pd.DataFrame]):
        """
        Plot statistical data, including mean and min-max ranges.

        Parameters:
            data (Union[np.ndarray, pd.DataFrame]):
                The statistical data to plot. Can be a NumPy array 
                or a Pandas DataFrame containing columns
                for mean, min, and max values.

        Raises:
            ImportError: If matplotlib is not installed.
        """
        plt.figure(figsize=(18, 6))
        plt.subplot(1, 1, 1)
        if isinstance(data, np.ndarray):
            plt.plot(data[:, 0], data[:, 1], label="Fina Stats Values")
            plt.fill_between(data[:, 0], data[:, 1], data[:, 3], alpha=0.2, label='Daily values min-max range')
            plt.plot(data[:, 0], data[:, 2], label='Daily mean values', lw=2)
        else:
            plt.fill_between(
                data.index,
                data['min'],
                data['max'],
                alpha=0.2,
                label='Daily values min-max range')
            plt.plot(data.index, data['mean'], label='Daily mean values', lw=2)
        plt.title("Fina Stats Values")
        plt.ylabel("Daily Values")
        plt.xlabel("time")

        FinaPlot.auto_plot_grid(x_grid=True, y_grid=True)
        plt.show()

    @staticmethod
    def plot_integrity(data: Union[np.ndarray, pd.DataFrame]):
        """
        Plot data integrity statistics, including daily points and finite values.

        Parameters:
            data (Union[np.ndarray, pd.DataFrame]): The integrity data to plot. Can be a NumPy array 
                or a Pandas DataFrame containing columns for finite values and total points.

        Raises:
            ImportError: If matplotlib is not installed.
        """
        color_y1 = "#780000"
        color_y2 = "#003049"
        color_fill = "#fb5607"

        plt.figure(figsize=(18, 6))
        plt.subplot(1, 1, 1)
        ax=plt.gca()
        ax.grid(which='minor', alpha=0.2)
        ax.grid(which='major', alpha=0.5)
        ax.set_ylabel("Daily Points", color=color_y1)
        ax.tick_params(axis="y", labelcolor=color_y1)
        ax.set_xlabel("time")
        if isinstance(data, np.ndarray):
            ax.plot(data[:, 0], data[:, 1] * 100 / data[:, 2],
                    label='Daily nb_finite (%)',
                    lw=3,
                    color=color_y1)
            ax2 = ax.twinx()
            ax2.set_ylabel("Daily Points (%)", color=color_y2)
            ax2.tick_params(axis="y", labelcolor=color_y2)
            ax2.plot(data[:, 0], data[:, 1],
                    label='Daily mean nb_finite values',
                    lw=3,
                    color=color_y2)
            ax2.fill_between(data[:, 0], 0, data[:, 2], alpha=0.2, label='Daily min-max nb_points',
                    color=color_fill)
        else:
            ax.plot(data.index, data['nb_finite'] * 100 / data['nb_total'],
                    label='Daily nb_finite (%)',
                    lw=3,
                    color=color_y1)
            ax2 = ax.twinx()
            ax2.set_ylabel("Daily Points (%)", color=color_y2)
            ax2.tick_params(axis="y", labelcolor=color_y2)
            ax2.plot(data.index, data['nb_finite'],
                    label='Daily mean nb_finite values',
                    lw=3,
                    color=color_y2)
            ax2.fill_between(
                data.index,
                0,
                data['nb_total'],
                alpha=0.2,
                label='Daily min-max nb_points',
                color=color_fill)
        ax2.legend()
        plt.title("Fina File Integrity Stats")

        FinaPlot.auto_plot_grid(x_grid=True, y_grid=False)
        plt.show()
