"""Tests for the EmonRequest class using async"""
import pytest
from emon_tools.api_utils import MESSAGE_KEY
from emon_tools.api_utils import SUCCESS_KEY
from emon_tools.emon_api_core import InputGetType
from emon_tools.emon_api_core import EmonHelper
from emon_tools.emon_api_core import EmonRequestCore
from emon_tools.emon_api_core import EmonInputsCore
from emon_tools.emon_api_core import EmonFeedsCore


class TestEmonHelper:
    """Tests for Utils class."""

    @pytest.mark.parametrize(
        "api_key",
        [
            (
                "123"
            ),
            (
                "abcdef"
            ),
        ],
    )
    def test_validate_api_key_valid(
        self,
        api_key
    ):
        """Test API key validation with a valid key."""
        validated_key = EmonHelper.validate_api_key(api_key)
        assert validated_key == api_key

    @pytest.mark.parametrize(
        "api_key, expected_exception, error_msg",
        [
            (
                123, ValueError,
                "API key must be a non-empty alphanumeric string."
            ),
            (
                "ftp://", ValueError,
                "API key must be a non-empty alphanumeric string."
            ),
        ],
    )
    def test_validate_api_key_invalid(
        self,
        api_key,
        expected_exception,
        error_msg
    ):
        """Test API key validation with an invalid key."""
        with pytest.raises(
                expected_exception,
                match=error_msg):
            EmonHelper.validate_api_key(api_key)

    def test_validate_url_valid(self):
        """Test URL validation with a valid URL."""
        validated_url = EmonHelper.validate_url("http://localhost:8080")
        assert validated_url == "http://localhost:8080"

    @pytest.mark.parametrize(
        "url, expected_exception, error_msg",
        [
            (
                123, TypeError,
                "URL must be a non-empty string."
            ),
            (
                "ftp://", ValueError,
                "URL must start with 'http://' or 'https://'."
            ),
        ],
    )
    def test_validate_url_invalid(
        self,
        url,
        expected_exception,
        error_msg
    ):
        """Test URL validation with an invalid URL."""
        with pytest.raises(expected_exception, match=error_msg):
            EmonHelper.validate_url(url)

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
        assert EmonHelper.is_filters_structure(filters) == expected_result

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
                EmonHelper.format_process_with_feed_id(
                    feed_id=feed_id,
                    process_id=process_id
                )
        else:
            assert EmonHelper.format_process_with_feed_id(
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
    def test_format_string_process_list(
        self,
        process_list,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonHelper.format_string_process_list(
            process_list) == expected_result

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
        assert EmonHelper.format_process_list(
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
        assert EmonHelper.clean_filters_items(
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
        assert EmonHelper.get_existant_structure(
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
        assert EmonHelper.clean_filters_structure(
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
        assert EmonHelper.get_inputs_filters_from_structure(
            structure) == expected_result

    @pytest.mark.parametrize(
        "data, expected_result",
        [
            (
                [
                    {"id": "1", "userid": "", "name": "a2", "nodeid": "n1"},
                    {"id": "1", "public": "0", "name": "a2", "nodeid": "n1"},
                    {"id": "1", "size": "32", "name": "a2", "nodeid": "n1"},
                    {"id": "1", "engine": "5", "name": "a2", "nodeid": "n1"},
                    {"key1": "1", "desc": "32", "name": "a2", "nodeid": "n1"},
                ],
                [
                    {"id": 1, "userid": '', "name": "a2", "nodeid": "n1"},
                    {"id": 1, "public": 0, "name": "a2", "nodeid": "n1"},
                    {"id": 1, "size": 32, "name": "a2", "nodeid": "n1"},
                    {"id": 1, "engine": 5, "name": "a2", "nodeid": "n1"},
                    {"key1": "1", "desc": "32", "name": "a2", "nodeid": "n1"},
                ]
            ),
            (
                "1,2",
                []
            ),
            (
                None,
                []
            ),
            (
                {},
                []
            ),
        ],
    )
    def test_format_list_of_dicts(
        self,
        data,
        expected_result
    ):
        """Test URL validation with an invalid URL."""
        assert EmonHelper.format_list_of_dicts(
            data) == expected_result

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
        assert EmonHelper.get_feeds_from_inputs_process(
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
        assert EmonHelper.get_extended_structure(
            inputs=input_data,
            feeds=feed_data,
            filter_inputs=filter_inputs,
            filter_feeds=filter_feeds,
            filter_in=filter_in) == expected_result


class TestEmonRequestCore:
    """Unit tests for EmonRequestCore class."""
    @pytest.mark.parametrize(
        "response, expected_response",
        [
            (
                {SUCCESS_KEY: True, MESSAGE_KEY: "ok"},
                {SUCCESS_KEY: True, MESSAGE_KEY: "ok"}
            ),
            (
                {SUCCESS_KEY: True, MESSAGE_KEY: "ok", "key1": "value1"},
                {SUCCESS_KEY: True, MESSAGE_KEY: "ok", "key1": "value1"}
            ),
            (
                {SUCCESS_KEY: False, MESSAGE_KEY: "error"},
                {SUCCESS_KEY: False, MESSAGE_KEY: "error"}
            ),
            (
                {SUCCESS_KEY: True},
                {SUCCESS_KEY: True, MESSAGE_KEY: ""}
            ),
            (
                "simple message",
                {SUCCESS_KEY: True, MESSAGE_KEY: "simple message"}
            ),
            (
                123,
                {SUCCESS_KEY: True, MESSAGE_KEY: 123}
            ),
            (
                [1, 2, 3, 4, 5],
                {SUCCESS_KEY: True, MESSAGE_KEY: [1, 2, 3, 4, 5]}
            ),
            (
                {'a': 1, 'b': 2},
                {SUCCESS_KEY: True, MESSAGE_KEY: {'a': 1, 'b': 2}}
            )

        ]
    )
    def test_compute_response(
        self,
        response,
        expected_response
    ):
        """Test compute_response method."""
        assert EmonRequestCore.compute_response(response) == expected_response

    @pytest.mark.parametrize(
        "params, expected_response, is_error, expected_exception, error_msg",
        [
            (
                {
                    "url": "http://127.0.0.1:8080",
                    "path": "/abc/def",
                    "msg": "encode_url_test"
                },
                "http://127.0.0.1:8080/abc/def",
                False, None, None
            ),
            (
                {
                    "url": "http://127.0.0.1:8080",
                    "path": "/abc/d e f",
                    "msg": "encode_url_test"
                },
                "http://127.0.0.1:8080/abc/d+e+f",
                False, None, None
            ),
            (
                {
                    "url": "http://127.0.0.1:8080",
                    "path": "/abc/def",
                    "msg": "encode_url_test"
                },
                "http://127.0.0.1:8080/abc/def",
                False, None, None
            )

        ]
    )
    def test_encode_url_path(
        self,
        params,
        expected_response,
        is_error,
        expected_exception,
        error_msg
    ):
        """Test compute_response method."""
        if is_error is True:
            with pytest.raises(expected_exception, match=error_msg):
                EmonRequestCore.encode_url_path(**params)
        else:
            assert EmonRequestCore.encode_url_path(
                **params) == expected_response

    @pytest.mark.parametrize(
        "params, expected_response",
        [
            (
                {
                    "params": {
                        "key1": "value1",
                        "key2": ["value1"],
                        "key3": 1,
                        "key4": "a a a",
                        "key5": "a a a",
                    },
                    "unquote_keys": ["key5"]
                },
                {
                    "key1": "value1",
                    "key2": '["value1"]',
                    "key3": 1,
                    "key4": "a+a+a",
                    "key5": "a a a",
                }
            )

        ]
    )
    def test_encode_params(
        self,
        params,
        expected_response
    ):
        """Test compute_response method."""
        assert EmonRequestCore.encode_params(
            **params) == expected_response


class TestEmonInputs:
    """Unit tests for EmonInputs class."""

    @pytest.mark.parametrize(
        "node, expected_path",
        [
            (None, "/input/get"),
            ("testNode", "/input/get/testNode"),
        ],
    )
    def test_prep_list_inputs(self, node, expected_path):
        """Test prep_list_inputs method."""
        path, params = EmonInputsCore.prep_list_inputs(node)
        assert path == expected_path
        assert params is None

    @pytest.mark.parametrize(
        "get_type, expected_path",
        [
            (InputGetType.PROCESS_LIST, "/input/getinputs"),
            (InputGetType.EXTENDED, "/input/list"),
        ],
    )
    def test_prep_list_inputs_fields(self, get_type, expected_path):
        """Test prep_list_inputs_fields method."""
        path, params = EmonInputsCore.prep_list_inputs_fields(get_type)
        assert path == expected_path
        assert params is None

    @pytest.mark.parametrize(
        "node, name, expected_path",
        [
            ("Node1", "Input1", "/input/get/Node1/Input1"),
        ],
    )
    def test_prep_input_fields(self, node, name, expected_path):
        """Test prep_input_fields method."""
        path, params = EmonInputsCore.prep_input_fields(node, name)
        assert path == expected_path
        assert params is None

    @pytest.mark.parametrize(
        "node, name, expected_exception",
        [
            ("", "Input1", ValueError),
            ("Node1", "", ValueError),
            ("", "", ValueError),
        ],
    )
    def test_prep_input_fields_invalid(
        self,
        node,
        name,
        expected_exception
    ):
        """Test prep_input_fields with invalid input."""
        with pytest.raises(expected_exception):
            EmonInputsCore.prep_input_fields(node, name)

    @pytest.mark.parametrize(
        (
            "input_id, fields, expected_params, "
            "is_error, expected_error, error_msg"
        ),
        [
            (
                123,
                {"field1": "value1", "field2": "value2"},
                {
                    "inputid": 123,
                    "fields": {
                        "field1": "value1",
                        "field2": "value2"
                    }
                },
                False, None, None
            ),
            (
                123,
                {},
                {},
                True, ValueError, "Invalid fields to post inputs."
            ),
            (
                123,
                None,
                {},
                True, ValueError, "Invalid fields to post inputs."
            ),
            (
                "123",
                {"field1": "value1", "field2": "value2"},
                {},
                True, ValueError, "Input Id must be an integer."
            ),
            (
                0,
                {"field1": "value1", "field2": "value2"},
                {},
                True, ValueError, "Input Id must be a positive integer."
            ),
        ],
    )
    def test_prep_set_input_fields(
        self,
        input_id,
        fields,
        expected_params,
        is_error,
        expected_error,
        error_msg
    ):
        """Test prep_set_input_fields method."""
        if is_error is True:
            with pytest.raises(expected_error, match=error_msg):
                EmonInputsCore.prep_set_input_fields(
                    input_id, fields
                )
        else:
            path, params = EmonInputsCore.prep_set_input_fields(
                input_id, fields)
            assert path == "/input/set"
            assert params == expected_params

    @pytest.mark.parametrize(
        "input_id, process_list, expected_params",
        [
            (
                123,
                "process1:1,process2:2",
                {
                    "params": {"inputid": 123},
                    "data": {"processlist": "process1:1,process2:2"},
                },
            ),
        ],
    )
    def test_prep_set_input_process_list(
        self,
        input_id,
        process_list,
        expected_params
    ):
        """Test prep_set_input_process_list method."""
        path, params = EmonInputsCore.prep_set_input_process_list(
            input_id, process_list)
        assert path == "/input/process/set"
        assert params == expected_params

    @pytest.mark.parametrize(
        "input_id, process_list, expected_exception, error_msg",
        [
            (
                "123", "",
                ValueError,
                "Input Id must be an integer."
            ),
            (
                123, None,
                ValueError,
                "Invalid data to post inputs."
            ),
            (
                "", "process1:1,process2:2",
                ValueError,
                ""
            ),
        ],
    )
    def test_prep_set_input_process_list_invalid(
        self,
        input_id,
        process_list,
        expected_exception,
        error_msg
    ):
        """Test prep_set_input_process_list with invalid input."""
        with pytest.raises(expected_exception, match=error_msg):
            EmonInputsCore.prep_set_input_process_list(input_id, process_list)

    @pytest.mark.parametrize(
        "node, data, expected_params",
        [
            (
                "Node1",
                {"key1": 1, "key2": 2.5},
                {
                    "node": "Node1",
                    "fulljson": {"key1": 1, "key2": 2.5},
                },
            ),
        ],
    )
    def test_prep_post_inputs(
        self,
        node,
        data,
        expected_params
    ):
        """Test prep_post_inputs method."""
        path, params = EmonInputsCore.prep_post_inputs(node, data)
        assert path == "/input/post"
        assert params == expected_params

    @pytest.mark.parametrize(
        "node, data, expected_exception",
        [
            ("Node1", {}, ValueError),
            ("Node1", None, ValueError),
            ("", {"key1": 1}, TypeError),
        ],
    )
    def test_prep_post_inputs_invalid(
        self,
        node,
        data,
        expected_exception
    ):
        """Test prep_post_inputs with invalid input."""
        with pytest.raises(expected_exception):
            EmonInputsCore.prep_post_inputs(node, data)

    @pytest.mark.parametrize(
        (
            "params, expected_params, "
            "is_error, expected_error, error_msg"
        ),
        [
            (
                {
                    "data": ["test"],
                    "timestamp": None,
                    "sentat": None,
                    "offset": None
                },
                (
                    "/input/bulk", {}, {"data": '["test"]'}
                ),
                False, None, None
            ),
            (
                {
                    "data": [],
                    "timestamp": None,
                    "sentat": None,
                    "offset": None
                },
                (),
                True, ValueError, "Invalid data to post inputs."
            ),
            (
                {
                    "data": {"a": "1"},
                    "timestamp": None,
                    "sentat": None,
                    "offset": None
                },
                (),
                True, ValueError, "Invalid data to post inputs."
            ),
            (
                {
                    "data": ["test"],
                    "timestamp": -1,
                    "sentat": None,
                    "offset": None
                },
                (),
                True, ValueError,
                "inputBulkTime timestamp must be a non-negative number."
            ),
            (
                {
                    "data": ["test"],
                    "timestamp": None,
                    "sentat": "-1",
                    "offset": None
                },
                (),
                True, ValueError,
                "inputBulkSentat must be an integer."
            ),
            (
                {
                    "data": ["test"],
                    "timestamp": None,
                    "sentat": None,
                    "offset": "-1"
                },
                (),
                True, ValueError,
                "inputBulkOffset must be an integer."
            ),
            (
                {
                    "data": ["test"],
                    "timestamp": 2,
                    "sentat": 1,
                    "offset": 1
                },
                (),
                True, ValueError,
                r"You must chose an unique format.*"
            ),
        ],
    )
    def test_prep_input_bulk(
        self,
        params,
        expected_params,
        is_error,
        expected_error,
        error_msg
    ):
        """Test prep_set_input_fields method."""
        if is_error is True:
            with pytest.raises(expected_error, match=error_msg):
                EmonInputsCore.prep_input_bulk(**params)
        else:
            result = EmonInputsCore.prep_input_bulk(
                **params)
            assert result == expected_params


class TestEmonFeeds:
    """
    Unit tests for the EmonFeeds class methods.

    This class tests all static methods in the EmonFeeds class,
    ensuring they return the expected outputs and handle all edge cases.
    """

    def test_prep_list_feeds(self):
        """Test the `prep_list_feeds` method for correctness."""
        assert EmonFeedsCore.prep_list_feeds() == ("/feed/list.json", None)

    @pytest.mark.parametrize("feed_id, expected", [
        (1, ("/feed/aget.json", {"id": 1})),
        (100, ("/feed/aget.json", {"id": 100})),
    ])
    def test_prep_feed_fields(self, feed_id, expected):
        """Test the `prep_feed_fields` method with valid inputs."""
        assert EmonFeedsCore.prep_feed_fields(feed_id) == expected

    def test_prep_feed_fields_invalid(self):
        """Test `prep_feed_fields` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeedsCore.prep_feed_fields(-1)  # Invalid feed ID

    @pytest.mark.parametrize("feed_id, expected", [
        (1, ("/feed/getmeta.json", {"id": 1})),
        (50, ("/feed/getmeta.json", {"id": 50})),
    ])
    def test_prep_feed_meta(self, feed_id, expected):
        """Test the `prep_feed_meta` method with valid inputs."""
        assert EmonFeedsCore.prep_feed_meta(feed_id) == expected

    def test_prep_feed_meta_invalid(self):
        """Test `prep_feed_meta` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeedsCore.prep_feed_meta(0)  # Invalid feed ID

    @pytest.mark.parametrize("feed_id, expected", [
        (1, ("/feed/timevalue.json", {"id": 1})),
        (75, ("/feed/timevalue.json", {"id": 75})),
    ])
    def test_prep_last_value_feed(self, feed_id, expected):
        """Test the `prep_last_value_feed` method with valid inputs."""
        assert EmonFeedsCore.prep_last_value_feed(feed_id) == expected

    def test_prep_last_value_feed_invalid(self):
        """Test `prep_last_value_feed` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeedsCore.prep_last_value_feed(-10)  # Invalid feed ID

    @pytest.mark.parametrize(
        "feed_id, start, end, interval, average, expected",
        [
            (
                1, 1609459200, 1609545600, 60, False,
                {
                    "id": 1, "start": 1609459200, "end": 1609545600,
                    "interval": 60, "average": 0, "time_format": "unix",
                    "skip_missing": 0, "limit_interval": 0, "delta": 0
                }
            ),
            (
                10, 1609459200, 1609545600, 30, True,
                {
                    "id": 10, "start": 1609459200, "end": 1609545600,
                    "interval": 30, "average": 1, "time_format": "unix",
                    "skip_missing": 0, "limit_interval": 0, "delta": 0
                }
            ),
        ]
    )
    def test_prep_fetch_feed_data(
        self, feed_id, start, end, interval, average, expected
    ):
        """Test the `prep_fetch_feed_data` method with valid parameters."""
        result = EmonFeedsCore.prep_fetch_feed_data(
            feed_id, start, end, interval, average
        )
        assert result == ("/feed/data.json", expected)

    def test_prep_fetch_feed_data_invalid(self):
        """Test `prep_fetch_feed_data` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeedsCore.prep_fetch_feed_data(
                -1, 1609459200, 1609545600, 60, False
            )  # Invalid feed ID

    def test_prep_create_feed(self):
        """Test the `prep_create_feed` method with valid inputs."""
        result = EmonFeedsCore.prep_create_feed(
            name="test_feed",
            tag="test_tag",
            engine=5,
            options={"type": "test"}
        )
        expected = (
            "/feed/create.json",
            {
                "tag": "test_tag", "name": "test_feed",
                "engine": 5, "options": {"type": "test"}
            }
        )
        assert result == expected

    def test_prep_create_feed_invalid(self):
        """Test `prep_create_feed` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeedsCore.prep_create_feed(name="", tag="tag")  # Invalid name

    def test_prep_update_feed(self):
        """Test the `prep_update_feed` method with valid inputs."""
        result = EmonFeedsCore.prep_update_feed(
            feed_id=1,
            fields={"tag": "value"}
        )
        expected = (
            "/feed/set.json", {"feed_id": 1, "fields": {"tag": "value"}})
        assert result == expected

    def test_prep_update_feed_invalid(self):
        """Test `prep_update_feed` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeedsCore.prep_update_feed(
                feed_id=1, fields={"name": "@123 /$*ù"})

    def test_prep_delete_feed(self):
        """Test the `prep_delete_feed` method with valid inputs."""
        result = EmonFeedsCore.prep_delete_feed(feed_id=1)
        assert result == ("/feed/delete.json", {"id": 1})

    def test_prep_delete_feed_invalid(self):
        """Test `prep_delete_feed` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeedsCore.prep_delete_feed(feed_id=-5)  # Invalid feed ID

    def test_prep_add_data_point(self):
        """Test the `prep_add_data_point` method with valid inputs."""
        result = EmonFeedsCore.prep_add_data_point(
            feed_id=1, time=1609459200, value=123.45)
        expected = (
            "/feed/insert.json",
            {"feed_id": 1, "time": 1609459200, "value": 123.45}
        )
        assert result == expected

    def test_prep_add_data_point_invalid(self):
        """Test `prep_add_data_point` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeedsCore.prep_add_data_point(
                feed_id=1, time=1609459200, value="abc")  # Invalid value

    def test_prep_add_data_points(self):
        """Test the `prep_add_data_points` method with valid inputs."""
        result = EmonFeedsCore.prep_add_data_points(
            feed_id=1,
            data=[[1609459200, 123.45], [1609545600, 678.90]]
        )
        expected = (
            "/feed/insert.json",
            {
                "feed_id": 1,
                "data": [[1609459200, 123.45], [1609545600, 678.90]]
            }
        )
        assert result == expected

    def test_prep_add_data_points_invalid(self):
        """Test `prep_add_data_points` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeedsCore.prep_add_data_points(
                feed_id=1, data=[[1609459200, "abc"]])
