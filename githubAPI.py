from ast import Param
from datetime import date
import requests
from unit import *
from time import sleep
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

GITHUB_API = 'https://api.github.com'
GITHUB_SEARCH_API = 'https://api.github.com/search/code'

USERNAMES = [config['Account']['userid'], config['Account']['userid_sub']]
TOKENS    = [config['Account']['token'], config['Account']['token_sub']]

USERIDX = 0
USERNAME = USERNAMES[USERIDX]
TOKEN = TOKENS[USERIDX]


'''
The Search API has a custom rate limit. For requests using Basic Authentication, 
OAuth, or client ID and secret, you can make up to 30 requests per minute. 
For unauthenticated requests, the rate limit allows you to make up to 10 requests per minute.
'''
config = ConfigParser()
config.read('config.ini')


def switchUser():
    global USERIDX, USERNAME, TOKEN
    USERIDX = 1-USERIDX
    USERNAME = USERNAMES[USERIDX]
    TOKEN = TOKENS[USERIDX]


def reqGet(url: str, params: dict = None):
    """
    request GET Method to github api, avoiding secondary rate limit
    https://docs.github.com/en/rest/overview/resources-in-the-rest-api#secondary-rate-limits
    """
    while 1:
        try:
            checkAPILimit()
            req = requests.get(url, params=params, auth=(USERNAME, TOKEN))
            data = req.json()
            if not 'message' in data.keys() and not 'documentation_url' in data.keys():
                break
            # due to secondary limit, you should take a break
            sleep(30)
        except:
            logger('retry...')
            sleep(5)
    return data


'''
https://docs.github.com/en/rest/reference/search
'''
def getSearchPageByCode(query, pageNo: int = 1) -> dict:
    """
    Get json request from github code search api. see github-api.example.json
    reference:
        https://docs.github.com/en/rest/reference/search
        https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-code
    The Search API has a custom rate limit.
    For requests using Basic Authentication, OAuth, or client ID and secret,
    you can make up to 30 requests per minute.
    For unauthenticated requests, the rate limit allows you to make up to 10 requests per minute.
    See the rate limit documentation for details on determining your current rate limit status.
    """
    res = reqGet(GITHUB_API + '/search/code', params={'q': query,
                                                  'per_page': 100,
                                                  'page': pageNo})
    return res

def checkAPILimit():
    while isLimitReach():
        logger("API LIMIT! Switch users")
        switchUser()
        logger(f"NOW USER:{USER}")
        sleep(5)
        logger("Work time!")


def isLimitReach() -> bool:
    data = getRateLimit()["resources"]
    core = data["core"]["remaining"]
    search = data["search"]["remaining"]
    coreReset = datetime.fromtimestamp(int(data["core"]["reset"])).time().isoformat()
    searchReset = datetime.fromtimestamp(int(data["search"]["reset"])).time().isoformat()
    logger(f"Remaining: core={core} by coreReset={coreReset}, search: searh={search} by search={searchReset}")
    return core < 100 or search == 0


#https://docs.github.com/en/rest/reference/rate-limit
def getRateLimit() -> dict:
    data = {}
    while True:
        try:
            res = requests.get(GITHUB_API+'/rate_limit',auth=(USERNAME, TOKEN))
            data = res.json()   
            break
        except:
            logger('request rate_limitretry...')
            sleep(3)
            continue
    return data
