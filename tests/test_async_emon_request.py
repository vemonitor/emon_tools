"""Tests for the EmonRequest class using async"""
from unittest.mock import AsyncMock, patch
from aiohttp import web, ClientSession
from aiohttp.client_exceptions import ClientError
import pytest
from emon_tools.async_emon_api import AsyncEmonRequest

API_KEY = "12345"
VALID_URL = "http://localhost:8080"
INVALID_URL = "http://localhost:9999"
INVALID_API_KEY = ""


class TestEmonRequest:
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
