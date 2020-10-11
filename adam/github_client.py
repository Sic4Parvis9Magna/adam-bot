import http.client as client
import adam.github_api_constants as HUB_API
import json
import datetime
import base64
import re
from os import getenv
# TODO refactor imports

GIT_REPO = getenv("GIT_REPO")
GIT_USER = getenv("GIT_USER")
GIT_AUTH = getenv("GIT_AUTH")

RESERVED_TAGS = ['title', 'link', 'gitpath']


def get_commits() -> list:
    url = get_list_commit_url()
    return make_rest_call(url=url, method=HUB_API.HTTP_GET)


def get_tree(sha: str) -> dict:
    url = get_tree_url(sha=sha)
    return make_rest_call(url=url, method=HUB_API.HTTP_GET)


def get_blob(sha: str) -> dict:
    url = get_blob_url(sha=sha)
    return make_rest_call(url=url, method=HUB_API.HTTP_GET)


def update_contents(body:dict, path:str) -> dict:
    conn = client.HTTPSConnection(HUB_API.BASE_URL)
    url = create_put_contents_url(path=path)
    
    headers = {
    HUB_API.USER_AGENT: HUB_API.DUMMY_AGENT,
    HUB_API.AUTHORIZATION: GIT_AUTH}

    json_body = json.dumps(body)
    bytes_body = bytes(json_body,encoding='utf-8')
    conn.request(method='PUT', url=url, headers=headers, body=bytes_body)

    response = conn.getresponse()
    raw_res = response.read()
    conn.close()
    json_res = json.loads(raw_res)
    return json_res


def get_blob_content(blob: dict) -> str:
    return base64.b64decode(bytes(blob["content"], "utf-8")).decode('utf-8')


def make_rest_call(url: str, method: str):
    conn = client.HTTPSConnection(HUB_API.BASE_URL)
    conn.request(method=method, url=url, headers={
                 HUB_API.USER_AGENT: HUB_API.DUMMY_AGENT})
    response = conn.getresponse()
    raw_res = response.read()
    conn.close()
    json_res = json.loads(raw_res)
    return json_res


def get_latest_commit_sha(commits: list) -> str:
    latest_sha = None
    latest_date = None
    for commit in commits:

        commit_timestamp = get_commit_timestamp(commit)
        commit_date = datetime.datetime.strptime(
            commit_timestamp, HUB_API.TIME_FORMAT)
        commit_sha = commit["sha"]

        if not latest_date:
            latest_date = commit_date
            latest_sha = commit_sha
            continue
        elif latest_date < commit_date:
            latest_date = commit_date
            latest_sha = commit_sha

    return latest_sha


def get_record_number(content: str) -> str:
    p = re.compile(r'Record-(\d{3})', re.MULTILINE)
    find_items = p.findall(content)

    if len(find_items) == 0:
        return '000'
    else:
        last_number = '000'
        for find_item in find_items:
            if last_number < find_item:
                last_number = find_item

        return get_next_int(last_number)


def get_next_int(str_number: str) -> str:
    previous_val = int(str_number)
    if previous_val < 0:
        return '000'
    next_number = previous_val + 1
    if next_number < 10:
        return f'00{next_number}'
    if next_number < 100:
        return f'0{next_number}'
    else:
        return str(next_number)


def find_blob_sha(tree: dict, file_name: str) -> dict:
    compound_path = file_name.split("/")
    file_path = compound_path[len(compound_path) - 1]

    current_tree = tree
    for path_part in compound_path:
        sha = get_blob_sha(tree=current_tree, path_part=path_part)
        if sha:
            if path_part == compound_path[len(compound_path) - 1]:
                return sha
            else:
                current_tree = get_tree(sha=sha)
        else:
            return None
    


def get_blob_sha(tree: dict, path_part: str) -> str:
    for blob_item in tree["tree"]:
        if path_part in blob_item["path"]:
            return blob_item["sha"]

    return None

def get_commit_timestamp(commit: dict):
    if has_author(commit):
        return commit["commit"]["author"]["date"]
    if has_commiter(commit):
        return commit["commit"]["committer"]["date"]
    else:
        return datetime.MINYEAR


def has_author(commit: dict) -> bool:
    try:
        commit["commit"]["author"]["date"]
        return True
    except KeyError:
        return False


def has_commiter(commit: dict) -> bool:
    try:
        commit["commit"]["committer"]["date"]
        return True
    except KeyError:
        return False


def generate_record(link, number="000", title="undefined", tags=[]) -> str:
    formatted_tags = [f"**#{tag}**"for tag in tags]
    joined_tags = ", ".join(formatted_tags)

    return f"\n\nRecord-{number}: {joined_tags}  \n[{title}]({link})"


def get_list_commit_url() -> str:
    return HUB_API.LIST_COMMITS.format(user=GIT_USER, repo=GIT_REPO)


def get_tree_url(sha: str) -> str:
    return HUB_API.GET_TREE_BY_SHA.format(sha=sha, user=GIT_USER, repo=GIT_REPO)


def get_blob_url(sha: str) -> str:
    return HUB_API.GET_BLOB_BY_SHA.format(sha=sha, user=GIT_USER, repo=GIT_REPO)


def create_put_contents_url(path: str) -> str:
    return HUB_API.PUT_BLOB.format(user=GIT_USER, repo=GIT_REPO, path=path)


def commit_record(file_name: str, record: dict) -> dict:
    commits = get_commits()
    sha = get_latest_commit_sha(commits=commits)
    tree = get_tree(sha=sha)
    blob_sha = find_blob_sha(tree=tree, file_name=file_name)
    blob = get_blob(sha=blob_sha)
    blob_content = get_blob_content(blob)
    
    record_number = get_record_number(blob_content)
    title = record["title"]
    record = generate_record(link=record["link"], number=record_number,
                          title=title, tags=record["tags"])

    updated_content = blob_content + record
    b64_content = base64.b64encode(bytes(updated_content, "utf-8")).decode('utf-8')
    body = {
        "message": f"add a new record with the title '{title}'",
        "sha": blob_sha,
        "content": b64_content
    } 
    
    result = update_contents(body=body, path=file_name)
    return result

def parse_record(text:str) -> dict:
    res_link = None
    res_tags = []

    p_title = re.compile(r'title:\s?\[([^[]+)\]') 
    m_title = p_title.findall(text)
    res_title = m_title[0] if m_title  else 'undefined'  

    p_link = re.compile(r'link:\s?\[([^[]+)\]') 
    m_link = p_link.findall(text)
    res_link = m_link[0] if m_link  else 'undefined'  

    p_tags = re.compile(r'#(\w+)') 
    m_tags = p_tags.findall(text)
    all_tags = m_tags if m_tags  else []  

    res_tags = filterout_reserved_tags(all_tags)

    return {
        "title": res_title,
        "link": res_link,
        "tags": res_tags
    }


def parse_github_path(text: str) -> str:
    p_title = re.compile(r'#gitpath:\s?\[([^[]+)\]') 
    m_title = p_title.findall(text)
    
    return m_title[0] if m_title  else 'undefined'




def filterout_reserved_tags(tags_list:list) -> list:
    result = []
    for item in tags_list:
        if item not in RESERVED_TAGS:
            result.append(item) 
    
    return result
