"""FinaData API Routes Unit Tests"""
import pytest
import numpy as np
from unittest.mock import MagicMock, patch, mock_open
from struct import pack
from backend import FastAPI
from fastapi.testclient import TestClient

# Import router and dependency functions
from emon_tools.emon_fina.fina_models import FinaByTimeParamsModel
from emon_tools.emon_fina.fina_services import FileReaderProps, FinaMeta
from backend.api.routes.fina_data import router
from backend.api.deps import get_current_user, get_db
from emon_tools.emon_fina.emon_fina import FinaData
from backend.controllers.data_path import DataPathController
from backend.controllers.files import FilesController
from backend.utils.emon_fina_helper import EmonFinaHelper
from backend.utils.files import FilesHelper
from tests.emon_fina.fina_data_test import EmonFinaDataTest

# Create a FastAPI instance and include the router
app = FastAPI()
app.include_router(router)

# Override dependencies to bypass authentication and DB access in tests
app.dependency_overrides[get_current_user] = lambda: MagicMock(
    id=1, is_superuser=True, is_active=True
)
app.dependency_overrides[get_db] = lambda: MagicMock()

client = TestClient(app)


class TestFinaDataAPI:
    """
    Unit tests for the FastAPI endpoints related to financial data.
    """
    @pytest.fixture
    def tmp_path_override(self, tmp_path):
        """
        Provide a fixture for a valid temporary path
        to simulate data directory.
        """
        data_dir = tmp_path / "test_data"
        data_dir.mkdir()
        return str(data_dir)

    @pytest.fixture
    @patch("builtins.open",
           new_callable=mock_open,
           read_data=pack("<2I", 10, 1575981140))
    @patch("emon_tools.emon_fina.fina_reader.isfile", return_value=True)
    @patch("emon_tools.emon_fina.fina_reader.getsize", return_value=400)
    def fdt(self,
            mock_open_file,
            mock_isfile,
            mock_getsize,
            tmp_path_override):
        """
        Fixture to provide a valid FinaData instance for testing.
        """
        file_name = "1"
        return FinaData(
            file_name=file_name,
            data_dir=tmp_path_override
        )

    @pytest.fixture
    def mock_reader_meta(self):
        """Fixture to mock the FinaReader."""
        mock_reader = MagicMock()
        # Two days of data at 10-second intervals
        mock_reader.read_meta.return_value = FinaMeta(
            **EmonFinaDataTest.get_fina_meta()
        )
        mock_reader.DEFAULT_CHUNK_SIZE = 1024
        mock_reader.CHUNK_SIZE_LIMIT = 4096
        return mock_reader

    @pytest.fixture
    def mock_reader(self):
        """Fixture to mock the FinaReader."""
        mock_reader = MagicMock()
        # Two days of data at 10-second intervals
        mock_reader.read_meta.return_value = FinaMeta(
            **EmonFinaDataTest.get_fina_meta()
        )
        reader_props = FileReaderProps(
            meta=FinaMeta(
                **EmonFinaDataTest.get_fina_meta()
            ),
            search=FinaByTimeParamsModel(
                start_time=EmonFinaDataTest.get_time_start(),
                time_interval=10,
                time_window=3600
            )
        )
        reader_props.initialise_reader()
        mock_reader.props = reader_props
        mock_reader.DEFAULT_CHUNK_SIZE = 1024
        mock_reader.CHUNK_SIZE_LIMIT = 4096
        return mock_reader

    @pytest.fixture
    def mock_session(self):
        """
        Create a mock session object for testing purposes.

        Returns:
            MagicMock: A dummy session object.
        """
        return MagicMock()

    @pytest.fixture
    def mock_current_user(self):
        """
        Create a mock current user object for testing purposes.

        Returns:
            MagicMock: A dummy user object with superuser privileges.
        """
        user = MagicMock()
        user.id = 1
        user.is_superuser = True
        user.is_active = True
        return user

    @patch.object(DataPathController, 'get_data_path')
    @patch.object(FilesHelper, 'is_readable_path')
    def test_is_valid_source(self, mock_is_readable_path, mock_get_data_path,
                             mock_session, mock_current_user):
        """
        Test that the is_valid_source endpoint returns a success
        response for a valid data path.
        """
        # Create a dummy data path item with owner_id matching user
        item_mock = MagicMock()
        item_mock.path = "/valid/path"
        item_mock.owner_id = 1
        mock_get_data_path.return_value = item_mock
        mock_is_readable_path.return_value = True

        response = client.get(
            "/fina_data/is-valid-data-path/1/",
            headers={"Authorization": "Bearer fake_token"}
        )

        assert response.status_code == 200
        assert response.json() == {"success": True}

    @patch.object(FilesController, 'get_files_from_data_path')
    @patch.object(EmonFinaHelper, 'append_fina_data')
    @patch.object(FilesController, 'register_files')
    def test_get_files_list(self, mock_register_files, mock_append_fina_data,
                            mock_get_files_from_data_path, mock_session,
                            mock_current_user):
        """
        Test that the get_files_list endpoint returns the expected
        response with an empty file list.
        """
        mock_get_files_from_data_path.return_value = []
        mock_append_fina_data.return_value = {
            "file_path": MagicMock(id=1),
            "files": []
        }
        mock_register_files.return_value = 0

        response = client.get(
            "/fina_data/files/1/",
            headers={"Authorization": "Bearer fake_token"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "path_id": 1,
            "nb_added": 0,
            "files": []
        }

    @patch.object(FilesController, 'get_file_item')
    def test_get_file_meta(self, mock_get_file_item, mock_session,
                           mock_current_user):
        """
        Test that the get_file_meta endpoint returns the correct meta
        information for a file.
        """
        # Create a dummy file item with a dummy datapath and owner_id
        file_item_mock = MagicMock(
            file_name="file",
            datapath=MagicMock(path="/path"),
            datapath_id=1,
            emonhost_id=1
        )
        file_item_mock.owner_id = 1
        mock_get_file_item.return_value = file_item_mock
        # Patch FinaData.__init__ to set a dummy meta attribute on the
        # instance. The meta.serialize() method will return an empty dict.
        def fake_init(self, file_name, data_dir):
            """Fake FinaData init"""
            self.meta = MagicMock()
            self.meta.serialize.return_value = {
                "start_time": 1,
                "end_time": 1000,
                "interval": 10,
                "npoints": 100,
                "size": 400,
            }

        with patch.object(FinaData, '__init__', fake_init):
            response = client.get(
                "/fina_data/meta/1/",
                headers={"Authorization": "Bearer fake_token"}
            )

        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "file_id": 1,
            "datapath_id": 1,
            "emonhost_id": 1,
            "meta": {
                "start_time": 1,
                "end_time": 1000,
                "interval": 10,
                "npoints": 100,
                "size": 400,
            }
        }

    @patch.object(FilesController, 'get_file_item')
    @patch.object(FinaData, 'get_fina_values')
    def test_get_file_data(self, mock_get_fina_values, mock_get_file_item,
                           mock_session, mock_current_user):
        """
        Test that the get_file_data endpoint returns the correct file
        data when provided valid parameters.
        """
        # Create a dummy file item with proper attributes
        file_item_mock = MagicMock(
            file_name="file",
            datapath=MagicMock(path="/path"),
            datapath_id=1,
            emonhost_id=1,
            feed_id=1,
            file_id=1,
            name="name"
        )
        file_item_mock.owner_id = 1
        mock_get_file_item.return_value = file_item_mock

        def fake_init(self, file_name, data_dir):
            """Fake FinaData __init__ to inject fake meta data."""
            self.meta = MagicMock()
            self.meta.serialize.return_value = {
                "start_time": 1,
                "end_time": 1000,
                "interval": 10,
                "npoints": 100,
                "size": 400,
            }

        # Patch __init__ and get_fina_values on FinaData
        with patch.object(FinaData, '__init__', fake_init):
            with patch.object(
                FinaData, 'get_fina_values',
                return_value=np.array([[0, 1], [10, 2]])
            ):
                # Provide query parameters so that window is less than end_time
                response = client.get(
                    "/fina_data/data/1/?start=0&interval=0&window=100",
                    headers={"Authorization": "Bearer fake_token"}
                )

        # Assert the response status and content match expectations
        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "file_id": 1,
            "feed_id": 1,
            "datapath_id": 1,
            "emonhost_id": 1,
            "file_name": "file",
            "name": "name",
            "data": [[0, 1], [10, 2]]
        }

    @patch.object(FilesController, 'get_file_item')
    @patch.object(FinaData, '__init__', return_value=None)
    @patch.object(FinaData, 'meta', new_callable=MagicMock)
    @patch.object(FinaData, 'get_fina_values')
    def test_get_file_stats(self, mock_get_fina_values, mock_fina_meta,
                            mock_fina_init, mock_get_file_item,
                            mock_session, mock_current_user):
        """
        Test that the get_file_stats endpoint returns the correct stats
        for a file.
        """
        # Create a dummy file item with proper attributes
        file_item_mock = MagicMock(
            file_name="file",
            datapath=MagicMock(path="/path"),
            datapath_id=1,
            emonhost_id=1,
            feed_id=1,
            name="name"
        )
        file_item_mock.owner_id = 1
        mock_get_file_item.return_value = file_item_mock

        # Setup FinaData meta information
        mock_fina_meta.start_time = 0
        mock_fina_meta.interval = 10
        mock_fina_meta.end_time = 100
        mock_get_fina_values.return_value = np.array([[0, 1], [10, 2]])

        response = client.get(
            "/fina_data/stats/1/",
            headers={"Authorization": "Bearer fake_token"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "success": True,
            "file_id": 1,
            "feed_id": 1,
            "datapath_id": 1,
            "emonhost_id": 1,
            "file_name": "file",
            "name": "name",
            "data": [[0, 1], [10, 2]]
        }
