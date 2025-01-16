"""
Api common utilities.
"""
import re
from typing import Optional, Union
from emon_tools.utils import Utils as Ut

HTTP_STATUS = {
    400: "invalid request",
    401: "unauthorized access",
    404: "Not found",
    406: "URI not acceptable",
}

MESSAGE_KEY = "message"
SUCCESS_KEY = "success"


class Utils(Ut):
    """
    Utility class to interact with Emoncms data.
    Provides methods to validate, format, and process data.
    """

    @staticmethod
    def is_valid_node(text: Union[str, None]) -> bool:
        """
        Validates if the provided text is a valid node or name value.

        :param text: Node value.
        :return: True if the text is valid, otherwise False.
        """
        if not Ut.is_str(text, not_empty=True):
            return False

        matches = re.findall(r'^[\w\s\-:]+$', text, flags=re.UNICODE)
        return bool(matches)

    @staticmethod
    def validate_node(
        text: Union[str, None],
        field_name: str
    ) -> bool:
        """
        Validates if the provided text is a valid node or name value.

        :param text: Node value.
        :return: True if the text is valid, otherwise False.
        """
        if not Ut.is_str(text, not_empty=True):
            raise TypeError(f"{field_name} must be a not empty string.")

        matches = re.findall(r'^[\w\s\-:]+$', text, flags=re.UNICODE)
        if not bool(matches):
            raise ValueError(f"{field_name} must be a valid string.")
        return text

    @staticmethod
    def is_request_success(result: Union[dict, None]) -> bool:
        """
        Checks if a request to Emoncms was successful.

        :param result: The JSON response from a request.
        :return: True if the request was successful, otherwise False.
        """
        return isinstance(result, dict)\
            and result.get(SUCCESS_KEY) in ("true", True)

    @staticmethod
    def filter_dict_by_keys(
        input_data: dict,
        filter_data: list,
        filter_in: bool = True
    ) -> list[dict]:
        """
        Extracts a specific items from input data list.
        """
        result = None
        if Ut.is_dict(input_data, not_empty=True)\
                and Ut.is_list(filter_data, not_empty=True):
            result = {
                x: input_data[x]
                for x in input_data
                if filter_in and x in filter_data
                or not filter_in and x not in filter_data
            }
        return result

    @staticmethod
    def filter_list_of_dicts(
        input_data: list[dict],
        filter_data: dict[str, Union[str, int, float, list]],
        filter_in: bool = True
    ) -> list[dict]:
        """
        Extracts a specific items from input data list.
        """
        result = []
        if Ut.is_list(input_data, not_empty=True)\
                and Ut.is_dict(filter_data, not_empty=True):
            nb_filters = len(filter_data)
            for item in input_data:
                valid = 0
                for k, v in filter_data.items():
                    if isinstance(v, list):
                        is_in = k in item and item[k] in v
                        if is_in:
                            valid += 1
                    elif k in item and item[k] == v:
                        valid += 1
                if filter_in is True and valid == nb_filters\
                        or (not filter_in and valid != nb_filters):
                    result.append(item)
        return result

    @staticmethod
    def compute_input_list_to_string(
        process_list: list[tuple]
    ) -> list:
        """
        Compute string inputs process list to list of tuples.
        """
        result = []
        if Ut.is_list(process_list, not_empty=True):
            result = [
                f"{process[0]}:{process[1]}"
                for process in process_list
                if (Ut.is_list(process)
                    or Ut.is_tuple(process)) and len(process) == 2
            ]
            result = ''.join(result)
        return result

    @staticmethod
    def compute_input_list_processes(
        process_list: str
    ) -> list[tuple]:
        """
        Compute string inputs process list to list of tuples.
        """
        result = []
        if isinstance(process_list, str) and len(process_list) > 0:
            result = Utils.get_process_to_list(process_list)
        return result

    @staticmethod
    def get_formatted_feed_name(
        node: Union[str, None],
        name: Union[str, None]
    ) -> Optional[str]:
        """
        Formats a feed name in the Emoncms style: "node:NODE:FEED".

        :param node: The node name.
        :param name: The feed name.
        :return: Formatted feed name or None if parameters are invalid.
        """
        if all(isinstance(arg, str) for arg in (node, name))\
                and node.strip()\
                and name.strip():
            return f'node:{node}:{name}'
        return None

    @staticmethod
    def is_process_feed(process: Union[str, list, None], feed_id: int) -> bool:
        """
        Checks if a feed ID exists in the process list.

        :param process: The process list.
        :param feed_id: The feed ID to check for.
        :return: True if feed ID exists in the process list, otherwise False.
        """
        if isinstance(feed_id, int) and feed_id > 0:
            if isinstance(process, str):
                process = Utils.get_process_to_list(process)

            if isinstance(process, list):
                return any(
                    isinstance(item, tuple) and item[1] == feed_id
                    for item in process)
        return False

    @staticmethod
    def remove_feed_from_process(
        process: Union[str, list, None],
        feed_id: int
    ) -> str:
        """
        Removes a feed ID from the process list.

        :param process: The process list.
        :param feed_id: The feed ID to remove.
        :return: Updated process list as a string.
        """
        if isinstance(feed_id, int) and feed_id > 0:
            if isinstance(process, str):
                process = Utils.get_process_to_list(process)

            if isinstance(process, list):
                filtered = [
                    item
                    for item in process
                    if isinstance(item, tuple) and item[1] != feed_id
                ]
                return Utils.get_list_to_comma_separated_values(filtered)
        return ""

    @staticmethod
    def get_comma_separated_values_to_list(
        process: Union[str, None]
    ) -> Optional[list]:
        """
        Converts a comma-separated string into a list of strings.

        :param process: The input string.
        :return: A list of strings, or None if the input is invalid.
        """
        result = None
        if isinstance(process, str) and process.strip():
            result = [item.strip() for item in process.split(',')]
        return result

    @staticmethod
    def split_process(process: Union[str, None]) -> Optional[tuple]:
        """
        Splits a process string into a tuple of integers.

        :param process: The process string.
        :return: A tuple of integers, or None if invalid.
        """
        result = None
        if isinstance(process, str) and ':' in process:
            parts = process.split(':')
            if len(parts) == 2:
                proc, feed_id = map(
                    lambda x: int(x) if x.isdigit() else 0, parts)
                if proc > 0 and feed_id > 0:
                    result = proc, feed_id
        return result

    @staticmethod
    def get_process_to_list(process: Union[str, None]) -> list:
        """
        Converts a comma-separated process string into a list of tuples.

        :param process: The process string.
        :return: A list of tuples.
        """
        result = []
        if isinstance(process, str):
            items = Utils.get_comma_separated_values_to_list(process)
            result = [
                Utils.split_process(item)
                for item in items
                if Utils.split_process(item)
            ]
        return result

    @staticmethod
    def get_list_to_comma_separated_values(process: Union[list, None]) -> str:
        """
        Converts a list of tuples into a comma-separated string.

        :param process: The input list.
        :return: A comma-separated string.
        """
        result = ""
        if isinstance(process, list):
            result = ','.join(
                f"{item[0]}:{item[1]}"
                if isinstance(item, tuple) and len(item) == 2 else str(item)
                for item in process
            )
        return result

    @staticmethod
    def validate_feed_fields(data: dict, is_create: bool = True) -> bool:
        """
        Validates feed fields according to specific rules.

        :param data: The feed data dictionary.
        :param is_create: Indicates whether the operation is a creation.
        :return: True if all fields are valid, otherwise raises ValueError.
        """
        if not isinstance(data, dict):
            raise ValueError("Input data must be a dictionary.")

        errors = []

        # Validate 'tag' and 'name'
        for field in ['tag', 'name']:
            if is_create and field not in data:
                errors.append(
                    f"Field '{field}' is required")
            elif is_create\
                    and not Utils.is_valid_node(data[field]):
                errors.append(
                    f"Invalid value for '{field}': {data.get(field)}")
            elif not is_create\
                    and field in data\
                    and not Utils.is_valid_node(data[field]):
                errors.append(
                    f"Invalid value for '{field}': {data.get(field)}")

        # Validate 'unit' (can contain all characters, no validation required)

        # Validate 'datatype', 'engine', and 'interval' (non-negative integers)
        for field in ['datatype', 'engine', 'interval']:
            if field in data\
                    and (
                        not isinstance(data[field], int)
                        or data[field] < 0):
                errors.append(
                    f"'{field}' must be a non-negative integer, "
                    f"got {data.get(field)}")

        # Validate 'public' (integer boolean value: 0 or 1)
        if 'public' in data and data['public'] not in [0, 1]:
            errors.append(f"'public' must be 0 or 1, got {data.get('public')}")

        if errors:
            raise ValueError("; ".join(errors))

        # Adjust 'interval' field for creation
        if is_create and 'interval' in data:
            data['options'] = f'{{"interval":{data.pop("interval")}}}'

        return True

    @staticmethod
    def validate_time_series_data_point(
        time: int,
        value: Union[int, float]
    ) -> bool:
        """
        Validates a time-series data point.

        :param time: The timestamp for the data point (Unix time).
        :param value: The value for the data point (numeric).
        :return:
            True if the data point is valid;
            raises an appropriate exception otherwise.
        """
        # Validate time (Unix time, positive integer)
        time = Utils.validate_integer(time, "time", positive=True)
        value = Utils.validate_number(value, "value")
        return True
