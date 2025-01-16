"""
emonpy common helper
"""
from emon_tools.api_utils import SUCCESS_KEY, MESSAGE_KEY


class EmonApiDataTest:
    """EmonApi data test common helper"""
    VALID_URL = "http://example.com"
    API_KEY = "testAPIKey123"
    MOCK_RESPONSE_SUCCESS = {"success": True, "message": "Request succeeded"}
    MOCK_RESPONSE_FAIL = {"success": False, "message": "Request failed"}