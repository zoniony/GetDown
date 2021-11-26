from githubAPI import *
import wget
import os

TILETYPE = config['File']['filetype']
CRAWLED_PAGE = 0
Query = "extension:otf size:<1000000 "
PATH = "/Users/zoniony/CVE/otf/in"


def crawPagt(Query: str, page: int) -> bool:
    pagefile = getSearchPageByCode(Query, page)
    logger(f"now crawing page #{page}")
    for file in pagefile['items']:
        name = file['name']
        html_url = file['html_url']
        wget.download(url=html_url,out=os.path.join(PATH, name))
        logger(f"oh! create{name}")


def start():
    global CRAWLED_PAGE 
    logger("start crawling~")
    page = getSearchPageByCode(Query)
    result = page['total_count']
    if not result:
        logger("No result!")
    else:
        while CRAWLED_PAGE < result // 100:
            pageToCrawl = CRAWLED_PAGE + 1
            crawPagt(Query, pageToCrawl)
            pageToCrawl += 1
            sleep(5)


if __name__ == '__main__':
    start()