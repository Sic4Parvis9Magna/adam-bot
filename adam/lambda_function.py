from json import loads, dumps
from os import getenv
import http.client as client
from random import randrange

import adam.constants as constants
import adam.telegram_client as telegram_client
import adam.github_client as github
import adam.mal_client as mal

SEARCH_COMMAND = 'search'
POLL_COMMAND = 'poll'
DIRS_COMMAND = 'dirs'
FORMAT_COMMAND = 'format'
GIT_TAG = '#gitpath'


def lambda_handler(event, context):
    body = loads(event['body'])
    chat_id = int(body['message']['chat']['id'])
    message = body['message']['text']

    try:
        handle_incoming_message(message=message, chat_id=chat_id)
    except Exception as e:
        response_text = "Something went wrong! Error log is: {error}".format(error=e)
        telegram_client.send_message(text=response_text, chat_id=chat_id)
        print("Error is: ", e)
    
    return {
        'statusCode': 200
    }


def handle_incoming_message(message:str, chat_id: int):
    if message.startswith( '/'):
        resolve_command(cmd=message, chat_id=chat_id)
    elif GIT_TAG in message:
        parse_and_commit_record(message=message, chat_id=chat_id)
    else:
        telegram_client.send_message(text=message, chat_id=chat_id)


def parse_and_commit_record(message: str, chat_id: int):
    record = github.parse_record(message)
    github_path = github.parse_github_path(message)

    result = github.commit_record(file_name=github_path, record=record)
    
    result_message = "Successfully committed the folllowing record:\n {record}\n to the following file: \n{github_path}".format(record=record, github_path=github_path)

    telegram_client.send_message(text=result_message, chat_id=chat_id)


def get_random_gintama_episode_name() -> str:
    series = constants.GIN_LIST
    size = len(series)
    number = randrange(size)
    return series[number]


def resolve_command(cmd: str, chat_id: int):
    error_message = constants.COMMAND_NOT_FOUND + cmd 
    if SEARCH_COMMAND in cmd:
        results= mal.get_results_for_genre('Action', 10)
        response_message = '\n'.join(results)
        telegram_client.send_message(text=response_message, chat_id=chat_id)
    elif POLL_COMMAND in cmd:
        generate_and_send_gintama_poll(chat_id=chat_id)
    elif DIRS_COMMAND in cmd:
        result = "\n".join(constants.DIR_LIST)
        telegram_client.send_message(text=result, chat_id=chat_id)
    elif FORMAT_COMMAND in cmd:
        telegram_client.send_message(text=constants.COMMIT_SUBMISSION_FORMAT, chat_id=chat_id)
    else:    
        telegram_client.send_message(text=error_message,chat_id=chat_id)


def generate_and_send_gintama_poll(chat_id):
    question = get_random_gintama_episode_name(),
    options_list = ["Y", "N", "22-30", "23-00", "23-15", "23-30"]
    
    telegram_client.send_poll(chat_id=chat_id, question=question, options=options_list, allow_multiple_answers=True, is_anonymous=False)
