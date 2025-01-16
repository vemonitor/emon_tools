"""emon_api unit test module."""
from unittest.mock import patch, MagicMock
import pytest
import requests
from emon_tools.api_utils import MESSAGE_KEY, SUCCESS_KEY
from emon_tools.emon_api_core import RequestType
from emon_tools.emon_api_core import InputGetType
from emon_tools.emon_api import EmonRequest
from emon_tools.emon_api import EmonInputsApi
from emon_tools.emon_api import EmonFeedsApi

VALID_URL = "http://example.com"
API_KEY = "testAPIKey123"
MOCK_RESPONSE_SUCCESS = {"success": True, "message": "Request succeeded"}
MOCK_RESPONSE_FAIL = {"success": False, "message": "Request failed"}


class TestEmonRequest:
    """Unit test class for EmonRequest."""

    @pytest.fixture
    def emon_request(self):
        """Fixture to initialize an EmonRequest instance."""
        return EmonRequest(VALID_URL, API_KEY)

    @pytest.mark.parametrize(
        "path,expected_url",
        [
            ("/feed/list.json", "http://example.com/feed/list.json"),
            ("feed/list.json", "http://example.com/feed/list.json"),
        ],
    )
    def test_execute_request_path_validation(
        self,
        path,
        expected_url,
        emon_request
    ):
        """Test that the URL is correctly formed."""
        with patch("emon_tools.emon_api.requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = MOCK_RESPONSE_SUCCESS
            mock_get.return_value = mock_response

            emon_request.execute_request(path=path, msg="test path validation")

            mock_get.assert_called_once_with(
                expected_url,
                params={"apikey": API_KEY},
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "charset": "UTF-8",
                },
                timeout=20,
            )

    @pytest.mark.parametrize(
        "status_code,expected_success,expected_message",
        [
            (200, True, "Request succeeded"),
            (
                404,
                False,
                "HTTP test error 404: Not found"
            ),
        ],
    )
    def test_compute_response(
        self,
        status_code,
        expected_success,
        expected_message,
        emon_request
    ):
        """Test response computation."""
        response_mock = MagicMock()
        response_mock.status_code = status_code
        response_mock.json.return_value = (
            MOCK_RESPONSE_SUCCESS if status_code == 200 else MOCK_RESPONSE_FAIL
        )
        with patch(
                "emon_tools.emon_api_core.EmonRequestCore.compute_response",
                return_value={
                    SUCCESS_KEY: expected_success,
                    MESSAGE_KEY: expected_message}
                ):
            result = emon_request.compute_response(
                response_mock, msg="test error")
            assert result[SUCCESS_KEY] == expected_success
            assert result[MESSAGE_KEY] == expected_message

    def test_execute_request_invalid_path(self, emon_request):
        """Test that invalid paths raise a ValueError."""
        with pytest.raises(
                ValueError, match="Path must be a non-empty string."):
            emon_request.execute_request(path=None, msg="Invalid path")

    @pytest.mark.parametrize(
        "params,expected_params",
        [
            (None, {"apikey": API_KEY}),
            ({"key": "value"}, {"apikey": API_KEY, "key": "value"}),
        ],
    )
    def test_execute_request_params_encoding(
        self,
        emon_request,
        params,
        expected_params
    ):
        """Test parameter encoding."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = MOCK_RESPONSE_SUCCESS
            mock_get.return_value = mock_response

            emon_request.execute_request(
                path="/feed/list.json",
                params=params,
                msg="test params encoding")

            mock_get.assert_called_once_with(
                "http://example.com/feed/list.json",
                params=expected_params,
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "charset": "UTF-8",
                },
                timeout=20,
            )

    def test_execute_request_timeout(self, emon_request):
        """Test handling of request timeouts."""
        with patch("requests.get", side_effect=requests.exceptions.Timeout):
            result = emon_request.execute_request(
                path="/feed/list.json", msg="test_timeout")
            assert not result["success"]
            assert result["message"] == "Request timeout: test_timeout."

    def test_execute_request_connection_error(self, emon_request):
        """Test handling of connection errors."""
        with patch(
                "requests.get",
                side_effect=requests.exceptions.ConnectionError(
                    "Connection error")):
            result = emon_request.execute_request(
                path="/feed/list.json", msg="test connection error")
            assert not result["success"]
            assert "Connection error" in result["message"]

    @pytest.mark.parametrize(
            "request_type", [RequestType.GET, RequestType.POST])
    def test_execute_request_request_type(self, emon_request, request_type):
        """Test execution for different request types."""
        with patch(
                "requests.get"
                if request_type == RequestType.GET
                else "requests.post") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = MOCK_RESPONSE_SUCCESS
            mock_request.return_value = mock_response

            emon_request.execute_request(
                path="/feed/list.json",
                msg="test request type",
                request_type=request_type
            )

            mock_request.assert_called_once()


class TestEmonInputsApi:
    """Unit test class for EmonInputsApi."""

    @pytest.fixture
    def emon_inputs_api(self):
        """Fixture to initialize an EmonInputsApi instance."""
        return EmonInputsApi(VALID_URL, API_KEY)

    def test_list_inputs(self, emon_inputs_api):
        """Test listing inputs."""
        with patch.object(
                emon_inputs_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_inputs_api.list_inputs(node="test_node")
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                "/input/get/test_node",
                msg="get list inputs"
            )

    @pytest.mark.parametrize(
        "get_type,expected_path",
        [
            (InputGetType.PROCESS_LIST, "/input/getinputs"),
            (InputGetType.EXTENDED, "/input/list"),
        ],
    )
    def test_list_inputs_fields(
        self,
        emon_inputs_api,
        get_type, expected_path
    ):
        """Test listing input fields."""
        with patch.object(
                emon_inputs_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_inputs_api.list_inputs_fields(get_type=get_type)
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                expected_path, msg="get list inputs fields")

    def test_get_input_fields(self, emon_inputs_api):
        """Test retrieving specific input fields."""
        with patch.object(
                emon_inputs_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_inputs_api.get_input_fields(
                node="node1", name="input1")
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                "/input/get/node1/input1",
                msg="get list inputs fields"
            )

    def test_set_input_fields(self, emon_inputs_api):
        """Test setting input fields."""
        with patch.object(
                emon_inputs_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_inputs_api.set_input_fields(
                input_id=1, fields={"key": "value"})
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/input/set',
                params={"inputid": 1, "fields": {"key": "value"}},
                msg="Set input fields",
                request_type=RequestType.GET
            )

    def test_set_input_process_list(self, emon_inputs_api):
        """Test setting input process list."""
        with patch.object(
                emon_inputs_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_inputs_api.set_input_process_list(
                input_id=1, process_list="test_process")
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/input/process/set',
                params={"inputid": 1},
                data={"processlist": "test_process"},
                msg="Set input process list",
                request_type=RequestType.POST
            )

    def test_post_inputs(self, emon_inputs_api):
        """Test posting input data."""
        with patch.object(
                emon_inputs_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            with patch(
                    "simplejson.dumps", side_effect=lambda x: '{"key": 123}'):
                result = emon_inputs_api.post_inputs(
                    node="test_node", data={"key": 123})
                assert result == MOCK_RESPONSE_SUCCESS
                mock_request.assert_called_once_with(
                    path='/input/post',
                    params={"node": "test_node", "fulljson": {'key': 123}},
                    msg="Add input data point",
                    request_type=RequestType.GET
                )

    def test_input_bulk(self, emon_inputs_api):
        """Test posting input data."""
        with patch.object(
                emon_inputs_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:

            result = emon_inputs_api.input_bulk(
                data=[[1, "test_node", {"temp": 21.2}, {"humidity": 54}]])
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/input/bulk',
                params={},
                data={
                    'data': '[[1, "test_node", {"temp": 21.2}, {"humidity": 54}]]'},
                msg="input_bulk",
                request_type=RequestType.POST
            )


class TestEmonFeedsApi:
    """Unit test class for EmonFeedsApi."""

    @pytest.fixture
    def emon_feeds_api(self):
        """Fixture to initialize an EmonFeedsApi instance."""
        return EmonFeedsApi(VALID_URL, API_KEY)

    def test_list_feeds(self, emon_feeds_api):
        """Test listing feeds."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.list_feeds()
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/list.json',
                msg="get list feeds"
            )

    def test_get_feed_fields(self, emon_feeds_api):
        """Test retrieving specific feed fields."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.get_feed_fields(feed_id=123)
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/aget.json',
                params={"id": 123},
                msg="get feed fields"
            )

    def test_get_feed_meta(self, emon_feeds_api):
        """Test retrieving metadata for a feed."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.get_feed_meta(feed_id=123)
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                '/feed/getmeta.json',
                params={"id": 123},
                msg="get feed meta"
            )

    def test_get_last_value_feed(self, emon_feeds_api):
        """Test retrieving the last value for a feed."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.get_last_value_feed(feed_id=123)
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                '/feed/timevalue.json',
                params={"id": 123},
                msg="get last feed value"
            )

    def test_get_fetch_feed_data(self, emon_feeds_api):
        """Test fetching feed data."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.get_fetch_feed_data(
                feed_id=123,
                start=1609459200,
                end=1609462800,
                interval=10,
                average=True,
                time_format="unix",
                skip_missing=False,
                limi_interval=False,
                delta=False
            )
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                "/feed/data.json",
                params={
                    "id": 123,
                    "start": 1609459200,
                    "end": 1609462800,
                    "interval": 10,
                    "average": 1,
                    "time_format": "unix",
                    "skip_missing": 0,
                    "limit_interval": 0,
                    "delta": 0,
                },
                msg="fetch data points"
            )

    def test_create_feed(self, emon_feeds_api):
        """Test creating a feed."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.create_feed(
                name="test_feed",
                tag="test_tag",
                engine=1,
                options={"type": "float"})
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/create.json',
                params={
                    "name": "test_feed",
                    "tag": "test_tag",
                    "engine": 1, "options": {"type": "float"}},
                msg="create feed",
                request_type=RequestType.GET
            )

    def test_update_feed(self, emon_feeds_api):
        """Test updating a feed."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.update_feed(
                feed_id=123, fields={"key": "value"})
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/set.json',
                params={"feed_id": 123, "fields": {"key": "value"}},
                msg="update feed fields"
            )

    def test_delete_feed(self, emon_feeds_api):
        """Test deleting a feed."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.delete_feed(feed_id=123)
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/delete.json',
                params={"id": 123},
                msg="delete feed"
            )

    def test_add_data_point(self, emon_feeds_api):
        """Test adding a data point to a feed."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.add_data_point(
                feed_id=123, time=1609459200, value=42.0)
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/insert.json',
                params={"feed_id": 123, "time": 1609459200, "value": 42.0},
                msg="add feed data point"
            )

    def test_add_data_points(self, emon_feeds_api):
        """Test adding multiple data points to a feed."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.add_data_points(
                feed_id=123, data=[[1609459200, 42.0], [1609459260, 43.0]])
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/insert.json',
                params={
                    "feed_id": 123,
                    "data": [[1609459200, 42.0], [1609459260, 43.0]]},
                msg="add feed data points"
            )

    def test_delete_data_point(self, emon_feeds_api):
        """Test deleting a data point from a feed."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.delete_data_point(
                feed_id=123, time=1609459200)
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/deletedatapoint.json',
                params={"feed_id": 123, "time": 1609459200},
                msg="delete feed data point"
            )

    def test_add_feed_process_list(self, emon_feeds_api):
        """Test adding a process list to a feed."""
        with patch.object(
                emon_feeds_api,
                "execute_request",
                return_value=MOCK_RESPONSE_SUCCESS) as mock_request:
            result = emon_feeds_api.add_feed_process_list(
                feed_id=123, process_id=1, process=2)
            assert result == MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path="/feed/process/set.json",
                params={"feed_id": 123, "processlist": '2:1'},
                msg="add_feed_process_list"
            )
