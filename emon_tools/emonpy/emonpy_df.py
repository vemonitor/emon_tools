"""Emon api runner"""
from typing import Optional
import numpy as np
import pandas as pd
from emon_tools.emon_api.emon_api_core import InputGetType
from emon_tools.emonpy.emonpy_core import EmonPyCore
from emon_tools.emon_api.emon_api import EmonFeedsApi
from emon_tools.emon_api.api_utils import Utils as Ut
from emon_tools.emon_api.api_utils import SUCCESS_KEY
from emon_tools.emon_api.api_utils import MESSAGE_KEY


class EmonDfPy(EmonFeedsApi):
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
        if Ut.is_request_success(inputs):
            # Format numeric fields
            inputs = EmonDfPy.format_inputs_df(
                data=EmonPyCore.format_list_of_dicts(
                        inputs.get(MESSAGE_KEY))
            )
            is_input_filter = EmonDfPy.validate_filter(
                input_filter,
                self.get_inputs_labels()
            )

            # filter inputs values
            if is_input_filter:
                inputs = inputs[
                    inputs[list(input_filter)].isin(input_filter).all(1)]
        else:
            inputs = None
        return inputs

    def get_feeds(
        self,
        feed_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs Feeds structure"""
        feeds = self.list_feeds()
        if Ut.is_request_success(feeds):
            # Format numeric fields
            feeds = EmonDfPy.format_feeds_df(
                data=EmonPyCore.format_list_of_dicts(
                    feeds.get(MESSAGE_KEY))
            )
            is_feed_filter = EmonDfPy.validate_filter(
                feed_filter,
                self.get_feeds_labels()
            )
            # filter inputs values
            if is_feed_filter:
                feeds = feeds[
                    feeds[list(feed_filter)].isin(feed_filter).all(1)]
        else:
            feeds = None
        return feeds

    def get_structure(
        self,
        input_filter: Optional[dict] = None,
        feed_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs Feeds structure"""
        inputs = self.get_inputs(input_filter=input_filter)
        feeds = self.get_feeds(feed_filter=feed_filter)
        is_input_filter = EmonDfPy.validate_filter(
            input_filter,
            self.get_inputs_labels()
        )
        is_feed_filter = EmonDfPy.validate_filter(
            feed_filter,
            self.get_feeds_labels()
        )
        if is_input_filter:
            return (
                EmonDfPy.format_inputs_df(
                    inputs.get(MESSAGE_KEY),
                ),
                EmonDfPy.format_feeds_df(
                    feeds.get(MESSAGE_KEY)
                )
            )
        return inputs, feeds

    def get_extended_inputs_by_filters(
        self,
        input_filter: Optional[dict] = None,
        feed_filter: Optional[dict] = None
    ):
        """Get extended inputs by filters"""
        result = None, None
        inputs, feeds = self.get_structure()
        is_input_filter = EmonDfPy.validate_filter(
            input_filter,
            self.get_inputs_labels()
        )
        is_feed_filter = EmonDfPy.validate_filter(
            feed_filter,
            self.get_feeds_labels()
        )
        if is_input_filter:
            df_inputs = inputs[
                inputs[list(input_filter)].isin(input_filter).all(1)]
            if df_inputs.shape[0] == 0:
                return result
            feed_ids = [
                x
                for xs in df_inputs['feed_id']
                for x in xs
            ]

            if len(feed_ids) == 0\
                    or not is_feed_filter:
                return df_inputs, None

            if is_feed_filter:
                feed_filter['id'] = feed_ids
                result = EmonDfPy.get_structure_by_filtered_feeds(
                    inputs=inputs,
                    feeds=feeds,
                    feed_filter=feed_filter
                )
        elif is_feed_filter:
            result = EmonDfPy.get_structure_by_filtered_feeds(
                    inputs=inputs,
                    feeds=feeds,
                    feed_filter=feed_filter
                )
        return result

    @staticmethod
    def get_process_ids(process_list: set):
        """Get emoncms Inputs Feeds structure"""
        result = None
        if Ut.is_set(process_list, not_empty=True):
            result = [y for _, y in process_list]
        return result

    @staticmethod
    def get_inputs_by_feeds(
        inputs: list[dict],
        feeds: list[dict]
    ):
        """Get emoncms Inputs Feeds structure"""
        result = None
        if Ut.is_list(feeds, not_empty=True):
            tmp_filter = feeds['id'].to_list()
            mask = []
            for xs in inputs['feed_id']:
                if Ut.is_list(xs, not_empty=True):
                    for x in xs:
                        mask.append(x in tmp_filter)
                else:
                    mask.append(False)

            return inputs[mask]
        return []

    @staticmethod
    def get_structure_by_filtered_feeds(
        inputs: list[dict],
        feeds: list[dict],
        feed_filter: Optional[dict] = None
    ):
        """Get emoncms Inputs Feeds structure"""
        result = None
        is_feed_filter = EmonDfPy.validate_filter(
            feed_filter,
            EmonDfPy.get_feeds_labels()
        )
        if Ut.is_list(feeds, not_empty=True)\
                and is_feed_filter:
            df_feeds = feeds[
                feeds[list(feed_filter)].isin(feed_filter).all(1)]
            tmp_filter = df_feeds['id'].to_list()
            mask = []
            for xs in inputs['feed_id']:
                if Ut.is_list(xs, not_empty=True):
                    for x in xs:
                        mask.append(x in tmp_filter)
                else:
                    mask.append(False)

            df_inputs = inputs[mask]
            result = df_inputs, df_feeds
        return result

    @staticmethod
    def format_inputs_df(data: list):
        """Get emoncms Inputs Feeds structure"""
        df = None
        if Ut.is_list(data, not_empty=True):
            df = pd.DataFrame(data)
            df['id'] = pd.to_numeric(df['id'])
            df['time'] = pd.to_numeric(df['time'])
            df['value'] = pd.to_numeric(df['value'])
            df['process_list'] = df['processList'].apply(
                EmonPyCore.get_string_process_list)
            df['feed_id'] = df['process_list'].apply(
                EmonDfPy.get_process_ids)
        return df

    @staticmethod
    def format_feeds_df(data: list):
        """Get emoncms Inputs Feeds structure"""
        df = None
        if Ut.is_list(data, not_empty=True):
            df = pd.DataFrame(data)
            df['public'] = df['public'].replace('', pd.NA)
            df['public'] = df['public'].fillna(0)
            df['processList'] = df['processList'].fillna('')
            df = df.astype(dtype={
                "id": "int64",
                "userid": "int64",
                "name": "string",
                "tag": "string",
                "public": "int64",
                "size": "int64",
                "engine": "int64",
                "processList": "string",
                "unit": "string",
                "time": "float64",
                "value": "float64",
                "start_time": "float64",
                "end_time": "float64",
                "interval": "float64",
            })
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df['start_time'] = pd.to_datetime(df['start_time'], unit='s')
            df['end_time'] = pd.to_datetime(df['end_time'], unit='s')
        return df

    @staticmethod
    def validate_filter(
        input_filter: dict,
        labels: list
    ):
        """Get Emoncms inputs labels"""
        result = False
        if Ut.is_dict(input_filter, not_empty=True)\
                and Ut.is_list(labels, not_empty=True):
            errors = []
            for key, item in input_filter.items():
                if key not in labels:
                    errors.append(key)
            if len(errors) > 0:
                raise ValueError(
                    "Invalid input filter keys: "
                    f"({', '.join(errors)})"
                )
            result = True
        return result

    @staticmethod
    def get_inputs_labels():
        """Get Emoncms inputs labels"""
        return [
            "id",
            "nodeid",
            "name",
            "description",
            "processList",
            "time",
            "value"
        ]

    @staticmethod
    def get_feeds_labels():
        """Get Emoncms feeds labels"""
        return [
            "id",
            "userid",
            "name",
            "tag",
            "public",
            "size",
            "engine",
            "processList",
            "unit",
            "time",
            "value",
            "start_time",
            "end_time",
            "interval"
        ]
