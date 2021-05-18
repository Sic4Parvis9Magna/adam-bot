import pytest
from unittest.mock import Mock, patch, call
from adam.telegram_client import send_message, send_poll, make_rest_api_call, BASE_DOMAIN, BASE_HEADERS

@patch('adam.telegram_client.make_rest_api_call')
def test_send_message(rest_api_call_mock):
    #given
    chat_id = 42
    text = "my message"
    expected_response = "test"
    rest_api_call_mock.return_value = expected_response

    #when
    actual_result = send_message(text=text, chat_id=42)

    #then
    rest_api_call_mock.assert_called_once()
    
    assert actual_result == expected_response


@patch('adam.telegram_client.make_rest_api_call')
def test_send_poll(rest_api_call_mock):
    #given
    chat_id = 42
    question = "why 42?"
    options = ["A", "B", "C"]

    #when
    send_poll(chat_id=chat_id, question=question, options=options)

    #then
    rest_api_call_mock.assert_called_once()


@patch('http.client.HTTPSConnection')
def test_make_rest_api_call(https_client):
    #given
    connection_mock = Mock()
    https_client.return_value = connection_mock
    response_mock = Mock()
    connection_mock.getresponse.return_value = response_mock
    response_mock.read.return_value = '{"foo": "bar"}'
    expected_result = {'foo': 'bar'}
    url = 'dummy/url/path'
    method = 'GET'
    headers=BASE_HEADERS

    #when
    actual_result = make_rest_api_call(url=url, method=method, body=None)

    #then
    https_client.assert_called_once_with(BASE_DOMAIN)
    connection_mock.request.assert_called_once_with(method, url, headers=headers, body=b'null')
    connection_mock.getresponse.assert_called_once()
    response_mock.read.assert_called_once()
    connection_mock.close.assert_called_once()

    assert expected_result == actual_result