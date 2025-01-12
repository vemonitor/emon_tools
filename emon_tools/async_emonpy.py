"""Emon api runner"""
from emon_tools.emon_api_core import InputGetType
from emon_tools.emon_api_core import EmonHelper
from emon_tools.async_emon_api import AsyncEmonFeeds
from emon_tools.api_utils import Utils as Ut
from emon_tools.api_utils import SUCCESS_KEY
from emon_tools.api_utils import MESSAGE_KEY


class AsyncEmonPy(AsyncEmonFeeds):
    """Emon py worker"""
    def __init__(self, url: str, api_key: str):
        AsyncEmonFeeds.__init__(self, url, api_key)

    async def get_structure(self):
        """Get emoncms Inputs Feeds structure"""
        inputs = await self.async_list_inputs_fields(
            InputGetType.EXTENDED
        )
        feeds = await self.async_list_feeds()
        if Ut.is_request_success(inputs)\
                and Ut.is_request_success(feeds):
            return inputs.get(MESSAGE_KEY), feeds.get(MESSAGE_KEY)
        return None, None

    async def create_input_feeds(
        self,
        feeds=list
    ):
        """Create input feeds structure"""
        processes = []
        if Ut.is_list(feeds, not_empty=True):
            for feed in feeds:
                if Ut.is_dict(feed, not_empty=True):
                    if "process" in feed:
                        del feed['process']
                    new_feed = await self.async_create_feed(
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
                    processes.append([1, feed_id])
        return processes

    async def create_inputs(
        self,
        inputs=list
    ):
        """Create input feeds structure"""
        result = False
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
                        new_inputs = await self.async_post_inputs(
                            node=node,
                            data=data
                        )
                        if new_inputs.get(SUCCESS_KEY) is False:
                            raise ValueError(
                                "Fatal error: "
                                "Unable to set inputs structure "
                                f"node {node} - names {items}"
                            )
                    result = True

        return result

    async def init_inputs_structure(
        self,
        structure: list
    ):
        """Initialyze inputs structure from EmonCms API."""
        result = None
        if Ut.is_list(structure, not_empty=True):
            filter_inputs = EmonHelper.get_inputs_filters_from_structure(
                structure=structure
            )
            inputs = await self.async_list_inputs_fields(
                InputGetType.EXTENDED
            )
            inputs_on = Ut.filter_list_of_dicts(
                inputs.get(MESSAGE_KEY),
                filter_data=filter_inputs,
                filter_in=True
            )
            if Ut.is_list(inputs_on, not_empty=True):
                inputs_filter = EmonHelper.get_inputs_filters_from_structure(
                    structure=inputs_on
                )
                inputs_out = Ut.filter_list_of_dicts(
                    input_data=structure,
                    filter_data=inputs_filter,
                    filter_in=False
                )
                if Ut.is_list(inputs_out, not_empty=True):
                    result = await self.create_inputs(
                        inputs=inputs_out
                    )
            else:
                result = await self.create_inputs(
                    inputs=structure
                )
        return result

    async def add_input_feeds_structure(
        self,
        input_item: dict,
        feeds_on: list
    ):
        """Create inputs feeds structure from EmonCms API."""
        processes = []
        if Ut.is_dict(input_item, not_empty=True):

            if Ut.is_list(feeds_on, not_empty=True):
                feeds_out = []
                for feed in input_item.get('feeds'):

                    for existant_feed in feeds_on:
                        is_new = feed.get('name') != existant_feed.get('name')\
                            and feed.get('tag') != existant_feed.get('tag')
                        if is_new:
                            feeds_out.append(feed)
                        else:
                            processes.append([1, int(existant_feed.get('id'))])

                if Ut.is_list(feeds_out, not_empty=True):
                    new_processes = await self.create_input_feeds(
                        feeds=feeds_out
                    )
                    if Ut.is_list(new_processes, not_empty=True):
                        processes += new_processes
            else:
                # create item feeds
                processes = await self.create_input_feeds(
                    feeds=input_item.get('feeds')
                )
        return processes

    async def set_input_fields(
        self,
        input_id: int,
        current: str,
        description: str
    ):
        """Initialyze inputs structure from EmonCms API."""
        result = None
        Ut.validate_integer(input_id, "Input Id", positive=True)
        if Ut.is_valid_node(description)\
                and current != description:
            fields = {"description": description}
            result = await self.async_set_input_fields(
                input_id=input_id,
                fields=fields
            )
        return result

    async def set_input_process_list(
        self,
        input_id: int,
        current_processes: str,
        new_processes: list
    ):
        """Initialyze inputs structure from EmonCms API."""
        result = None
        process_list = EmonHelper.format_process_list(new_processes)

        nb_process = len(process_list)
        nb_current = 0
        if Ut.is_str(current_processes) and nb_process > 0:
            currents = EmonHelper.format_string_process_list(current_processes)
            if Ut.is_set(currents, not_empty=True):
                nb_current = len(currents)
                process_list = process_list.union(currents)

        if nb_process > 0\
                and nb_current != nb_process:
            process_list = ','.join(process_list)
            result = await self.async_set_input_process_list(
                input_id=input_id,
                process_list=process_list
            )
        return result

    async def create_structure(
        self,
        structure=list
    ):
        """Create inputs feeds structure from EmonCms API."""
        result = None
        if Ut.is_list(structure, not_empty=True):
            result = {}
            result['init_inputs'] = await self.init_inputs_structure(
                structure=structure
            )
            inputs, feeds = await self.get_structure()

            for item in structure:
                inputs_on, feeds_on = EmonHelper.get_existant_structure(
                    input_item=item,
                    inputs=inputs,
                    feeds=feeds
                )
                if Ut.is_list(inputs_on) and Ut.is_list(feeds_on):
                    # Create Input Feeds
                    processes = await self.add_input_feeds_structure(
                        input_item=item,
                        feeds_on=feeds_on
                    )

                    # create item input
                    if not Ut.is_list(inputs_on)\
                            or len(inputs_on) != 1:
                        raise ValueError(
                            "Fatal Error, inputs was not added to server."
                        )
                    inputs_on = inputs_on[0]
                    input_id = int(inputs_on.get('id'))
                    key = f"input_{input_id}"
                    result[key] = {}
                    # Set Input description
                    result[key]['fields'] = await self.set_input_fields(
                        input_id=input_id,
                        current=inputs_on.get('description'),
                        description=item.get('description')
                    )
                    # Set input Process list
                    result[key]['process'] = await self.set_input_process_list(
                        input_id=input_id,
                        current_processes=inputs_on.get('processList'),
                        new_processes=processes
                    )
        return result
