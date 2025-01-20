"""
Emonpy Core Helper Methods

The `emonpy_core` module contains helper classes and methods
designed to sort, filter, arrange, and format EmonCMS Inputs and Feeds data.
"""
import logging
from typing import Optional
from typing import Union
from emon_tools.api_utils import MESSAGE_KEY
from emon_tools.api_utils import Utils as Ut
from emon_tools.emon_api_core import EmonProcessList
from emon_tools.emon_api_core import EmonApiCore

logging.basicConfig()


class EmonFilterItem:
    """
    A class for managing filter item structure for inputs and feeds.
    """
    def __init__(
        self,
        filter_item: Optional[dict] = None
    ):
        self._item: Optional[dict] = filter_item or {}

    @property
    def item(self) -> dict:
        """
        Get the filter item.

        Returns:
            dict: The current input filters.
        """
        return self._item

    def add_filter(self, key: str, value: Union[str, int, float, bool]):
        """
        Add values to the filter item under a specified key.

        Args:
            key (str): The key for the input filter.
            values (Union[str, int, float, bool]):
                Values to add to the input filter.
        """
        if key not in self._item:
            self._item[key] = set()
        if isinstance(value, (str, int, float, bool)):
            self._item[key].add(value)

    def reset_filter(self):
        """
        Reset all input filters to an empty state.
        """
        self._item = {}


class EmonFilters:
    """
    A class for managing filter structures for inputs and feeds.
    """

    def __init__(
        self,
        input_filters: Optional[dict] = None,
        feed_filters: Optional[dict] = None,
    ):
        """
        Initialize the EmonFilters object with input and feed filters.

        Args:
            input_filters (Optional[dict]): Initial input filter structure.
            feed_filters (Optional[dict]): Initial feed filter structure.
        """
        self._filter_inputs = EmonFilterItem(input_filters)
        self._filter_feeds = EmonFilterItem(feed_filters)

    @property
    def filter_inputs(self) -> dict:
        """
        Get the input filters.

        Returns:
            dict: The current input filters.
        """
        return self._filter_inputs.item

    @property
    def filter_feeds(self) -> dict:
        """
        Get the feed filters.

        Returns:
            dict: The current feed filters.
        """
        return self._filter_feeds.item

    def add_input_filter(self, key: str, value: Union[str, int, float, bool]):
        """
        Add values to the input filters under a specified key.

        Args:
            key (str): The key for the input filter.
            values (Union[str, int, float, bool]):
                Values to add to the input filter.
        """
        self._filter_inputs.add_filter(
            key=key,
            value=value
        )

    def add_feed_filter(self, key: str, value: Union[str, int, float, bool]):
        """
        Add values to the feed filters under a specified key.

        Args:
            key (str): The key for the feed filter.
            values (Union[str, int, float, bool]):
                Values to add to the feed filter.
        """
        self._filter_feeds.add_filter(
            key=key,
            value=value
        )

    def reset_input_filters(self):
        """
        Reset all input filters to an empty state.
        """
        self._filter_inputs.reset_filter()

    def reset_feed_filters(self):
        """
        Reset all feed filters to an empty state.
        """
        self._filter_feeds.reset_filter()

    def get_combined_filters(self) -> tuple[dict, dict]:
        """
        Get the combined structure of input and feed filters.

        Returns:
            tuple[dict, dict]: A tuple containing input and feed filters.
        """
        return self._filter_inputs.item, self._filter_feeds.item

    @staticmethod
    def is_valid_filter(filter_item: dict):
        """Test if filter_item is valid filter"""


class EmonPyCore(EmonApiCore):
    """
    Helper methods for interacting with EmonCMS data.
    This class provides static methods to manage filters, processes,
    and input-feed relationships in a structured and efficient manner.
    """

    @staticmethod
    def filter_inputs_list(
        inputs: list,
        input_filter: Optional[dict] = None
    ) -> Optional[list[dict]]:
        """
        Formats and filters the list of EmonCMS inputs.

        This method processes a list of input dictionaries by formatting them
        and applying an optional filter. It also appends additional process
        list data if applicable.

        Args:
            inputs (list): A list of input dictionaries wrapped in a dictionary
                containing a key defined by `MESSAGE_KEY`.
            input_filter (Optional[dict]): A dictionary with filter criteria to
                apply to the inputs. If not provided or empty, no filtering is
                applied.

        Returns:
            Optional[list[dict]]:
                - A list of formatted and filtered inputs (if successful).
                - `None` if the input request is not successful.

        Notes:
            - Inputs are validated using `Ut.is_request_success`.
            - Numeric fields are formatted using
            `EmonPyCore.format_list_of_dicts`.
            - Filtering is applied using `Ut.filter_list_of_dicts` if a valid
            filter is provided.
            - Process list data is appended to inputs using
            `EmonPyCore.append_inputs_process_list`.

        Example:
            >>> inputs = {
            ...     "success": True,
            ...     "message": [
            ...         {"id": 1, "name": "Input1", "value": 10.5},
            ...         {"id": 2, "name": "Input2", "value": 20.0}
            ...     ]
            ... }
            >>> input_filter = {"name": "Input1"}
            >>> result = EmonPyCore.filter_inputs_list(inputs, input_filter)
            >>> print(result)
            [{'id': 1, 'name': 'Input1', 'value': 10.5}]
        """
        if Ut.is_request_success(inputs):
            # Format numeric fields
            inputs = EmonPyCore.format_list_of_dicts(
                inputs.get(MESSAGE_KEY))
            # filter inputs values
            if Ut.is_dict(input_filter, not_empty=True):
                inputs = Ut.filter_list_of_dicts(
                    input_data=inputs,
                    filter_data=input_filter
                )
            # unpack processList data
            EmonPyCore.append_inputs_process_list(
                input_data=inputs)
        else:
            inputs = None
        return inputs

    @staticmethod
    def filter_feeds_list(
        feeds: list,
        feed_filter: Optional[dict] = None
    ) -> Optional[list[dict]]:
        """
        Formats and filters the list of EmonCMS feeds.

        This method processes a list of feed dictionaries by formatting them
        and applying an optional filter. It also appends additional process
        list data if applicable.

        Args:
            feeds (list): A list of feed dictionaries wrapped in a dictionary
                containing a key defined by `MESSAGE_KEY`.
            feed_filter (Optional[dict]): A dictionary with filter criteria to
                apply to the feeds. If not provided or empty, no filtering is
                applied.

        Returns:
            Optional[list[dict]]:
                - A list of formatted and filtered feeds (if successful).
                - `None` if the feed request is not successful.

        Notes:
            - Feeds are validated using `Ut.is_request_success`.
            - Numeric fields are formatted using
            `EmonPyCore.format_list_of_dicts`.
            - Filtering is applied using `Ut.filter_list_of_dicts` if a valid
            filter is provided.
            - Process list data is appended to feeds using
            `EmonPyCore.append_inputs_process_list`.

        Example:
            >>> feeds = {
            ...     "success": True,
            ...     "message": [
            ...         {"id": 1, "name": "Feed1", "value": 30.5},
            ...         {"id": 2, "name": "Feed2", "value": 40.0}
            ...     ]
            ... }
            >>> feed_filter = {"name": "Feed1"}
            >>> result = EmonPyCore.filter_feeds_list(feeds, feed_filter)
            >>> print(result)
            [{'id': 1, 'name': 'Feed1', 'value': 30.5}]
        """
        if Ut.is_request_success(feeds):
            # Format numeric fields
            feeds = EmonPyCore.format_list_of_dicts(
                feeds.get(MESSAGE_KEY))
            # filter inputs values
            if Ut.is_dict(feed_filter, not_empty=True):
                feeds = Ut.filter_list_of_dicts(
                    input_data=feeds,
                    filter_data=feed_filter
                )
            # unpack processList data
            EmonPyCore.append_inputs_process_list(
                input_data=feeds)
        else:
            feeds = None
        return feeds

    @staticmethod
    def filter_inputs_feeds(
        inputs: list,
        feeds: list,
        input_filter: Optional[dict] = None,
        feed_filter: Optional[dict] = None
    ) -> tuple[Optional[list[dict]], Optional[list[dict]]]:
        """
        Filters and formats EmonCMS inputs and feeds.

        This method applies filtering to the inputs and feeds based on the
        provided filters. If an input filter is provided, it filters the feeds
        to match the inputs and then filters the inputs to match the feeds. If
        only a feed filter is provided,
        it filters the inputs to match the feeds.

        Args:
            inputs (list): A list of input dictionaries representing EmonCMS
                inputs.
            feeds (list):
            A list of feed dictionaries representing EmonCMS feeds.
            input_filter (Optional[dict]): A dictionary specifying filtering
                criteria for the inputs.
                If not provided or empty, no input-based filtering is applied.
            feed_filter (Optional[dict]): A dictionary specifying filtering
                criteria for the feeds. If not provided or empty, no feed-based
                filtering is applied.

        Returns:
            tuple[Optional[list[dict]], Optional[list[dict]]]:
                - A tuple containing the filtered inputs and feeds.

        Notes:
            - If both `input_filter` and `feed_filter` are empty or None, no
            filtering is applied.
            - The method uses `EmonPyCore.filter_feeds_by_inputs` to filter
            feeds based on inputs and `EmonPyCore.filter_inputs_by_feeds`
            to filter inputs based on feeds.

        Example:
            >>> inputs = [
            ...     {"id": 1, "name": "Input1", "value": 15.0},
            ...     {"id": 2, "name": "Input2", "value": 25.0}
            ... ]
            >>> feeds = [
            ...     {"id": 1, "name": "Feed1", "linked_input": 1},
            ...     {"id": 2, "name": "Feed2", "linked_input": 2}
            ... ]
            >>> input_filter = {"name": "Input1"}
            >>> filtered = EmonPyCore.filter_inputs_feeds(
            ...     inputs, feeds, input_filter=input_filter)
            >>> print(filtered)
            ([{'id': 1, 'name': 'Input1', 'value': 15.0}],
            [{'id': 1, 'name': 'Feed1', 'linked_input': 1}])
        """
        if Ut.is_dict(input_filter, not_empty=True):
            feeds = EmonPyCore.filter_feeds_by_inputs(
                input_data=inputs,
                feed_data=feeds
            )
            inputs = EmonPyCore.filter_inputs_by_feeds(
                inputs=inputs,
                feeds=feeds
            )

        elif Ut.is_dict(feed_filter, not_empty=True):
            inputs = EmonPyCore.filter_inputs_by_feeds(
                inputs=inputs,
                feeds=feeds
            )
        return inputs, feeds

    @staticmethod
    def iter_feeds_to_add(
        feeds: list
    ):
        """
        Iterates over a list of feeds, formatting them for addition.

        This method validates and processes each feed in the provided list.
        If a feed contains the key "process", it removes it before
        yielding the feed.
        Otherwise, the feed is yielded as is.

        Args:
            feeds (list): A list of feed dictionaries to process.

        Yields:
            dict: A feed dictionary formatted for addition.

        Notes:
            - Feeds are validated to ensure they are non-empty dictionaries.
            - The "process" key, if present, is removed from the feed before it
            is yielded.

        Example:
            >>> feeds = [
            ...     {"id": 1, "name": "Feed1", "process": "some_process"},
            ...     {"id": 2, "name": "Feed2"}
            ... ]
            >>> for feed in EmonPyCore.iter_feeds_to_add(feeds):
            ...     print(feed)
            {'id': 1, 'name': 'Feed1'}
            {'id': 2, 'name': 'Feed2'}
        """
        if Ut.is_list(feeds, not_empty=True):
            for feed in feeds:
                if Ut.is_dict(feed, not_empty=True):
                    if "process" in feed:
                        yield Ut.filter_dict_by_keys(
                            input_data=feed,
                            filter_data=['process'],
                            filter_in=False
                        )
                    else:
                        yield feed

    @staticmethod
    def iter_inputs_to_add(
        inputs: list
    ):
        """
        Format and filter response inputs list
        """
        if Ut.is_list(inputs, not_empty=True):
            inputs_tmp = {}
            for item in inputs:
                node = item.get('nodeid')
                if node not in inputs_tmp:
                    inputs_tmp[node] = set()
                inputs_tmp[node].add((item.get('name'), 0))

            if Ut.is_dict(inputs_tmp, not_empty=True):
                for node, items in inputs_tmp.items():
                    data = {
                        tmp[0]: tmp[1]
                        for tmp in items
                    }
                    yield node, items, data

    @staticmethod
    def init_inputs_structure(
        structure: list,
        inputs: list
    ):
        """
        Format and filter response inputs list
        """
        inputs_out = None
        if Ut.is_list(structure, not_empty=True)\
                and Ut.is_list(inputs, not_empty=True):
            inputs_filter = EmonPyCore.get_inputs_filters_from_structure(
                structure=inputs
            )
            inputs_out = Ut.filter_list_of_dicts(
                input_data=structure,
                filter_data=inputs_filter,
                filter_in=False
            )
        return inputs_out

    @staticmethod
    def get_feeds_to_add(
        input_item: dict,
        feeds_on: list
    ):
        """
        Format and filter response inputs list
        """
        feeds_out, processes = [], []
        if Ut.is_dict(input_item, not_empty=True)\
                and Ut.is_list(feeds_on, not_empty=True):
            feeds_out = []
            for feed in input_item.get('feeds'):

                for existant_feed in feeds_on:
                    is_new = feed.get('name') != existant_feed.get('name')\
                        or feed.get('tag') != existant_feed.get('tag')
                    if is_new:
                        feeds_out.append(feed)
                    else:
                        processes.append([1, int(existant_feed.get('id'))])
        return feeds_out, processes

    @staticmethod
    def prepare_input_process_list(
        current_processes: str,
        new_processes: list
    ):
        """
        Format and filter response inputs list
        """
        result = None
        process_list = EmonPyCore.format_process_list(new_processes)

        nb_process = len(process_list)
        nb_current = 0
        if Ut.is_str(current_processes) and nb_process > 0:
            currents = EmonPyCore.format_string_process_list(current_processes)
            if Ut.is_set(currents, not_empty=True):
                nb_current = len(currents)
                process_list = process_list.union(currents)
        if nb_process > 0\
                and nb_current != nb_process:
            result = ','.join(process_list)
        return result

    @staticmethod
    def is_filters_structure(
        filters: dict
    ) -> tuple[dict, dict]:
        """
        Validate if the provided dictionary is a valid filter structure.

        Args:
            filters (dict): Dictionary containing filters for inputs and feeds.

        Returns:
            tuple[dict, dict]: Validation result as a tuple of dictionaries.
        """
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
        """
        Format a process with its associated feed ID.

        Args:
            feed_id (int): The ID of the feed.
            process_id (int, optional): The ID of the process. Defaults to 1.

        Returns:
            tuple[str, int]: Tuple containing the process name and feed ID.

        Raises:
            ValueError: If feed_id or process_id is not a positive integer.
        """
        Ut.validate_integer(feed_id, "Feed id", positive=True)
        Ut.validate_integer(process_id, "Process id", positive=True)

        name = EmonProcessList.get_name_by_id(process_id)
        return [name, feed_id]

    @staticmethod
    def get_string_process_list(
        process_list: str
    ) -> tuple[dict, dict]:
        """
        Convert a string representation of process lists to a set of tuples.

        Args:
            process_list (str):
                Comma-separated string of processes in the format 'int:int'.

        Returns:
            set[tuple[str, int]]:
                Set of tuples containing process names and feed IDs.

        Raises:
            ValueError: If the process_list string is malformed.
        """
        result = set()
        if Ut.is_str(process_list, not_empty=True):
            process = Ut.get_comma_separated_values_to_list(process_list)
            if Ut.is_list(process, not_empty=True):
                for item in process:
                    proc, feed_id = Ut.split_process(item)
                    result.add((
                        EmonProcessList.get_name_by_id(proc),
                        feed_id))
        return result

    @staticmethod
    def format_string_process_list(
        process_list: str
    ) -> tuple[dict, dict]:
        """
        Format a string process list into a set of formatted process strings.

        Args:
            process_list (str): Comma-separated string
            of processes in the format 'int:int'.

        Returns:
            set[str]: Set of formatted process strings.

        Raises:
            ValueError: If the process_list string is malformed.
        """
        result = set()
        if Ut.is_str(process_list, not_empty=True):
            process = Ut.get_comma_separated_values_to_list(process_list)
            if Ut.is_list(process, not_empty=True):
                try:
                    process = [
                        Ut.split_process(item)
                        for item in process
                    ]
                    result = EmonPyCore.format_process_list(
                        process_list=process
                    )
                except (ValueError, TypeError) as ex:
                    raise ValueError(
                        "Error: Malformed processList value. "
                        "ProcessList value must be a string as 'int:int'"
                    ) from ex
            else:
                raise ValueError(
                    "Error: Malformed processList value. "
                    "ProcessList value must be a string as 'int:int'"
                )
        return result

    @staticmethod
    def format_process_list(
        process_list: list
    ) -> tuple[dict, dict]:
        """
        Format a list of process tuples into a set of formatted strings.

        Args:
            process_list (list[tuple[int, int]]):
                List of tuples containing process and feed IDs.

        Returns:
            set[str]:
                Set of formatted process strings
                in the format 'process_name:feed_id'.
        """
        result = set()
        if Ut.is_list(process_list, not_empty=True):
            for process in process_list:
                if isinstance(process, (list, tuple))\
                        and len(process) == 2:
                    pid, fid = EmonPyCore.format_process_with_feed_id(
                        feed_id=process[1],
                        process_id=process[0]
                    )
                    result.add(f"{pid}:{fid}")
        return result

    @staticmethod
    def clean_filters_items(
        filters: dict
    ) -> tuple[dict, dict]:
        """
        Clean filter items by sorting and simplifying their structure.

        Args:
            filters (dict): Dictionary containing filter items to clean.

        Returns:
            dict: Cleaned dictionary with sorted items.
        """
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
        """
        Initialize input and feed structures based on the provided item.

        Args:
            input_item (dict): Structure item to filter inputs and feeds.
            inputs (list): List of available inputs.
            feeds (list): List of available feeds.

        Returns:
            tuple[Optional[list], Optional[list]]: Filtered inputs and feeds.
        """
        inputs_on, feeds_on = None, None
        filters = EmonPyCore.get_input_filters_from_structure(
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
        """
        Clean and organize filter structure by categorizing items
        and simplifying lists.

        Args:
            filters (dict): Dictionary containing filter structures.

        Returns:
            Optional[dict]:
                A cleaned dictionary with organized and sorted filters,
                or None if the input structure is invalid.
        """
        result = None
        if EmonPyCore.is_filters_structure(filters):
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
            result = EmonPyCore.clean_filters_items(
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

            result = EmonPyCore.clean_filters_structure(
                filters=result
            )
        return result

    @staticmethod
    def get_filters_from_structure(
        structure: list
    ) -> tuple[dict, dict]:
        """Get filter from inputs structure"""
        result = None
        if Ut.is_list(structure, not_empty=True):
            result = EmonFilters()
            for structure_item in structure:
                if Ut.is_dict(structure_item, not_empty=True)\
                        and Ut.is_valid_node(structure_item.get("nodeid"))\
                        and Ut.is_valid_node(structure_item.get("name")):
                    result.add_input_filter(
                        key="nodeid",
                        value=structure_item.get("nodeid"))
                    result.add_input_filter(
                        key="name",
                        value=structure_item.get("name"))
                    if Ut.is_list(structure_item.get("feeds"), not_empty=True):
                        for feed in structure_item.get("feeds"):
                            if Ut.is_dict(feed, not_empty=True)\
                                    and Ut.is_valid_node(feed.get("tag"))\
                                    and Ut.is_valid_node(feed.get("name")):
                                result.add_feed_filter(
                                    key="tag",
                                    value=feed.get("tag"))
                                result.add_feed_filter(
                                    key="name",
                                    value=feed.get("name"))
        return result

    @staticmethod
    def get_feeds_from_input_item(
        process_list: list[tuple],
        feed_data: list[dict]
    ) -> list[dict]:
        """
        Compute string inputs process list to list of tuples.
        """
        result = []
        if Ut.is_list(process_list, not_empty=True)\
                and Ut.is_list(feed_data, not_empty=True):
            # get feed ids from process list
            ids = []
            for process in process_list:
                feed_id = process[1]
                if isinstance(feed_id, int) and feed_id > 0:
                    ids.append(feed_id)

            if len(ids) > 0:
                result = Ut.filter_list_of_dicts(
                    feed_data,
                    filter_data={'id': ids}
                )
        return result

    @staticmethod
    def append_inputs_process_list(
        input_data: list[dict]
    ) -> list[dict]:
        """
        Compute string inputs process list to list of tuples.
        """
        if Ut.is_list(input_data, not_empty=True):
            for item in input_data:
                # compute process lists
                process_list = Ut.compute_input_list_processes(
                    item.get('processList', '')
                )
                item['process_list'] = process_list

    @staticmethod
    def filter_feeds_by_inputs(
        input_data: list[dict],
        feed_data: list[dict]
    ) -> list[dict]:
        """
        Compute string inputs process list to list of tuples.
        """
        result = []
        if Ut.is_list(input_data, not_empty=True)\
                and Ut.is_list(feed_data, not_empty=True):
            for item in input_data:
                # get feed ids from process list
                input_feeds = EmonPyCore.get_feeds_from_input_item(
                    process_list=item.get('process_list', []),
                    feed_data=feed_data
                )
                if len(input_feeds) > 0:
                    result += input_feeds
        return result

    @staticmethod
    def filter_inputs_by_feeds(
        inputs: list[dict],
        feeds: list[dict]
    ):
        """Get emoncms Inputs Feeds structure"""
        inputs_on = []
        if Ut.is_list(inputs, not_empty=True)\
                and Ut.is_list(feeds, not_empty=True):
            ids = [x.get('id') for x in feeds]
            inputs_on = []
            for item in inputs:
                if len(item['process_list']) > 0:
                    for process_list in item['process_list']:
                        if len(process_list) == 2\
                                and process_list[1] in ids:
                            inputs_on.append(item)
                            break

        return inputs_on
