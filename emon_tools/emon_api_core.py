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
from enum import Enum
import logging
from typing import Any, Optional, Dict, Union
from urllib.parse import quote_plus, urljoin
import simplejson as sj
from emon_tools.api_utils import Utils as Ut
from emon_tools.api_utils import MESSAGE_KEY
from emon_tools.api_utils import SUCCESS_KEY

logging.basicConfig()


class RequestType(Enum):
    """Request Type Method Enum"""
    GET = "get"
    POST = "post"


class InputGetType(Enum):
    """Remove Nan Method Enum"""
    PROCESS_LIST = "process_list"
    EXTENDED = "extended"


class EmonEngines(Enum):
    """EmonCms Available Engines Method Enum"""
    MYSQL = 0  # Deprecated
    TIMESTORE = 1
    PHPTIMESERIES = 2
    GRAPHITE = 3  # Deprecated
    PHPTIMESTORE = 4
    PHPFINA = 5
    PHPFIWA = 6  # Deprecated
    # Virtual feed, on demand post processing
    VIRTUALFEED = 7
    # Mysql with MEMORY tables on RAM. All data is lost on shutdown
    MYSQLMEMORY = 8
    # (internal use only) Redis Read/Write buffer, for low write mode
    REDISBUFFER = 9
    CASSANDRA = 10


class ProcessArg(Enum):
    """EmonCms Available Engines Method Enum"""
    VALUE = 0
    INPUTID = 1
    FEEDID = 2
    NONE = 3
    TEXT = 4
    SCHEDULEID = 5


class EmonProcessList(Enum):
    """EmonCms Available Engines Method Enum"""
    LOG_TO_FEED = (1, "process__log_to_feed", ProcessArg.FEEDID)
    SCALE = (2, "process__scale", ProcessArg.VALUE)
    OFFSET = (3, "process__offset", ProcessArg.VALUE)
    POWER_TO_KWH = (4, "process__power_to_kwh", ProcessArg.FEEDID)
    POWER_TO_KWHD = (5, "process__power_to_kwhd", ProcessArg.FEEDID)
    TIMES_INPUT = (6, "process__times_input", ProcessArg.INPUTID)
    INPUT_ONTIME = (7, "process__input_ontime", ProcessArg.FEEDID)
    WHINC_TO_KWHD = (8, "process__whinc_to_kwhd", ProcessArg.FEEDID)
    KWH_TO_KWHD_OLD = (9, "process__kwh_to_kwhd_old", ProcessArg.FEEDID)
    UPDATE_FEED_DATA = (10, "process__update_feed_data", ProcessArg.FEEDID)
    ADD_INPUT = (11, "process__add_input", ProcessArg.INPUTID)
    DIVIDE_INPUT = (12, "process__divide_input", ProcessArg.INPUTID)
    PHASESHIFT = (13, "process__phaseshift", ProcessArg.VALUE)
    ACCUMULATOR = (14, "process__accumulator", ProcessArg.FEEDID)
    RATECHANGE = (15, "process__ratechange", ProcessArg.FEEDID)
    HISTOGRAM = (16, "process__histogram", ProcessArg.FEEDID)
    AVERAGE = (17, "process__average", ProcessArg.FEEDID)
    HEAT_FLUX = (18, "process__heat_flux", ProcessArg.FEEDID)
    POWER_ACC_TO_KWHD = (19, "process__power_acc_to_kwhd", ProcessArg.FEEDID)
    PULSE_DIFF = (20, "process__pulse_diff", ProcessArg.FEEDID)
    KWH_TO_POWER = (21, "process__kwh_to_power", ProcessArg.FEEDID)
    SUBTRACT_INPUT = (22, "process__subtract_input", ProcessArg.INPUTID)
    KWH_TO_KWHD = (23, "process__kwh_to_kwhd", ProcessArg.FEEDID)
    ALLOW_POSITIVE = (24, "process__allowpositive", ProcessArg.NONE)
    ALLOW_NEGATIVE = (25, "process__allownegative", ProcessArg.NONE)
    SIGNED_TO_UNSIGNED = (26, "process__signed2unsigned", ProcessArg.NONE)
    MAX_DAILY_VALUE = (27, "process__max_value", ProcessArg.FEEDID)
    MIN_DAILY_VALUE = (28, "process__min_value", ProcessArg.FEEDID)
    ADD_FEED = (29, "process__add_feed", ProcessArg.FEEDID)
    SUB_FEED = (30, "process__sub_feed", ProcessArg.FEEDID)
    MULTIPLY_BY_FEED = (31, "process__multiply_by_feed", ProcessArg.FEEDID)
    DIVIDE_BY_FEED = (32, "process__divide_by_feed", ProcessArg.FEEDID)
    RESET_TO_ZERO = (33, "process__reset2zero", ProcessArg.NONE)
    WH_ACCUMULATOR = (34, "process__wh_accumulator", ProcessArg.FEEDID)
    PUBLISH_TO_MQTT = (35, "process__publish_to_mqtt", ProcessArg.TEXT)
    RESET_TO_NULL = (36, "process__reset2null", ProcessArg.NONE)
    RESET_TO_ORIGINAL = (37, "process__reset2original", ProcessArg.NONE)
    IF_ZERO_SKIP = (42, "process__if_zero_skip", ProcessArg.NONE)
    IF_NOT_ZERO_SKIP = (43, "process__if_not_zero_skip", ProcessArg.NONE)
    IF_NULL_SKIP = (44, "process__if_null_skip", ProcessArg.NONE)
    IF_NOT_NULL_SKIP = (45, "process__if_not_null_skip", ProcessArg.NONE)
    IF_GT_SKIP = (46, "process__if_gt_skip", ProcessArg.VALUE)
    IF_GT_EQUAL_SKIP = (47, "process__if_gt_equal_skip", ProcessArg.VALUE)
    IF_LT_SKIP = (48, "process__if_lt_skip", ProcessArg.VALUE)
    IF_LT_EQUAL_SKIP = (49, "process__if_lt_equal_skip", ProcessArg.VALUE)
    IF_EQUAL_SKIP = (50, "process__if_equal_skip", ProcessArg.VALUE)
    IF_NOT_EQUAL_SKIP = (51, "process__if_not_equal_skip", ProcessArg.VALUE)
    GOTO_PROCESS = (52, "process__goto_process", ProcessArg.VALUE)
    SOURCE_FEED = (53, "process__source_feed_data_time", ProcessArg.FEEDID)
    ADD_SOURCE_FEED = (55, "process__add_source_feed", ProcessArg.FEEDID)
    SUB_SOURCE_FEED = (56, "process__sub_source_feed", ProcessArg.FEEDID)
    MULTIPLY_BY_SOURCE_FEED = (
        57, "process__multiply_by_source_feed", ProcessArg.FEEDID)
    DIVIDE_BY_SOURCE_FEED = (
        58, "process__divide_by_source_feed", ProcessArg.FEEDID)
    RECIPROCAL_BY_SOURCE_FEED = (
        59, "process__reciprocal_by_source_feed", ProcessArg.FEEDID)
    EXIT = (60, "process__error_found", ProcessArg.NONE)
    MAX_VALUE_ALLOWED = (61, "process__max_value_allowed", ProcessArg.VALUE)
    MIN_VALUE_ALLOWED = (62, "process__min_value_allowed", ProcessArg.VALUE)
    ABSOLUTE_VALUE = (63, "process__abs_value", ProcessArg.VALUE)
    KWH_ACCUMULATOR = (64, "process__kwh_accumulator", ProcessArg.FEEDID)
    LOG_TO_FEED_JOIN = (65, "process__log_to_feed_join", ProcessArg.FEEDID)
    MAX_BY_INPUT = (66, "process__max_input", ProcessArg.INPUTID)
    MIN_BY_INPUT = (67, "process__min_input", ProcessArg.INPUTID)
    MAX_BY_FEED = (68, "process__max_feed", ProcessArg.FEEDID)
    MIN_BY_FEED = (69, "process__min_feed", ProcessArg.FEEDID)

    @classmethod
    def get_members(cls) -> list:
        """Get list of Enum members and values (member, value)."""
        return [
            (member, member.value)
            for name, member in cls.__members__.items()
        ]

    @classmethod
    def get_name_by_id(cls, process_id: int):
        """Get Name of process list by process id."""
        result = 0
        values_list = cls.get_members()
        for member_value in values_list:
            if process_id == member_value[1][0]:
                result = member_value[1][1]
                break
        return result


class EmonHelper:
    """Emon api helper methods"""
    @staticmethod
    def validate_url(url: str) -> str:
        """
        Ensure the URL is valid and properly formatted.

        Args:
            url (str): The base URL.

        Returns:
            str: Sanitized URL.

        Raises:
            ValueError: If the URL is empty or improperly formatted.
        """
        if not Ut.is_str(url, not_empty=True):
            raise TypeError("URL must be a non-empty string.")
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError("URL must start with 'http://' or 'https://'.")
        return url.rstrip("/")  # Remove trailing slash for consistency.

    @staticmethod
    def validate_api_key(api_key: str) -> str:
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

    @staticmethod
    def is_filters_structure(
        filters: dict
    ) -> tuple[dict, dict]:
        """Test if is valid filters structure"""
        return Ut.is_dict(filters)\
            and Ut.is_dict(filters.get('filter_inputs'))\
            and Ut.is_set(filters["filter_inputs"].get('nodeid'))\
            and Ut.is_set(filters["filter_inputs"].get('name'))\
            and Ut.is_dict(filters.get('filter_feeds'))\
            and Ut.is_set(filters["filter_feeds"].get('tag'))\
            and Ut.is_set(filters["filter_feeds"].get('name'))

    @staticmethod
    def format_process_with_feed_id(
        feed_id: int,
        process_id: int = 1
    ) -> tuple[dict, dict]:
        """Test if is valid filters structure"""
        Ut.validate_integer(feed_id, "Feed id", positive=True)
        Ut.validate_integer(process_id, "Process id", positive=True)

        name = EmonProcessList.get_name_by_id(process_id)
        return [name, feed_id]

    @staticmethod
    def format_string_process_list(
        process_list: str
    ) -> tuple[dict, dict]:
        """Test if is valid filters structure"""
        result = set()
        if Ut.is_str(process_list, not_empty=True):
            process = Ut.get_comma_separated_values_to_list(process_list)
            if Ut.is_list(process, not_empty=True):
                process = [
                    Ut.split_process(item)
                    for item in process
                ]
                result = EmonHelper.format_process_list(
                    process_list=process
                )
        return result

    @staticmethod
    def format_process_list(
        process_list: list
    ) -> tuple[dict, dict]:
        """Test if is valid filters structure"""
        result = set()
        if Ut.is_list(process_list, not_empty=True):
            for process in process_list:
                if isinstance(process, (list, tuple))\
                        and len(process) == 2:
                    pid, fid = EmonHelper.format_process_with_feed_id(
                        feed_id=process[1],
                        process_id=process[0]
                    )
                    result.add(f"{pid}:{fid}")
        return result

    @staticmethod
    def clean_filters_items(
        filters: dict
    ) -> tuple[dict, dict]:
        """Clean structure filters"""
        result = None
        if Ut.is_dict(filters):
            result = {}
            for item_key, filter_item in filters.items():
                nb_items = len(filter_item)
                if nb_items > 1:
                    result[item_key] = list(filter_item)
                    result[item_key].sort()
                elif nb_items == 1:
                    result[item_key] = list(filter_item)[0]
        return result

    @staticmethod
    def get_existant_structure(
        input_item: dict,
        inputs: list,
        feeds: list
    ):
        """Initialyze inputs structure from EmonCms API."""
        inputs_on, feeds_on = None, None
        filters = EmonHelper.get_input_filters_from_structure(
            structure_item=input_item
        )
        if Ut.is_dict(filters):
            inputs_on = Ut.filter_list_of_dicts(
                inputs,
                filter_data=filters.get('filter_inputs'),
                filter_in=True
            )
            feeds_on = Ut.filter_list_of_dicts(
                feeds,
                filter_data=filters.get('filter_feeds'),
                filter_in=True
            )
        return inputs_on, feeds_on

    @staticmethod
    def clean_filters_structure(
        filters: dict
    ) -> tuple[dict, dict]:
        """Clean structure filters"""
        result = None
        if EmonHelper.is_filters_structure(filters):
            result = {}
            for cat_key, filter_cat in filters.items():
                for item_key, filter_item in filter_cat.items():
                    nb_items = len(filter_item)
                    if nb_items > 1:
                        if not Ut.is_dict(result.get(cat_key)):
                            result[cat_key] = {}
                        result[cat_key][item_key] = list(filter_item)
                        result[cat_key][item_key].sort()
                    elif nb_items == 1:
                        if not Ut.is_dict(result.get(cat_key)):
                            result[cat_key] = {}
                        result[cat_key][item_key] = list(filter_item)[0]
        return result

    @staticmethod
    def get_inputs_filters_from_structure(
        structure: list
    ) -> dict:
        """Get filter from inputs structure"""
        result = None
        if Ut.is_list(structure, not_empty=True):
            result = {
                "nodeid": set(),
                "name": set()
            }
            for item in structure:
                result["nodeid"].add(
                    item.get("nodeid"))
                result["name"].add(
                    item.get("name"))
            result = EmonHelper.clean_filters_items(
                filters=result
            )
        return result

    @staticmethod
    def get_input_filters_from_structure(
        structure_item: dict
    ) -> tuple[dict, dict]:
        """Get filter from inputs structure"""
        result = None
        if Ut.is_dict(structure_item, not_empty=True):
            result = {
                "filter_inputs": {
                    "nodeid": set(),
                    "name": set()
                },
                "filter_feeds": {
                    "tag": set(),
                    "name": set()
                }
            }
            result["filter_inputs"]["nodeid"].add(
                structure_item.get("nodeid"))
            result["filter_inputs"]["name"].add(
                structure_item.get("name"))
            if Ut.is_list(structure_item.get("feeds"), not_empty=True):
                for feed in structure_item.get("feeds"):
                    result["filter_feeds"]["tag"].add(
                        feed.get("tag"))
                    result["filter_feeds"]["name"].add(
                        feed.get("name"))

            result = EmonHelper.clean_filters_structure(
                filters=result
            )
        return result

    @staticmethod
    def format_list_of_dicts(
        data: list[dict]
    ) -> list[dict]:
        """
        Extracts a specific items from input data list.
        """
        result = []
        if isinstance(data, list) and len(data) > 0:
            for item in data:
                int_keys = [
                    'id', 'userid', 'public', 'size', 'engine', 'interval']
                tmp = item.copy()
                for k, v in item.items():
                    if k in int_keys:
                        if isinstance(v, str) and len(v) > 0:
                            tmp[k] = int(v)
                result.append(tmp)
        return result

    @staticmethod
    def get_feeds_from_inputs_process(
        input_data: list[dict],
        feed_data: list[dict]
    ) -> list[dict]:
        """
        Compute string inputs process list to list of tuples.
        """
        result = []
        input_data = EmonHelper.format_list_of_dicts(input_data)
        feed_data = EmonHelper.format_list_of_dicts(feed_data)
        if Ut.is_list(input_data, not_empty=True)\
                and Ut.is_list(feed_data, not_empty=True):
            for item in input_data:
                tmp = item.copy()
                # compute process lists
                tmp['processList'] = Ut.compute_input_list_processes(
                    item.get('processList', '')
                )
                # get feed ids from process list
                ids = []
                for process in tmp.get('processList', []):
                    feed_id = process[1]
                    if isinstance(feed_id, int) and feed_id > 0:
                        ids.append(feed_id)

                if len(ids) > 0:
                    feeds = Ut.filter_list_of_dicts(
                        feed_data,
                        filter_data={'id': ids}
                    )
                    if len(feeds) > 0:

                        tmp['feeds'] = feeds
                result.append(tmp)
        return result

    @staticmethod
    def get_extended_structure(
        inputs: list,
        feeds: list,
        filter_inputs: Optional[dict] = None,
        filter_feeds: Optional[dict] = None,
        filter_in: bool = True
    ) -> list:
        """Get extended inputs structure from EmonCms API."""
        if Ut.is_list(inputs)\
                and Ut.is_list(feeds):

            if Ut.is_dict(filter_inputs):
                inputs = Ut.filter_list_of_dicts(
                    inputs,
                    filter_data=filter_inputs,
                    filter_in=filter_in
                )

            if Ut.is_dict(filter_feeds):
                feeds = Ut.filter_list_of_dicts(
                    feeds,
                    filter_data=filter_feeds,
                    filter_in=filter_in
                )

            return EmonHelper.get_feeds_from_inputs_process(
                input_data=inputs,
                feed_data=feeds
            )
        return []


class EmonRequestCore:
    """EmonRequest common helper"""
    @staticmethod
    def compute_response(
        response: Union[dict, list, str, None]
    ) -> tuple[bool, Union[str, list, dict]]:
        """
        Computes and interprets the response from Emoncms.

        :param result: The response from Emoncms.
        :return: A tuple of success status and message.
        """
        result = {SUCCESS_KEY: False, MESSAGE_KEY: "Invalid response"}
        is_dict = isinstance(response, dict)
        is_json = is_dict\
            and SUCCESS_KEY in response\
            and MESSAGE_KEY in response
        if is_json:
            result[SUCCESS_KEY] = bool(response[SUCCESS_KEY])
            extra = Ut.filter_dict_by_keys(
                input_data=response,
                filter_data=[SUCCESS_KEY],
                filter_in=False
            )
            if Ut.is_dict(extra, not_empty=True):
                result[SUCCESS_KEY] = bool(response[SUCCESS_KEY])
                del result[MESSAGE_KEY]
                result.update(extra)

        elif is_dict and SUCCESS_KEY in response and len(response) == 1:
            result[SUCCESS_KEY] = bool(response[SUCCESS_KEY])
            result[MESSAGE_KEY] = ''

        elif isinstance(response, (list, dict, str, int, float)):
            result[SUCCESS_KEY] = True
            result[MESSAGE_KEY] = response
        return result

    @staticmethod
    def encode_url_path(
        url: str,
        path: str,
        msg: str
    ) -> str:
        """Encode request params"""
        EmonHelper.validate_url(url)
        if not Ut.is_str(path, not_empty=True):
            raise ValueError(
                f"Request error: {msg}. "
                "Url Path must be a non-empty string."
                )

        # Encode unsafe characters in the path.
        path = quote_plus(path.lstrip('/'), safe="/")
        # Safely join the base URL and path.
        return urljoin(url, path)

    @staticmethod
    def encode_params(
        params: Optional[Dict[str, Any]] = None,
        unquote_keys: Optional[list[str]] = None
    ) -> Dict[str, Any]:
        """Encode request params"""
        encoded_params = {}

        if not Ut.is_list(unquote_keys):
            unquote_keys = []

        if Ut.is_dict(params, not_empty=True):
            for key, value in params.items():
                is_not_object = isinstance(value, (float, str))\
                    and key not in unquote_keys
                if is_not_object:
                    encoded_params[key] = quote_plus(str(value), safe="-")
                elif isinstance(value, (list, dict)):
                    encoded_params[key] = sj.dumps(value)
                else:
                    encoded_params[key] = value
        return encoded_params


class EmonInputsCore:
    """Emon Inputs Api"""
    @staticmethod
    def prep_list_inputs(
        node: Optional[str] = None
    ) -> tuple[str, Optional[Dict[str, Any]]]:
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
        path = f"/input/get/{quote_plus(node)}" if node else "/input/get"
        return path, None

    @staticmethod
    def prep_list_inputs_fields(
        get_type: InputGetType = InputGetType.PROCESS_LIST
    ) -> tuple[str, Optional[Dict[str, Any]]]:
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
        return path, None

    @staticmethod
    def prep_input_fields(
        node: str,
        name: str
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Fetch specific input details from a node and input name.

        Args:
            node (str): The name of the node containing the input.
            name (str): The name of the input to retrieve.

        Returns:
            tuple[str, Optional[Dict[str, Any]]]:
                A dictionary of input details
                or None if the input does not exist.
        """
        if not node or not name:
            raise ValueError("Node and name must be non-empty strings.")
        path = f"/input/get/{quote_plus(node)}/{quote_plus(name)}"
        return path, None

    @staticmethod
    def prep_set_input_fields(
        input_id: str,
        fields: dict
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Add inputs data points to input node.
        On error return a dict as:
        - {"success": false, "message": "Invalid Inputs"}
        """
        _ = Ut.validate_integer(input_id, 'Input Id', positive=True)
        if not Ut.is_dict(fields, not_empty=True):
            raise ValueError("Invalid fields to post inputs.")
        params = {
            "inputid": input_id,
            "fields": fields
        }

        return "/input/set", params

    @staticmethod
    def prep_set_input_process_list(
        input_id: str,
        process_list: str
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Add inputs data points to input node.
        On error return a dict as:
        - {"success": false, "message": "Invalid Inputs"}
        """
        _ = Ut.validate_integer(input_id, 'Input Id', positive=True)
        if not Ut.is_str(process_list, not_empty=True):
            raise ValueError("Invalid data to post inputs.")
        query_data = {
            "params": {
                "inputid": input_id,
            },
            "data": {"processlist": process_list}
        }

        return "/input/process/set", query_data

    @staticmethod
    def prep_post_inputs(
        node: str,
        data: dict
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Add inputs data points to input node.
        On error return a dict as:
        - {"success": false, "message": "Invalid Inputs"}
        """
        if not Ut.is_dict(data, not_empty=True):
            raise ValueError("Invalid data to post inputs.")
        _ = Ut.validate_node(node, 'Input node')
        data = {
            Ut.validate_node(
                key, 'Input Key'): Ut.validate_number(value, 'Input Value')
            for key, value in data.items()
        }
        params = {
            "node": node,
            "fulljson": data
        }

        return "/input/post", params

    @staticmethod
    def prep_input_bulk(
        data: list,
        timestamp: Optional[int] = None,
        sentat: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> tuple[str, Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Add inputs data points to input node as bulk.
        """
        if not Ut.is_list(data, not_empty=True):
            raise ValueError("Invalid data to post inputs.")
        params = {}
        if timestamp is not None:
            Ut.validate_timestamp(
                timestamp, "inputBulkTime")
            params.update({"time": timestamp})
        if sentat is not None:
            Ut.validate_integer(
                sentat, "inputBulkSentat")
            params.update({"sentat": sentat})
        if offset is not None:
            Ut.validate_integer(
                offset, "inputBulkOffset")
            params.update({"offset": offset})

        if len(params) > 1:
            raise ValueError(
                "You must chose an unique format "
                "from (timestamp, sentat or offset)."
                )
        data = {
            "data": sj.dumps(data)
        }

        return "/input/bulk", params, data


class EmonFeedsCore:
    """Emon Feeds Api"""
    @staticmethod
    def prep_list_feeds() -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Retrieve the list of feeds.

        Returns:
            Optional[List[Dict[str, Any]]]: A list of feed dictionaries
            or None if retrieval fails.
        """
        return "/feed/list.json", None

    @staticmethod
    def prep_feed_fields(
        feed_id: int
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Get all fields for a specific feed by ID.

        Args:
            feed_id (int): The ID of the feed to retrieve.

        Returns:
            tuple[str, Optional[Dict[str, Any]]]:
                A dictionary of feed fields or None if the feed does not exist.
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        return "/feed/aget.json", {"id": feed_id}

    @staticmethod
    def prep_feed_meta(
        feed_id: int
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Get metadata for a specific feed by ID.

        Args:
            feed_id (int): The ID of the feed to retrieve metadata for.

        Returns:
            tuple[str, Optional[Dict[str, Any]]]: A dictionary of metadata
                or None if the feed does not exist.
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        return "/feed/getmeta.json", {"id": feed_id}

    @staticmethod
    def prep_last_value_feed(
        feed_id: int
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Get the last time and value for a specific feed by ID.

        Args:
            feed_id (int): The ID of the feed to retrieve.

        Returns:
            tuple[str, Optional[Dict[str, Any]]]:
                A dictionary containing the last time and value
                or None if the feed does not exist.
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        return "/feed/timevalue.json", {"id": feed_id}

    @staticmethod
    def prep_fetch_feed_data(
        feed_id: int,
        start: int,
        end: int,
        interval: int,
        average: bool = False,
        time_format: str = "unix",
        skip_missing: bool = False,
        limi_interval: bool = False,
        delta: bool = False,
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Fetch feed data from specic time.

        Args:
            node (str): The name of the node containing the input.
            name (str): The name of the input to retrieve.

        Returns:
            tuple[str, Optional[Dict[str, Any]]]:
                A dictionary of input details
                or None if the input does not exist.
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        params = {
            "id": feed_id,
            "start": start,
            "end": end,
            "interval": interval,
            "average": int(average),
            "time_format": time_format,
            "skip_missing": int(skip_missing),
            "limit_interval": int(limi_interval),
            "delta": int(delta)
        }
        return "/feed/data.json", params

    @staticmethod
    def prep_create_feed(
        name: str,
        tag: str,
        engine: Optional[int] = None,
        options: Optional[dict] = None
    ) -> tuple[str, Optional[Dict[str, Any]]]:
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
            - > await create_feed( name"tmp" ) => 1
            - > UType.is_str(value="tmp", not_null=True) => True
            - > UType.is_str( 0 ) => False
        :param name: Name of the new Feed
        :param tag: Feed related Tag or Node
        :param engine: Engine used to store data
        :param options: Dict of options
        :return: True if the given value is a str instance, otherwise False.
        """
        params = {
                "tag": tag,
                "name": name,
                "engine": engine,
                "options": options
            }
        Ut.validate_feed_fields(params, is_create=True)
        return "/feed/create.json", params

    @staticmethod
    def prep_update_feed(
        feed_id: int,
        fields: dict
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Update feed fields.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        Ut.validate_feed_fields(fields, is_create=False)
        params = {
                "feed_id": feed_id,
                "fields": fields
            }
        return "/feed/set.json", params

    @staticmethod
    def prep_delete_feed(
        feed_id: int
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Delete existant feed.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        return "/feed/delete.json", {"id": feed_id}

    @staticmethod
    def prep_add_data_point(
        feed_id: int,
        time: int,
        value: Union[int, float]
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Add data point to feed id.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        Ut.validate_time_series_data_point(time, value)
        params = {
            "feed_id": feed_id,
            "time": time,
            "value": value
        }
        return "/feed/insert.json", params

    @staticmethod
    def prep_add_data_points(
        feed_id: int,
        data: list[list[int, Union[int, float]]]
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Add data points to feed id.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        for item in data:
            Ut.validate_time_series_data_point(item[0], item[1])

        params = {
            "feed_id": feed_id,
            "data": data
        }
        return "/feed/insert.json", params

    @staticmethod
    def prep_delete_data_point(
        feed_id: int,
        time: int
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Delete data point by time from feed id.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        time = Ut.validate_integer(time, "time", positive=True)

        params = {
            "feed_id": feed_id,
            "time": time
        }
        return "/feed/deletedatapoint.json", params

    @staticmethod
    def prep_add_feed_process_list(
        feed_id: int,
        process_id: int,
        process: int
    ) -> tuple[str, Optional[Dict[str, Any]]]:
        """
        Delete data point by time from feed id.
        On error return a dict as:
        - {"success": false, "message": "Invalid fields"}
        """
        feed_id = Ut.validate_integer(feed_id, "Feed ID", positive=True)
        process_id = Ut.validate_integer(process_id, "Process ID")
        process = Ut.validate_integer(process, "Process")
        params = {
            "feed_id": feed_id,
            "processlist": f"{process}:{process_id}"
        }
        return "/feed/process/set.json", params
