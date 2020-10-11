import json
import pytest
import random
from unittest.mock import Mock, patch, call

from adam.mal_client import get_results_for_genre, handle_response
import adam.constants as constants
import test.utils as tutils


@patch('http.client.HTTPConnection')
@patch('adam.mal_client.handle_response')
def test_get_results_for_genre(handle_response_mock, http_connection_mock):
    #given
    expected_result = Mock()
    handle_response_mock.return_value = expected_result

    connection_mock = Mock()
    http_connection_mock.return_value = connection_mock
    response_mock = Mock()
    connection_mock.getresponse.return_value = response_mock

    genre = 'Action'
    num_results = 42

    #when
    actual_result = get_results_for_genre(genre=genre, num_results=num_results)
    
    #then
    assert expected_result == actual_result
    http_connection_mock.assert_called_once_with(constants.JIKAN_API_HOST)
    connection_mock.request.assert_called_once_with("GET", '/v3/search/anime?genre=1&type=tv&limit=3&score=7&status=completed')
    connection_mock.getresponse.assert_called_once()
    handle_response_mock.assert_called_once_with(response_mock)
    

def test_handle_response():
    #given
    string_response = tutils.read_test_data_as_string('test/resources/jikan_response.json')
    input_response_mock = Mock()
    encoded_data_mock = Mock()
    input_response_mock.read.return_value = encoded_data_mock
    encoded_data_mock.decode.return_value = string_response 

    expected_results_size = 3

    #when
    actual_result = handle_response(response=input_response_mock)

    #then
    assert len(actual_result) == expected_results_size
    input_response_mock.read.assert_called_once()
    encoded_data_mock.decode.assert_called_once()