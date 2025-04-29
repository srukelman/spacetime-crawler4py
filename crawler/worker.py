from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger, get_urlhash
from urllib.parse import urlparse
import json
import os
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        self.subdomains = {}
        self.subdomains_file = "subdomains-test.json"
        if not os._exists(self.subdomains_file):
            with open(self.subdomains_file, 'w') as f:
                json.dump({}, f)
        else:
            with open(self.subdomains_file, 'r') as f:
                self.subdomains = json.load(f)
        super().__init__(daemon=True)
        
    def run(self):
        max_page_length = 0
        max_page_url = ''
        try:
            while True:
                tbd_url = self.frontier.get_tbd_url()
                if not tbd_url:
                    self.logger.info("Frontier is empty. Stopping Crawler.")
                    break
                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                scraped_urls, length = scraper.scraper(tbd_url, resp)
                if length > max_page_length:
                    max_page_url = tbd_url
                    max_page_length = length
                subdomain = urlparse(tbd_url).netloc
                self.subdomains[subdomain] = 1 + self.subdomains.get(subdomain, 0)
                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
                self.frontier.mark_url_complete(tbd_url)
                time.sleep(self.config.time_delay)
        finally:
            with open(self.subdomains_file, 'w') as f:
                json.dump(self.subdomains, f)
        print(f'Longest Page: {max_page_url} with {max_page_length}')
