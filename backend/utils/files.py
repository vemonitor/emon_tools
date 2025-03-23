"""
Files Helper utils module.

This module provides utility functions to assist with file operations,
such as checking if a path is a directory and scanning a directory for
files.
"""
from os import scandir
from os.path import isdir, isfile, getsize, splitext


class FilesHelper:
    """
    Utility class for file operations.

    This class provides static methods to determine if a given path is a
    directory and to scan a directory for files.
    """
    ALLOWED_IMG_MIME_TYPES = {"image/jpeg", "image/png", "image/gif"}
    ALLOWED_IMG_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
    MAX_IMG_FILE_SIZE = 2 * 1024 * 1024  # e.g., 2MB size limit

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Get the file extension from the provided filename.
        """
        return splitext(filename)[1].lower()

    @staticmethod
    def is_readable_path(file_path):
        """
        Check if the provided path is a directory.

        Parameters:
            file_path (str): The path to check.

        Returns:
            bool: True if the path is a directory, False otherwise.
        """
        return isdir(file_path)

    @staticmethod
    def scan_dir(file_path) -> list:
        """
        Scan the specified directory for files.

        Parameters:
            file_path (str): The directory path to scan.

        Returns:
            list: A list of file names found in the directory.
        """
        result = []
        if isdir(file_path):
            for file_item in scandir(file_path):
                if isfile(file_item):
                    result.append(file_item.name)
        return result

    @staticmethod
    def get_path_file_sizes(file_path) -> int:
        """
        Scan the specified directory and get sum of file sizes.

        Parameters:
            file_path (str): The directory path to scan.

        Returns:
            int: Sum of sizes of all files in current path.
        """
        result = 0
        if isdir(file_path):
            for file_item in scandir(file_path):
                if isfile(file_item):
                    result += getsize(file_item)
        return result
