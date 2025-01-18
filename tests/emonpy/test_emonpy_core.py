"""Tests for the EmonRequest class using async"""
import pytest
from emon_tools.emonpy_core import EmonPyCore


class TestEmonPyCore:
    """Tests EmonPyCore class."""
    @pytest.mark.parametrize(
        "filters, expected_result",
        [
            (
                {
                    "filter_inputs": {"nodeid": set(), "name": set()},
                    "filter_feeds": {"tag": set(), "name": set()}
                },
                True
            ),
            (
                {
                    "filter_inputs": {"nodeid": 1, "name": "aa"},
                    "filter_feeds": {"tag": set(), "name": set()}
                },
                False
            ),
            (
                {
                    "filter_inputs": {"nodeid": set(), "name": set()},
                    "filter_feeds": {"tag": 1, "name": "aa"}
                },
                False
            ),
            (
                {
                    "filter_inputs": {"nodeid": set(), "name": set()}
                },
                False
            ),
            (
                {
                    "filter_inputs": {"nodeid": set(), "name": set()}
                },
                False
            ),
        ],
    )
    def test_is_filters_structure(
        self,
        filters,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonPyCore.is_filters_structure(filters) == expected_result

    @pytest.mark.parametrize(
        (
            "feed_id, process_id, expected_result, "
            "is_error, expected_error, error_msg"),
        [
            (
                1,
                1,
                ['process__log_to_feed', 1],
                False, None, None
            ),
            (
                0,
                1,
                None,
                True, ValueError,
                "Feed id must be a positive integer."
            ),
            (
                1,
                0,
                None,
                True, ValueError,
                "Process id must be a positive integer."
            ),
            (
                -1,
                1,
                None,
                True, ValueError,
                "Feed id must be a positive integer."
            ),
            (
                1,
                -1,
                None,
                True, ValueError,
                "Process id must be a positive integer."
            ),
        ],
    )
    def test_format_process_with_feed_id(
        self,
        feed_id,
        process_id,
        expected_result,
        is_error,
        expected_error,
        error_msg
    ):
        """Test the validate_feed_fields method."""
        if is_error:
            with pytest.raises(expected_error, match=error_msg):
                EmonPyCore.format_process_with_feed_id(
                    feed_id=feed_id,
                    process_id=process_id
                )
        else:
            assert EmonPyCore.format_process_with_feed_id(
                feed_id=feed_id,
                process_id=process_id
            ) == expected_result

    @pytest.mark.parametrize(
        "process_list, expected_result",
        [
            (
                "1:1,2:3",
                {'process__log_to_feed:1', 'process__scale:3'}
            ),
            (
                None,
                set()
            ),
            (
                {},
                set()
            ),
        ],
    )
    def test_format_string_process_list(
        self,
        process_list,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonPyCore.format_string_process_list(
            process_list) == expected_result

    @pytest.mark.parametrize(
        "process_list, expected_error, error_msg",
        [
            (
                "1:1,2:a",
                ValueError,
                r"Error: Malformed processList value.*"
            ),
            (
                "1:1,a:2",
                ValueError,
                r"Error: Malformed processList value.*"
            ),
            (
                "abc",
                ValueError,
                r"Error: Malformed processList value.*"
            ),
            (
                "1,2",
                ValueError,
                r"Error: Malformed processList value.*"
            )
        ],
    )
    def test_format_string_process_list_invalid(
        self,
        process_list,
        expected_error,
        error_msg
    ):
        """Test URL validation with an invalid URL."""
        with pytest.raises(expected_error, match=error_msg):
            EmonPyCore.format_string_process_list(
                process_list)

    @pytest.mark.parametrize(
        "process_list, expected_result",
        [
            (
                [[1, 1], [2, 3]],
                {'process__log_to_feed:1', 'process__scale:3'}
            ),
            (
                "abc",
                set()
            ),
            (
                "1,2",
                set()
            ),
            (
                None,
                set()
            ),
            (
                {},
                set()
            ),
        ],
    )
    def test_format_process_list(
        self,
        process_list,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonPyCore.format_process_list(
            process_list) == expected_result

    @pytest.mark.parametrize(
        "filters, expected_result",
        [
            (
                {"key1": {1, 2, 3}, "key2": ["hello"]},
                {"key1": [1, 2, 3], "key2": "hello"}
            ),
            (
                "abc",
                None
            ),
            (
                "1,2",
                None
            ),
            (
                None,
                None
            ),
            (
                {},
                {}
            ),
        ],
    )
    def test_clean_filters_items(
        self,
        filters,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonPyCore.clean_filters_items(
            filters) == expected_result

    @pytest.mark.parametrize(
        "input_item, inputs, feeds, expected_result",
        [
            (
                {"name": "abc", "nodeid": "def", "feeds": [
                    {"name": "f1", "tag": "def"},
                    {"name": "f2", "tag": "def"},
                ]},
                [
                    {"name": "abc", "nodeid": "def"},
                    {"name": "a1", "nodeid": "def"},
                    {"name": "b1", "nodeid": "def"},
                    {"name": "c1", "nodeid": "def"},
                    {"name": "az1", "nodeid": "z1"},
                    {"name": "az2", "nodeid": "z1"},
                ],
                [
                    {"name": "f1", "tag": "def"},
                    {"name": "f2", "tag": "def"},
                    {"name": "f3", "tag": "def"},
                    {"name": "f4", "tag": "def"},
                    {"name": "fz1", "tag": "z1"},
                    {"name": "fz2", "tag": "z1"},
                ],
                (
                    [
                        {'name': 'abc', 'nodeid': 'def'}
                    ],
                    [
                        {'name': 'f1', 'tag': 'def'},
                        {'name': 'f2', 'tag': 'def'}
                    ]
                )
            ),
            (
                "abc", [], [],
                (None, None)
            ),
            (
                None, [], [],
                (None, None)
            ),
            (
                {}, [], [],
                (None, None)
            ),
        ],
    )
    def test_get_existant_structure(
        self,
        input_item,
        inputs,
        feeds,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonPyCore.get_existant_structure(
            input_item=input_item,
            inputs=inputs,
            feeds=feeds) == expected_result

    @pytest.mark.parametrize(
        "structure, expected_result",
        [
            (
                {
                    "filter_inputs": {
                        "nodeid": {"n1", "n2", "n3"},
                        "name": {"a1", "a2", "a3"}
                    },
                    "filter_feeds": {
                        "tag": {"n1"},
                        "name": {"f1", "f2", "f3"}
                    }
                },
                {
                    "filter_inputs": {
                        "nodeid": ["n1", "n2", "n3"],
                        "name": ['a1', 'a2', 'a3']
                    },
                    "filter_feeds": {
                        "tag": "n1",
                        "name": ["f1", "f2", "f3"]
                    }
                }
            ),
            (
                "1,2",
                None
            ),
            (
                None,
                None
            ),
            (
                {},
                None
            ),
        ],
    )
    def test_clean_filters_structure(
        self,
        structure,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonPyCore.clean_filters_structure(
            structure) == expected_result

    @pytest.mark.parametrize(
        "structure, expected_result",
        [
            (
                [
                    {"name": "a1", "nodeid": "n1"},
                    {"name": "a2", "nodeid": "n1"},
                    {"name": "a3", "nodeid": "n1"},
                ],
                {
                    "nodeid": "n1",
                    "name": ['a1', 'a2', 'a3']
                }
            ),
            (
                [
                    {"name": "a1", "nodeid": "n1"},
                    {"name": "a2", "nodeid": "n1"},
                    {"name": "b1", "nodeid": "n2"},
                    {"name": "b2", "nodeid": "n2"},
                ],
                {
                    "nodeid": ["n1", "n2"],
                    "name": ['a1', 'a2', 'b1', 'b2']
                }
            ),
            (
                "1,2",
                None
            ),
            (
                None,
                None
            ),
            (
                {},
                None
            ),
        ],
    )
    def test_get_inputs_filters_from_structure(
        self,
        structure,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonPyCore.get_inputs_filters_from_structure(
            structure) == expected_result

    @pytest.mark.parametrize(
        "input_data, feed_data, expected_result",
        [
            (
                [
                    {"name": "a1", "nodeid": "n1", "processList": "1:1"},
                    {"name": "a2", "nodeid": "n1", "processList": "1:2"},
                    {"name": "a3", "nodeid": "n1", "processList": "1:3"},
                ],
                [
                    {"id": "1", "name": "f1", "nodeid": "n1"},
                    {"id": "2", "name": "f2", "nodeid": "n1"},
                    {"id": "3", "name": "f3", "nodeid": "n1"},
                    {"id": "4", "name": "f4", "nodeid": "n1"},
                ],
                [
                    {
                        'name': 'a1', 'nodeid': 'n1',
                        'processList': [(1, 1)],
                        'feeds': [{'id': 1, 'name': 'f1', 'nodeid': 'n1'}]
                    },
                    {
                        'name': 'a2', 'nodeid': 'n1',
                        'processList': [(1, 2)],
                        'feeds': [{'id': 2, 'name': 'f2', 'nodeid': 'n1'}]
                    },
                    {
                        'name': 'a3', 'nodeid': 'n1',
                        'processList': [(1, 3)],
                        'feeds': [{'id': 3, 'name': 'f3', 'nodeid': 'n1'}]
                    }
                ]
            ),
            (
                "1,2", [],
                []
            ),
            (
                None, [],
                []
            ),
            (
                {}, [],
                []
            ),
        ],
    )
    def test_get_feeds_from_inputs_process(
        self,
        input_data,
        feed_data,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonPyCore.get_feeds_from_inputs_process(
            input_data=input_data,
            feed_data=feed_data) == expected_result

    @pytest.mark.parametrize(
        (
            "input_data, feed_data, filter_inputs, "
            "filter_feeds, filter_in, expected_result"
        ),
        [
            (
                [
                    {"name": "a1", "nodeid": "n1", "processList": "1:1"},
                    {"name": "a2", "nodeid": "n1", "processList": "1:2"},
                    {"name": "a3", "nodeid": "n1", "processList": "1:3"},
                ],
                [
                    {"id": "1", "name": "f1", "tag": "n1"},
                    {"id": "2", "name": "f2", "tag": "n1"},
                    {"id": "3", "name": "f3", "tag": "n1"},
                    {"id": "4", "name": "f4", "tag": "n1"},
                ],
                {
                    "nodeid": "n1",
                    "name": ['a1', 'a2', 'a3']
                },
                {
                    "tag": "n1",
                    "name": ["f1", "f2", "f3"]
                },
                True,
                [
                    {
                        'name': 'a1', 'nodeid': 'n1',
                        'processList': [(1, 1)],
                        'feeds': [{'id': 1, 'name': 'f1', 'tag': 'n1'}]
                    },
                    {
                        'name': 'a2', 'nodeid': 'n1',
                        'processList': [(1, 2)],
                        'feeds': [{'id': 2, 'name': 'f2', 'tag': 'n1'}]
                    },
                    {
                        'name': 'a3', 'nodeid': 'n1',
                        'processList': [(1, 3)],
                        'feeds': [{'id': 3, 'name': 'f3', 'tag': 'n1'}]
                    }
                ]
            ),
            (
                "1,2", [], [], {}, True,
                []
            ),
            (
                None, [], [], {}, True,
                []
            ),
            (
                {}, [], [], {}, True,
                []
            ),
        ],
    )
    def test_get_extended_structure(
        self,
        input_data,
        feed_data,
        filter_inputs,
        filter_feeds,
        filter_in,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonPyCore.get_extended_structure(
            inputs=input_data,
            feeds=feed_data,
            filter_inputs=filter_inputs,
            filter_feeds=filter_feeds,
            filter_in=filter_in) == expected_result
