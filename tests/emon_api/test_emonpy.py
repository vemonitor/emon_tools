"""Test Suite for EmonPy class."""
from unittest.mock import MagicMock
import pytest
from emon_tools.api_utils import SUCCESS_KEY
from emon_tools.emonpy import EmonPy
from tests.emon_api.emonpy_test_data import EmonpyDataTest as dtest


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
        "inputs_response, feeds_response, expected_result",
        dtest.GET_STRUCTURE_PARAMS
    )
    def test_get_structure(
        self,
        api,
        inputs_response,
        feeds_response,
        expected_result
    ):
        """Test the get_structure method."""
        api.list_inputs_fields.return_value = inputs_response
        api.list_feeds.return_value = feeds_response

        result = api.get_structure()
        assert result == expected_result

    @pytest.mark.parametrize(
        "feeds, create_feed_results, expected_processes",
        dtest.CREATE_INPUT_FEEDS_PARAMS,
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

        _, result = api.create_input_feeds(feeds=feeds)
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
        dtest.CREATE_INPUTS_PARAMS
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
        dtest.INIT_INPUTS_STRUCTURE_PARAMS
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
        dtest.ADD_INPUT_FEEDS_STRUCTURE_PARAMS
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
        _, result = api.add_input_feeds_structure(
            input_item=input_item,
            feeds_on=feeds_on)
        assert result == expected_process

    @pytest.mark.parametrize(
        (
            "input_id, current, description, "
            "set_input_fields_response, expected_result"
        ),
        dtest.UPDATE_INPUT_FIELDS_PARAMS
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
            "set_process_list_response, expected_result"
        ),
        dtest.UPDATE_INPUT_PROCESS_LIST_PARAMS
    )
    def test_update_input_process_list(
        self,
        api,
        input_id,
        current_processes,
        new_processes,
        set_process_list_response,
        expected_result,
    ):
        """Test the update_input_process_list method."""
        api.set_input_process_list.return_value = set_process_list_response

        result = api.update_input_process_list(
            input_id=input_id,
            current_processes=current_processes,
            new_processes=new_processes
        )
        assert result == expected_result

    @pytest.mark.parametrize(
        (
            "structure, get_structure_return, "
            "raises_error, expected_result"
        ),
        dtest.CREATE_STRUCTURE_PARAMS
    )
    def test_create_structure(
        self,
        api,
        structure,
        get_structure_return,
        raises_error,
        expected_result,
    ):
        """Test the create_structure method."""
        api.init_inputs_structure = MagicMock(
            return_value=len(structure))
        api.get_structure = MagicMock(
            return_value=get_structure_return)
        api.add_input_feeds_structure = MagicMock(
            return_value=(0, [])
        )
        api.update_input_fields = MagicMock(return_value=0)
        api.update_input_process_list = MagicMock(return_value=0)

        if raises_error is True:
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
            result = api.create_structure(
                structure=structure
            )
            assert result == expected_result

    @pytest.mark.parametrize(
        (
            "structure, get_structure_return, "
            "raises_error, expected_result"
        ),
        dtest.GET_EXTENDED_STRUCTURE_PARAMS
    )
    def test_get_extended_structure(
        self,
        api,
        structure,
        get_structure_return,
        raises_error,
        expected_result,
    ):
        """Test the create_structure method."""
        api.get_structure = MagicMock(
            return_value=get_structure_return)

        if raises_error is True:
            with pytest.raises(
                    ValueError,
                    match="Fatal Error, inputs was not added to server."):
                api.get_extended_structure(structure=structure)
        else:
            result = api.get_extended_structure(
                structure=structure
            )
            assert result == expected_result
