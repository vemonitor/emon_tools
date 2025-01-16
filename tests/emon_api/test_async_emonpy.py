"""
Unit tests for the AsyncEmonPy class.

This module tests the functionality of the AsyncEmonPy class, ensuring:
1. Correct behavior in normal scenarios.
2. Proper handling of edge cases and exceptions.
3. Full compliance with the expected API interactions.

Test coverage is designed to achieve 100% coverage with appropriate mocks.
"""
from unittest.mock import AsyncMock, patch
import pytest
from emon_tools.emon_api_core import EmonHelper
from emon_tools.async_emonpy import AsyncEmonPy
from emon_tools.api_utils import SUCCESS_KEY, MESSAGE_KEY


@pytest.mark.asyncio
class TestAsyncEmonPy:
    """Unit tests for the AsyncEmonPy class."""

    @pytest.fixture
    def api(self):
        """Fixture to create an instance of AsyncEmonPy."""
        return AsyncEmonPy(url="http://test-url", api_key="123")

    @pytest.mark.parametrize(
        "inputs_response, feeds_response, expected_inputs, expected_feeds",
        [
            (
                {SUCCESS_KEY: True, MESSAGE_KEY: "Inputs data"},
                {SUCCESS_KEY: True, MESSAGE_KEY: "Feeds data"},
                "Inputs data",
                "Feeds data",
            ),
            (
                {SUCCESS_KEY: False},
                {SUCCESS_KEY: True, MESSAGE_KEY: "Feeds data"},
                None,
                None,
            ),
        ],
    )
    async def test_get_structure(
        self,
        api,
        inputs_response,
        feeds_response,
        expected_inputs,
        expected_feeds
    ):
        """
        Test the get_structure method.

        This method validates the behavior
        of get_structure under various API response conditions.
        """
        api.async_list_inputs_fields = AsyncMock(return_value=inputs_response)
        api.async_list_feeds = AsyncMock(return_value=feeds_response)

        inputs, feeds = await api.get_structure()

        assert inputs == expected_inputs
        assert feeds == expected_feeds

    @pytest.mark.parametrize(
        (
            "feeds, feed_responses, expected_result, "
            "raises_exception, exception_message"),
        [
            (
                [{"name": "feed1", "tag": "tag1"}],
                [{SUCCESS_KEY: True, MESSAGE_KEY: {"feedid": "1"}}],
                (1, [[1, 1]]),
                False,
                None,
            ),
            (
                [{"name": "feed1", "tag": "tag1"}],
                [{SUCCESS_KEY: False}],
                None,
                True,
                (
                    "Fatal error: "
                    "Unable to set feed structure node tag1 - name feed1"),
            ),
        ],
    )
    async def test_create_input_feeds(
        self,
        api,
        feeds,
        feed_responses,
        expected_result,
        raises_exception,
        exception_message,
    ):
        """
        Test the create_input_feeds method.

        This method validates successful creation and error handling for feeds.
        """
        api.async_create_feed = AsyncMock(side_effect=feed_responses)

        if raises_exception:
            with pytest.raises(ValueError, match=exception_message):
                await api.create_input_feeds(feeds=feeds)
        else:
            result = await api.create_input_feeds(feeds=feeds)
            assert result == expected_result

    @pytest.mark.parametrize(
        (
            "structure, inputs, feeds, init_inputs_result, "
            "add_inputs_result, inputs_on, raises_exception, exception_message"
        ),
        [
            # Case 1: Successful structure creation
            (
                [
                    {
                        "nodeid": "node1", "name": "input1",
                        "description": "desc1", "feeds": []
                    }
                ],
                [
                    {
                        "id": 1, "nodeid": "node1", "name": "input1",
                        "description": "desc1", "processList": ""
                    }
                ],
                [],  # Feeds
                1,  # init_inputs_structure result
                [1, [[1, 1]]],  # add_input_feeds_structure result
                [
                    {
                        "id": 1, "nodeid": "node1", "name": "input1",
                        "description": "desc1"
                    }
                ],  # inputs_on
                False,  # No exception expected
                None,
            ),
            # Case 2: Structure creation fails, raising a ValueError
            (
                [
                    {
                        "nodeid": "node1", "name": "input1",
                        "description": "desc1", "feeds": []
                    }
                ],
                [],  # Inputs are not successfully added
                [],  # Feeds
                1,  # init_inputs_structure result
                (0, []),  # add_input_feeds_structure returns no inputs
                [],  # inputs_on
                True,  # Exception expected
                "Fatal Error, inputs was not added to server.",
            ),
        ],
    )
    async def test_create_structure(
        self,
        api,
        structure,
        inputs,
        feeds,
        init_inputs_result,
        add_inputs_result,
        inputs_on,
        raises_exception,
        exception_message,
    ):
        """
        Test the create_structure method.

        Ensures that the method correctly handles both success
        and failure cases for creating structures with the EmonCMS API.
        """
        with patch(
                "emon_tools.emon_api_core.EmonHelper.get_existant_structure",
                return_value=(inputs_on, feeds)):
            # Mock dependencies
            api.init_inputs_structure = AsyncMock(
                return_value=init_inputs_result)
            api.get_structure = AsyncMock(
                return_value=(inputs, feeds))
            api.add_input_feeds_structure = AsyncMock(
                return_value=add_inputs_result)
            api.set_input_fields = AsyncMock(return_value=0)
            api.set_input_process_list = AsyncMock(return_value=0)

            if raises_exception:
                with pytest.raises(ValueError, match=exception_message):
                    await api.create_structure(structure=structure)
            else:
                result = await api.create_structure(structure=structure)
                expected_result = {
                    'nb_updated_inputs': 0,
                    "nb_added_inputs": init_inputs_result,
                    'nb_added_feeds': 1,
                    "input_1": {
                        "input_feeds": 1,
                        "input_fields": 0,
                        "input_process": 0
                    },
                }
                assert result == expected_result

            # Validate that mocked methods
            # are called with appropriate arguments
            api.init_inputs_structure.assert_awaited_once_with(
                structure=structure)
            api.get_structure.assert_awaited_once()
            if not raises_exception:
                api.add_input_feeds_structure.assert_awaited()

    @pytest.mark.parametrize(
        "input_id, current, description, expected_result",
        [
            (1, "current_desc", "new_desc", 1),
            (1, "current_desc", "current_desc", 0),
        ],
    )
    async def test_set_input_fields(
        self, api, input_id, current, description, expected_result
    ):
        """
        Test the set_input_fields method.

        This method ensures fields are updated only when necessary.
        """
        api.async_set_input_fields = AsyncMock(
            return_value={SUCCESS_KEY: True, MESSAGE_KEY: 'Field updated'})

        result = await api.update_input_fields(
            input_id=input_id, current=current, description=description
        )

        assert result == expected_result

    @pytest.mark.parametrize(
        "input_id, current_processes, new_processes, expected_result",
        [
            (1, "", [[1, 1]], 1),  # Update required
            (1, "1:1", [[1, 1]], 0),            # No update needed
        ],
    )
    async def test_set_input_process_list(
        self, api, input_id, current_processes, new_processes, expected_result
    ):
        """
        Test the set_input_process_list method.

        Ensures the process list is updated only when necessary.
        """
        # Mock the async method to simulate API behavior
        api.async_set_input_process_list = AsyncMock(
            return_value={
                SUCCESS_KEY: True,
                MESSAGE_KEY: 'Input processlist updated'})

        # Call the method under test
        result = await api.update_input_process_list(
            input_id=input_id,
            current_processes=current_processes,
            new_processes=new_processes,
        )

        # Validate the result matches expectations
        assert result == expected_result

        # Ensure async_set_input_process_list
        # is only called when update is needed
        if expected_result:
            api.async_set_input_process_list.assert_awaited_once_with(
                input_id=input_id,
                process_list=",".join(
                    EmonHelper.format_process_list(new_processes)),
            )
        else:
            api.async_set_input_process_list.assert_not_awaited()
