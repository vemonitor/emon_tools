"""
Emoncms Client for interacting with feed, input, and user data.

This module provides an asynchronous client
to communicate with an Emoncms server,
allowing users to retrieve feeds, inputs,
and other related data through the Emoncms API.

Emoncms API behavior:
- For the `feed` module:
  - A non-existing JSON route responds with a JSON object:
    `{success: false, message: "Feed does not exist"}`.
  - Examples of invalid routes:
    - `/feed/aget.json?id=200` if feed 200 does not exist.
    - `/feed/basket.json` if the route is invalid.
  - The route `/feed/list.json` always returns an array of JSON objects,
    which can be empty if no feeds exist.
- For the `user` module:
  - A non-existing JSON route responds with `false`,
    which is not a JSON object.
  - This behavior can result in a `TypeError`
    when accessing keys in the response.

Security and validation:
- Parameters such as `url`, `path`, and query parameters are validated
  and sanitized to prevent injection attacks.
- The API key is validated to ensure it is alphanumeric and secure.
"""
import asyncio
from enum import Enum
import logging
from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar, List, Dict
from urllib.parse import quote, urljoin

from aiohttp import ClientError, ClientSession
from emon_tools.api_utils import Utils as Ut
from emon_tools.api_utils import HTTP_STATUS
from emon_tools.api_utils import MESSAGE_KEY
from emon_tools.api_utils import SUCCESS_KEY

logging.basicConfig()

Self = TypeVar("Self", bound="EmonRequest")


class InputGetType(Enum):
    """Remove Nan Method Enum"""
    PROCESS_LIST = "process_list"
    EXTENDED = "extended"


@dataclass
class EmonRequest:
    """
    Base class for interacting with the Emoncms API.

    This class handles HTTP GET requests to the Emoncms server,
    ensuring that requests are properly validated and secured.
    It includes utilities for session management and common error handling.

    Attributes:
        url (str):
            The base URL of the Emoncms server (e.g., "http://emoncms.local").
        api_key (str):
            The API key for authenticating with the Emoncms server.
        request_timeout (int):
            Timeout for HTTP requests in seconds (default: 20).
    """
    url: str
    api_key: str
    request_timeout: int = 20
    _session: Optional[ClientSession] = field(default=None, init=False)
    _close_session: bool = field(default=False, init=False)
    logger = logging.getLogger(__name__)

    def __post_init__(self):
        """Validate and sanitize initialization parameters."""
        self.url = self._sanitize_url(self.url)
        self.api_key = self._validate_api_key(self.api_key)

    @staticmethod
    def _sanitize_url(url: str) -> str:
        """
        Ensure the URL is valid and properly formatted.

        Args:
            url (str): The base URL.

        Returns:
            str: Sanitized URL.

        Raises:
            ValueError: If the URL is empty or improperly formatted.
        """
        if not isinstance(url, str) or not url.strip():
            raise TypeError("URL must be a non-empty string.")
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError("URL must start with 'http://' or 'https://'.")
        return url.rstrip("/")  # Remove trailing slash for consistency.

    @staticmethod
    def _validate_api_key(api_key: str) -> str:
        """
        Validate the API key for proper format.

        Args:
            api_key (str): The API key.

        Returns:
            str: Validated API key.

        Raises:
            ValueError: If the API key is not a non-empty alphanumeric string.
        """
        if not isinstance(api_key, str) or not api_key.isalnum():
            raise ValueError(
                "API key must be a non-empty alphanumeric string."
            )
        return api_key

    @property
    def session(self) -> ClientSession:
        """
        Get or create an aiohttp ClientSession.

        Returns:
            ClientSession: The active session for making HTTP requests.
        """
        if self._session is None:
            self._session = ClientSession()
            self._close_session = True
        return self._session

    async def async_request(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the Emoncms server.

        Args:
            path (str): API endpoint path (e.g., "/feed/list.json").
            params (Optional[Dict[str, Any]]):
                Query parameters to include in the request.

        Returns:
            Dict[str, Any]: A dictionary containing the response data.

        Raises:
            ValueError: If the path is invalid or empty.
        """
        if not path or not isinstance(path, str):
            raise ValueError("Path must be a non-empty string.")

        # Encode unsafe characters in the path.
        path = quote(path.lstrip('/'), safe="/")
        # Safely join the base URL and path.
        full_url = urljoin(self.url, path)

        if params is None:
            params = {}
        # Ensure the API key is always included.
        params["apikey"] = self.api_key

        # Validate and encode all parameters
        encoded_params = {
            key: quote(str(value), safe="")
            for key, value in params.items()
        }

        data = {SUCCESS_KEY: False, MESSAGE_KEY: None}
        self.logger.debug(
            "Requesting URL: %s with params: %s",
            full_url,
            encoded_params)

        try:
            async with self.session.get(
                full_url, timeout=self.request_timeout, params=encoded_params
            ) as response:
                if response.status == 200:
                    success, message = Ut.compute_response(
                        await response.json()
                    )
                    data[SUCCESS_KEY] = success
                    data[MESSAGE_KEY] = message
                else:
                    error_msg = (
                        f"HTTP {response.status}: "
                        f"{HTTP_STATUS.get(response.status, 'Unknown error')}")
                    data[MESSAGE_KEY] = error_msg
                    self.logger.error(error_msg)
        except ClientError as err:
            error_msg = f"Client error: {err}"
            data[MESSAGE_KEY] = error_msg
            self.logger.error(error_msg)
        except asyncio.TimeoutError:
            error_msg = "Request timeout."
            data[MESSAGE_KEY] = error_msg
            self.logger.error(error_msg)

        return data

    async def close(self) -> None:
        """Close the ClientSession if it was created internally."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> Self:
        """Enter an asynchronous context manager."""
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Exit an asynchronous context manager and close the session."""
        await self.close()


@dataclass
class EmonReader(EmonRequest):
    """
    Extended client for interacting with specific Emoncms endpoints.

    Provides additional methods for fetching feed, input, and user data.
    """

    async def async_list_feeds(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve the list of feeds.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of feed dictionaries
            or None if retrieval fails.
        """
        feed_data = await self.async_request("/feed/list.json")
        if feed_data.get(SUCCESS_KEY):
            return feed_data.get(MESSAGE_KEY)
        self.logger.warning(
            "Failed to list feeds: %s", feed_data.get(MESSAGE_KEY))
        return None

    async def async_get_feed_fields(
        self,
        feed_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get all fields for a specific feed by ID.

        Args:
            feed_id (int): The ID of the feed to retrieve.

        Returns:
            Optional[Dict[str, Any]]:
                A dictionary of feed fields or None if the feed does not exist.
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        params = {"id": feed_id}
        response = await self.async_request("/feed/aget.json", params=params)
        if response.get(SUCCESS_KEY):
            return response.get(MESSAGE_KEY)
        self.logger.warning(
            "Failed to get feed fields: %s", response.get(MESSAGE_KEY))
        return None

    async def async_get_feed_meta(
        self,
        feed_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific feed by ID.

        Args:
            feed_id (int): The ID of the feed to retrieve metadata for.

        Returns:
            Optional[Dict[str, Any]]: A dictionary of metadata
                or None if the feed does not exist.
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        params = {"id": feed_id}
        feed_data = await self.async_request(
            "/feed/getmeta.json",
            params=params)
        if feed_data.get(SUCCESS_KEY):
            return feed_data.get(MESSAGE_KEY)
        self.logger.warning(
            "Failed to get feed meta: %s", feed_data.get(MESSAGE_KEY))
        return None

    async def async_get_last_value_feed(
        self,
        feed_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get the last time and value for a specific feed by ID.

        Args:
            feed_id (int): The ID of the feed to retrieve.

        Returns:
            Optional[Dict[str, Any]]:
                A dictionary containing the last time and value
                or None if the feed does not exist.
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        params = {"id": feed_id}
        feed_data = await self.async_request(
            "/feed/timevalue.json",
            params=params)
        if feed_data.get(SUCCESS_KEY):
            return feed_data.get(MESSAGE_KEY)
        self.logger.warning(
            "Failed to get last feed value: %s", feed_data.get(MESSAGE_KEY))
        return None

    async def async_list_inputs(
        self,
        node: Optional[str] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve a list of inputs, optionally filtered by node.

        Args:
            node (Optional[str]):
                The node name to filter inputs by. If not provided,
                all inputs are retrieved.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of input dictionaries
            or None if retrieval fails.
        """
        path = f"/input/get/{quote(node)}" if node else "/input/get"
        feed_data = await self.async_request(path)
        if feed_data.get(SUCCESS_KEY):
            return feed_data.get(MESSAGE_KEY)
        self.logger.warning(
            "Failed to list inputs: %s", feed_data.get(MESSAGE_KEY))
        return None

    async def async_list_inputs_fields(
        self,
        get_type: InputGetType = InputGetType.PROCESS_LIST
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve a list of inputs fields, optionally filtered by get_type.

        Args:
            get_type (InputGetType): The type of output to retrieve.
                - InputGetType.PROCESS_LIST:
                    Retrieve the list of inputs
                    with id's and process_list's values.
                - InputGetType.EXTENDED:
                    Retrieve the list of inputs with all fields.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of input dictionaries
            or None if retrieval fails.
        """
        if get_type == InputGetType.PROCESS_LIST:
            path = "/input/getinputs"
        else:
            path = "/input/list"

        feed_data = await self.async_request(path)
        if feed_data.get(SUCCESS_KEY):
            return feed_data.get(MESSAGE_KEY)
        self.logger.warning(
            "Failed to list inputs fields: %s", feed_data.get(MESSAGE_KEY))
        return None

    async def async_get_input_fields(
        self,
        node: str,
        name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch specific input details from a node and input name.

        Args:
            node (str): The name of the node containing the input.
            name (str): The name of the input to retrieve.

        Returns:
            Optional[Dict[str, Any]]:
                A dictionary of input details
                or None if the input does not exist.
        """
        if not node or not name:
            raise ValueError("Node and name must be non-empty strings.")
        path = f"/input/get/{quote(node)}/{quote(name)}"
        response = await self.async_request(path)
        if response.get(SUCCESS_KEY):
            return response.get(MESSAGE_KEY)
        self.logger.warning(
            "Failed to get input fields: %s", response.get(MESSAGE_KEY))
        return None


@dataclass
class EmoncmsWrite(EmonRequest):
    """Emoncms Write client Api."""

    async def async_create_feed(self,
                                name: str,
                                tag: str,
                                engine: Optional[int] = None,
                                options: Optional[dict] = None
                                ) -> Optional[dict[str, Any]]:
        """
        Create new feed.
        On error return a dict as:
        - {"success": false, "message": "Error Message"}

        Error messages are:
        - [Bad tag Name]: invalid characters in feed tag
        - [Bad name]: invalid characters in feed name
        - [invalid engine number]: ABORTED: Engine id x is not supported.

        On Success ruturn a dict as:
        - {"success": true, "feedid": 1, "result": true}

        [see valid engines here](https://github.com/emoncms/emoncms/blob/master/Lib/enum.php#L40)

        :Example :
            - > await async_create_feed( name"tmp" ) => 1
            - > UType.is_str(value="tmp", not_null=True) => True
            - > UType.is_str( 0 ) => False
        :param name: Name of the new Feed
        :param tag: Feed related Tag or Node
        :param engine: Engine used to store data
        :param options: Dict of options
        :return: True if the given value is a str instance, otherwise False.
        """
        result = None
        if Ut.is_valid_node(name)\
                and Ut.is_valid_node(tag):
            params = {
                "apikey": self.api_key,
                "tag": tag,
                "name": name,
                "engine": engine,
                "options": options
            }
            feed_data = await self.async_request(
                "/feed/create.json", params=params)
            if feed_data.get(SUCCESS_KEY):
                return feed_data.get(MESSAGE_KEY)
        return result
