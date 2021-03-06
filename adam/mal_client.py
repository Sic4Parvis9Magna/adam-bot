import adam.constants as constants

import json
import http.client as client
#  HTTPConnection, HTTPResponse

"""
Supposed to be a number of method those would make calls to unofficial MAL DB
See api here:   
q=Fate/Zero&genre=2&type=tv&limit=3&score=7&status=completed
"""

def get_results_for_genre(genre: str, num_results: int):

    resolved_genre = constants.ANIME_GENRE[genre]
    print("genre: ", resolved_genre)
    base_url = constants.JIKAN_API_VERSION + constants.METHODS['search']
    formated_ulr = '{}/{}?genre={}&{}'.format(base_url, 'anime', resolved_genre, 'type=tv&limit=3&score=7&status=completed')
    print('formatted uri : ', formated_ulr)

    conn = client.HTTPConnection(constants.JIKAN_API_HOST)
    conn.request("GET", formated_ulr)
    response = conn.getresponse()
    
    return handle_response(response)

def handle_response(response: client.HTTPResponse) -> list:
    encoded_response_data = response.read()
    decoded_response_data = encoded_response_data.decode()
    dict_response = json.loads(decoded_response_data)
    results_key = 'results'
    results = []
    if results_key in dict_response and  dict_response[results_key] is not None:
        for result in dict_response[results_key]:
            results.append(result['url'])
    return results