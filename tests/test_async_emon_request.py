from aiohttp import web, ClientSession
from aiohttp.client_exceptions import ClientError
from unittest.mock import AsyncMock, patch
from emon_tools.emon_api import EmonRequest
import pytest

API_KEY = "12345"
VALID_URL = "http://localhost:8080"
INVALID_URL = "http://localhost:9999"
INVALID_API_KEY = ""


@pytest.fixture
def mock_emon_request():
    """Fixture for creating a mock EmonRequest instance."""
    return EmonRequest(url=VALID_URL, api_key=API_KEY)


async def mock_handler(request):
    """Mock handler for the aiohttp server."""
    if "apikey" not in request.query or request.query["apikey"] != API_KEY:
        raise web.HTTPUnauthorized(text="Invalid API key")
    return web.json_response({"success": True, "message": "Mock response"})


@pytest.fixture
def aiohttp_server_mock(loop, aiohttp_server):
    """Fixture to mock an aiohttp server."""
    app = web.Application()
    app.router.add_get("/valid-path", mock_handler)
    return loop.run_until_complete(aiohttp_server(app))


@pytest.mark.asyncio
async def test_async_request_success(aiohttp_server_mock, mock_emon_request):
    """Test async_request with valid URL and API key."""
    mock_emon_request.url = str(aiohttp_server_mock.make_url("/"))
    response = await mock_emon_request.async_request("/valid-path")
    assert response["success"] is True
    assert response["message"] == "Mock response"


@pytest.mark.asyncio
async def test_async_request_invalid_path(mock_emon_request):
    """Test async_request with an invalid path."""
    with pytest.raises(ValueError, match="Path must be a non-empty string."):
        await mock_emon_request.async_request("")


@pytest.mark.asyncio
async def test_async_request_invalid_api_key(
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
async def test_async_request_timeout(mock_emon_request):
    """Test async_request handling of timeouts."""
    mock_emon_request.url = INVALID_URL
    mock_emon_request.request_timeout = 0.0001
    response = await mock_emon_request.async_request("/valid-path")
    assert response["success"] is False
    assert response["message"] == "Request timeout."


@pytest.mark.asyncio
async def test_async_request_client_error(mock_emon_request):
    """Test async_request handling of ClientError."""
    with patch(
            "aiohttp.ClientSession.get",
            side_effect=ClientError("Mock client error")):
        response = await mock_emon_request.async_request("/valid-path")
        assert response["success"] is False
        assert "client error" in response["message"]


@pytest.mark.asyncio
async def test_close_session(mock_emon_request):
    """Test closing of the aiohttp session."""
    session_mock = AsyncMock()
    mock_emon_request._session = session_mock
    mock_emon_request._close_session = True
    await mock_emon_request.close()
    session_mock.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_session_creation(mock_emon_request):
    """Test session creation when no session exists."""
    assert mock_emon_request._session is None
    session = mock_emon_request.session
    assert session is not None
    assert isinstance(session, ClientSession)


@pytest.mark.asyncio
async def test_get_session_reuse(mock_emon_request):
    """Test reusing an existing session."""
    session = mock_emon_request.session
    assert mock_emon_request.session is session


@pytest.mark.asyncio
async def test_validate_api_key_valid(mock_emon_request):
    """Test API key validation with a valid key."""
    validated_key = mock_emon_request._validate_api_key(API_KEY)
    assert validated_key == API_KEY


@pytest.mark.asyncio
async def test_validate_api_key_invalid(mock_emon_request):
    """Test API key validation with an invalid key."""
    with pytest.raises(
            ValueError,
            match="API key must be a non-empty alphanumeric string."):
        mock_emon_request._validate_api_key(INVALID_API_KEY)


@pytest.mark.asyncio
async def test_validate_url_valid(mock_emon_request):
    """Test URL validation with a valid URL."""
    validated_url = mock_emon_request._sanitize_url(VALID_URL)
    assert validated_url == VALID_URL


@pytest.mark.parametrize(
    "url, expected_exception, error_msg",
    [
        (
            123, TypeError,
            "URL must be a non-empty string."
        ),
        (
            "ftp://", ValueError,
            "URL must start with 'http://' or 'https://'."
        ),
    ],
)
@pytest.mark.asyncio
async def test_validate_url_invalid(
    url,
    expected_exception,
    error_msg,
    mock_emon_request
):
    """Test URL validation with an invalid URL."""
    with pytest.raises(expected_exception, match=error_msg):
        mock_emon_request._sanitize_url(url)
