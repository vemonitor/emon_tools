"""Files Helper utils module"""
from os import scandir
from os.path import isdir, isfile


class FilesHelper:
    """Files Helper class"""
    @staticmethod
    def is_readable_path(file_path):
        """Scan files from path"""
        return isdir(file_path)

    @staticmethod
    def scan_dir(file_path):
        """Scan files from path"""
        result = []
        if isdir(file_path):
            for file_item in scandir(file_path):
                if isfile(file_item):
                    result.append(file_item.name)
        return result
