"""Tests for the EmonRequest class using async"""
from unittest.mock import AsyncMock, patch
from aiohttp import web, ClientSession
from aiohttp.client_exceptions import ClientError
import pytest
from emon_tools.emon_api_core import InputGetType
from emon_tools.emon_api_core import RequestType
from emon_tools.async_emon_api import AsyncEmonRequest
from emon_tools.async_emon_api import AsyncEmonInputs
from emon_tools.async_emon_api import AsyncEmonFeeds
from tests.emon_api.emon_api_data_test import EmonApiDataTest as dtest

API_KEY = "12345"
VALID_URL = "http://localhost:8080"
INVALID_URL = "http://localhost:9999"
INVALID_API_KEY = ""

MOCK_FEEDS = [
    {
        "id": "1",
        "userid": "1",
        "name": "Cellule_Tcircuit",
        "tag": " sofrel_circuit_Cellule",
        "public": "0",
        "size": "35811340",
        "engine": "5",
        "processList": "",
        "unit": "",
        "time": 1665509570,
        "value": 17.690000534058,
    }
]
MOCK_INPUT_LIST = {
    "V": {"time": None, "value": None, "processList": "1:88"},
    "I": {"time": None, "value": None, "processList": "1:89"},
    "P": {"time": None, "value": None, "processList": "1:90"},
}

MOCK_INPUT_LIST_PROCESS = [
    {"id": "1", "processList": "1:88"}
]

MOCK_INPUT_LIST_FIELDS = {
    "success": True,
    "message": [
        {
            "id": "1", "node_id": "emontx", "name": "temp",
            "description": "", "processList": "1:88",
            "time": None, "value": None
        }
    ]
}


MOCK_INPUT_DETAILS = {
    "success": True,
    "message": {"time": None, "value": None, "processList": "1:88"}
}


class TestAsyncEmonRequest:
    """AsyncEmonRequest unit test class"""
    @pytest.fixture
    def mock_emon_request(self):
        """Fixture for creating a mock EmonRequest instance."""
        return AsyncEmonRequest(url=VALID_URL, api_key=API_KEY)

    async def mock_handler(self, request):
        """Mock handler for the aiohttp server."""
        if "apikey" not in request.query or request.query["apikey"] != API_KEY:
            raise web.HTTPUnauthorized(text="Invalid API key")
        return web.json_response({"success": True, "message": "Mock response"})

    @pytest.fixture
    def aiohttp_server_mock(self, loop, aiohttp_server):
        """Fixture to mock an aiohttp server."""
        app = web.Application()
        app.router.add_get("/valid-path", self.mock_handler)
        return loop.run_until_complete(aiohttp_server(app))

    @pytest.mark.asyncio
    async def test_async_request_success(
        self,
        aiohttp_server_mock,
        mock_emon_request
    ):
        """Test async_request with valid URL and API key."""
        mock_emon_request.url = str(aiohttp_server_mock.make_url("/"))
        response = await mock_emon_request.async_request("/valid-path")
        assert response["success"] is True
        assert response["message"] == "Mock response"

    @pytest.mark.asyncio
    async def test_async_request_invalid_path(self, mock_emon_request):
        """Test async_request with an invalid path."""
        with pytest.raises(
                ValueError, match="Path must be a non-empty string."):
            await mock_emon_request.async_request("")

    @pytest.mark.asyncio
    async def test_async_request_invalid_api_key(
        self,
        aiohttp_server_mock,
        mock_emon_request
    ):
        """Test async_request with an invalid API key."""
        mock_emon_request.url = str(aiohttp_server_mock.make_url("/"))
        mock_emon_request.api_key = INVALID_API_KEY
        response = await mock_emon_request.async_request("/valid-path")
        assert response["success"] is False
        assert "unauthorized" in response["message"]

    @pytest.mark.asyncio
    async def test_async_request_timeout(self, mock_emon_request):
        """Test async_request handling of timeouts."""
        mock_emon_request.url = INVALID_URL
        mock_emon_request.request_timeout = 0.0001
        response = await mock_emon_request.async_request(
            "/valid-path", msg='test async')
        assert response["success"] is False
        assert response["message"] == "Request timeout: test async."

    @pytest.mark.asyncio
    async def test_async_request_client_error(self, mock_emon_request):
        """Test async_request handling of ClientError."""
        with patch(
                "aiohttp.ClientSession.get",
                side_effect=ClientError("Mock client error")):
            response = await mock_emon_request.async_request(
                "/valid-path", msg='test async')
            assert response["success"] is False
            assert "client error" in response["message"]

    @pytest.mark.asyncio
    async def test_close_session(self, mock_emon_request):
        """Test closing of the aiohttp session."""
        session_mock = AsyncMock()
        mock_emon_request._session = session_mock
        mock_emon_request._close_session = True
        await mock_emon_request.close()
        session_mock.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_get_session_creation(self, mock_emon_request):
        """Test session creation when no session exists."""
        assert mock_emon_request._session is None
        session = mock_emon_request.session
        assert session is not None
        assert isinstance(session, ClientSession)

    @pytest.mark.asyncio
    async def test_get_session_reuse(self, mock_emon_request):
        """Test reusing an existing session."""
        session = mock_emon_request.session
        assert mock_emon_request.session is session


MOCK_INPUTS = [{"id": 1, "name": "input1"}, {"id": 2, "name": "input2"}]


class TestAsyncEmonInputs:
    """AsyncEmonInputs unit test class"""

    @pytest.fixture
    def emon_inputs(self):
        """Fixture to initialize an AsyncEmonInputs instance."""
        return AsyncEmonInputs(VALID_URL, API_KEY)

    @pytest.mark.asyncio
    async def test_async_list_inputs_empty(self, emon_inputs):
        """Test retrieving an empty input list."""
        with patch.object(
            emon_inputs, "async_request", new=AsyncMock()
        ) as mock_request:
            mock_request.return_value = {"success": False}
            inputs = await emon_inputs.async_list_inputs()
            assert inputs == {"success": False}
            mock_request.assert_called_once_with(
                "/input/get", msg="get list inputs"
            )

    @pytest.mark.asyncio
    async def test_async_list_inputs(self, emon_inputs):
        """Test listing inputs."""
        with patch.object(
            emon_inputs, "async_request", new=AsyncMock()
        ) as mock_request:
            mock_request.return_value = {
                "success": True, "message": MOCK_INPUTS}
            inputs = await emon_inputs.async_list_inputs()
            assert inputs == {"success": True, "message": MOCK_INPUTS}
            mock_request.assert_called_once_with(
                "/input/get", msg="get list inputs"
            )

    @pytest.mark.asyncio
    async def test_async_list_inputs_with_node(self, emon_inputs):
        """Test listing inputs filtered by node."""
        with patch.object(
            emon_inputs, "async_request", new=AsyncMock()
        ) as mock_request:
            mock_request.return_value = {
                "success": True, "message": MOCK_INPUTS}
            inputs = await emon_inputs.async_list_inputs(node="test_node")
            assert inputs == {"success": True, "message": MOCK_INPUTS}
            mock_request.assert_called_once_with(
                "/input/get/test_node", msg="get list inputs"
            )

    @pytest.mark.asyncio
    async def test_async_list_inputs_fields(self, emon_inputs):
        """Test retrieving inputs with fields."""
        with patch.object(
            emon_inputs, "async_request", new=AsyncMock()
        ) as mock_request:
            mock_request.return_value = {
                "success": True, "message": MOCK_INPUTS}
            inputs = await emon_inputs.async_list_inputs_fields(
                get_type=InputGetType.PROCESS_LIST
            )
            assert inputs == {"success": True, "message": MOCK_INPUTS}
            mock_request.assert_called_once_with(
                "/input/getinputs", msg="get list inputs fields"
            )

    @pytest.mark.asyncio
    async def test_async_list_inputs_extended_fields(self, emon_inputs):
        """Test listing inputs."""
        with patch.object(
                emon_inputs, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = MOCK_INPUT_LIST_FIELDS
            inputs = await emon_inputs.async_list_inputs_fields(
                get_type=InputGetType.EXTENDED
            )
            assert inputs == MOCK_INPUT_LIST_FIELDS
            mock_request.assert_called_once_with(
                "/input/list", msg='get list inputs fields')

    @pytest.mark.asyncio
    async def test_async_get_input_fields(self, emon_inputs):
        """Test retrieving specific input fields."""
        with patch.object(
            emon_inputs, "async_request", new=AsyncMock()
        ) as mock_request:
            mock_request.return_value = {"id": 1, "name": "input1"}
            input_fields = await emon_inputs.async_get_input_fields(
                node="test_node", name="input1"
            )
            assert input_fields == {"id": 1, "name": "input1"}
            mock_request.assert_called_once_with(
                "/input/get/test_node/input1", msg="get list inputs fields"
            )

    @pytest.mark.asyncio
    async def test_async_set_input_fields(self, emon_inputs):
        """Test setting input fields."""
        with patch.object(
            emon_inputs, "async_request", new=AsyncMock()
        ) as mock_request:
            mock_request.return_value = True
            result = await emon_inputs.async_set_input_fields(
                input_id=1, fields={"key": "value"}
            )
            assert result is True
            mock_request.assert_called_once_with(
                path="/input/set",
                params={"inputid": 1, "fields": {"key": "value"}},
                msg="Set input fields",
                request_type=RequestType.GET,
            )

    @pytest.mark.asyncio
    async def test_async_set_input_process_list(self, emon_inputs):
        """Test setting input process list."""
        with patch.object(
            emon_inputs, "async_request", new=AsyncMock()
        ) as mock_request:
            mock_request.return_value = True
            result = await emon_inputs.async_set_input_process_list(
                input_id=1, process_list="[]"
            )
            assert result is True
            mock_request.assert_called_once_with(
                path="/input/process/set",
                params={"inputid": 1},
                data={'processlist': '[]'},
                json=None,
                msg="Set input process list",
                request_type=RequestType.POST,
            )

    @pytest.mark.asyncio
    async def test_async_post_inputs(self, emon_inputs):
        """Test posting input data points."""
        with patch.object(
            emon_inputs, "async_request", new=AsyncMock()
        ) as mock_request:
            mock_request.return_value = True
            result = await emon_inputs.async_post_inputs(
                node="test_node", data={"key": 123}
            )
            assert result is True
            mock_request.assert_called_once_with(
                path="/input/post",
                params={"node": "test_node", "fulljson": {"key": 123}},
                msg="Add input data point",
                request_type=RequestType.GET,
            )

    @pytest.mark.asyncio
    async def test_input_bulk(self, emon_inputs):
        """Test posting input data."""
        with patch.object(
                emon_inputs,
                "async_request",
                return_value=dtest.MOCK_RESPONSE_SUCCESS) as mock_request:

            result = await emon_inputs.async_input_bulk(
                data=[[1, "test_node", {"temp": 21.2}, {"humidity": 54}]])
            assert result == dtest.MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/input/bulk',
                params={},
                data={
                    'data': '[[1, "test_node", {"temp": 21.2}, {"humidity": 54}]]'},
                msg="input_bulk",
                request_type=RequestType.POST
            )


class TestAsyncEmonFeeds:
    """AsyncEmonFeeds unit test class"""
    @pytest.fixture
    def emon_feeds(self):
        """Fixture to initialize an EmonReader instance."""
        return AsyncEmonFeeds(VALID_URL, API_KEY)

    @pytest.mark.asyncio
    async def test_async_list_feeds_empty(self, emon_feeds):
        """Test retrieving UUID."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = {"success": False}
            feeds = await emon_feeds.async_list_feeds()
            assert feeds == {'success': False}
            mock_request.assert_called_once_with(
                path="/feed/list.json", msg='get list feeds')

    @pytest.mark.asyncio
    async def test_async_list_feeds(self, emon_feeds):
        """Test listing feeds."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = {
                "success": True, "message": MOCK_FEEDS}
            feeds = await emon_feeds.async_list_feeds()
            assert feeds == {
                "success": True, "message": MOCK_FEEDS}
            mock_request.assert_called_once_with(
                path="/feed/list.json", msg='get list feeds')

    @pytest.mark.asyncio
    async def test_async_get_feed_fields(self, emon_feeds):
        """Test retrieving feed fields."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = {
                "success": True, "message": MOCK_FEEDS[0]}
            fields = await emon_feeds.async_get_feed_fields(1)
            assert fields == {
                "success": True, "message": MOCK_FEEDS[0]}
            mock_request.assert_called_once_with(
                path="/feed/aget.json",
                msg='get feed fields',
                params={"id": 1}
            )

    @pytest.mark.asyncio
    async def test_async_get_feed_fields_empty(self, emon_feeds):
        """Test retrieving UUID."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = {'success': False}
            feeds = await emon_feeds.async_get_feed_fields(1)
            assert feeds == {'success': False}
            mock_request.assert_called_once_with(
                path="/feed/aget.json",
                params={"id": 1},
                msg='get feed fields'
            )

    @pytest.mark.asyncio
    async def test_async_get_feed_fields_invalid(self, emon_feeds):
        """Test retrieving UUID."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = {"success": False}
            with pytest.raises(
                    ValueError, match="Feed ID must be a positive integer."):
                feeds = await emon_feeds.async_get_feed_fields(-1)
                assert feeds is None

                mock_request.assert_called_once_with(
                    "/feed/aget.json", params={"id": 1}
                )

    @pytest.mark.asyncio
    async def test_async_get_feed_meta(self, emon_feeds):
        """Test retrieving feed metadata."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = {
                "success": True, "message": MOCK_FEEDS[0]}
            meta = await emon_feeds.async_get_feed_meta(1)
            assert meta == {
                "success": True, "message": MOCK_FEEDS[0]}
            mock_request.assert_called_once_with(
                "/feed/getmeta.json",
                params={"id": 1},
                msg='get feed meta')

    @pytest.mark.asyncio
    async def test_async_get_last_value_feed(self, emon_feeds):
        """Test retrieving last value of a feed."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = {
                "success": True, "message": MOCK_FEEDS[0]}
            timevalue = await emon_feeds.async_get_last_value_feed(1)
            assert timevalue == {
                "success": True, "message": MOCK_FEEDS[0]}
            mock_request.assert_called_once_with(
                "/feed/timevalue.json",
                params={"id": 1},
                msg='get last feed value')

    @pytest.mark.asyncio
    async def test_get_fetch_feed_data(self, emon_feeds):
        """Test fetching feed data."""
        with patch.object(
                emon_feeds,
                "async_request",
                return_value=dtest.MOCK_RESPONSE_SUCCESS) as mock_request:
            result = await emon_feeds.async_get_fetch_feed_data(
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
            assert result == dtest.MOCK_RESPONSE_SUCCESS
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

    @pytest.mark.asyncio
    async def test_create_feed(self, emon_feeds):
        """Test creating a feed."""
        with patch.object(
                emon_feeds,
                "async_request",
                return_value=dtest.MOCK_RESPONSE_SUCCESS) as mock_request:
            result = await emon_feeds.async_create_feed(
                name="test_feed",
                tag="test_tag",
                engine=1,
                options={"type": "float"})
            assert result == dtest.MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/create.json',
                params={
                    "name": "test_feed",
                    "tag": "test_tag",
                    "engine": 1, "options": {"type": "float"}},
                msg="create feed"
            )

    @pytest.mark.asyncio
    async def test_update_feed(self, emon_feeds):
        """Test updating a feed."""
        with patch.object(
                emon_feeds,
                "async_request",
                return_value=dtest.MOCK_RESPONSE_SUCCESS) as mock_request:
            result = await emon_feeds.async_update_feed(
                feed_id=123, fields={"key": "value"})
            assert result == dtest.MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/set.json',
                params={"feed_id": 123, "fields": {"key": "value"}},
                msg="update feed fields"
            )

# ------------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_delete_feed(self, emon_feeds):
        """Test deleting a feed."""
        with patch.object(
                emon_feeds,
                "async_request",
                return_value=dtest.MOCK_RESPONSE_SUCCESS) as mock_request:
            result = await emon_feeds.async_delete_feed(feed_id=123)
            assert result == dtest.MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/delete.json',
                params={"id": 123},
                msg="delete feed"
            )

    @pytest.mark.asyncio
    async def test_add_data_point(self, emon_feeds):
        """Test adding a data point to a feed."""
        with patch.object(
                emon_feeds,
                "async_request",
                return_value=dtest.MOCK_RESPONSE_SUCCESS) as mock_request:
            result = await emon_feeds.async_add_data_point(
                feed_id=123, time=1609459200, value=42.0)
            assert result == dtest.MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/insert.json',
                params={"feed_id": 123, "time": 1609459200, "value": 42.0},
                msg="add feed data point"
            )

    @pytest.mark.asyncio
    async def test_add_data_points(self, emon_feeds):
        """Test adding multiple data points to a feed."""
        with patch.object(
                emon_feeds,
                "async_request",
                return_value=dtest.MOCK_RESPONSE_SUCCESS) as mock_request:
            result = await emon_feeds.async_add_data_points(
                feed_id=123, data=[[1609459200, 42.0], [1609459260, 43.0]])
            assert result == dtest.MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/insert.json',
                params={
                    "feed_id": 123,
                    "data": [[1609459200, 42.0], [1609459260, 43.0]]},
                msg="add feed data points"
            )

    @pytest.mark.asyncio
    async def test_delete_data_point(self, emon_feeds):
        """Test deleting a data point from a feed."""
        with patch.object(
                emon_feeds,
                "async_request",
                return_value=dtest.MOCK_RESPONSE_SUCCESS) as mock_request:
            result = await emon_feeds.async_delete_data_point(
                feed_id=123, time=1609459200)
            assert result == dtest.MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path='/feed/deletedatapoint.json',
                params={"feed_id": 123, "time": 1609459200},
                msg="delete feed data point"
            )

    @pytest.mark.asyncio
    async def test_add_feed_process_list(self, emon_feeds):
        """Test adding a process list to a feed."""
        with patch.object(
                emon_feeds,
                "async_request",
                return_value=dtest.MOCK_RESPONSE_SUCCESS) as mock_request:
            result = await emon_feeds.async_add_feed_process_list(
                feed_id=123, process_id=1, process=2)
            assert result == dtest.MOCK_RESPONSE_SUCCESS
            mock_request.assert_called_once_with(
                path="/feed/process/set.json",
                params={"feed_id": 123, "processlist": '2:1'},
                msg="add_feed_process_list"
            )