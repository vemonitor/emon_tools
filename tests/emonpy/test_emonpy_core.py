"""Tests for the EmonRequest class using async"""
import pytest
from emon_tools.emonpy_core import EmonPyCore
from emon_tools.emonpy_core import EmonFilters
from emon_tools.emonpy_core import EmonFilterItem


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
        "process_list, feed_data, expected_result",
        [
            (
                [[1, 1], [2, 2]],
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"},
                    {"id": 3, "name": "Feed3"}
                ],
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"}
                ]
            ),
            (
                [[1, 1], [2, 2]],
                [
                    {"id": 3, "name": "Feed3"},
                    {"id": 4, "name": "Feed4"}
                ],
                []
            ),
            (
                [],
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"}
                ],
                []
            ),
            (
                [[1, 1], [2, 2]],
                [],
                []
            ),
            (
                None,
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"}
                ],
                []
            ),
            (
                [[1, 1], [2, "a"]],
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"}
                ],
                [
                    {"id": 1, "name": "Feed1"}
                ]
            ),
        ],
    )
    def test_get_feeds_from_input_item(
        self,
        process_list,
        feed_data,
        expected_result
    ):
        """Test getting feeds from input item."""
        assert EmonPyCore.get_feeds_from_input_item(
            process_list=process_list,
            feed_data=feed_data
        ) == expected_result

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
                    {"process_list": [[1, 1], [2, 2]]},
                    {"process_list": [[3, 3], [4, 4]]}
                ],
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"},
                    {"id": 3, "name": "Feed3"},
                    {"id": 4, "name": "Feed4"}
                ],
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"},
                    {"id": 3, "name": "Feed3"},
                    {"id": 4, "name": "Feed4"}
                ]
            ),
            (
                [
                    {"process_list": [[1, 1], [2, 2]]},
                    {"process_list": [[3, 3], [4, 4]]}
                ],
                [],
                []
            ),
            (
                [],
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"},
                    {"id": 3, "name": "Feed3"},
                    {"id": 4, "name": "Feed4"}
                ],
                []
            ),
            (
                [],
                [],
                []
            ),
        ],
    )
    def test_filter_feeds_by_inputs(
        self,
        input_data,
        feed_data,
        expected_result
    ):
        """Test filtering feeds by inputs."""
        assert EmonPyCore.filter_feeds_by_inputs(
            input_data=input_data,
            feed_data=feed_data
        ) == expected_result

    @pytest.mark.parametrize(
        "inputs, feeds, expected_result",
        [
            (
                [
                    {"process_list": [[1, 1], [2, 2]]},
                    {"process_list": [[3, 3], [4, 4]]}
                ],
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"},
                    {"id": 3, "name": "Feed3"},
                    {"id": 4, "name": "Feed4"}
                ],
                [
                    {"process_list": [[1, 1], [2, 2]]},
                    {"process_list": [[3, 3], [4, 4]]}
                ]
            ),
            (
                [
                    {"process_list": [[1, 1], [2, 2]]},
                    {"process_list": [[3, 3], [4, 4]]}
                ],
                [],
                []
            ),
            (
                [],
                [
                    {"id": 1, "name": "Feed1"},
                    {"id": 2, "name": "Feed2"},
                    {"id": 3, "name": "Feed3"},
                    {"id": 4, "name": "Feed4"}
                ],
                []
            ),
            (
                [],
                [],
                []
            ),
        ],
    )
    def test_filter_inputs_by_feeds(
        self,
        inputs,
        feeds,
        expected_result
    ):
        """Test filtering inputs by feeds."""
        assert EmonPyCore.filter_inputs_by_feeds(
            inputs=inputs,
            feeds=feeds
        ) == expected_result


class TestEmonFilterItem:
    """Tests EmonFilterItem class."""
    def test_add_filter(self):
        """Test adding filters to EmonFilterItem."""
        filter_item = EmonFilterItem()
        filter_item.add_filter("key1", "value1")
        filter_item.add_filter("key1", "value2")
        filter_item.add_filter("key2", 10)
        assert filter_item.item == {
            "key1": {"value1", "value2"},
            "key2": {10}
        }

    def test_reset_filter(self):
        """Test resetting filters in EmonFilterItem."""
        filter_item = EmonFilterItem({"key1": {"value1"}})
        filter_item.reset_filter()
        assert filter_item.item == {}


class TestEmonFilters:
    """Tests EmonFilters class."""
    def test_add_input_filter(self):
        """Test adding input filters to EmonFilters."""
        filters = EmonFilters()
        filters.add_input_filter("key1", "value1")
        filters.add_input_filter("key1", "value2")
        filters.add_input_filter("key2", 10)
        assert filters.filter_inputs == {
            "key1": {"value1", "value2"},
            "key2": {10}
        }

    def test_add_feed_filter(self):
        """Test adding feed filters to EmonFilters."""
        filters = EmonFilters()
        filters.add_feed_filter("key1", "value1")
        filters.add_feed_filter("key1", "value2")
        filters.add_feed_filter("key2", 10)
        assert filters.filter_feeds == {
            "key1": {"value1", "value2"},
            "key2": {10}
        }

    def test_reset_input_filters(self):
        """Test resetting input filters in EmonFilters."""
        filters = EmonFilters({"key1": {"value1"}})
        filters.reset_input_filters()
        assert filters.filter_inputs == {}

    def test_reset_feed_filters(self):
        """Test resetting feed filters in EmonFilters."""
        filters = EmonFilters(feed_filters={"key1": {"value1"}})
        filters.reset_feed_filters()
        assert filters.filter_feeds == {}

    def test_get_combined_filters(self):
        """Test getting combined filters from EmonFilters."""
        filters = EmonFilters(
            input_filters={"key1": {"value1"}},
            feed_filters={"key2": {"value2"}}
        )
        assert filters.get_combined_filters() == (
            {"key1": {"value1"}},
            {"key2": {"value2"}}
        )
        class TestEmonPyCore:
            """Tests EmonPyCore class."""
            
            # Existing tests...

            



