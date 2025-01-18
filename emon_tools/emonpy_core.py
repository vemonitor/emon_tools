"""
Emonpy Core Helper Methods

The `emonpy_core` module contains helper classes and methods
designed to sort, filter, arrange, and format EmonCMS Inputs and Feeds data.
"""
import logging
from typing import Optional
from emon_tools.api_utils import Utils as Ut
from emon_tools.emon_api_core import EmonProcessList
from emon_tools.emon_api_core import EmonApiCore

logging.basicConfig()


class EmonPyCore(EmonApiCore):
    """
    Helper methods for interacting with EmonCMS data.
    This class provides static methods to manage filters, processes,
    and input-feed relationships in a structured and efficient manner.
    """

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
    def get_feeds_from_inputs_process(
        input_data: list[dict],
        feed_data: list[dict]
    ) -> list[dict]:
        """
        Compute string inputs process list to list of tuples.
        """
        result = []
        input_data = EmonPyCore.format_list_of_dicts(input_data)
        feed_data = EmonPyCore.format_list_of_dicts(feed_data)
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
                feeds = Ut.filter_list_of_dicts(
                    feed_data,
                    filter_data={'id': ids}
                )
                if len(feeds) == 1:
                    result = feeds[0]
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
    def get_feeds_from_inputs_list(
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
                    result.append(input_feeds)
        return result

    @staticmethod
    def get_inputs_from_feed_list(
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
                # compute process lists
                process_list = Ut.compute_input_list_processes(
                    item.get('processList', '')
                )
                # get feed ids from process list
                feeds = EmonPyCore.get_feeds_from_input_item(
                    process_list=process_list,
                    feed_data=feed_data
                )
                if len(feeds) > 0:
                    result.append(feeds)
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

            return EmonPyCore.get_feeds_from_inputs_process(
                input_data=inputs,
                feed_data=feeds
            )
        return []
