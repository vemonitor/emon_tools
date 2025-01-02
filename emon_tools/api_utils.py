"""
Api common utilities.
"""
import re
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
    """Emoncms data Helper"""

    @staticmethod
    def is_valid_node(text) -> bool:
        """
        Test if text is valid node or name values.

        [Original regex from emoncms](https://github.com/emoncms/emoncms/blob/master/Modules/feed/feed_model.php#L99)

        :Example :
            >>> Utils.is_valid_node(text="Node1")
            >>> True

        :param text: str: Node value.
        :return: bool: True if text is valid node.
        """
        result = False
        if Utils.is_str(text):
            matches = re.findall(r'[\w\s\-:]', text, flags=re.UNICODE)
            result = Utils.is_list(matches, not_empty=True)
        return result

    @staticmethod
    def is_request_success(result) -> bool:
        """
        Test if request to emoncms is success.

        :Example :
            >>> Utils.is_request_success(result={"success": "true"})
            >>> True
        :param result: dict: The request json response.
        :return: bool: True if the request return success.
        """
        return Utils.is_dict(result)\
            and result.get('success') == "true"

    @staticmethod
    def compute_response(result: dict) -> bool:
        """
        Compute the response from emoncms.
        """
        if Utils.is_dict(result):
            success = result.get(SUCCESS_KEY) is True
            message = result.get(MESSAGE_KEY)
        elif Utils.is_str(result):
            success = True
            message = result
        else:
            success = False
            message = "Invalid response"
        return success, message
