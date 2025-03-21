import pytest
from unittest.mock import patch, MagicMock
from backend.utils.files import FilesHelper

@patch('backend.utils.files.isdir')
def test_is_readable_path(mock_isdir):
    mock_isdir.return_value = True
    assert FilesHelper.is_readable_path('/some/path')
    mock_isdir.assert_called_once_with('/some/path')

    mock_isdir.return_value = False
    assert not FilesHelper.is_readable_path('/some/other/path')
    mock_isdir.assert_called_with('/some/other/path')

@patch('backend.utils.files.scandir')
@patch('backend.utils.files.isdir')
@patch('backend.utils.files.isfile')
def test_scan_dir(mock_isfile, mock_isdir, mock_scandir):
    mock_isdir.return_value = True
    mock_file_item = MagicMock()
    mock_file_item.name = 'file1.txt'
    mock_scandir.return_value = [mock_file_item]
    mock_isfile.return_value = True

    result = FilesHelper.scan_dir('/some/path')
    assert result == ['file1.txt']
    mock_isdir.assert_called_once_with('/some/path')
    mock_scandir.assert_called_once_with('/some/path')
    mock_isfile.assert_called_once_with(mock_file_item)

    mock_isdir.return_value = False
    result = FilesHelper.scan_dir('/some/other/path')
    assert result == []
    mock_isdir.assert_called_with('/some/other/path')
