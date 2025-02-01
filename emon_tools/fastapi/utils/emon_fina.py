"""EmonFina Helper utils module"""
from emon_tools.fastapi.utils.files import FilesHelper
from emon_tools.emon_api.api_utils import Utils as Ut
from emon_tools.fastapi.core.config import settings


class EmonFinaHelper:
    """Files Helper class"""
    @staticmethod
    def get_files_source(
        source: str
    ) -> str:
        """Get files source path"""
        result = None
        if source == "emoncms":
            result = settings.EMON_FINA_PATH
        elif source == "archive":
            result = settings.ARCHIVE_FINA_PATH
        return result

    @staticmethod
    def scan_fina_dir(
        source: str
    ):
        """Scan files from path"""
        result = {
            "success": False,
            "message": "Unable to scan emoncms fina directory.",
        }
        file_path = EmonFinaHelper.get_files_source(
            source=source
        )
        if file_path is not None:
            files = FilesHelper.scan_dir(
                file_path=file_path
            )
            dat_files, meta_files = EmonFinaHelper.get_fina_files_structure(
                files=files
            )
            result = {
                "success": True,
                "file_path": file_path,
                "files": dat_files,
                "invalid": EmonFinaHelper.get_fina_invalid_files(
                    dat_files=dat_files,
                    meta_files=meta_files
                )
            }
        return result

    @staticmethod
    def get_fina_files_structure(files: list):
        """Get structure files"""
        dat_files, meta_files = [], []
        if Ut.is_list(files, not_empty=True):
            dat_files, meta_files = [], []
            for f in files:
                tmp = f.split('.')
                if len(tmp) == 2:
                    ext = tmp[-1]
                    if ext == 'dat':
                        dat_files.append(f)
                    elif ext == 'meta':
                        meta_files.append(f)
        return dat_files, meta_files

    @staticmethod
    def get_fina_invalid_files(
        dat_files: list,
        meta_files: list
    ):
        """Get structure files"""
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
