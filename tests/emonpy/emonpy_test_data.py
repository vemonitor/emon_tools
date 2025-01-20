"""
emonpy common helper
"""
from emon_tools.api_utils import SUCCESS_KEY, MESSAGE_KEY
from emon_tools.emon_api_core import EmonProcessList


class EmonpyDataTest:
    """EmonPy data test common helper"""
    MOCK_INPUTS = [
        {
            'id': '266', 'nodeid': 'emon_tools_ex1', 'name': 'I3',
            'description': 'Managed Input', 'processList': '1:172',
            'time': 1737155100, 'value': 38
        },
        {
            'id': '267', 'nodeid': 'emon_tools_ex1', 'name': 'I1',
            'description': 'Managed Input', 'processList': '1:170',
            'time': 1737155100, 'value': 5
        },
        {
            'id': '268', 'nodeid': 'emon_tools_ex1', 'name': 'I2',
            'description': 'Managed Input', 'processList': '1:171',
            'time': 1737155100, 'value': 23
        }
    ]

    MOCK_INPUTS_FORMATED = [
        {
            'id': 266, 'nodeid': 'emon_tools_ex1', 'name': 'I3',
            'description': 'Managed Input', 'processList': '1:172',
            'time': 1737155100, 'value': 38, 'process_list': [(1, 172)]
        },
        {
            'id': 267, 'nodeid': 'emon_tools_ex1', 'name': 'I1',
            'description': 'Managed Input', 'processList': '1:170',
            'time': 1737155100, 'value': 5, 'process_list': [(1, 170)]
        },
        {
            'id': 268, 'nodeid': 'emon_tools_ex1', 'name': 'I2',
            'description': 'Managed Input', 'processList': '1:171',
            'time': 1737155100, 'value': 23, 'process_list': [(1, 171)]
        }
    ]

    MOCK_FEEDS = [
        {
            'id': '172', 'userid': '1', 'name': 'F3',
            'tag': 'emon_tools_ex1',
            'public': '', 'size': '', 'engine': '5', 'unit': '',
            'processList': '', 'value': 38, 'time': 1737155100,
            'start_time': 1736895600, 'end_time': 1737155100, 'interval': 1
        },
        {
            'id': '170', 'userid': '1', 'name': 'I1',
            'tag': 'emon_tools_ex1',
            'public': '', 'size': '', 'engine': 5, 'unit': '',
            'processList': '', 'value': 5, 'time': 1737155100,
            'start_time': 1736895600, 'end_time': 1737155100, 'interval': 1
        },
        {
            'id': '171', 'userid': '1', 'name': 'F2A',
            'tag': 'emon_tools_ex1_f1',
            'public': '', 'size': '', 'engine': 5, 'unit': '',
            'processList': '', 'value': 23, 'time': 1737155100,
            'start_time': 1736895600, 'end_time': 1737155100, 'interval': 1
        }
    ]

    MOCK_FEEDS_FORMATED = [
        {
            'id': 172, 'userid': 1, 'name': 'F3', 'tag': 'emon_tools_ex1',
            'public': 0, 'size': 0, 'engine': 5, 'unit': '',
            'processList': '', 'value': 38, 'time': 1737155100,
            'start_time': 1736895600, 'end_time': 1737155100, 'interval': 1,
            'process_list': []
        },
        {
            'id': 170, 'userid': 1, 'name': 'I1', 'tag': 'emon_tools_ex1',
            'public': 0, 'size': 0, 'engine': 5, 'unit': '',
            'processList': '', 'value': 5, 'time': 1737155100,
            'start_time': 1736895600, 'end_time': 1737155100, 'interval': 1,
            'process_list': []
        },
        {
            'id': 171, 'userid': 1, 'name': 'F2A', 'tag': 'emon_tools_ex1_f1',
            'public': 0, 'size': 0, 'engine': 5, 'unit': '',
            'processList': '', 'value': 23, 'time': 1737155100,
            'start_time': 1736895600, 'end_time': 1737155100, 'interval': 1,
            'process_list': []
        }
    ]

    GET_INPUTS_PARAMS = [
        (
            # inputs_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_INPUTS},
            # input_filter
            {"name": ['I1', 'I3']},
            # expected_result
            MOCK_INPUTS_FORMATED[0:2],
        ),
        (
            # inputs_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_INPUTS},
            # input_filter
            {"name": ['I1']},
            # expected_result
            MOCK_INPUTS_FORMATED[1:2],
        ),
        (
            # inputs_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_INPUTS},
            # input_filter
            {"nodeid": ['emon_tools_ex1']},
            # expected_result
            MOCK_INPUTS_FORMATED,
        ),
        (
            # inputs_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_INPUTS},
            # input_filter
            {"name": []},
            # expected_result
            MOCK_INPUTS_FORMATED,
        ),
        (
            # inputs_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_INPUTS},
            # input_filter
            None,
            # expected_result
            MOCK_INPUTS_FORMATED,
        ),
    ]

    GET_FEEDS_PARAMS = [
        (
            # feeds_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_FEEDS},
            # feed_filter
            {"name": ['I1', 'F3']},
            # expected_result
            MOCK_FEEDS_FORMATED[0:2],
        ),
        (
            # feeds_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_FEEDS},
            # feed_filter
            {"name": ['I1']},
            # expected_result
            MOCK_FEEDS_FORMATED[1:2],
        ),
        (
            # feeds_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_FEEDS},
            # feed_filter
            {"tag": ['emon_tools_ex1']},
            # expected_result
            MOCK_FEEDS_FORMATED[0:2],
        ),
        (
            # feeds_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_FEEDS},
            # feed_filter
            {"name": []},
            # expected_result
            MOCK_FEEDS_FORMATED,
        ),
        (
            # feeds_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_FEEDS},
            # feed_filter
            None,
            # expected_result
            MOCK_FEEDS_FORMATED,
        ),
    ]

    GET_STRUCTURE_PARAMS = [
        (
            # inputs_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_INPUTS},
            # feeds_response
            {SUCCESS_KEY: True, MESSAGE_KEY: MOCK_FEEDS},
            # expected_result
            (MOCK_INPUTS_FORMATED, MOCK_FEEDS_FORMATED),
        ),
        (
            # inputs_response
            {SUCCESS_KEY: False},
            # feeds_response
            {
                SUCCESS_KEY: True,
                MESSAGE_KEY: [{"id": "1", "name": "test_feed"}]
            },
            # expected_result
            (None, [{"id": 1, "name": "test_feed", 'process_list': []}]),
        ),
        (
            # inputs_response
            {
                SUCCESS_KEY: True,
                MESSAGE_KEY: [{"id": "1", "name": "test_feed"}]
            },
            # feeds_response
            {SUCCESS_KEY: False},
            # expected_result
            ([{"id": 1, "name": "test_feed", "process_list": []}], None),
        ),
        (
            # inputs_response
            {SUCCESS_KEY: False},
            # feeds_response
            {SUCCESS_KEY: False},
            # expected_result
            (None, None),
        ),
    ]

    CREATE_INPUT_FEEDS_PARAMS = [
        (
            # feeds
            [{"name": "feed1", "tag": "tag1"}],
            # create_feed_results
            [{"message": {"feedid": "1"}, SUCCESS_KEY: True}],
            # expected_processes
            [[1, 1]],
        ),
        (
            # feeds
            [{"name": "feed1", "tag": "tag1", "process": "1:1"}],
            # create_feed_results
            [{"message": {"feedid": "1"}, SUCCESS_KEY: True}],
            # expected_processes
            [[1, 1]],
        ),
        (
            # feeds
            [],
            # create_feed_results
            [],
            # expected_processes
            [],
        ),
    ]

    CREATE_INPUTS_PARAMS = [
        (
            # inputs
            [{"nodeid": "node1", "name": "input1"}],
            # post_inputs_responses
            [{"message": {}, SUCCESS_KEY: True}],
            # expected_count
            1,
        ),
        (
            # inputs
            [],
            # post_inputs_responses
            [],
            # expected_count
            0,
        ),
    ]

    INIT_INPUTS_STRUCTURE_PARAMS = [
        (
            # structure
            [
                {"nodeid": "node2", "name": "input1"},
                {"nodeid": "node2", "name": "input2"},
            ],
            # inputs
            {
                SUCCESS_KEY: True,
                MESSAGE_KEY: [
                    {"nodeid": "node1", "name": "input1"},
                    {"nodeid": "node1", "name": "input2"},
                    {"nodeid": "node1", "name": "input3"},
                    {"nodeid": "node2", "name": "input1"},
                ],
            },
            # expected_count
            1,
        ),
        (
            # structure
            [
                {"nodeid": "node3", "name": "input1"},
                {"nodeid": "node3", "name": "input2"},
            ],
            # inputs
            {
                SUCCESS_KEY: True,
                MESSAGE_KEY: [
                    {"nodeid": "node1", "name": "input1"},
                    {"nodeid": "node1", "name": "input2"},
                    {"nodeid": "node1", "name": "input3"},
                    {"nodeid": "node2", "name": "input1"},
                ],
            },
            # expected_count
            1,
        ),
        (
            # structure
            [],
            # inputs
            [],
            # expected_count
            0,
        ),
    ]

    ADD_INPUT_FEEDS_STRUCTURE_PARAMS = [
        (
            # input_item
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
            # feeds_on
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
            # expected_created
            (1, [[1, 159]]),
            # expected_process
            [[1, 158], [1, 159]],
        ),
        (
            # input_item
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
            # feeds_on
            [],
            # expected_created
            (1, [[1, 158], [1, 159]]),
            # expected_process
            [[1, 158], [1, 159]],
        ),
        (
            # input_item
            {},
            # feeds_on
            [],
            # expected_created
            [],
            # expected_process
            [],
        ),
    ]

    UPDATE_INPUT_FIELDS_PARAMS = [
        (
            # input_id
            1,
            # current
            "old_description",
            # description
            "new_description",
            # set_input_fields_response
            {SUCCESS_KEY: True, MESSAGE_KEY: "Field updated"},
            # expected_result
            1,
        ),
        (
            # input_id
            1,
            # current
            "same_description",
            # description
            "same_description",
            # set_input_fields_response
            None,
            # expected_result
            0,
        ),
    ]

    UPDATE_INPUT_PROCESS_LIST_PARAMS = [
        (
            # input_id
            1,
            # current_processes
            "1:5,1:6,1:7",
            # new_processes
            [[1, 4]],
            # set_process_list_response
            {SUCCESS_KEY: True, MESSAGE_KEY: "Input processlist updated"},
            # expected_result
            1,
        ),
        (
            # input_id
            1,
            # current_processes
            "1:2,1:6,1:7",
            # new_processes
            [[1, 2]],
            # set_process_list_response
            None,
            # expected_result
            0,
        ),
    ]

    CREATE_STRUCTURE_PARAMS = [
        (
            # structure
            [
                {"nodeid": "n1", "name": "a1", "feeds": [
                    {"name": "f1", "tag": "n1"}
                ]},
                {"nodeid": "n1", "name": "a2", "feeds": [
                    {"name": "f2", "tag": "n1"}
                ]}
            ],
            # get_structure_return
            (
                [
                    {
                        "id": "1", "name": "a1", "nodeid": "n1",
                        "processList": "1:1"
                    },
                    {
                        "id": "2", "name": "a2", "nodeid": "n1",
                        "processList": "1:2"
                    },
                    {
                        "id": "3", "name": "a3", "nodeid": "n1",
                        "processList": "1:3"
                    },
                ],
                [
                    {"id": "1", "name": "f1", "tag": "n1"},
                    {"id": "2", "name": "f2", "tag": "n1"},
                    {"id": "3", "name": "f3", "tag": "n1"},
                    {"id": "4", "name": "f4", "tag": "n1"},
                ]
            ),
            # raises_error
            False,
            # expected_result
            {
                'nb_updated_inputs': 0,
                'nb_added_inputs': 2,
                'nb_added_feeds': 0,
                'input_1': {
                    'input_feeds': 0,
                    'input_fields': 0,
                    'input_process': 0},
                'input_2': {
                    'input_feeds': 0,
                    'input_fields': 0,
                    'input_process': 0}
            },
        ),
        (
            # structure
            [
                {"nodeid": "node1", "name": "input1"}
            ],
            # get_structure_return
            ([], []),
            # raises_error
            True,
            # expected_result
            None,
        ),
    ]

    GET_EXTENDED_STRUCTURE_PARAMS = [
        (
            # structure
            [
                {"nodeid": "n1", "name": "a1", "feeds": [
                    {"name": "f1", "tag": "n1"}
                ]},
                {"nodeid": "n1", "name": "a2", "feeds": [
                    {"name": "f2", "tag": "n1"}
                ]}
            ],
            # get_structure_return
            (
                [
                    {
                        "id": "1", "name": "a1", "nodeid": "n1",
                        "processList": "1:1"
                    },
                    {
                        "id": "2", "name": "a2", "nodeid": "n1",
                        "processList": "1:2"
                    },
                    {
                        "id": "3", "name": "a3", "nodeid": "n1",
                        "processList": "1:3"
                    },
                ],
                [
                    {"id": "1", "name": "f1", "tag": "n1"},
                    {"id": "2", "name": "f2", "tag": "n1"},
                    {"id": "3", "name": "f3", "tag": "n1"},
                    {"id": "4", "name": "f4", "tag": "n1"},
                ]
            ),
            # raises_error
            False,
            # expected_result
            [
                {
                    "id": "1", "name": "a1", "nodeid": "n1",
                    "processList": "1:1", "feeds": [{
                        "id": "1", "name": "f1", "tag": "n1"}]
                },
                {
                    "id": "2", "name": "a2", "nodeid": "n1",
                    "processList": "1:2", "feeds": [{
                        "id": "2", "name": "f2", "tag": "n1"}]
                }
            ],
        ),
        (
            # structure
            [
                {"nodeid": "node1", "name": "input1"}
            ],
            # get_structure_return
            ([], []),
            # raises_error
            False,
            # expected_result
            [],
        ),
    ]
