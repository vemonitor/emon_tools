"""Emon api runner"""
from typing import Optional
from emon_tools.emon_api_core import InputGetType
from emon_tools.emonpy_core import EmonPyCore
from emon_tools.emon_api import EmonFeedsApi
from emon_tools.api_utils import Utils as Ut
from emon_tools.api_utils import SUCCESS_KEY
from emon_tools.api_utils import MESSAGE_KEY


class EmonPy(EmonFeedsApi):
    """Emon py worker"""
    def __init__(self, url: str, api_key: str):
        EmonFeedsApi.__init__(self, url, api_key)

    def get_inputs(
        self,
        input_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs list"""
        inputs = self.list_inputs_fields(
            InputGetType.EXTENDED
        )
        return EmonPyCore.filter_inputs_list(
            inputs=inputs,
            input_filter=input_filter
        )

    def get_feeds(
        self,
        feed_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs Feeds structure"""
        feeds = self.list_feeds()
        return EmonPyCore.filter_feeds_list(
            feeds=feeds,
            feed_filter=feed_filter
        )

    def get_structure(
        self,
        input_filter: Optional[dict] = None,
        feed_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs Feeds structure"""
        inputs = self.get_inputs(input_filter=input_filter)
        feeds = self.get_feeds(feed_filter=feed_filter)
        return EmonPyCore.filter_inputs_feeds(
            inputs=inputs,
            feeds=feeds,
            input_filter=input_filter,
            feed_filter=feed_filter
        )

    def create_input_feeds(
        self,
        feeds: list
    ):
        """Create input feeds structure"""
        nb_added, processes = 0, []
        if Ut.is_list(feeds, not_empty=True):
            for feed in feeds:
                if Ut.is_dict(feed, not_empty=True):
                    if "process" in feed:
                        new_feed = self.create_feed(
                            **Ut.filter_dict_by_keys(
                                input_data=feed,
                                filter_data=['process'],
                                filter_in=False
                            )
                        )
                    else:
                        new_feed = self.create_feed(
                            **feed
                        )
                    if new_feed.get(SUCCESS_KEY) is False:
                        raise ValueError(
                            "Fatal error: "
                            "Unable to set feed structure "
                            f"node {feed.get('tag')} - name {feed.get('name')}"
                        )
                    response = new_feed.get('message')
                    feed_id = Ut.validate_integer(
                        int(response.get('feedid')),
                        "Feed id",
                        positive=True
                    )
                    nb_added += 1
                    processes.append([1, feed_id])
        return nb_added, processes

    def create_inputs(
        self,
        inputs: list
    ) -> int:
        """Create input feeds structure"""
        result = 0
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
                    new_inputs = self.post_inputs(
                        node=node,
                        data=data
                    )
                    if new_inputs.get(SUCCESS_KEY) is False:
                        raise ValueError(
                            "Fatal error: "
                            "Unable to set inputs structure "
                            f"node {node} - names {items}"
                        )
                    result += len(items)

        return result

    def init_inputs_structure(
        self,
        structure: list
    ) -> int:
        """Initialyze inputs structure from EmonCms API."""
        result = 0
        if Ut.is_list(structure, not_empty=True):
            filter_inputs = EmonPyCore.get_inputs_filters_from_structure(
                structure=structure
            )
            inputs = self.list_inputs_fields(
                InputGetType.EXTENDED
            )
            inputs_on = Ut.filter_list_of_dicts(
                inputs.get(MESSAGE_KEY),
                filter_data=filter_inputs,
                filter_in=True
            )
            if Ut.is_list(inputs_on, not_empty=True):
                inputs_filter = EmonPyCore.get_inputs_filters_from_structure(
                    structure=inputs_on
                )
                inputs_out = Ut.filter_list_of_dicts(
                    input_data=structure,
                    filter_data=inputs_filter,
                    filter_in=False
                )
                if Ut.is_list(inputs_out, not_empty=True):
                    result = self.create_inputs(
                        inputs=inputs_out
                    )
            else:
                result = self.create_inputs(
                    inputs=structure
                )
        return result

    def add_input_feeds_structure(
        self,
        input_item: dict,
        feeds_on: list
    ) -> list:
        """Create inputs feeds structure from EmonCms API."""
        nb_added, processes = 0, []
        if Ut.is_dict(input_item, not_empty=True):

            if Ut.is_list(feeds_on, not_empty=True):
                feeds_out = []
                for feed in input_item.get('feeds'):

                    for existant_feed in feeds_on:
                        is_new = feed.get('name') != existant_feed.get('name')\
                            or feed.get('tag') != existant_feed.get('tag')
                        if is_new:
                            feeds_out.append(feed)
                        else:
                            processes.append([1, int(existant_feed.get('id'))])

                if Ut.is_list(feeds_out, not_empty=True):
                    nb_added, new_processes = self.create_input_feeds(
                        feeds=feeds_out
                    )
                    if Ut.is_list(new_processes, not_empty=True):
                        processes += new_processes
            else:
                # create item feeds
                nb_added, processes = self.create_input_feeds(
                    feeds=input_item.get('feeds')
                )
        return nb_added, processes

    def update_input_fields(
        self,
        input_id: int,
        current: str,
        description: str
    ) -> int:
        """Initialyze inputs structure from EmonCms API."""
        result = 0
        response = None
        Ut.validate_integer(input_id, "Input Id", positive=True)
        if Ut.is_valid_node(description)\
                and current != description:
            fields = {"description": description}
            response = self.set_input_fields(
                input_id=input_id,
                fields=fields
            )
        if Ut.is_request_success(response)\
                and response[MESSAGE_KEY] == 'Field updated':
            result += 1
        return result

    def update_input_process_list(
        self,
        input_id: int,
        current_processes: str,
        new_processes: list
    ) -> int:
        """Initialyze inputs structure from EmonCms API."""
        result = 0
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
            process_list = ','.join(process_list)
            response = self.set_input_process_list(
                input_id=input_id,
                process_list=process_list
            )
            if Ut.is_request_success(response)\
                    and response[MESSAGE_KEY] == 'Input processlist updated':
                result += 1
        return result

    def create_structure(
        self,
        structure: list
    ):
        """Create inputs feeds structure from EmonCms API."""
        result = None
        if Ut.is_list(structure, not_empty=True):
            result = {
                'nb_updated_inputs': 0,
                'nb_added_inputs': 0,
                'nb_added_feeds': 0
            }
            result['nb_added_inputs'] = self.init_inputs_structure(
                structure=structure
            )
            inputs, feeds = self.get_structure()

            for item in structure:
                inputs_on, feeds_on = EmonPyCore.get_existant_structure(
                    input_item=item,
                    inputs=inputs,
                    feeds=feeds
                )
                # is invalid current input
                if not Ut.is_list(inputs_on)\
                        or len(inputs_on) != 1:
                    raise ValueError(
                        "Fatal Error, inputs was not added to server."
                    )
                # Create Input Feeds
                nb_added, processes = self.add_input_feeds_structure(
                    input_item=item,
                    feeds_on=feeds_on
                )

                inputs_on = inputs_on[0]
                input_id = int(inputs_on.get('id'))
                key = f"input_{input_id}"
                result[key] = {}

                result['nb_added_feeds'] += nb_added
                result[key]['input_feeds'] = nb_added
                # Set Input description
                nb_updated = self.update_input_fields(
                    input_id=input_id,
                    current=inputs_on.get('description'),
                    description=item.get('description')
                )
                result['nb_updated_inputs'] += nb_updated
                result[key]['input_fields'] = nb_updated
                # Set input Process list
                nb_updated = self.update_input_process_list(
                    input_id=input_id,
                    current_processes=inputs_on.get('processList'),
                    new_processes=processes
                )
                result['nb_updated_inputs'] += nb_updated
                result[key]['input_process'] = nb_updated
        return result

    def get_extended_structure(
        self,
        structure: list
    ):
        """Get extended structure."""
        result = []
        if Ut.is_list(structure, not_empty=True):
            inputs, feeds = self.get_structure()
            for item in structure:
                inputs_on, feeds_on = EmonPyCore.get_existant_structure(
                    input_item=item,
                    inputs=inputs,
                    feeds=feeds
                )
                if Ut.is_list(inputs_on) and len(inputs_on) == 1:
                    inputs_on = inputs_on[0]
                    inputs_on.update({'feeds': feeds_on})
                    result.append(
                        inputs_on
                    )
        return result

    def get_extended_inputs_by_filters(
        self,
        input_filter: dict,
        feed_filter: dict
    ):
        """Get extended structure."""
        inputs, feeds = self.get_structure()
        if Ut.is_dict(input_filter, not_empty=True):
            # filter inputs
            inputs_on = Ut.filter_list_of_dicts(
                input_data=inputs,
                filter_data=input_filter
            )
            if len(inputs_on) == 0:
                return [], []
            inputs_feeds = EmonPyCore.get_feeds_from_inputs_list(
                input_data=inputs_on,
                feed_data=feeds
            )
            return EmonPy.get_structure_by_filtered_feeds(
                inputs=inputs_on,
                feeds=inputs_feeds,
                feed_filter=feed_filter
            )

        if Ut.is_dict(feed_filter, not_empty=True):
            return EmonPy.get_structure_by_filtered_feeds(
                inputs=inputs_on,
                feeds=inputs_feeds,
                feed_filter=feed_filter
            )
        return inputs, feeds

    @staticmethod
    def get_structure_by_filtered_feeds(
        inputs: list[dict],
        feeds: list[dict],
        feed_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs Feeds structure"""
        if Ut.is_dict(feed_filter, not_empty=True)\
                and Ut.is_list(feeds, not_empty=True):
            feeds_on = Ut.filter_list_of_dicts(
                input_data=feeds,
                filter_data=feed_filter
            )
            ids = [x.get('id') for x in feeds_on]
            inputs_on = [
                item
                for item in inputs
                if len(item['process_list']) > 0
                for process_list in item['process_list']
                if len(process_list) == 2 and process_list[1] in ids
            ]
            return inputs_on, feeds_on
        return inputs, feeds
