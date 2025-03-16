"""
DashBoard Models
"""
# pylint: disable=W0718
from enum import Enum


class RangeActivityType(str, Enum):
    """
    Category type Enum
    """
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
