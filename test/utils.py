import json


def read_test_data(path: str):
    json_text = read_test_data_as_string(path=path)

    return json.loads(json_text)

def read_test_data_as_string(path: str) -> str:
    with open(path, 'r') as test_data_file:
        return test_data_file.read()