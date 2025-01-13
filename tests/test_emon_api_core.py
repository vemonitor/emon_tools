"""Tests for the EmonRequest class using async"""
import pytest
from emon_tools.emon_api_core import InputGetType
from emon_tools.emon_api_core import EmonHelper
from emon_tools.emon_api_core import EmonInputs
from emon_tools.emon_api_core import EmonFeeds


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
        validated_url = EmonHelper.sanitize_url("http://localhost:8080")
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
            EmonHelper.sanitize_url(url)


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
        path, params = EmonInputs.prep_list_inputs(node)
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
        path, params = EmonInputs.prep_list_inputs_fields(get_type)
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
        path, params = EmonInputs.prep_input_fields(node, name)
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
            EmonInputs.prep_input_fields(node, name)

    @pytest.mark.parametrize(
        "input_id, fields, expected_params",
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
            ),
        ],
    )
    def test_prep_set_input_fields(
        self,
        input_id,
        fields,
        expected_params
    ):
        """Test prep_set_input_fields method."""
        path, params = EmonInputs.prep_set_input_fields(input_id, fields)
        assert path == "/input/set"
        assert params == expected_params

    @pytest.mark.parametrize(
        "input_id, fields, expected_exception",
        [
            ("123", {}, ValueError),
            ("123", None, ValueError),
            ("", {"field1": "value1"}, ValueError),
        ],
    )
    def test_prep_set_input_fields_invalid(
        self,
        input_id,
        fields,
        expected_exception
    ):
        """Test prep_set_input_fields with invalid input."""
        with pytest.raises(expected_exception):
            EmonInputs.prep_set_input_fields(input_id, fields)

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
        path, params = EmonInputs.prep_set_input_process_list(
            input_id, process_list)
        assert path == "/input/process/set"
        assert params == expected_params

    @pytest.mark.parametrize(
        "input_id, process_list, expected_exception",
        [
            ("123", "", ValueError),
            ("123", None, ValueError),
            ("", "process1:1,process2:2", ValueError),
        ],
    )
    def test_prep_set_input_process_list_invalid(
        self,
        input_id,
        process_list,
        expected_exception
    ):
        """Test prep_set_input_process_list with invalid input."""
        with pytest.raises(expected_exception):
            EmonInputs.prep_set_input_process_list(input_id, process_list)

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
        path, params = EmonInputs.prep_post_inputs(node, data)
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
            EmonInputs.prep_post_inputs(node, data)


class TestEmonFeeds:
    """
    Unit tests for the EmonFeeds class methods.

    This class tests all static methods in the EmonFeeds class,
    ensuring they return the expected outputs and handle all edge cases.
    """

    def test_prep_list_feeds(self):
        """Test the `prep_list_feeds` method for correctness."""
        assert EmonFeeds.prep_list_feeds() == ("/feed/list.json", None)

    @pytest.mark.parametrize("feed_id, expected", [
        (1, ("/feed/aget.json", {"id": 1})),
        (100, ("/feed/aget.json", {"id": 100})),
    ])
    def test_prep_feed_fields(self, feed_id, expected):
        """Test the `prep_feed_fields` method with valid inputs."""
        assert EmonFeeds.prep_feed_fields(feed_id) == expected

    def test_prep_feed_fields_invalid(self):
        """Test `prep_feed_fields` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeeds.prep_feed_fields(-1)  # Invalid feed ID

    @pytest.mark.parametrize("feed_id, expected", [
        (1, ("/feed/getmeta.json", {"id": 1})),
        (50, ("/feed/getmeta.json", {"id": 50})),
    ])
    def test_prep_feed_meta(self, feed_id, expected):
        """Test the `prep_feed_meta` method with valid inputs."""
        assert EmonFeeds.prep_feed_meta(feed_id) == expected

    def test_prep_feed_meta_invalid(self):
        """Test `prep_feed_meta` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeeds.prep_feed_meta(0)  # Invalid feed ID

    @pytest.mark.parametrize("feed_id, expected", [
        (1, ("/feed/timevalue.json", {"id": 1})),
        (75, ("/feed/timevalue.json", {"id": 75})),
    ])
    def test_prep_last_value_feed(self, feed_id, expected):
        """Test the `prep_last_value_feed` method with valid inputs."""
        assert EmonFeeds.prep_last_value_feed(feed_id) == expected

    def test_prep_last_value_feed_invalid(self):
        """Test `prep_last_value_feed` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeeds.prep_last_value_feed(-10)  # Invalid feed ID

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
        result = EmonFeeds.prep_fetch_feed_data(
            feed_id, start, end, interval, average
        )
        assert result == ("/feed/data.json", expected)

    def test_prep_fetch_feed_data_invalid(self):
        """Test `prep_fetch_feed_data` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeeds.prep_fetch_feed_data(
                -1, 1609459200, 1609545600, 60, False
            )  # Invalid feed ID

    def test_prep_create_feed(self):
        """Test the `prep_create_feed` method with valid inputs."""
        result = EmonFeeds.prep_create_feed(
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
            EmonFeeds.prep_create_feed(name="", tag="tag")  # Invalid name

    def test_prep_update_feed(self):
        """Test the `prep_update_feed` method with valid inputs."""
        result = EmonFeeds.prep_update_feed(
            feed_id=1,
            fields={"tag": "value"}
        )
        expected = (
            "/feed/set.json", {"feed_id": 1, "fields": {"tag": "value"}})
        assert result == expected

    def test_prep_update_feed_invalid(self):
        """Test `prep_update_feed` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeeds.prep_update_feed(
                feed_id=1, fields={"name": "@123 /$*ù"})

    def test_prep_delete_feed(self):
        """Test the `prep_delete_feed` method with valid inputs."""
        result = EmonFeeds.prep_delete_feed(feed_id=1)
        assert result == ("/feed/delete.json", {"id": 1})

    def test_prep_delete_feed_invalid(self):
        """Test `prep_delete_feed` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeeds.prep_delete_feed(feed_id=-5)  # Invalid feed ID

    def test_prep_add_data_point(self):
        """Test the `prep_add_data_point` method with valid inputs."""
        result = EmonFeeds.prep_add_data_point(
            feed_id=1, time=1609459200, value=123.45)
        expected = (
            "/feed/insert.json",
            {"feed_id": 1, "time": 1609459200, "value": 123.45}
        )
        assert result == expected

    def test_prep_add_data_point_invalid(self):
        """Test `prep_add_data_point` method with invalid inputs."""
        with pytest.raises(ValueError):
            EmonFeeds.prep_add_data_point(
                feed_id=1, time=1609459200, value="abc")  # Invalid value

    def test_prep_add_data_points(self):
        """Test the `prep_add_data_points` method with valid inputs."""
        result = EmonFeeds.prep_add_data_points(
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
            EmonFeeds.prep_add_data_points(
                feed_id=1, data=[[1609459200, "abc"]])
