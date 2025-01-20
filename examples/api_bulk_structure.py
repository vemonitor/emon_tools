"""
Emoncms API example.

Inputs Feeds structure supervision.
Create or Update Emoncms Inputs Feeds structure,
based on structured dictionary returned by `get_emon_structure`.


Input bulk post data example.
Send 5 * 60 dummy data points at 1s interval,
to supervised inputs.
"""
import os
import sys
import argparse
import time
import random
from typing import Optional
from dotenv import load_dotenv
from emon_tools.__init__ import __version__
from emon_tools.emon_api_core import EmonEngines
from emon_tools.emon_api_core import EmonProcessList
from emon_tools.api_utils import Utils as Ut
from emon_tools.fina_utils import Utils as Fut
from emon_tools.emonpy import EmonPy

SEAPARATOR = '-' * 20


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


class DataBulk:
    """Emoncms DataBulk example"""
    def __init__(self, url: str, apikey: str):
        self.cli = EmonPy(
            url=url,
            api_key=apikey
        )

    def init_structure(self, structure):
        """Init Inputs feeds structure"""
        start_time = time.perf_counter()
        result = self.cli.create_structure(
            structure=structure
        )
        print("Emoncms Inputs Feeds structure supervision example.")
        print(SEAPARATOR)
        print(
            "Emoncms Input Feeds structure verrified in "
            f"{time.perf_counter() - start_time}s.\n"
            "Only add needed Inputs or feeds from structure data."
        )
        print(SEAPARATOR)
        print(f"Nb added inputs: {result['nb_added_inputs']}")
        print(
            f"Nb updated inputs: {result['nb_updated_inputs']}"
        )
        print(
            f"Nb Added Feeds: {result['nb_added_feeds']}"
        )
        # print(result)

    def dummy_bulk(self, structure):
        """
        Bulk dummy data to Emoncms from input feeds structure.
        """
        extended = self.cli.get_extended_structure(
            structure=structure
        )
        start_time = int(Fut.get_start_day(time.time(), timezone=None))
        perf = []
        time_range = 60
        # bulk time_rage * 5 points
        for i in range(1, 6):
            start_perf = time.perf_counter()
            ref_time = int(start_time + (i * time_range))
            response = self.cli.input_bulk(
                data=DataBulk.generate_dummy_data(
                    structure=extended,
                    time_range=time_range),
                timestamp=ref_time
            )
            nb_perfs = len(perf)
            diff_item = 0
            item_start = ref_time - time_range
            if nb_perfs > 0:
                last_item = perf[-1]
                diff_item = last_item['end_time'] - item_start

            perf.append({
                "i": i,
                "start_time": item_start,
                "end_time": ref_time,
                "diff": diff_item,
                "nb_inputs": len(extended),
                "res": response,
                "perf": time.perf_counter() - start_perf})
            time.sleep(0.1)
        print(SEAPARATOR * 2)
        print(
            "Writing Emoncms Input Bulk random dummy data points. \n"
            "In total 5 * 60s at 1s interval"
        )
        print(SEAPARATOR)
        start_date = Ut.get_string_datetime_from_timestamp(
            perf[0]['start_time'],
            timezone=None
        )
        end_date = Ut.get_string_datetime_from_timestamp(
            perf[-1]['end_time'],
            timezone=None
        )
        print(SEAPARATOR)
        print(
            "Look  in your Emoncms instance at: \n"
            f"{self.cli.url}/graph/{extended[0]['feeds'][0]['id']} \n"
            f"Dummy data was writed from {start_date} to {end_date}."
        )
        print(SEAPARATOR)
        print(perf)
        print(SEAPARATOR)
        return perf

    def extended_inputs(self):
        """
        Get extended Inputs structure from Emoncms Api
        """
        inputs, feeds = self.cli.get_structure(
            input_filter={
                "nodeid": ["emon_tools_ex1"],
                "name": ["I1", "I2", "I3"]
            },
            feed_filter={
                "name": ["F2A", "I1", "F3"],
            }
        )
        print(SEAPARATOR)
        print("Inputs: ", inputs)
        print(SEAPARATOR)
        print("Feeds: ", feeds)

    @staticmethod
    def generate_dummy_data(
        structure: list,
        time_range: int
    ):
        """Generate dummy data by time_range"""
        data = []
        if Ut.is_list(structure, not_empty=True):

            for time_ref in range(-time_range, 1):
                values = []
                node = None
                for input_item in structure:
                    values.append({
                        input_item.get('name'): random.randrange(-10, 45)})
                    node = input_item.get('nodeid')
                data.append([
                    time_ref,
                    node
                ] + values)
        return data


def parse_args(args):
    """
    Parsing function
    :param args: arguments passed from the command line
    :return: return parser
    """
    # create arguments
    parser = argparse.ArgumentParser(
        prog='emon-tools',
        description='Example usage of emonpy module.'
    )
    parser.add_argument(
        '--all',
        help='Execute all actions.',
        required=False,
        action='store_true'
    )
    parser.add_argument(
        '-s', '--src',
        help='Search for particualar inputs feeds structure.',
        required=False,
        action='store_true'
    )
    parser.add_argument(
        '-a', '--ast',
        help='Supervise particualar inputs feeds structure.',
        required=False,
        action='store_true'
    )
    parser.add_argument(
        '-p', '--post',
        help='Post input bulk dummy data.',
        required=False,
        action='store_true'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='emon-tools ' + __version__
    )

    # parse arguments from script parameters
    return parser.parse_args(args)


def get_actions(parsed: Optional[argparse.Namespace]):
    """
    Parsing function
    :param args: arguments passed from the command line
    :return: return parser
    """
    result = {
        'all': False,
        'src': True,
        'ast': False,
        'post': False,
    }
    if parsed is not None:
        result = {
            'all': parsed.all,
            'src': parsed.src,
            'ast': parsed.ast,
            'post': parsed.post,
        }
    return result


if __name__ == "__main__":
    options = None
    sys.argv.append('--ast')
    if len(sys.argv) > 1:
        options = parse_args(sys.argv[1:])
    options = get_actions(options)
    print(SEAPARATOR * 2)
    print("emon-tools Example usage. \n")
    print("(to execute you will need set up your .env file)")
    print(SEAPARATOR * 2)

    load_dotenv()
    emon_url = os.getenv("EMONCMS_URL")
    api_key = os.getenv("API_KEY")
    emonpy = DataBulk(
        url=emon_url,
        apikey=api_key)

    print(
        "Search for particualar inputs feeds structure (--src): ",
        options.get('src'))
    if options.get('all', False) or options.get('src', False):
        emonpy.extended_inputs()

    print('\n', SEAPARATOR)
    print(
        "Supervise particualar inputs feeds structure (--ast): ",
        options.get('ast'))
    if options.get('all', False) or options.get('ast', False):
        emonpy.init_structure(
            structure=get_emon_structure()
        )

    print('\n', SEAPARATOR)
    print(
        "Post input bulk dummy data (--post): ",
        options.get('post'))
    if options.get('all', False) or options.get('post', False):
        emonpy.dummy_bulk(
            structure=get_emon_structure()
        )
