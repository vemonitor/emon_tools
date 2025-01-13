"""
Emoncms API example.

Create EmonCms Inputs Feeds structure if not exist.
"""
import os
import time
from emon_tools.emon_api_core import EmonEngines
from emon_tools.emon_api_core import EmonProcessList
from emon_tools.emonpy import EmonPy


def get_emon_structure():
    """Set inputs feeds structure"""
    return [
        {
            "name": "I1",
            "nodeid": "emon_tools_ex1",
            "description": "Managed Input",
            "feeds": [
                {"name": "I1", "tag": "emon_tools_ex1",
                 "process": EmonProcessList.LOG_TO_FEED,
                 "engine": EmonEngines.PHPFINA.value,
                 "options": {"interval": 1}
                 }
            ]
        },
        {
            "name": "I2",
            "nodeid": "emon_tools_ex1",
            "description": "Managed Input",
            "feeds": [
                {"name": "F2A", "tag": "emon_tools_ex1_f1",
                 "process": EmonProcessList.LOG_TO_FEED,
                 "engine": EmonEngines.PHPFINA.value,
                 "options": {"interval": 1}
                 }
            ]
        },
        {
            "name": "I3",
            "nodeid": "emon_tools_ex1",
            "description": "Managed Input",
            "feeds": [
                {"name": "F3", "tag": "emon_tools_ex1",
                 "process": EmonProcessList.LOG_TO_FEED,
                 "engine": EmonEngines.PHPFINA.value,
                 "options": {"interval": 1}
                 }
            ]
        }
    ]


def main():
    """fetches somes datas in emoncms"""
    start_time = time.perf_counter()
    emonpy = EmonPy(
        os.getenv('EMONCMS_URL'), os.getenv('API_KEY'))
    result = emonpy.create_structure(
        structure=get_emon_structure()
    )
    print(
        f"Emoncms Input Feeds structure created in "
        f"{time.perf_counter() - start_time}s"
    )
    print(result)


if __name__ == "__main__":
    main()
