from json import loads, dumps
import http.client as client

BASE_DOMAIN = 'api.telegram.org'
BASE_ENCODING = 'utf-8'
CONTENT_TYPE_HEADER_NAME = 'Content-Type'
CONTENT_TYPE_APPLICATION_JSON = 'application/json'
BASE_HEADERS = {CONTENT_TYPE_HEADER_NAME: CONTENT_TYPE_APPLICATION_JSON}

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