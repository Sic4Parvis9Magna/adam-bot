BASE_URL = "api.github.com"
USER_AGENT = "User-Agent"
DUMMY_AGENT = "dymmy_agent"
AUTHORIZATION = "Authorization"

HTTP_GET = "GET"

TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

BASE_REPO_PREFIX  = "/repos/{user}/{repo}" 
LIST_COMMITS =  BASE_REPO_PREFIX + "/commits"
GET_TREE_BY_SHA = BASE_REPO_PREFIX + "/git/trees/{sha}"
GET_BLOB_BY_SHA = BASE_REPO_PREFIX + "/git/blobs/{sha}"
PUT_BLOB = BASE_REPO_PREFIX + "/contents/{path}"