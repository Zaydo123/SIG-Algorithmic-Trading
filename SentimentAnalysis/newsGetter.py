from concurrent.futures import ThreadPoolExecutor
from typing import List, Set, Union
from time import time
import feedparser
import logging
import os

# Set the log level to DEBUG if the environment is not production
log_level = logging.DEBUG if "prod" not in (os.getenv('ENVIRONMENT') or "").lower() else logging.INFO
logging.basicConfig(level=log_level)

MAX_WORKERS = 10 # Number of threads to use for parsing feeds

"""
    Wrapper function to measure the execution time of a function
"""
def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        logging.debug(f"Execution time for {func.__name__}: {round(end - start, 2)} seconds")
        return result
    return wrapper

"""
    RSS Feed class
"""
class RSSFeed:

    def __init__(self, url, **kwargs):
        self.url: str = url
        self.last_fetched: float = 0
        self.tags: List[str] = kwargs.get('tags', [])
        
    """
        Parse the feed and return a dictionary with the requested fields
    """
    def parse(self, select_fields: List[str] = None) -> Union[dict, None]:
        feed = feedparser.parse(self.url)
        
        if feed.bozo:
            logging.error(f"Malformed feed: {feed.bozo_exception} : {self.url}")
            return {}

        self.last_fetched = time()
        
        # BFS to select only the required fields
        if select_fields:
            def bfs(node, fields):
                result = {}
                for field in fields:
                    if field in node:
                        result[field] = node[field]
                if 'entries' in node:
                    result['entries'] = []
                    for entry in node['entries']:
                        result['entries'].append(bfs(entry, fields))
                return result
            return bfs(feed, select_fields)
        
        return feed
    
    def __str__(self):
        return f"RSSFeed({self.url}, {self.tags}, {self.last_fetched})"
    
    def __repr__(self):
        return self.__str__()
    
"""
    Class to store a library of RSS feeds
"""
class FeedLibrary:

    def __init__(self):
        self.feeds = []
    
    def add_feed(self, feed: RSSFeed) -> None:
        self.feeds.append(feed)
    
    def remove_feed(self, feed: Union[RSSFeed, str]) -> None:
        if isinstance(feed, str):
            self.feeds = [f for f in self.feeds if f.url != feed]  # More Pythonic
        else:
            try:
                self.feeds.remove(feed)
            except ValueError:
                logging.warning(f"Feed {feed} not found in the library.")

    def list_feeds(self) -> List[RSSFeed]:
        return self.feeds

    def get_all_tags(self) -> Set[str]:
        tags = set()
        for feed in self.feeds:
            tags.update(feed.tags)
        return tags

    @measure_execution_time
    def parse_all_feeds(self, fields=None):
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            results = list(executor.map(lambda feed: feed.parse(fields), self.feeds))
        # Filter out None values
        return [res for res in results if res]


if __name__ == '__main__':
    import json

    test_library = FeedLibrary()

    test_library.add_feed(RSSFeed('http://abcnews.go.com/abcnews/usheadlines', tags=['news', 'us']))

    with open('_feeds.json', 'w+') as f:
        parsed_list = test_library.parse_all_feeds(fields=['title', 'link', 'published', 'summary'])
        json.dump(parsed_list, f, indent=4)

    print(test_library.list_feeds())
    print(test_library.get_all_tags())