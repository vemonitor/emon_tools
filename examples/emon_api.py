"""Emoncms API example."""
import os
import time
from emon_tools.emon_api_core import EmonEngines
from emon_tools.emon_api_core import EmonProcessList
from emon_tools.emonpy import EmonPy


def print_results(response, title):
    """Prints the response."""
    print("-" * 20)
    print(title)
    print("-" * 20)
    if response is not None:
        print("nb - ", len(response))
    print(response)


def print_emon_structure(extended_inputs):
    """Prints the response."""
    sep = "-" * 20
    ident = "   "
    print(sep)
    print("Emoncms Inputs Feeds Structure")
    print("nb inputs - ", len(extended_inputs))
    print(sep)
    if isinstance(extended_inputs, list):
        for input_data in extended_inputs:
            print("Input: ", input_data["name"])
            print("Node: ", input_data["nodeid"])
            print("Related feeds: ")
            for feed in input_data["feeds"]:
                print(ident, "id: ", feed["id"])
                print(ident, "name: ", feed["name"])
                print(ident, "node: ", feed["tag"])
                print(ident, "last value: ", feed["value"])
                print(ident, "last time: ", feed["time"])
                print(sep)
            print(sep)
            print(sep)


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
