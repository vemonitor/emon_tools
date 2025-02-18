"""
Common utilities for Fina Files processing.
"""
from os.path import isdir, isfile, getsize
from os.path import abspath, splitext
from os.path import join as path_join
from struct import unpack
from typing import Tuple
from typing import Generator
import logging
import mmap
import numpy as np
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel
from emon_tools.emon_fina.fina_models import FinaMetaModel
from emon_tools.emon_fina.fina_services import FileReaderProps, FinaMeta
from emon_tools.emon_fina.fina_utils import Utils as Ut

logging.basicConfig()
et_logger = logging.getLogger(__name__)


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
    # Prefered number of values to read in a chunk
    # 4 B = 4096 bytes / 4 bytes = 1024 points
    DEFAULT_CHUNK_SIZE = 1024
    # Max number of values to read in a chunk
    # 64 KB = 16384 bytes / 4 bytes = 4096 points
    CHUNK_SIZE_LIMIT = 4096
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
            raise ValueError("Error: feed_id must be a positive integer.")
        if not Ut.is_str(data_dir) or not isdir(data_dir):
            raise ValueError("Error: Invalid PhpFina directory path.")

        self._feed_id = feed_id
        self._data_dir = data_dir
        self.props: FileReaderProps = None

    def _sanitize_path(self, filename: str) -> str:
        """
        Ensure that the file path is within the allowed directory
        and has a valid extension.
        """
        filepath = abspath(path_join(self._data_dir, filename))
        if not filepath.startswith(self._data_dir):
            raise ValueError(
                "Attempt to access files outside the allowed directory.")
        if splitext(filepath)[1] not in self.VALID_FILE_EXTENSIONS:
            raise ValueError("Invalid file extension.")
        return filepath

    def _validate_file_size(self, filepath: str, expected_size: int = 1024):
        """
        Ensure that the file size is within the allowed limit.
        """
        file_size = getsize(filepath)
        if file_size > expected_size:
            raise ValueError(
                "File size exceeds the limit: "
                f"{file_size} / {expected_size} bytes.")

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
        self._feed_id = Ut.validate_integer(value, "feed_id", positive=True)

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

    def read_meta(self) -> FinaMeta:
        """
        Read metadata from the .meta file.

        Returns:
            FinaMeta: Metadata object.

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
            end_time = 0
            if start_time > 0:
                end_time = start_time + (npoints * interval) - interval

            return FinaMeta(
                interval=interval,
                start_time=start_time,
                end_time=end_time,
                npoints=npoints,
                size=data_size
            )
        except Exception as e:
            raise IOError(
                f"Error reading meta file: {e}"
            ) from e

    def initialise_reader(
        self,
        meta: FinaMetaModel,
        props: FinaByTimeParamsModel,
        auto_pos: bool = True
    ):
        """
        Initialise reader props for read fina data on file
        """
        self.props = FileReaderProps(
            meta=meta,
            search=props,
            auto_pos=auto_pos
        )
        self.props.initialise_reader()

    def read_file(
        self
    ) -> Generator[Tuple[np.ndarray, np.ndarray], None, None]:
        """
        Read data values from the .dat file in chunks.

        Parameters:
            npoints (int): Total number of points in the file.
            start_pos (int):
                Starting position (index) in the file. Defaults to 0.
            chunk_size (int):
                Number of values to read in each chunk. Defaults to 1024.
            window (Optional[int]):
                Maximum number of points to read.
                If None, reads all available points.
            set_pos (bool):
                Whether to automatically increment the position after reading.

        Yields:
            Tuple[np.ndarray, np.ndarray]:
                - Array of positions (indices).
                - Array of corresponding data values.

        Raises:
            ValueError: If parameters are invalid or data reading fails.
            IOError: If file access fails.
        """
        data_path = self._get_data_path()
        self.props.current_pos = self.props.start_pos
        try:
            with open(data_path, "rb") as file:
                with mmap.mmap(
                        file.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    while self.props.has_remaining_points():
                        # Calculate current chunk size
                        current_chunk_size = self.props.iter_update_before()

                        # Compute offsets and read data
                        offset = self.props.current_pos * 4
                        end_offset = offset + current_chunk_size * 4
                        chunk_data = mm[offset:end_offset]

                        if len(chunk_data) != current_chunk_size * 4:
                            raise ValueError(
                                "Failed to read expected chunk "
                                f"at position {self.props.current_pos}. "
                                f"Expected {current_chunk_size * 4} bytes, "
                                f"got {len(chunk_data)}."
                            )

                        # Convert to values and yield
                        values = np.frombuffer(chunk_data, dtype='<f4')
                        positions = np.arange(
                            self.props.current_pos,
                            self.props.current_pos + current_chunk_size)
                        yield positions, values

                        # Update reader props
                        if self.props.auto_pos:
                            self.props.update_step_boundaries()
                            self.props.iter_update_after()

        except IOError as e:
            raise IOError(
                f"Error accessing data file at path {data_path}: {e}"
            ) from e
        except ValueError as e:
            raise ValueError(f"Data reading failed: {e}") from e
