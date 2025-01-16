"""
Emoncms API example.

Create EmonCms Inputs Feeds structure if not exist.
"""
import os
import time
import random
from emon_tools.emon_api_core import EmonEngines
from emon_tools.emon_api_core import EmonProcessList
from emon_tools.api_utils import Utils as Ut
from emon_tools.fina_utils import Utils as Fut
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


class DataBulk:
    """Emoncms DataBulk example"""
    def __init__(self, url: str, api_key: str):
        self.cli = EmonPy(
            url=url,
            api_key=api_key
        )

    def init_structure(self, structure):
        """Init Inputs feeds structure"""
        start_time = time.perf_counter()
        result = self.cli.create_structure(
            structure=structure
        )
        print('-' * 10)
        print('-' * 10)
        print(
            "Emoncms Input Feeds structure verrified in "
            f"{time.perf_counter() - start_time}s.\n"
            "Only add needed Inputs or feeds from structure data."
        )
        print('-' * 10)
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
        print('-' * 10)
        print('-' * 10)
        print(
            "Writing Emoncms Input Bulk random dummy data points. \n"
            "In total 5 * 60s at 1s interval"
        )
        print('-' * 10)
        start_date = Ut.get_string_datetime_from_timestamp(
            perf[0]['start_time'],
            timezone=None
        )
        end_date = Ut.get_string_datetime_from_timestamp(
            perf[-1]['end_time'],
            timezone=None
        )
        print('-' * 10)
        print(
            "Look  in your Emoncms instance at: \n"
            f"{self.cli.url}/graph/{extended[0]['feeds'][0]['id']} \n"
            f"Dummy data was writed from {start_date} to {end_date}."
        )
        print('-' * 10)
        print(perf)
        print('-' * 10)
        return perf

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


def main():
    """fetches somes datas in emoncms"""
    emonpy = DataBulk(
        os.getenv('EMONCMS_URL'), os.getenv('API_KEY'))
    emonpy.init_structure(
        structure=get_emon_structure()
    )
    emonpy.dummy_bulk(
        structure=get_emon_structure()
    )


if __name__ == "__main__":
    main()
