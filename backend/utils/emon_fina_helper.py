"""
EmonFina Helper utils module.

This module provides helper functions for managing file sources and 
file structures for EmonFina data. It includes utilities to retrieve 
file source paths based on the given source type, validate source 
directories, scan directories for files, and analyze file structures.
"""
from emon_tools.emon_fina.emon_fina import FinaData
from backend.utils.files import FilesHelper
from emon_tools.emon_api.api_utils import Utils as Ut
from backend.core.config import settings


class EmonFinaHelper:
    """
    Helper class for EmonFina file operations.

    This class provides static methods to retrieve file source paths,
    validate directories, scan directories, and determine file 
    structures for EmonFina data.
    """
    @staticmethod
    def get_files_source(
        source: str
    ) -> str:
        """
        Retrieve the file source path based on the provided source.

        Parameters:
            source (str):
                The identifier for the file source. Valid options are
                "emoncms" and "archive".

        Returns:
            str:
                The file path associated with the provided source.
                If the source is not recognized, returns None.
        """
        result = None
        if source == "emoncms":
            result = settings.EMON_FINA_PATH
        elif source == "archive":
            result = settings.ARCHIVE_FINA_PATH
        return result

    @staticmethod
    def is_valid_files_source(
        source: str
    ) -> str:
        """
        Validate if the file source directory exists and is readable.

        Parameters:
            source (str):
                The identifier for the file source.

        Returns:
            dict:
                A dictionary with a 'success' key indicating whether 
                the directory is valid and a 'message' key providing 
                additional information.
        """
        result = {
            "success": False,
            "message": "Directory is not present.",
        }
        file_path = EmonFinaHelper.get_files_source(
            source=source
        )
        if file_path is not None\
                and FilesHelper.is_readable_path(file_path):
            result = {
                "success": True,
                "message": "Valid source Directory.",
            }
        return result

    @staticmethod
    def order_fina_files(
        dat_files: list[str],
        meta_files: list[str],
        file_names: set[str]
    ) -> list:
        """
        Validate if the file source directory exists and is readable.

        Parameters:
            source (str):
                The identifier for the file source.

        Returns:
            dict:
                A dictionary with a 'success' key indicating whether
                the directory is valid and a 'message' key providing
                additional information.
        """
        result = []
        if Ut.is_list(dat_files)\
                and Ut.is_list(meta_files)\
                and Ut.is_set(file_names):
            for name in file_names:
                dat, meta = None, None
                if name in dat_files:
                    dat = f"{name}.dat"
                if name in meta_files:
                    meta = f"{name}.meta"
                result.append({
                    'file_name': name,
                    'dat_file': dat,
                    'meta_file': meta,
                    'is_valid': Ut.is_str(dat) and Ut.is_str(meta)
                })
        return result

    @staticmethod
    def scan_fina_dir(
        file_path: str
    ):
        """
        Scan the file source directory for files and determine their 
        structure.

        Parameters:
            source (str):
                The identifier for the file source.

        Returns:
            dict:
                A dictionary containing the scan results with the keys:
                - "success": A boolean indicating if scanning was 
                  successful.
                - "file_path": The path that was scanned.
                - "files": A list of '.dat' files found.
                - "invalid": A list of files that are invalid based on 
                  the expected structure.
                If scanning fails, returns a dictionary with 'success' 
                set to False and an error 'message'.
        """
        result = None
        if file_path is not None:
            files = FilesHelper.scan_dir(
                file_path=file_path
            )
            dat_files, meta_files, file_names = \
                EmonFinaHelper.get_fina_files_structure(
                    files=files
                )
            ordered = EmonFinaHelper.order_fina_files(
                dat_files=dat_files,
                meta_files=meta_files,
                file_names=file_names
            )
            result = {
                "file_path": file_path,
                "files": ordered,
                "file_names": file_names
            }
        return result

    @staticmethod
    def append_fina_data(
        files: dict
    ):
        """
        Append fina meta data to scanned files
        """
        result = None
        if Ut.is_dict(files)\
                and Ut.is_list(files.get('files'))\
                and len(files.get('files')) > 0:
            output_files = []

            for file_item in files.get('files'):
                try:
                    if file_item.get('is_valid'):
                        file_name = file_item.get('file_name')
                        fina = FinaData(
                            file_name=file_name,
                            data_dir=files.get('file_path').path
                        )
                        output_files.append({
                            "file_name": file_name,
                            "name": file_item.get('dat_file'),
                            "meta": fina.meta.serialize(),
                            "file_db": file_item.get('file_db'),
                        })
                except (ValueError, TypeError, OSError) as ex:
                    pass
            files['files'] = sorted(output_files, key=lambda d: d['name'])
            result = files
        return result

    @staticmethod
    def scan_fina_dir_by_source(
        source: str
    ):
        """
        Scan the file source directory for files and determine their 
        structure.

        Parameters:
            source (str):
                The identifier for the file source.

        Returns:
            dict:
                A dictionary containing the scan results with the keys:
                - "success": A boolean indicating if scanning was 
                  successful.
                - "file_path": The path that was scanned.
                - "files": A list of '.dat' files found.
                - "invalid": A list of files that are invalid based on 
                  the expected structure.
                If scanning fails, returns a dictionary with 'success' 
                set to False and an error 'message'.
        """
        file_path = EmonFinaHelper.get_files_source(
            source=source
        )
        return EmonFinaHelper.scan_fina_dir(
            file_path=file_path
        )

    @staticmethod
    def get_fina_files_structure(
        files: list
    ) -> tuple[list[str], list[str], set[str]]:
        """
        Separate files into '.dat' and '.meta' files based on their 
        extensions.

        Parameters:
            files (list):
                A list of filenames to analyze.

        Returns:
            tuple:
                A tuple containing two lists:
                - The first list contains filenames ending with '.dat'.
                - The second list contains filenames ending with '.meta'.
        """
        dat_files, meta_files, file_names = [], [], set()
        if Ut.is_list(files, not_empty=True):
            dat_files, meta_files = [], []
            for f in files:
                splitted = f.split('.')
                nb_items = len(splitted)
                if nb_items > 1:
                    current_name = '.'.join(splitted[0: -1])
                    ext = splitted[-1]
                    if ext == 'dat':
                        dat_files.append(current_name)
                    elif ext == 'meta':
                        meta_files.append(current_name)
                    file_names.add(current_name)
        return dat_files, meta_files, file_names

    @staticmethod
    def get_fina_invalid_files(
        dat_files: list,
        meta_files: list
    ):
        """
        Determine invalid files based on the pairing of '.dat' and 
        '.meta' files.

        Parameters:
            dat_files (list):
                A list of filenames with the '.dat' extension.
            meta_files (list):
                A list of filenames with the '.meta' extension.

        Returns:
            list:
                A list of filenames that do not have a matching pair.
                If both lists are present, returns files from the list 
                with the greater count that do not have a corresponding 
                pair in the other list. If only one type is present, 
                returns a copy of that list.
        """
        is_dat = Ut.is_list(dat_files, not_empty=True)
        is_meta = Ut.is_list(meta_files, not_empty=True)
        if is_dat and is_meta:
            bad = []
            nb_dat, nb_meta = len(dat_files), len(meta_files)
            if nb_dat >= nb_meta:
                bad = [
                    f
                    for f in dat_files
                    if f"{f.split('.')[0]}.meta" not in meta_files
                ]
            elif nb_meta >= nb_dat:
                bad = [
                    f
                    for f in meta_files
                    if f"{f.split('.')[0]}.dat" not in dat_files
                ]
            return bad

        if is_dat and not is_meta:
            return dat_files.copy()
        if not is_dat and is_meta:
            return meta_files.copy()
        return []
