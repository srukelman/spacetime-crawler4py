from threading import Thread

from inspect import getsource
from utils.download import download
from utils import get_logger, get_urlhash
from urllib.parse import urlparse
import json
import os
import scraper
import time
from scraper import update_report


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
        self.page_count = 0
        self.page_count_file = "page_count-test.json"
        self.checksum_set = set()
        self.checksum_file = "checksum-test.json"
        if not os._exists(self.subdomains_file):
            with open(self.subdomains_file, 'w') as f:
                json.dump({}, f)
        else:
            with open(self.subdomains_file, 'r') as f:
                self.subdomains = json.load(f)
        if not os.path.exists(self.page_count_file):
            with open(self.page_count_file, 'w') as f:
                json.dump(0, f)
        else:
            with open(self.page_count_file, 'r') as f:
                self.page_count = json.load(f)
        if not os.path.exists(self.checksum_file):
            with open(self.checksum_file, 'w') as f:
                json.dump(list(), f)
        else:
            with open(self.checksum_file, 'r') as f:
                self.checksum_set = set(json.load(f))
        super().__init__(daemon=True)
        
    def run(self):
        max_page_length = 0
        max_page_url = ''
        try:
            while True:
                tbd_url = self.frontier.get_tbd_url()
                if not tbd_url:
                    update_report()
                    self.logger.info("Frontier is empty. Stopping Crawler.")
                    break
                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                if resp.status >= 400:
                    self.frontier.mark_url_complete(tbd_url)
                    time.sleep(self.config.time_delay)
                    continue
                n = len(self.checksum_set)
                scraped_urls, length = scraper.scraper(tbd_url, resp, self.checksum_set)
                if length > max_page_length:
                    max_page_url = tbd_url
                    max_page_length = length
                if resp.status == 200 and n != len(self.checksum_set):
                    subdomain = urlparse(tbd_url).netloc
                    self.subdomains[subdomain] = 1 + self.subdomains.get(subdomain, 0)
                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
                self.frontier.mark_url_complete(tbd_url)
                time.sleep(self.config.time_delay)
        finally:
            with open(self.subdomains_file, 'w') as f:
                json.dump(self.subdomains, f)
            update_report()
        print(f'Longest Page: {max_page_url} with {max_page_length}')
