"""
Unit tests for the AsyncEmonPy class.

This module tests the functionality of the AsyncEmonPy class, ensuring:
1. Correct behavior in normal scenarios.
2. Proper handling of edge cases and exceptions.
3. Full compliance with the expected API interactions.

Test coverage is designed to achieve 100% coverage with appropriate mocks.
"""
from unittest.mock import AsyncMock
import pytest
from emon_tools.async_emonpy import AsyncEmonPy
from emon_tools.api_utils import SUCCESS_KEY
from tests.emon_api.emonpy_test_data import EmonpyDataTest as dtest


@pytest.mark.asyncio
class TestAsyncEmonPy:
    """Unit tests for the AsyncEmonPy class."""

    @pytest.fixture
    def api(self):
        """Fixture to create an instance of AsyncEmonPy."""
        emon = AsyncEmonPy(url="http://test-url", api_key="123")
        emon.async_list_inputs_fields = AsyncMock()
        emon.async_list_feeds = AsyncMock()
        emon.async_create_feed = AsyncMock()
        emon.async_post_inputs = AsyncMock()
        emon.async_set_input_fields = AsyncMock()
        emon.async_set_input_process_list = AsyncMock()
        return emon

    def test_init(self):
        """Test initialization of EmonPy."""
        emon = AsyncEmonPy(url="http://example.com", api_key="123")
        assert emon.api_key == "123"
        assert emon.url == "http://example.com"

    @pytest.mark.parametrize(
        "inputs_response, feeds_response, expected_result",
        dtest.GET_STRUCTURE_PARAMS
    )
    async def test_get_structure(
        self,
        api,
        inputs_response,
        feeds_response,
        expected_result
    ):
        """
        Test the get_structure method.

        This method validates the behavior
        of get_structure under various API response conditions.
        """
        api.async_list_inputs_fields.return_value = inputs_response
        api.async_list_feeds.return_value = feeds_response

        result = await api.get_structure()

        assert result == expected_result

    @pytest.mark.parametrize(
        "feeds, create_feed_results, expected_processes",
        dtest.CREATE_INPUT_FEEDS_PARAMS,
    )
    async def test_create_input_feeds(
        self,
        api,
        feeds,
        create_feed_results,
        expected_processes
    ):
        """
        Test the create_input_feeds method.

        This method validates successful creation and error handling for feeds.
        """
        api.async_create_feed.side_effect = create_feed_results

        _, result = await api.create_input_feeds(feeds=feeds)
        assert result == expected_processes

    async def test_create_input_feeds_invalid(
        self,
        api
    ):
        """Test the create_input_feeds method."""
        api.async_create_feed.side_effect = [
            {"message": "Error", SUCCESS_KEY: False}
        ]

        with pytest.raises(
                ValueError,
                match="Fatal error: Unable to set feed structure.*"):
            await api.create_input_feeds(
                feeds=[{"name": "feed1", "tag": "tag1"}])

    @pytest.mark.parametrize(
        "inputs, post_inputs_responses, expected_count",
        dtest.CREATE_INPUTS_PARAMS
    )
    async def test_create_inputs(
        self,
        api,
        inputs,
        post_inputs_responses,
        expected_count
    ):
        """Test the create_inputs method."""
        api.async_post_inputs.side_effect = post_inputs_responses

        result = await api.create_inputs(inputs=inputs)
        assert result == expected_count

    async def test_create_inputs_invalid(
        self,
        api
    ):
        """Test the create_input_feeds method."""
        api.async_post_inputs.side_effect = [
            {"message": "Error", SUCCESS_KEY: False}
        ]

        with pytest.raises(
                ValueError,
                match="Fatal error: Unable to set inputs structure.*"):
            await api.create_inputs(
                inputs=[{"nodeid": "node1", "name": "input1"}])

    @pytest.mark.parametrize(
        "structure, inputs, expected_count",
        dtest.INIT_INPUTS_STRUCTURE_PARAMS
    )
    async def test_init_inputs_structure(
        self,
        api,
        structure,
        inputs,
        expected_count
    ):
        """Test the init_inputs_structure method."""
        api.list_inputs_fields = AsyncMock(return_value=inputs)
        api.create_inputs = AsyncMock(return_value=expected_count)
        result = await api.init_inputs_structure(structure=structure)
        assert result == expected_count

    @pytest.mark.parametrize(
        "input_item, feeds_on, expected_created, expected_process",
        dtest.ADD_INPUT_FEEDS_STRUCTURE_PARAMS
    )
    async def test_add_input_feeds_structure(
        self,
        api,
        input_item,
        feeds_on,
        expected_created,
        expected_process
    ):
        """Test the init_inputs_structure method."""
        api.create_input_feeds = AsyncMock(return_value=expected_created)
        _, result = await api.add_input_feeds_structure(
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
    async def test_update_input_fields(
        self,
        api,
        input_id,
        current,
        description,
        set_input_fields_response,
        expected_result
    ):
        """Test the update_input_fields method."""
        api.async_set_input_fields.return_value = set_input_fields_response

        result = await api.update_input_fields(
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
    async def test_update_input_process_list(
        self,
        api,
        input_id,
        current_processes,
        new_processes,
        set_process_list_response,
        expected_result,
    ):
        """Test the update_input_process_list method."""
        api.async_set_input_process_list.return_value = set_process_list_response

        result = await api.update_input_process_list(
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
    async def test_create_structure(
        self,
        api,
        structure,
        get_structure_return,
        raises_error,
        expected_result,
    ):
        """Test the create_structure method."""
        api.init_inputs_structure = AsyncMock(
            return_value=len(structure))
        api.get_structure = AsyncMock(
            return_value=get_structure_return)
        api.add_input_feeds_structure = AsyncMock(
            return_value=(0, [])
        )
        api.update_input_fields = AsyncMock(return_value=0)
        api.update_input_process_list = AsyncMock(return_value=0)

        if raises_error is True:
            api.add_input_feeds_structure = AsyncMock(
                side_effect=ValueError(
                    "Fatal Error, inputs was not added to server."
                )
            )
            with pytest.raises(
                    ValueError,
                    match="Fatal Error, inputs was not added to server."):
                await api.create_structure(structure=structure)
        else:
            result = await api.create_structure(
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
    async def test_get_extended_structure(
        self,
        api,
        structure,
        get_structure_return,
        raises_error,
        expected_result,
    ):
        """Test the create_structure method."""
        api.get_structure = AsyncMock(
            return_value=get_structure_return)

        if raises_error is True:
            with pytest.raises(
                    ValueError,
                    match="Fatal Error, inputs was not added to server."):
                await api.get_extended_structure(structure=structure)
        else:
            result = await api.get_extended_structure(
                structure=structure
            )
            assert result == expected_result
