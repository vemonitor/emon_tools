from backend.utils.emon_fina_helper import EmonFinaHelper
from backend.utils.files import FilesHelper
from backend.core.config import settings


def test_get_files_source_emoncms(monkeypatch):
    monkeypatch.setattr(settings, 'EMON_FINA_PATH', '/data/dir')
    result = EmonFinaHelper.get_files_source('emoncms')
    assert result == settings.EMON_FINA_PATH


def test_get_files_source_archive(monkeypatch):
    monkeypatch.setattr(settings, 'ARCHIVE_FINA_PATH', '/data/dir')
    result = EmonFinaHelper.get_files_source('archive')
    assert result == settings.ARCHIVE_FINA_PATH

def test_get_files_source_invalid():
    result = EmonFinaHelper.get_files_source('invalid')
    assert result is None

def test_is_valid_files_source_valid(monkeypatch):
    def mock_is_readable_path(path):
        return True

    monkeypatch.setattr(FilesHelper, 'is_readable_path', mock_is_readable_path)
    monkeypatch.setattr(settings, 'EMON_FINA_PATH', 'emoncms')
    result = EmonFinaHelper.is_valid_files_source('emoncms')
    assert result == {"success": True, "message": "Valid source Directory."}

def test_is_valid_files_source_invalid(monkeypatch):
    def mock_is_readable_path(path):
        return False

    monkeypatch.setattr(FilesHelper, 'is_readable_path', mock_is_readable_path)
    monkeypatch.setattr(settings, 'EMON_FINA_PATH', 'emoncms')
    result = EmonFinaHelper.is_valid_files_source('emoncms')
    assert result == {"success": False, "message": "Directory is not present."}

def test_scan_fina_dir_valid(monkeypatch):
    def mock_get_files_source(source):
        return 'emoncms'

    def mock_scan_dir(file_path):
        return ['1.dat', '2.meta']

    def mock_get_fina_files_structure(files):
        return (['1.dat'], ['2.meta'])

    def mock_get_fina_invalid_files(dat_files, meta_files):
        return []

    monkeypatch.setattr(EmonFinaHelper, 'get_files_source', mock_get_files_source)
    monkeypatch.setattr(FilesHelper, 'scan_dir', mock_scan_dir)
    monkeypatch.setattr(EmonFinaHelper, 'get_fina_files_structure', mock_get_fina_files_structure)
    monkeypatch.setattr(EmonFinaHelper, 'get_fina_invalid_files', mock_get_fina_invalid_files)

    result = EmonFinaHelper.scan_fina_dir('emoncms')
    assert result == {
        "success": True,
        "file_path": 'emoncms',
        "files": ['1.dat'],
        "invalid": []
    }

def test_scan_fina_dir_invalid(monkeypatch):
    def mock_get_files_source(source):
        return None

    monkeypatch.setattr(EmonFinaHelper, 'get_files_source', mock_get_files_source)
    result = EmonFinaHelper.scan_fina_dir('emoncms')
    assert result == {
        "success": False,
        "message": "Unable to scan emoncms fina directory.",
    }

def test_get_fina_files_structure_valid():
    files = ['1.dat', '2.meta']
    result = EmonFinaHelper.get_fina_files_structure(files)
    assert result == (['1.dat'], ['2.meta'], ['1', '2'])

def test_get_fina_files_structure_invalid():
    files = []
    result = EmonFinaHelper.get_fina_files_structure(files)
    assert result == ([], [], [])

def test_get_fina_invalid_files_valid():
    dat_files = ['1.dat']
    meta_files = ['1.meta']
    result = EmonFinaHelper.get_fina_invalid_files(dat_files, meta_files)
    assert result == []

def test_get_fina_invalid_files_missing_meta():
    dat_files = ['1.dat']
    meta_files = []
    result = EmonFinaHelper.get_fina_invalid_files(dat_files, meta_files)
    assert result == ['1.dat']

def test_get_fina_invalid_files_missing_dat():
    dat_files = []
    meta_files = ['1.meta']
    result = EmonFinaHelper.get_fina_invalid_files(dat_files, meta_files)
    assert result == ['1.meta']
