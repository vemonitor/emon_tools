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
import logging
from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar
from typing import List, Dict, Union
import simplejson as sjson

from aiohttp import ClientError, ClientSession
from emon_tools.api_utils import HTTP_STATUS
from emon_tools.api_utils import MESSAGE_KEY
from emon_tools.api_utils import SUCCESS_KEY
from emon_tools.emon_api_core import InputGetType
from emon_tools.emon_api_core import RequestType
from emon_tools.emon_api_core import EmonRequestCore
from emon_tools.emon_api_core import EmonInputsCore
from emon_tools.emon_api_core import EmonFeedsCore
from emon_tools.emon_api_core import EmonHelper

logging.basicConfig()

Self = TypeVar("Self", bound="AsyncEmonRequest")


@dataclass
class AsyncEmonRequest:
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
        """Validate initialization parameters."""
        self.url = EmonHelper.validate_url(self.url)
        self.api_key = EmonHelper.validate_api_key(self.api_key)

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

    async def async_response(
        self,
        response,
        msg: str = None
    ) -> Dict[str, Any]:
        """Compute request response"""
        result = {SUCCESS_KEY: False, MESSAGE_KEY: None}
        if response.status in [200, 201]:
            if response.content_type == 'text/plain':
                response_data = await response.text()
                if '"' in response_data:
                    response_data = sjson.loads(response_data)
            else:
                response_data = await response.json()
            self.logger.debug(
                "Response %s json: %s",
                msg,
                response_data
            )
            result = EmonRequestCore.compute_response(
                response_data
            )
        else:
            error_msg = (
                f"HTTP {msg} {response.status}: "
                f"{HTTP_STATUS.get(response.status, 'Unknown error')}")
            result[MESSAGE_KEY] = error_msg
            self.logger.error(error_msg)
        return result

    async def async_request(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        msg: str = None,
        request_type: RequestType = RequestType.GET
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
        full_url = EmonRequestCore.encode_url_path(
            url=self.url, path=path, msg=msg)

        if params is None:
            params = {}
        # Ensure the API key is always included.
        params["apikey"] = self.api_key

        # Validate and encode all parameters
        encoded_params = EmonRequestCore.encode_params(params)
        encoded_json = None

        if json is not None:
            encoded_json = sjson.dumps(json)

        result = {SUCCESS_KEY: False, MESSAGE_KEY: None}
        self.logger.debug(
            "Requesting %s - URL: %s with params: %s",
            msg,
            full_url,
            encoded_params)
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'UTF-8'
        }
        try:
            if request_type == RequestType.GET:
                async with self.session.get(
                    full_url,
                    timeout=self.request_timeout,
                    params=encoded_params,
                    data=data,
                    headers=headers
                ) as response:
                    result = await self.async_response(
                        response=response,
                        msg=msg
                    )

            if request_type == RequestType.POST:
                async with self.session.post(
                    full_url,
                    timeout=self.request_timeout,
                    params=encoded_params,
                    data=data,
                    json=encoded_json,
                    headers=headers
                ) as response:
                    result = await self.async_response(
                        response=response,
                        msg=msg
                    )
        except ClientError as err:
            error_msg = f"Client error: {msg} - {err}"
            result[MESSAGE_KEY] = error_msg
            self.logger.error(error_msg)
        except asyncio.TimeoutError:
            error_msg = f"Request timeout: {msg}."
            result[MESSAGE_KEY] = error_msg
            self.logger.error(error_msg)

        return result

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
class AsyncEmonInputs(AsyncEmonRequest):
    """
    Extended client for interacting with specific Emoncms endpoints.

    Provides additional methods for fetching inputs.
    """
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
        path, _ = EmonInputsCore.prep_list_inputs(
            node=node
        )
        return await self.async_request(
            path,
            msg="get list inputs"
        )

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
        path, _ = EmonInputsCore.prep_list_inputs_fields(
            get_type=get_type
        )
        return await self.async_request(
            path,
            msg="get list inputs fields"
        )

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
        path, _ = EmonInputsCore.prep_input_fields(
            node=node,
            name=name
        )
        return await self.async_request(
            path,
            msg="get list inputs fields"
        )

    async def async_set_input_fields(
        self,
        input_id: int,
        fields: dict
    ) -> bool:
        """
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, params = EmonInputsCore.prep_set_input_fields(
            input_id=input_id,
            fields=fields
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="Set input fields",
            request_type=RequestType.GET
        )

    async def async_set_input_process_list(
        self,
        input_id: int,
        process_list: str
    ) -> bool:
        """
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, query_data = EmonInputsCore.prep_set_input_process_list(
            input_id=input_id,
            process_list=process_list
        )
        return await self.async_request(
            path=path,
            params=query_data.get('params'),
            data=query_data.get('data'),
            json=query_data.get('json'),
            msg="Set input process list",
            request_type=RequestType.POST
        )

    async def async_post_inputs(
        self,
        node: str,
        data: dict
    ) -> bool:
        """
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, params = EmonInputsCore.prep_post_inputs(
            node=node,
            data=data
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="Add input data point",
            request_type=RequestType.GET
        )

    async def async_input_bulk(
        self,
        data: list,
        timestamp: Optional[int] = None,
        sentat: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> bool:
        """
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, params, data_post = EmonInputsCore.prep_input_bulk(
            data=data,
            timestamp=timestamp,
            sentat=sentat,
            offset=offset
        )
        response = await self.async_request(
            path=path,
            params=params,
            data=data_post,
            msg="input_bulk",
            request_type=RequestType.POST
        )
        response['nb_points'] = len(data)
        return response


@dataclass
class AsyncEmonFeeds(AsyncEmonInputs):
    """
    Extended client for interacting with specific Emoncms endpoints.

    Provides additional methods for fetching feeds.
    """

    async def async_list_feeds(self) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve the list of feeds.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of feed dictionaries
            or None if retrieval fails.
        """
        path, _ = EmonFeedsCore.prep_list_feeds()
        return await self.async_request(
            path=path,
            msg="get list feeds"
        )

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
        path, params = EmonFeedsCore.prep_feed_fields(
            feed_id=feed_id
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="get feed fields"
        )

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
        path, params = EmonFeedsCore.prep_feed_meta(
            feed_id=feed_id
        )
        return await self.async_request(
            path,
            params=params,
            msg="get feed meta"
        )

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
        path, params = EmonFeedsCore.prep_last_value_feed(
            feed_id=feed_id
        )
        return await self.async_request(
            path,
            params=params,
            msg="get last feed value"
        )

    async def async_get_fetch_feed_data(
        self,
        feed_id: int,
        start: int,
        end: int,
        interval: int,
        average: bool = False,
        time_format: str = "unix",
        skip_missing: bool = False,
        limi_interval: bool = False,
        delta: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch feed data from specic time.

        Args:
            node (str): The name of the node containing the input.
            name (str): The name of the input to retrieve.

        Returns:
            Optional[Dict[str, Any]]:
                A dictionary of input details
                or None if the input does not exist.
        """
        path, params = EmonFeedsCore.prep_fetch_feed_data(
            feed_id=feed_id,
            start=start,
            end=end,
            interval=interval,
            average=average,
            time_format=time_format,
            skip_missing=skip_missing,
            limi_interval=limi_interval,
            delta=delta
        )
        return await self.async_request(
            path,
            params=params,
            msg="fetch data points"
        )

    async def async_create_feed(
        self,
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
        path, params = EmonFeedsCore.prep_create_feed(
            name=name,
            tag=tag,
            engine=engine,
            options=options
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="create feed"
        )

    async def async_update_feed(
        self,
        feed_id: int,
        fields: dict
    ) -> Optional[dict[str, Any]]:
        """
        Update feed fields.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, params = EmonFeedsCore.prep_update_feed(
            feed_id=feed_id,
            fields=fields
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="update feed fields"
        )

    async def async_delete_feed(
        self,
        feed_id: int
    ) -> Optional[dict[str, Any]]:
        """
        Delete existant feed.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, params = EmonFeedsCore.prep_delete_feed(
            feed_id=feed_id
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="delete feed"
        )

    async def async_add_data_point(
        self,
        feed_id: int,
        time: int,
        value: Union[int, float]
    ) -> bool:
        """
        Add data point to feed id.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, params = EmonFeedsCore.prep_add_data_point(
            feed_id=feed_id,
            time=time,
            value=value
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="add feed data point"
        )

    async def async_add_data_points(
        self,
        feed_id: int,
        data: list[list[int, Union[int, float]]]
    ) -> bool:
        """
        Add data points to feed id.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, params = EmonFeedsCore.prep_add_data_points(
            feed_id=feed_id,
            data=data
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="add feed data points"
        )

    async def async_delete_data_point(
        self,
        feed_id: int,
        time: int
    ) -> bool:
        """
        Delete data point by time from feed id.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, params = EmonFeedsCore.prep_delete_data_point(
            feed_id=feed_id,
            time=time
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="delete feed data point"
        )

    async def async_add_feed_process_list(
        self,
        feed_id: int,
        process_id: int,
        process: int
    ) -> bool:
        """

        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        path, params = EmonFeedsCore.prep_add_feed_process_list(
            feed_id=feed_id,
            process_id=process_id,
            process=process
        )
        return await self.async_request(
            path=path,
            params=params,
            msg="add_feed_process_list"
        )
