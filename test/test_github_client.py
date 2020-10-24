import pytest
from unittest.mock import Mock, patch, call
import os
import json
from test.utils import read_test_data
from adam.github_api_constants import HTTP_GET, USER_AGENT, DUMMY_AGENT, AUTHORIZATION, BASE_URL
from adam.github_client import (get_record_number, get_next_int, filterout_reserved_tags,
 RESERVED_TAGS, get_commits, parse_github_path, 
 parse_record, create_put_contents_url, get_blob_url,
 get_tree_url, get_list_commit_url, generate_record,
 has_author, has_commiter, get_commit_timestamp,
 get_commits, get_tree, get_blob,
 get_blob_content, update_contents, make_rest_call,
 get_record_number, get_blob_sha, find_blob_sha,
 get_latest_commit_sha, commit_record)
import datetime

get_next_int_params = [
    ('001','002'),
    ('041', '042'),
    ('101', '102'),
    ('1023', '1024')
]

dummy_timestamp = 'Wed Jul 29 02:13:29 2020 +0300'
dummy_sha = '54cb3f95b913e9e884976532845f31b8a1c62b5c'

@pytest.mark.parametrize("input_data,expected_result", get_next_int_params)
def test_get_next_int(input_data, expected_result):
    #when
    actual_result = get_next_int(str_number=input_data)

    #then
    assert actual_result == expected_result

def test_get_next_int_negative_input():
    #given
    input_number = '-42'
    expected_result = '000'

    #when
    actual_result =  get_next_int(str_number=input_number)

    #then
    assert actual_result == expected_result

@pytest.mark.parametrize("input_data", [('0.042'),('foo')])
def test_get_next_int_not_int_number_input(input_data):
    #when & then
    with pytest.raises(ValueError):
        get_next_int(str_number=input_data)

def generate_input_tags() -> list:
    result = [tuple([])]
    base_tags = ['devops', 'linux', 'java']
    
    for i in range(len(RESERVED_TAGS)):
        cutted_tags = RESERVED_TAGS[:i]
        print("cutted tags: ", cutted_tags)
        tags_list = base_tags.copy()
        tags_list.extend(cutted_tags)
        item = tuple(tags_list)
        result.append(item)

    return result

generated_input_tags = generate_input_tags()

@pytest.mark.parametrize("input_data", generated_input_tags)
def test_filterout_reserved_tags(input_data):
    #when
    actual_result = filterout_reserved_tags(tags_list=input_data)

    #then
    for tag in RESERVED_TAGS:
        assert tag not in actual_result 


@patch('adam.github_client.get_list_commit_url')
@patch('adam.github_client.make_rest_call')
def test_get_commits(rest_call_func_mock, commits_url_func_mock):
    #given
    commits_url = '/repos/test_user/test_repo/commits'
    rest_call_result = 'call_result'
    commits_url_func_mock.return_value = commits_url
    rest_call_func_mock.return_value = rest_call_result 

    #when
    actual_result = get_commits()
    
    #then
    commits_url_func_mock.assert_called_once()
    rest_call_func_mock.assert_called_once_with(url=commits_url, method=HTTP_GET)

    assert actual_result ==  rest_call_result


@patch('adam.github_client.get_tree_url')
@patch('adam.github_client.make_rest_call')
def test_get_tree(rest_call_func_mock, tree_url_func_mock):
    #given
    commits_url = '/repos/test_user/test_repo/git/trees/'
    sha = '54cb3f95b913e9e884976532845f31b8a1c62b5c'
    rest_call_result = 'call_result'
    tree_url_func_mock.return_value = commits_url
    rest_call_func_mock.return_value = rest_call_result 

    #when
    actual_result = get_tree(sha=sha)
    
    #then
    tree_url_func_mock.assert_called_once_with(sha=sha)
    rest_call_func_mock.assert_called_once_with(url=commits_url, method=HTTP_GET)

    assert actual_result ==  rest_call_result


@patch('adam.github_client.get_blob_url')
@patch('adam.github_client.make_rest_call')
def test_get_blob(rest_call_func_mock, blob_url_func_mock):
    #given
    commits_url = '/repos/test_user/test_repo/git/blobs/'
    sha = '54cb3f95b913e9e884976532845f31b8a1c62b5c'
    rest_call_result = 'call_result'
    blob_url_func_mock.return_value = commits_url
    rest_call_func_mock.return_value = rest_call_result 

    #when
    actual_result = get_blob(sha=sha)
    
    #then
    blob_url_func_mock.assert_called_once_with(sha=sha)
    rest_call_func_mock.assert_called_once_with(url=commits_url, method=HTTP_GET)

    assert actual_result ==  rest_call_result

@patch('http.client.HTTPSConnection')
@patch('adam.github_client.create_put_contents_url')
def test_update_blob(create_put_contents_url, https_client):
    #given
    path = 'test_path/test_dir'
    request_body = {
        "message": "add a new record with the title 'dummy title'",
        "sha": '54cb3f95b913e9e884976532845f31b8a1c62b5c',
        "content": 'ZHVtbXkgY29udGVudA=='
    } 

    put_blob_url =  '/repos/test_user/test_repo/contents/' + path
    create_put_contents_url.return_value = put_blob_url
    connection_mock = Mock()
    https_client.return_value = connection_mock
    response_mock = Mock()
    connection_mock.getresponse.return_value = response_mock
    response_mock.read.return_value = '{"foo": "bar"}'
    expected_result = {'foo': 'bar'}
    headers = {
    USER_AGENT: DUMMY_AGENT,
    AUTHORIZATION: None
    }

    json_body = json.dumps(request_body)
    bytes_body = bytes(json_body,encoding='utf-8')

    #when
    actual_result = update_contents(body=request_body, path=path)
    
    #then
    https_client.assert_called_once_with(BASE_URL)
    create_put_contents_url.assert_called_once_with(path=path)
    connection_mock.request.assert_called_once_with(method='PUT', url =put_blob_url, headers=headers, body=bytes_body)
    connection_mock.getresponse.assert_called_once()
    response_mock.read.assert_called_once()
    connection_mock.close.assert_called_once()

    assert expected_result == actual_result

def test_get_blob_content():
    #given
    blob ={"content": 'aGVsbG8='}
    expected_result = 'hello'

    #when
    actual_result = get_blob_content(blob=blob)

    #then
    assert expected_result == actual_result

@patch('http.client.HTTPSConnection')
def test_make_rest_call(https_client):
    #given
    connection_mock = Mock()
    https_client.return_value = connection_mock
    response_mock = Mock()
    connection_mock.getresponse.return_value = response_mock
    response_mock.read.return_value = '{"foo": "bar"}'
    expected_result = {'foo': 'bar'}
    url = 'dummy/url/path'
    method = 'GET'
    headers={USER_AGENT: DUMMY_AGENT}

    #when
    actual_result = make_rest_call(url=url, method=method)

    #then
    https_client.assert_called_once_with(BASE_URL)
    connection_mock.request.assert_called_once_with(method=method, url =url, headers=headers)
    connection_mock.getresponse.assert_called_once()
    response_mock.read.assert_called_once()
    connection_mock.close.assert_called_once()

    assert expected_result == actual_result

def test_find_latest_commit_found():
    #given
    commits = read_test_data(path='test/resources/get_commits_list_response.json')
    expected_sha = 'c04cf3ff85e7944d759effeddd78696858ab33d0' 

    #when
    actual_result = get_latest_commit_sha(commits=commits)

    #then
    assert actual_result == expected_sha

def test_find_latest_commit_not_found():
    #given
    commits =[]
    
    #when
    actual_result = get_latest_commit_sha(commits=commits)

    #then
    assert actual_result == None

get_record_number_params = [
    ("""
Record-001: **#k8s**, **#vagrant**, **#ansible**    
[Kubernetes Setup Using Ansible and Vagrant](https://kubernetes.io/blog/2019/03/15/kubernetes-setup-using-ansible-and-vagrant/)

Record-002: **#k8s**, **#storage**, **#performance**    
[State of Persistent Storage in K8s — A Benchmark](https://itnext.io/state-of-persistent-storage-in-k8s-a-benchmark-77a96bb1ac29)

Record-003: **#k8s**, **#egrees**, **#ingrees**   
[NGINX Ingress Controller: Exposing TCP and UDP services](https://kubernetes.github.io/ingress-nginx/user-guide/exposing-tcp-udp-services/)

Record-004: **#ci**, **#martin_fowler**  
[Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
""", '005'),
    ("""
    Record-005: **#deployment**, **#architecture**  
[Deployment strategies](https://storage.googleapis.com/cdn.thenewstack.io/media/2017/11/9e09392d-k8s_deployment_strategies.png)
    """, '006'),
    ('some random text \n 54969 foo bar', '000'),
    ('', '000')
]

@pytest.mark.parametrize("input_data, expected_result", get_record_number_params)
def test_get_record_number(input_data, expected_result):
    #when
    actual_result = get_record_number(content=input_data)

    #then
    assert expected_result == actual_result


@patch('adam.github_client.get_blob_sha')
def test_get_blob_info_not_found(get_blob_sha_mock):
    #given
    get_blob_sha_mock.return_value = None
    path = 'foo/bar.md'
    path_first_part = path.split('/')[0]
    tree = Mock()

    #when
    actual_result = find_blob_sha(tree=tree, file_name=path)

    #then
    get_blob_sha_mock.assert_called_once_with(tree=tree, path_part=path_first_part)
    assert actual_result == None

@patch('adam.github_client.get_blob_sha')
def test_get_blob_info_found(get_blob_sha_mock):
    #given
    get_blob_sha_mock.return_value = dummy_sha
    path = 'bar.md'
    path_first_part = path.split('/')[0]
    tree = Mock()

    #when
    actual_result = find_blob_sha(tree=tree, file_name=path)

    #then
    get_blob_sha_mock.assert_called_once_with(tree=tree, path_part=path_first_part)

    assert dummy_sha == actual_result


@patch('adam.github_client.get_tree')
@patch('adam.github_client.get_blob_sha')
def test_get_blob_info_found_second(get_blob_sha_mock, get_tree_mock):
    #given
    get_blob_sha_mock.side_effect = [dummy_sha, dummy_sha]
    path = 'foo/bar.md'
    path_first_part = path.split('/')[0]
    path_second_part = path.split('/')[1]
    first_tree = Mock()
    second_tree = Mock()
    get_tree_mock.return_value = second_tree

    #when
    actual_result = find_blob_sha(tree=first_tree, file_name=path)

    #then
    get_blob_sha_mock_calls = [
        call(tree=first_tree, path_part=path_first_part),
        call(tree=second_tree, path_part=path_second_part)
    ]
    get_blob_sha_mock.assert_has_calls(get_blob_sha_mock_calls)
    get_tree_mock.assert_called_once_with(sha=dummy_sha)

    assert dummy_sha == actual_result

get_blob_sha_parameters = [
    ({"tree": [
        {"sha": dummy_sha,
        "path": "/foo"},
        {"sha": "another_sha",
        "path": "/bar"}
    ]}, "/foo", dummy_sha),
    ({"tree": [
        {"sha": dummy_sha,
        "path": "/bar"}
    ]}, "/foo", None)
]

@pytest.mark.parametrize("input_tree, input_path, expected_result", get_blob_sha_parameters)
def test_get_blob_sha(input_tree, input_path, expected_result):
    #when
    actual_result = get_blob_sha(tree=input_tree, path_part=input_path)

    #then
    assert expected_result == actual_result

get_commit_timestamp_params = [
    (
        {
            "commit":{
                "author": {
                    "date" : dummy_timestamp
                }
            }
        }, dummy_timestamp
    ),
    ( {
            "commit":{
                "committer": {
                    "date" : dummy_timestamp
                }
            }
        }, dummy_timestamp
    ),
    ({"empty": "commit"}, datetime.MINYEAR)
]

@pytest.mark.parametrize("input_data, expected_result", get_commit_timestamp_params)
def test_get_commit_timestamp(input_data, expected_result):
    #when
    actual_result = get_commit_timestamp(commit=input_data)

    #then
    assert expected_result == actual_result

def test_has_author():
    #given
    commit = {
        "sha": "dummy_sha",
        "commit": {
            "author": {
                "date": dummy_timestamp
            }
        }
    }
    #when
    actual_result_positive = has_author(commit=commit)
    actual_result_negative = has_author(commit={"commit": {"foo": "bar"}})

    #then
    assert True == actual_result_positive
    assert False == actual_result_negative

def test_has_commiter():
    #given
    commit = {
        "sha": "dummy_sha",
        "commit": {
            "committer": {
                "date": dummy_timestamp
            }
        }
    }
    #when
    actual_result_positive = has_commiter(commit=commit)
    actual_result_negative = has_commiter(commit={"commit": {"foo": "bar"}})

    #then
    assert True == actual_result_positive
    assert False == actual_result_negative

def test_generate_record():
    #given
    expected_record_without_number = '\n\nRecord-000: **#k8s**, **#mongo**, **#aws**  \n[Modern software desing](www.example.com)'
    expected_record_without_title = '\n\nRecord-042: **#k8s**, **#mongo**, **#aws**  \n[undefined](www.example.com)'
    expected_record_without_tags = '\n\nRecord-042:   \n[Modern software desing](www.example.com)'
    link = 'www.example.com'
    number = '042'
    title = 'Modern software desing'
    tags = ['k8s', 'mongo', 'aws']

    #given
    actual_record_without_number = generate_record(link=link, title=title, tags=tags)
    actual_record_without_title = generate_record(link=link, number=number, tags=tags)
    actual_record_without_tags = generate_record(link=link, number=number, title=title)

    #then
    assert expected_record_without_number == actual_record_without_number
    assert expected_record_without_title == actual_record_without_title
    assert expected_record_without_tags == actual_record_without_tags


#TODO refactor
def test_get_list_commit_url():
    #given
    expected_result = '/repos/None/None/commits'

    #when
    actual_result = get_list_commit_url()

    #then
    assert expected_result == actual_result 


#TODO refactor
def test_get_tree_url():
    #given
    sha = '54cb3f95b913e9e884976532845f31b8a1c62b5c'
    expected_result = '/repos/None/None/git/trees/' + sha
    
    #when
    actual_result = get_tree_url(sha=sha)

    #then
    assert expected_result == actual_result


#TODO refactor
def test_get_blob_url():
    #given
    sha = '54cb3f95b913e9e884976532845f31b8a1c62b5c'
    expected_result = '/repos/None/None/git/blobs/' + sha
    
    #when
    actual_result = get_blob_url(sha=sha)

    #then
    assert expected_result == actual_result


#TODO refactor
def test_create_put_blob_url(monkeypatch):
    #given
    path = 'foo/bar'
    expected_result = '/repos/None/None/contents/foo/bar'
    
    #when
    actual_result = create_put_contents_url(path=path)

    #then
    assert expected_result == actual_result

@patch('adam.github_client.update_contents')
@patch('adam.github_client.get_blob')
@patch('adam.github_client.get_tree')
@patch('adam.github_client.get_commits')
def test_commit_record(get_commits_mock, get_tree_mock, get_blob_mock, update_contents_mock):
    #given
    commits_list = read_test_data(path='test/resources/get_commits_list_response.json')
    get_commits_mock.return_value = commits_list

    tree = read_test_data(path='test/resources/get_tree_response.json')
    get_tree_mock.return_value = tree

    blob = read_test_data(path='test/resources/get_blob_response.json')
    get_blob_mock.return_value = blob

    update_contents_response = read_test_data(path='test/resources/update_contents_response.json')
    update_contents_mock.return_value = update_contents_response

    file_name = 'test_file.MD'
    record = {
        'title': 'dummy title',
        'link': 'http://dymmylink.com',
        'tags': ['testA', 'testB', 'testC']
    }

    expected_result = update_contents_response
    #when
    actual_result = commit_record(file_name=file_name, record=record)

    #then
    assert actual_result == expected_result

parse_record_params = [
    (
        """
        #jit
        #java 
        #compilers
        #title: [How JIT Compilers are Implemented and Fast: Pypy, LuaJIT, Graal and More]
        #gitpath: [dev/dev-links.MD]
        """
        ,
        {
        "title": "How JIT Compilers are Implemented and Fast: Pypy, LuaJIT, Graal and More",
        "link": "undefined",
        "tags": ["jit", "java", "compilers"]
        }
    ),
    ("""
        #jit
        #java 
        #compilers
        #gitpath: [dev/dev-links.MD]
        #link: [https://carolchen.me/blog/jits-impls/]
        """
        ,
        {
        "title": "undefined",
        "link": "https://carolchen.me/blog/jits-impls/",
        "tags": ["jit", "java", "compilers"]
        }
    ),
    ("""
        #title: [How JIT Compilers are Implemented and Fast: Pypy, LuaJIT, Graal and More]
        #gitpath: [dev/dev-links.MD]
        #link: [https://carolchen.me/blog/jits-impls/]
        """
        ,
        {
        "title": "How JIT Compilers are Implemented and Fast: Pypy, LuaJIT, Graal and More",
        "link": "https://carolchen.me/blog/jits-impls/",
        "tags": []
        }
    )
]

@pytest.mark.parametrize("input_data, expected_result", parse_record_params)
def test_parse_record(input_data, expected_result):
    #when
    actual_result = parse_record(input_data)

    #then
    assert expected_result == actual_result


parse_github_params = [
    (
        """
        #jit
        #java 
        #compilers
        #title: [How JIT Compilers are Implemented and Fast: Pypy, LuaJIT, Graal and More]
        #gitpath: [dev/dev-links.MD]
        #link: [https://carolchen.me/blog/jits-impls/]
        """,
        'dev/dev-links.MD'
    ),
    (
        """
        #jit
        #java 
        #compilers
        #title: [How JIT Compilers are Implemented and Fast: Pypy, LuaJIT, Graal and More]
        #link: [https://carolchen.me/blog/jits-impls/]
        """,
        'undefined'
    )
]
@pytest.mark.parametrize("input_data, expected_result", parse_github_params)
def test_parse_github_path(input_data, expected_result):
    #when
    actual_result = parse_github_path(input_data)

    #then
    assert expected_result == actual_result

