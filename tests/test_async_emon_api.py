"""Tests for the EmonRequest class using async"""
from unittest.mock import AsyncMock, patch
from aiohttp import web, ClientSession
from aiohttp.client_exceptions import ClientError
import pytest
from emon_tools.emon_api_core import InputGetType
from emon_tools.async_emon_api import AsyncEmonRequest
from emon_tools.async_emon_api import AsyncEmonInputs
from emon_tools.async_emon_api import AsyncEmonFeeds

API_KEY = "12345"
VALID_URL = "http://localhost:8080"
INVALID_URL = "http://localhost:9999"
INVALID_API_KEY = ""

MOCK_UUID = "abcd1234-5678-90ef-ghij-klmnopqrstuv"
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
        assert response["message"] == "Request test async timeout."

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
    async def test_async_list_inputs(self, emon_feeds):
        """Test listing inputs."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = MOCK_INPUT_LIST
            inputs = await emon_feeds.async_list_inputs()
            assert inputs == MOCK_INPUT_LIST
            mock_request.assert_called_once_with(
                "/input/get", msg='get list inputs')

    @pytest.mark.asyncio
    async def test_async_list_inputs_process_fields(self, emon_feeds):
        """Test listing inputs."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = MOCK_INPUT_LIST_PROCESS
            inputs = await emon_feeds.async_list_inputs_fields(
                get_type=InputGetType.PROCESS_LIST
            )
            assert inputs == MOCK_INPUT_LIST_PROCESS
            mock_request.assert_called_once_with(
                "/input/getinputs", msg='get list inputs fields')

    @pytest.mark.asyncio
    async def test_async_list_inputs_extended_fields(self, emon_feeds):
        """Test listing inputs."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = MOCK_INPUT_LIST_FIELDS
            inputs = await emon_feeds.async_list_inputs_fields(
                get_type=InputGetType.EXTENDED
            )
            assert inputs == MOCK_INPUT_LIST_FIELDS
            mock_request.assert_called_once_with(
                "/input/list", msg='get list inputs fields')

    @pytest.mark.asyncio
    async def test_async_get_input_fields(self, emon_feeds):
        """Test retrieving input fields."""
        with patch.object(
                emon_feeds, "async_request", new=AsyncMock()) as mock_request:
            mock_request.return_value = MOCK_INPUT_DETAILS
            input_details = await emon_feeds.async_get_input_fields(
                "test", "V")
            assert input_details == MOCK_INPUT_DETAILS
            mock_request.assert_called_once_with(
                "/input/get/test/V", msg='get list inputs fields')
