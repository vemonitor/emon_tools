"""
Common utilities for Fina Files processing.
"""
from os.path import isdir, isfile, getsize
from os.path import abspath, splitext
from os.path import join as path_join
from struct import unpack
from typing import Tuple
from typing import Optional
from typing import Generator
import logging
import mmap
import math
import datetime as dt
import numpy as np

from emon_tools.fina_utils import Utils

logging.basicConfig()
et_logger = logging.getLogger(__name__)


class MetaData:
    """
    Class to manage metadata with validation, serialization,
    and string representation.

    Attributes:
        interval (int): Interval between data points in seconds.
        start_time (int): Start time as a UNIX timestamp.
        npoints (int): Total number of data points.
        end_time (int): End time as a UNIX timestamp.
    """

    def __init__(self,
                 interval: int,
                 start_time: int,
                 npoints: int,
                 end_time: int
                 ):
        """
        Initialize the MetaData instance.

        Parameters:
            interval (int): Interval between data points in seconds.
            start_time (int): Start time as a UNIX timestamp.
            npoints (int): Total number of data points.
            end_time (int): End time as a UNIX timestamp.

        Raises:
            ValueError:
                If any parameter is invalid or start_time is not less than end_time.
        """
        self.interval = interval
        self.start_time = start_time
        self.npoints = npoints
        self.end_time = end_time

    def _validate_date_order(self):
        """
        Ensure that start_time precedes end_time.

        Raises:
            ValueError: If start_time is not less than end_time.
        """
        if self._start_time >= self._end_time:
            raise ValueError("start_time must be less than end_time.")

    @property
    def interval(self) -> int:
        """
        Get the interval between data points in seconds.

        Returns:
            int: Interval in seconds.
        """
        return self._interval

    @interval.setter
    def interval(self, value: int):
        """
        Set the interval between data points in seconds.

        Parameters:
            value (int): Interval in seconds.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        self._interval = Utils.validate_integer(value, "interval", positive=True)

    @property
    def start_time(self) -> int:
        """
        Get the start time as a UNIX timestamp.

        Returns:
            int: Start time in seconds since the epoch.
        """
        return self._start_time

    @start_time.setter
    def start_time(self, value: int):
        """
        Set the start time as a UNIX timestamp.

        Parameters:
            value (int): Start time in seconds since the epoch.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        self._start_time = Utils.validate_timestamp(value, "start_time")
        if hasattr(self, "_end_time"):
            self._validate_date_order()

    @property
    def npoints(self) -> int:
        """
        Get the total number of data points.

        Returns:
            int: Number of data points.
        """
        return self._npoints

    @npoints.setter
    def npoints(self, value: int):
        """
        Set the total number of data points.

        Parameters:
            value (int): Number of data points.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        self._npoints = Utils.validate_integer(value, "npoints", positive=True)

    @property
    def end_time(self) -> int:
        """
        Get the end time as a UNIX timestamp.

        Returns:
            int: End time in seconds since the epoch.
        """
        return self._end_time

    @end_time.setter
    def end_time(self, value: int):
        """
        Set the end time as a UNIX timestamp.

        Parameters:
            value (int): End time in seconds since the epoch.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        self._end_time = Utils.validate_timestamp(value, "end_time")
        if hasattr(self, "_start_time"):
            self._validate_date_order()

    def calculate_nb_days(self) -> int:
        """
        Calculate the number of days covered by the data.

        Returns:
            int: Number of days.
        """
        start = dt.datetime.fromtimestamp(self._start_time, dt.timezone.utc)
        end = dt.datetime.fromtimestamp(self._end_time, dt.timezone.utc)
        delta = (end - start).total_seconds() / (3600 * 24)
        return math.ceil(delta)

    def serialize(self) -> dict:
        """
        Serialize the metadata into a dictionary.

        Returns:
            dict: Serialized metadata.
        """
        return {
            "interval": self._interval,
            "start_time": self._start_time,
            "npoints": self._npoints,
            "end_time": self._end_time,
        }

    def __str__(self) -> str:
        return f"{self.serialize()}"


class FinaReader:
    """
    Class to handle the reading of Fina data files and associated metadata.

    Attributes:
        feed_id (int): Identifier for the data feed.
        data_dir (str): Directory containing the Fina data files.
        pos (int): Current read position in the data file.
    """

    MAX_DATA_SIZE = 100 * 1024 * 1024  # 100 MB limit for files
    MAX_META_SIZE = 1024  # 1Kb limit for files
    CHUNK_SIZE_LIMIT = 4096  # Max number of values to read in a chunk
    VALID_FILE_EXTENSIONS = {".dat", ".meta"}

    def __init__(self, feed_id: int, data_dir: str):
        """
        Initialize the FinaReader instance.

        Parameters:
            feed_id (int): Identifier for the data feed.
            data_dir (str): Directory containing the Fina data files.

        Raises:
            ValueError: If feed_id is not positive or data_dir is invalid.
        """
        if feed_id <= 0:
            raise ValueError("feed_id must be a positive integer.")
        if not isdir(data_dir):
            raise ValueError(f"{data_dir} is not a valid directory.")

        self._feed_id = feed_id
        self._data_dir = data_dir
        self._pos = 0
        self._chunk_size = 0

    def _sanitize_path(self, filename: str) -> str:
        """
        Ensure that the file path is within the allowed directory and has a valid extension.
        """
        filepath = abspath(path_join(self._data_dir, filename))
        if not filepath.startswith(self._data_dir):
            raise ValueError("Attempt to access files outside the allowed directory.")
        if splitext(filepath)[1] not in self.VALID_FILE_EXTENSIONS:
            raise ValueError("Invalid file extension.")
        return filepath

    def _validate_file_size(self, filepath: str, expected_size: int = 1024):
        """
        Ensure that the file size is within the allowed limit.
        """
        file_size = getsize(filepath)
        if file_size > expected_size:
            raise ValueError(f"File size exceeds the limit: {file_size} / {expected_size} bytes.")

    def _get_base_path(self) -> str:
        return path_join(self._data_dir, str(self._feed_id))

    def _get_meta_path(self) -> str:
        file_path = f"{self._get_base_path()}.meta"
        file_path = self._sanitize_path(file_path)
        if not isfile(file_path):
            raise FileNotFoundError(f"Meta file does not exist: {file_path}")
        self._validate_file_size(file_path, self.MAX_META_SIZE)
        return file_path

    def _get_data_path(self) -> str:
        file_path = f"{self._get_base_path()}.dat"
        file_path = self._sanitize_path(file_path)
        if not isfile(file_path):
            raise FileNotFoundError(f"Data file does not exist: {file_path}")
        self._validate_file_size(file_path, self.MAX_DATA_SIZE)
        return file_path

    def _validate_read_params(
        self,
        npoints: int,
        start_pos: int,
        chunk_size: int,
        window: Optional[int],
    ) -> int:
        """
        Validate read parameters and calculate total points to process.

        Parameters:
            npoints (int): Total number of points in the file.
            start_pos (int): Starting position (index) in the file.
            chunk_size (int): Number of values to read per chunk.
            window (Optional[int]): Maximum number of points to read.

        Returns:
            int: Total points to process based on input parameters.

        Raises:
            ValueError: If parameters are invalid.
        """
        npoints = Utils.validate_integer(npoints, "npoints", positive=True)
        self.chunk_size = Utils.validate_integer(chunk_size, "chunk_size", positive=True)

        if not isinstance(start_pos, int) or start_pos < 0:
            raise ValueError(f"start_pos ({start_pos}) must be an integer upper or equal to zero.")

        if start_pos >= npoints:
            raise ValueError(f"start_pos ({start_pos}) exceeds total npoints ({npoints}).")

        if window is not None:
            window = Utils.validate_integer(window, "window", positive=True)
            total_points = min(npoints - start_pos, window)
        else:
            total_points = npoints - start_pos

        return total_points

    @property
    def feed_id(self) -> int:
        """
        Get the identifier for the data feed.

        Returns:
            int: Data feed identifier.
        """
        return self._feed_id

    @feed_id.setter
    def feed_id(self, value: int):
        """
        Set the identifier for the data feed.

        Parameters:
            value (int): Data feed identifier.

        Raises:
            ValueError: If the value is not a positive integer.
        """
        self._feed_id = Utils.validate_integer(value, "feed_id", positive=True)

    @property
    def data_dir(self) -> str:
        """
        Get the directory containing the Fina data files.

        Returns:
            str: Directory path.
        """
        return self._data_dir

    @data_dir.setter
    def data_dir(self, value: str):
        """
        Set the directory containing the Fina data files.

        Parameters:
            value (str): Directory path.

        Raises:
            ValueError: If the directory is invalid.
        """
        if not isdir(value):
            raise ValueError("data_dir must be a valid directory.")
        self._data_dir = value

    @property
    def pos(self) -> str:
        """
        Get the current read position in the data file.

        Returns:
            int: Current read position.
        """
        return self._pos

    @pos.setter
    def pos(self, value: str):
        """
        Set the current read position in the data file.

        Parameters:
            value (int): Read position.

        Raises:
            ValueError: If the position is negative.
        """
        if value < 0:
            raise ValueError("pos must be a positive integer.")
        self._pos = value

    @property
    def chunk_size(self) -> str:
        """
        Get the current read chunk_size in the data file.

        Returns:
            int: Current read chunk_size.
        """
        return self._chunk_size

    @chunk_size.setter
    def chunk_size(self, value: str):
        """
        Set the current read chunk_size in the data file.

        Parameters:
            value (int): Read chunk_size.

        Raises:
            ValueError: If the chunk_size is negative.
        """
        self._chunk_size = max(
            Utils.validate_integer(value, "chunk_size", positive=True),
            self.CHUNK_SIZE_LIMIT
        )

    def read_meta(self) -> MetaData:
        """
        Read metadata from the .meta file.

        Returns:
            MetaData: Metadata object.

        Raises:
            IOError: If there is an issue reading the meta file.
        """
        try:
            with open(self._get_meta_path(), "rb") as file:
                file.seek(8)
                hexa = file.read(8)
                if len(hexa) != 8:
                    raise ValueError("Meta file is corrupted.")
                interval, start_time = unpack("<2I", hexa)

            data_size = getsize(self._get_data_path())
            npoints = data_size // 4
            end_time = start_time + npoints * interval - interval

            return MetaData(interval, start_time, npoints, end_time)
        except Exception as e:
            raise IOError(
                f"Error reading meta file: {e}"
            ) from e

    def read_file(
        self,
        npoints: int,
        start_pos: int = 0,
        chunk_size: int = 1024,
        window: Optional[int] = None,
        set_pos: bool = True,
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Read data values from the .dat file in chunks.

        Parameters:
            npoints (int): Total number of points in the file.
            start_pos (int): Starting position (index) in the file. Defaults to 0.
            chunk_size (int): Number of values to read in each chunk. Defaults to 1024.
            window (Optional[int]): 
                Maximum number of points to read.
                If None, reads all available points.
            set_pos (bool): Whether to automatically increment the position after reading.

        Yields:
            Tuple[np.ndarray, np.ndarray]: 
                - Array of positions (indices).
                - Array of corresponding data values.

        Raises:
            ValueError: If parameters are invalid or data reading fails.
            IOError: If file access fails.
        """
        # Validate inputs and compute total points to read
        total_points = self._validate_read_params(
            npoints=npoints,
            start_pos=start_pos,
            chunk_size=chunk_size,
            window=window
        )

        data_path = self._get_data_path()
        self._pos = start_pos

        try:
            with open(data_path, "rb") as file:
                with mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    while self._pos < start_pos + total_points:
                        # Calculate current chunk size
                        remaining_points = start_pos + total_points - self._pos
                        current_chunk_size = min(self.chunk_size, remaining_points)

                        # Compute offsets and read data
                        offset = self._pos * 4
                        end_offset = offset + current_chunk_size * 4
                        chunk_data = mm[offset:end_offset]

                        if len(chunk_data) != current_chunk_size * 4:
                            raise ValueError(
                                f"Failed to read expected chunk at position {self._pos}. "
                                f"Expected {current_chunk_size * 4} bytes, got {len(chunk_data)}."
                            )

                        # Convert to values and yield
                        values = np.frombuffer(chunk_data, dtype='<f4')
                        positions = np.arange(self._pos, self._pos + current_chunk_size)
                        yield positions, values

                        # Increment position
                        if set_pos:
                            self._pos += current_chunk_size

        except IOError as e:
            raise IOError(
                f"Error accessing data file at path {data_path}: {e}"
            ) from e
        except ValueError as e:
            raise ValueError(f"Data reading failed: {e}") from e
