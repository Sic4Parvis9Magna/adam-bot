import json
import pytest
from unittest.mock import Mock, patch, call

from test.utils import read_test_data
from adam.constants import GIN_LIST
from adam.lambda_function import (
    lambda_handler, get_random_gintama_episode_name, handle_incoming_message,
     parse_and_commit_record, resolve_command, SEARCH_COMMAND,
     POLL_COMMAND, DIRS_COMMAND, FORMAT_COMMAND,
     send_message, generate_and_send_gintama_poll)
from adam import constants


@patch('adam.lambda_function.handle_incoming_message')
def test_lambda_handler_should_handle_events(handle_incoming_message_mock):
    #given
    event = read_test_data(path='test/resources/event.json')
    expected_message = 'test message'    
    expected_chat_id = 42    
    context = None
    expected_result = {'statusCode': 200}

    #when
    actual_result = lambda_handler(event, context)

    #then
    handle_incoming_message_mock.assert_called_once_with(message=expected_message, chat_id=expected_chat_id)
    assert actual_result == expected_result


@patch('adam.lambda_function.send_message')
@patch('adam.lambda_function.handle_incoming_message')
def test_lambda_handler_should_handle_errors(handle_incoming_message_mock, send_message_mock):
    #given
    event = read_test_data(path='test/resources/event.json')
    expected_message = 'test message'    
    expected_chat_id = 42    
    context = None
    expected_result = {'statusCode': 200}
    handle_incoming_message_mock.side_effect = Exception('error msg')

    #when
    actual_result = lambda_handler(event, context)

    #then
    handle_incoming_message_mock.assert_called_once_with(message=expected_message, chat_id=expected_chat_id)
    send_message_mock.assert_called_once_with(text='Something went wrong! Error log is: error msg', chat_id=expected_chat_id)
    assert actual_result == expected_result


@patch('adam.lambda_function.resolve_command')
def test_handle_incoming_message_with_command(resolve_command_mock):
    #given
    message = '/poll'
    chat_id = 42

    #when
    handle_incoming_message(message=message, chat_id=chat_id)
    
    #then
    resolve_command_mock.assert_called_once_with(cmd=message, chat_id=chat_id)


@patch('adam.lambda_function.parse_and_commit_record')
def test_handle_incoming_message_with_git_tag(parse_and_commit_record_mock):
     #given
    message ="""#sql#tips_tricks#pagination#title: [Why You Shouldn’t Use OFFSET and LIMIT For Your Pagination]#gitpath: [dev/dev-links.MD]#link: [https://medium.com/swlh/why-you-shouldnt-use-offset-and-limit-for-your-pagination-4440e421ba87]"""
    chat_id = 42

    #when
    handle_incoming_message(message=message, chat_id=chat_id)
    
    #then
    parse_and_commit_record_mock.assert_called_once_with(message=message, chat_id=chat_id)


@patch('adam.lambda_function.send_message')
def test_handle_incoming_message_with_regular_text(send_message_mock):
    #given
    message = 'dummy text'
    chat_id = 42

    #when
    handle_incoming_message(message=message, chat_id=chat_id)
    
    #then
    send_message_mock.assert_called_once_with(text=message, chat_id=chat_id)

@patch('adam.lambda_function.send_message')
@patch('adam.github_client.commit_record')
@patch('adam.github_client.parse_github_path')
@patch('adam.github_client.parse_record')
def test_parse_and_commit_record(parse_record_mock, parse_github_path_mock,
                                    commit_record_mock, send_message_mock):
    #given
    parsed_record_mock = Mock()

    parse_record_mock.return_value = parsed_record_mock

    parsed_gitpath_mock = Mock()
    parse_github_path_mock.return_value = parsed_gitpath_mock

    commit_record_result_mock = Mock()
    commit_record_mock.return_value = commit_record_result_mock

    message = 'dummy message'
    chat_id = 42

    #when
    parse_and_commit_record(message=message, chat_id=chat_id)

    #then
    parse_record_mock.assert_called_once_with(message)
    parse_github_path_mock.assert_called_once_with(message)
    commit_record_mock.assert_called_once_with(file_name=parsed_gitpath_mock, record=parsed_record_mock)
    send_message_mock.assert_called_once()


def test_get_random_gintama_episode_name():
    #when
    actual_result = get_random_gintama_episode_name()
    
    #then
    assert actual_result in GIN_LIST


@patch('adam.lambda_function.send_message')
@patch('adam.mal_client.get_results_for_genre')
# @pytest.mark.skip(reason="fix needed")
def test_resolve_command_search(get_results_for_genre_mock, send_message_mock):
    #given
    expected_response = ['a', 'b']
    expected_text = '\n'.join(expected_response)
    get_results_for_genre_mock.return_value = expected_response 
    cmd = '/' + SEARCH_COMMAND + "some text"
    chat_id = 42


    #when
    resolve_command(cmd=cmd, chat_id=chat_id)

    #then
    get_results_for_genre_mock.assert_called_once()
    send_message_mock.assert_called_once_with(text=expected_text, chat_id=chat_id)



@patch('adam.lambda_function.generate_and_send_gintama_poll')
def test_resolve_command_poll(generate_and_send_gintama_poll_mock):
    #given
    cmd = '/' + POLL_COMMAND 
    chat_id = 42

    #when
    resolve_command(cmd=cmd, chat_id=chat_id)

    #then
    generate_and_send_gintama_poll_mock.assert_called_once_with(chat_id=chat_id)


@patch('adam.lambda_function.send_message')
def test_resolve_command_dirs(send_message_mock):
    #given
    expected_text = "\n".join(constants.DIR_LIST)
    cmd = '/' + DIRS_COMMAND 
    chat_id = 42

    #when
    resolve_command(cmd=cmd, chat_id=chat_id)

    #then
    send_message_mock.assert_called_once_with(text=expected_text, chat_id=chat_id)

@patch('adam.lambda_function.send_message')
def test_resolve_command_format(send_message_mock):
    #given
    cmd = '/' + FORMAT_COMMAND 
    chat_id = 42

    #when
    resolve_command(cmd=cmd, chat_id=chat_id)

    #then
    send_message_mock.assert_called_once_with(text=constants.COMMIT_SUBMISSION_FORMAT, chat_id=chat_id)


@patch('adam.lambda_function.send_message')
def test_resolve_command_not_found(send_message_mock):
    #given
    cmd = 'dummy text'
    chat_id = 42
    expected_text = constants.COMMAND_NOT_FOUND + cmd

    #when
    resolve_command(cmd=cmd, chat_id=chat_id)

    #then
    send_message_mock.assert_called_once_with(text=expected_text, chat_id=chat_id)


@patch('adam.telegram_client.make_rest_api_call')
def test_send_message(make_rest_api_call_mock):
    #given
    text = 'random text'
    chat_id = 42

    #when
    send_message(text=text, chat_id=chat_id)

    #then
    make_rest_api_call_mock.assert_called_once()
    

@patch('adam.telegram_client.make_rest_api_call')
def test_generate_and_send_gintama_poll(make_rest_api_call_mock):
    #given
    text = 'random text'
    chat_id = 42

    #when
    generate_and_send_gintama_poll(chat_id=chat_id)

    #then
    make_rest_api_call_mock.assert_called_once()