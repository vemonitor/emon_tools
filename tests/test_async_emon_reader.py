"""Tests for async_request method."""

from unittest.mock import AsyncMock, patch
import pytest
from emon_tools.emon_api import EmonReader, InputGetType

API_KEY = "12345"
BASE_URL = "http://localhost:8080"

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

MOCK_INPUT_LIST_FIELDS = [
    {
        "id": "1", "node_id": "emontx", "name": "temp",
        "description": "", "processList": "1:88",
        "time": None, "value": None}
]

MOCK_INPUT_DETAILS = {"time": None, "value": None, "processList": "1:88"}


@pytest.fixture
def emon_reader():
    """Fixture to initialize an EmonReader instance."""
    return EmonReader(BASE_URL, API_KEY)


@pytest.mark.asyncio
async def test_async_list_feeds_empty(emon_reader):
    """Test retrieving UUID."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {"success": False}
        feeds = await emon_reader.async_list_feeds()
        assert feeds is None
        mock_request.assert_called_once_with("/feed/list.json")


@pytest.mark.asyncio
async def test_async_list_feeds(emon_reader):
    """Test listing feeds."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {"success": True, "message": MOCK_FEEDS}
        feeds = await emon_reader.async_list_feeds()
        assert feeds == MOCK_FEEDS
        mock_request.assert_called_once_with("/feed/list.json")


@pytest.mark.asyncio
async def test_async_get_feed_fields(emon_reader):
    """Test retrieving feed fields."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {"success": True, "message": MOCK_FEEDS[0]}
        fields = await emon_reader.async_get_feed_fields(1)
        assert fields == MOCK_FEEDS[0]
        mock_request.assert_called_once_with(
            "/feed/aget.json", params={"id": 1})


@pytest.mark.asyncio
async def test_async_get_feed_fields_empty(emon_reader):
    """Test retrieving UUID."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {"success": False}
        feeds = await emon_reader.async_get_feed_fields(1)
        assert feeds is None
        mock_request.assert_called_once_with(
            "/feed/aget.json", params={"id": 1}
        )


@pytest.mark.asyncio
async def test_async_get_feed_fields_invalid(emon_reader):
    """Test retrieving UUID."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {"success": False}
        with pytest.raises(
                ValueError, match="Feed ID must be a positive integer."):
            feeds = await emon_reader.async_get_feed_fields(-1)
            assert feeds is None

            mock_request.assert_called_once_with(
                "/feed/aget.json", params={"id": 1}
            )


@pytest.mark.asyncio
async def test_async_get_feed_meta(emon_reader):
    """Test retrieving feed metadata."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {"success": True, "message": MOCK_FEEDS[0]}
        meta = await emon_reader.async_get_feed_meta(1)
        assert meta == MOCK_FEEDS[0]
        mock_request.assert_called_once_with(
            "/feed/getmeta.json", params={"id": 1})


@pytest.mark.asyncio
async def test_async_get_last_value_feed(emon_reader):
    """Test retrieving last value of a feed."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {"success": True, "message": MOCK_FEEDS[0]}
        timevalue = await emon_reader.async_get_last_value_feed(1)
        assert timevalue == MOCK_FEEDS[0]
        mock_request.assert_called_once_with(
            "/feed/timevalue.json", params={"id": 1})


@pytest.mark.asyncio
async def test_async_list_inputs(emon_reader):
    """Test listing inputs."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {
            "success": True, "message": MOCK_INPUT_LIST}
        inputs = await emon_reader.async_list_inputs()
        assert inputs == MOCK_INPUT_LIST
        mock_request.assert_called_once_with("/input/get")


@pytest.mark.asyncio
async def test_async_list_inputs_process_fields(emon_reader):
    """Test listing inputs."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {
            "success": True, "message": MOCK_INPUT_LIST_PROCESS}
        inputs = await emon_reader.async_list_inputs_fields(
            get_type=InputGetType.PROCESS_LIST
        )
        assert inputs == MOCK_INPUT_LIST_PROCESS
        mock_request.assert_called_once_with("/input/getinputs")


@pytest.mark.asyncio
async def test_async_list_inputs_extended_fields(emon_reader):
    """Test listing inputs."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {
            "success": True, "message": MOCK_INPUT_LIST_FIELDS}
        inputs = await emon_reader.async_list_inputs_fields(
            get_type=InputGetType.EXTENDED
        )
        assert inputs == MOCK_INPUT_LIST_FIELDS
        mock_request.assert_called_once_with("/input/list")


@pytest.mark.asyncio
async def test_async_get_input_fields(emon_reader):
    """Test retrieving input fields."""
    with patch.object(
            emon_reader, "async_request", new=AsyncMock()) as mock_request:
        mock_request.return_value = {
            "success": True, "message": MOCK_INPUT_DETAILS}
        input_details = await emon_reader.async_get_input_fields("test", "V")
        assert input_details == MOCK_INPUT_DETAILS
        mock_request.assert_called_once_with("/input/get/test/V")
