from json import loads, dumps
import http.client as client
from os import getenv

BASE_DOMAIN = 'api.telegram.org'
BASE_ENCODING = 'utf-8'
CONTENT_TYPE_HEADER_NAME = 'Content-Type'
CONTENT_TYPE_APPLICATION_JSON = 'application/json'
BASE_HEADERS = {CONTENT_TYPE_HEADER_NAME: CONTENT_TYPE_APPLICATION_JSON}

BOT_TOKEN = getenv("BOT_TOKEN")
BASE_URL = f"/bot{BOT_TOKEN}"
SEND_MESSAGE_ENDPOINT = f"{BASE_URL}/sendMessage"
SEND_POLL_ENDPOINT = f"{BASE_URL}/sendPoll"


def send_message(text: str, chat_id: int):
    body = {
        "text": text,
        "chat_id": chat_id
    }

    return make_rest_api_call(url=SEND_MESSAGE_ENDPOINT, method='POST', body=body)


def send_poll(chat_id: int, question: str, options: list, allow_multiple_answers=False, is_anonymous=False):
    body = {
        "chat_id" : chat_id,
        "question": question,
        "options": options,
        "allows_multiple_answers": allow_multiple_answers,
        "is_anonymous": is_anonymous
    }
    make_rest_api_call(url=SEND_POLL_ENDPOINT, method='POST', body=body)


def make_rest_api_call(url: str, method: str, body: dict):
    conn = client.HTTPSConnection(BASE_DOMAIN)
    json_body = dumps(body)
    bytes_body = bytes(json_body,encoding=BASE_ENCODING)

    conn.request(method, url, headers=BASE_HEADERS, body=bytes_body)
    response = conn.getresponse()
    raw_res = response.read()
    conn.close()
    json_res = loads(raw_res)

    return json_res