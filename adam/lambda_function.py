from json import loads, dumps
from os import getenv
import http.client as client
from random import randrange

import adam.constants
import adam.github_client as github
from adam.mal_client import get_results_for_genre

BASE_URL_TEMPLATE = "/bot{token}"
BOT_TOKEN = getenv("BOT_TOKEN")
BASE_URL = BASE_URL_TEMPLATE.format(token=BOT_TOKEN)
SEARCH_COMMAND = 'search'
POLL_COMMAND = 'poll'
DIRS_COMMAND = 'dirs'
FORMAT_COMMAND = 'format'
GIT_TAG = '#gitpath'


def lambda_handler(event, context):
    body = loads(event['body'])
    chat_id = body['message']['chat']['id']
    message = body['message']['text']

    try:
        handle_incoming_message(message=message, chat_id=chat_id)
    except Exception as e:
        response_text = "Something went wrong! Error log is: {error}".format(error=e)
        send_message(text=response_text, chat_id=chat_id)
        print("Error is: ", e)
    
    return {
        'statusCode': 200
    }


def handle_incoming_message(message:str, chat_id: int):
    if message.startswith( '/'):
        resolve_command(message, chat_id)
    elif GIT_TAG in message:
        handle_git_commit(message, chat_id)
    else:
        send_message(message, chat_id)


def handle_git_commit(message: str, chat_id: int):
    record = github.parse_record(message)
    github_path = github.parse_github_path(message)

    result = github.commit_record(file_name=github_path, record=record)
    
    result_message = "Successfully committed the folllowing record:\n {record}\n to the following file: \n{github_path}".format(record=record, github_path=github_path)

    send_message(text=result_message, chat_id=chat_id)


def get_rn_gin() -> str:
    series = constants.GIN_LIST
    size = len(series)
    number = randrange(size)
    return series[number]


def resolve_command(cmd: str, chat_id: int):
    message = 'Unresolved command =( : ' + cmd 
    if SEARCH_COMMAND in cmd:
        response_message = '\n'.join(get_results_for_genre('Action', 10))
        send_message(text=response_message, chat_id=chat_id)
    elif POLL_COMMAND in cmd:
        sendGintamaPoll(chat_id=chat_id)
    elif DIRS_COMMAND in cmd:
        result = "\n".join(constants.DIR_LIST)
        send_message(text=result, chat_id=chat_id)
    elif FORMAT_COMMAND in cmd:
        send_message(text=constants.COMMIT_SUBMISSION_FORMAT, chat_id=chat_id)
    else:    
        send_message(test=message,chat_id=chat_id)


def send_message(text, chat_id):
    url = BASE_URL + "/sendMessage".format(token=BOT_TOKEN)
    body = {
        "text": text,
        "chat_id": chat_id
    }
    return make_rest_call(url=url, method='POST', body=body)


def sendGintamaPoll(chat_id):
    url = BASE_URL + "/sendPoll".format(token=BOT_TOKEN)
    body = {
        "chat_id" : chat_id,
        "question": get_rn_gin(),
        "options": ["Y", "N", "22-30", "23-00", "23-15", "23-30"],
        "allows_multiple_answers": True,
        "is_anonymous": False
    }
    make_rest_call(url=url, method='POST', body=body)


def make_rest_call(url: str, method: str, body: dict):
    conn = client.HTTPSConnection('api.telegram.org')
    json_body = dumps(body)
    bytes_body = bytes(json_body,encoding="utf-8")

    headers = {"Content-Type": "application/json"}

    conn.request(method, url, headers=headers, body=bytes_body)
    response = conn.getresponse()
    raw_res = response.read()
    conn.close()
    json_res = loads(raw_res)

    return json_res
