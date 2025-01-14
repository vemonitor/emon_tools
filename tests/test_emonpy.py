"""Test Suite for EmonPy class with 100% coverage."""
from unittest.mock import MagicMock
import pytest
from emon_tools.api_utils import SUCCESS_KEY, MESSAGE_KEY
from emon_tools.emon_api_core import EmonProcessList
from emon_tools.emonpy import EmonPy


class TestEmonPy:
    """Unit tests for the EmonPy class."""

    @pytest.fixture
    def api(self):
        """Fixture to provide an EmonPy instance."""
        emon = EmonPy(url="http://example.com", api_key="123")
        emon.list_inputs_fields = MagicMock()
        emon.list_feeds = MagicMock()
        emon.create_feed = MagicMock()
        emon.post_inputs = MagicMock()
        emon.set_input_fields = MagicMock()
        emon.set_input_process_list = MagicMock()
        return emon

    def test_init(self):
        """Test initialization of EmonPy."""
        emon = EmonPy(url="http://example.com", api_key="123")
        assert emon.api_key == "123"
        assert emon.url == "http://example.com"

    @pytest.mark.parametrize(
        "inputs_response, feeds_response, expected",
        [
            (
                {SUCCESS_KEY: True, MESSAGE_KEY: [{"nodeid": "test_node"}]},
                {
                    SUCCESS_KEY: True,
                    MESSAGE_KEY: [{"id": 1, "name": "test_feed"}]},
                ([{"nodeid": "test_node"}], [{"id": 1, "name": "test_feed"}]),
            ),
            (
                {SUCCESS_KEY: False},
                {
                    SUCCESS_KEY: True,
                    MESSAGE_KEY: [{"id": 1, "name": "test_feed"}]},
                (None, None),
            ),
        ],
    )
    def test_get_structure(
        self,
        api,
        inputs_response,
        feeds_response,
        expected
    ):
        """Test the get_structure method."""
        api.list_inputs_fields.return_value = inputs_response
        api.list_feeds.return_value = feeds_response

        result = api.get_structure()
        assert result == expected

    @pytest.mark.parametrize(
        "feeds, create_feed_results, expected_processes",
        [
            (
                [{"name": "feed1", "tag": "tag1"}],
                [{"message": {"feedid": "1"}, SUCCESS_KEY: True}],
                [[1, 1]],
            ),
            (
                [{"name": "feed1", "tag": "tag1", "process": "1:1"}],
                [{"message": {"feedid": "1"}, SUCCESS_KEY: True}],
                [[1, 1]],
            ),
            ([], [], []),
        ],
    )
    def test_create_input_feeds(
        self,
        api,
        feeds,
        create_feed_results,
        expected_processes
    ):
        """Test the create_input_feeds method."""
        api.create_feed.side_effect = create_feed_results

        result = api.create_input_feeds(feeds=feeds)
        assert result == expected_processes

    def test_create_input_feeds_invalid(
        self,
        api
    ):
        """Test the create_input_feeds method."""
        api.create_feed.side_effect = [
            {"message": "Error", SUCCESS_KEY: False}
        ]

        with pytest.raises(
                ValueError,
                match="Fatal error: Unable to set feed structure.*"):
            api.create_input_feeds(feeds=[{"name": "feed1", "tag": "tag1"}])

    @pytest.mark.parametrize(
        "inputs, post_inputs_responses, expected_count",
        [
            (
                [{"nodeid": "node1", "name": "input1"}],
                [{"message": {}, SUCCESS_KEY: True}],
                1,
            ),
            ([], [], 0),
        ],
    )
    def test_create_inputs(
        self,
        api,
        inputs,
        post_inputs_responses,
        expected_count
    ):
        """Test the create_inputs method."""
        api.post_inputs.side_effect = post_inputs_responses

        result = api.create_inputs(inputs=inputs)
        assert result == expected_count

    def test_create_inputs_invalid(
        self,
        api
    ):
        """Test the create_input_feeds method."""
        api.post_inputs.side_effect = [
            {"message": "Error", SUCCESS_KEY: False}
        ]

        with pytest.raises(
                ValueError,
                match="Fatal error: Unable to set inputs structure.*"):
            api.create_inputs(inputs=[{"nodeid": "node1", "name": "input1"}])

    @pytest.mark.parametrize(
        "structure, inputs, expected_count",
        [
            (
                [
                    {"nodeid": "node2", "name": "input1"},
                    {"nodeid": "node2", "name": "input2"}
                ],
                {
                    SUCCESS_KEY: True,
                    MESSAGE_KEY: [
                        {"nodeid": "node1", "name": "input1"},
                        {"nodeid": "node1", "name": "input2"},
                        {"nodeid": "node1", "name": "input3"},
                        {"nodeid": "node2", "name": "input1"}
                    ]
                },
                1
            ),
            (
                [
                    {"nodeid": "node3", "name": "input1"},
                    {"nodeid": "node3", "name": "input2"}
                ],
                {
                    SUCCESS_KEY: True,
                    MESSAGE_KEY: [
                        {"nodeid": "node1", "name": "input1"},
                        {"nodeid": "node1", "name": "input2"},
                        {"nodeid": "node1", "name": "input3"},
                        {"nodeid": "node2", "name": "input1"}
                    ]
                },
                1
            ),
            ([], [], 0),
        ],
    )
    def test_init_inputs_structure(
        self,
        api,
        structure,
        inputs,
        expected_count
    ):
        """Test the init_inputs_structure method."""
        api.list_inputs_fields = MagicMock(return_value=inputs)
        api.create_inputs = MagicMock(return_value=expected_count)
        result = api.init_inputs_structure(structure=structure)
        assert result == expected_count

    @pytest.mark.parametrize(
        "input_item, feeds_on, expected_created, expected_process",
        [
            (
                {
                    'name': 'I1', 'nodeid': 'emon_tools_ex1',
                    'description': 'Managed Input',
                    'feeds': [
                        {
                            'name': 'I1', 'tag': 'emon_tools_ex1',
                            'process': EmonProcessList.LOG_TO_FEED,
                            'engine': 5,
                            'options': {'interval': 1}
                        },
                        {
                            'name': 'I2', 'tag': 'emon_tools_ex1',
                            'process': EmonProcessList.LOG_TO_FEED,
                            'engine': 5,
                            'options': {'interval': 10}
                        }
                    ]
                },
                [
                    {
                        'id': '158', 'userid': '1',
                        'name': 'I1', 'tag': 'emon_tools_ex1',
                        'public': '', 'size': '0',
                        'engine': '5', 'unit': '',
                        'time': None, 'value': None,
                        'start_time': 0, 'end_time': 0,
                        'interval': 5
                    }
                ],
                [[1, 159]],
                [[1, 158], [1, 159]]
            ),
            (
                {
                    'name': 'I1', 'nodeid': 'emon_tools_ex1',
                    'description': 'Managed Input',
                    'feeds': [
                        {
                            'name': 'I1', 'tag': 'emon_tools_ex1',
                            'process': EmonProcessList.LOG_TO_FEED,
                            'engine': 5,
                            'options': {'interval': 1}
                        },
                        {
                            'name': 'I2', 'tag': 'emon_tools_ex1',
                            'process': EmonProcessList.LOG_TO_FEED,
                            'engine': 5,
                            'options': {'interval': 10}
                        }
                    ]
                },
                [],
                [[1, 158], [1, 159]],
                [[1, 158], [1, 159]]
            ),
            ({}, [], [], []),
        ],
    )
    def test_add_input_feeds_structure(
        self,
        api,
        input_item,
        feeds_on,
        expected_created,
        expected_process
    ):
        """Test the init_inputs_structure method."""
        api.create_input_feeds = MagicMock(return_value=expected_created)
        result = api.add_input_feeds_structure(
            input_item=input_item,
            feeds_on=feeds_on)
        assert result == expected_process

    @pytest.mark.parametrize(
        (
            "input_id, current, description, "
            "set_input_fields_response, expected_result"
        ),
        [
            (
                1, "old_description", "new_description",
                {SUCCESS_KEY: True, MESSAGE_KEY: "Field updated"}, 1),
            (
                1, "same_description", "same_description", None, 0),
        ],
    )
    def test_update_input_fields(
        self,
        api,
        input_id,
        current,
        description,
        set_input_fields_response,
        expected_result
    ):
        """Test the update_input_fields method."""
        api.set_input_fields.return_value = set_input_fields_response

        result = api.update_input_fields(
            input_id=input_id, current=current, description=description
        )
        assert result == expected_result

    @pytest.mark.parametrize(
        (
            "input_id, current_processes, new_processes, "
            "set_input_process_list_response, expected_result"
        ),
        [
            (
                1,
                "1:5,1:6,1:7",
                [[1, 4]],
                {SUCCESS_KEY: True, MESSAGE_KEY: "Input processlist updated"},
                1,
            ),
            (1, "1:2,1:6,1:7", [[1, 2]], None, 0),
        ],
    )
    def test_update_input_process_list(
        self,
        api,
        input_id,
        current_processes,
        new_processes,
        set_input_process_list_response,
        expected_result,
    ):
        """Test the update_input_process_list method."""
        api.set_input_process_list.return_value = set_input_process_list_response

        result = api.update_input_process_list(
            input_id=input_id,
            current_processes=current_processes,
            new_processes=new_processes
        )
        assert result == expected_result

    @pytest.mark.parametrize(
        (
            "structure, get_structure_return, inputs_on, feeds_on, "
            "raises_error, expected_result"
        ),
        [
            (
                [{"nodeid": "node1", "name": "input1"}],
                ([], []),
                None,
                None,
                True,  # Expecting a ValueError
                None,
            ),
            (
                [{"nodeid": "node1", "name": "input1"}],
                ([], []),
                [
                    {"id": 1, "description": "test"},
                    {"id": 2, "description": "test2"}
                ],  # More than one input
                [],
                True,
                None,
            ),
            (
                [],
                ([], []),
                None,
                None,
                False,
                None,
            ),
        ],
    )
    def test_create_structure(
        self,
        api,
        structure,
        get_structure_return,
        inputs_on,
        feeds_on,
        raises_error,
        expected_result,
    ):
        """Test the create_structure method."""
        api.init_inputs_structure = MagicMock(return_value=len(structure))
        api.get_structure = MagicMock(return_value=get_structure_return)
        api.add_input_feeds_structure = MagicMock(return_value=[])
        api.update_input_fields = MagicMock(return_value=0)
        api.update_input_process_list = MagicMock(return_value=0)

        if raises_error:
            api.add_input_feeds_structure = MagicMock(
                side_effect=ValueError(
                    "Fatal Error, inputs was not added to server."
                )
            )
            with pytest.raises(
                    ValueError,
                    match="Fatal Error, inputs was not added to server."):
                api.create_structure(structure=structure)
        else:
            result = api.create_structure(structure=structure)
            assert result == expected_result
