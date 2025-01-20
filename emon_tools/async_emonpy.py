"""Emon api runner"""
from typing import Optional
from emon_tools.emon_api_core import InputGetType
from emon_tools.emonpy_core import EmonPyCore
from emon_tools.async_emon_api import AsyncEmonFeeds
from emon_tools.api_utils import Utils as Ut
from emon_tools.api_utils import SUCCESS_KEY
from emon_tools.api_utils import MESSAGE_KEY


class AsyncEmonPy(AsyncEmonFeeds):
    """Emon py worker"""
    def __init__(self, url: str, api_key: str):
        AsyncEmonFeeds.__init__(self, url, api_key)

    async def get_inputs(
        self,
        input_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs Feeds structure"""
        inputs = await self.async_list_inputs_fields(
            InputGetType.EXTENDED
        )
        return EmonPyCore.filter_inputs_list(
            inputs=inputs,
            input_filter=input_filter
        )

    async def get_feeds(
        self,
        feed_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs Feeds structure"""
        feeds = await self.async_list_feeds()
        return EmonPyCore.filter_feeds_list(
            feeds=feeds,
            feed_filter=feed_filter
        )

    async def get_structure(
        self,
        input_filter: Optional[dict] = None,
        feed_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs Feeds structure"""
        inputs = await self.get_inputs(input_filter=input_filter)
        feeds = await self.get_feeds(feed_filter=feed_filter)
        return EmonPyCore.filter_inputs_feeds(
            inputs=inputs,
            feeds=feeds,
            input_filter=input_filter,
            feed_filter=feed_filter
        )

    async def create_input_feeds(
        self,
        feeds: list
    ):
        """Create input feeds structure"""
        nb_added, processes = 0, []
        for feed in EmonPyCore.iter_feeds_to_add(feeds):
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
            nb_added += 1
            processes.append([1, feed_id])
        return nb_added, processes

    async def create_inputs(
        self,
        inputs: list
    ) -> int:
        """Create input feeds structure"""
        result = 0
        for node, items, data in EmonPyCore.iter_inputs_to_add(inputs):
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
            result += len(items)

        return result

    async def init_inputs_structure(
        self,
        structure: list
    ) -> int:
        """Initialyze inputs structure from EmonCms API."""
        result = 0
        if Ut.is_list(structure, not_empty=True):
            filter_inputs = EmonPyCore.get_inputs_filters_from_structure(
                structure=structure
            )
            inputs = await self.get_inputs(
                input_filter=filter_inputs
            )
            inputs_on = Ut.filter_list_of_dicts(
                inputs,
                filter_data=filter_inputs,
                filter_in=True
            )
            if Ut.is_list(inputs_on, not_empty=True):
                inputs_out = EmonPyCore.init_inputs_structure(
                    structure=structure,
                    inputs=inputs
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
    ) -> list:
        """Create inputs feeds structure from EmonCms API."""
        nb_added, processes = 0, []
        if Ut.is_dict(input_item, not_empty=True):

            if Ut.is_list(feeds_on, not_empty=True):
                feeds_out, processes = EmonPyCore.get_feeds_to_add(
                    input_item=input_item,
                    feeds_on=feeds_on
                )
                if Ut.is_list(feeds_out, not_empty=True):
                    nb_added, new_processes = await self.create_input_feeds(
                        feeds=feeds_out
                    )
                    if Ut.is_list(new_processes, not_empty=True):
                        processes += new_processes
            else:
                # create item feeds
                nb_added, processes = await self.create_input_feeds(
                    feeds=input_item.get('feeds')
                )
        return nb_added, processes

    async def update_input_fields(
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
            response = await self.async_set_input_fields(
                input_id=input_id,
                fields=fields
            )
        if Ut.is_request_success(response)\
                and response[MESSAGE_KEY] == 'Field updated':
            result += 1
        return result

    async def update_input_process_list(
        self,
        input_id: int,
        current_processes: str,
        new_processes: list
    ) -> int:
        """Initialyze inputs structure from EmonCms API."""
        result = 0
        process_list = EmonPyCore.prepare_input_process_list(
            current_processes=current_processes,
            new_processes=new_processes
        )

        if Ut.is_str(process_list, not_empty=True):
            response = await self.async_set_input_process_list(
                input_id=input_id,
                process_list=process_list
            )
            if Ut.is_request_success(response)\
                    and response[MESSAGE_KEY] == 'Input processlist updated':
                result += 1
        return result

    async def create_structure(
        self,
        structure: list
    ):
        """Create inputs feeds structure from EmonCms API."""
        result = {
            'nb_updated_inputs': 0,
            'nb_added_inputs': 0,
            'nb_added_feeds': 0
        }
        if Ut.is_list(structure, not_empty=True):
            filters = EmonPyCore.get_filters_from_structure(
                structure=structure
            )
            inputs, feeds = await self.get_structure(
                input_filter=filters.filter_inputs,
                feed_filter=filters.filter_feeds
            )
            result['nb_added_inputs'] = await self.init_inputs_structure(
                structure=structure
            )

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
                nb_added, processes = await self.add_input_feeds_structure(
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
                nb_updated = await self.update_input_fields(
                    input_id=input_id,
                    current=inputs_on.get('description'),
                    description=item.get('description')
                )
                result['nb_updated_inputs'] += nb_updated
                result[key]['input_fields'] = nb_updated
                # Set input Process list
                nb_updated = await self.update_input_process_list(
                    input_id=input_id,
                    current_processes=inputs_on.get('processList'),
                    new_processes=processes
                )
                result['nb_updated_inputs'] += nb_updated
                result[key]['input_process'] = nb_updated
        return result

    async def get_extended_structure(
        self,
        structure: list
    ):
        """Get extended structure."""
        result = []
        if Ut.is_list(structure, not_empty=True):
            filters = EmonPyCore.get_filters_from_structure(
                structure=structure
            )
            inputs, feeds = await self.get_structure(
                input_filter=filters.filter_inputs,
                feed_filter=filters.filter_feeds
            )
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
