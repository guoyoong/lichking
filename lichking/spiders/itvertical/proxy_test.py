# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
import json
from bs4 import BeautifulSoup
from lichking.util.str_clean import *
from lxml import etree
import logging


class IfanrSpider(scrapy.Spider):
    name = "proxy_test"
    allowed_domains = ["api.ipify.org"]
    start_urls = ['api.ipify.org']
    source_short = "proxy_test"

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 1.0,
        'DEFAULT_REQUEST_HEADERS': {
            'user-agent':
                'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
        }
    }

    def __init__(self):
        source_name = "proxy_test"

    # scrapy start and check page num
    def start_requests(self):
        yield scrapy.Request(
            "http://api.ipify.org/",
            meta={"proxy": MongoClient.get_random_proxy()},
            callback=self.generate_article_url
        )

    def generate_article_url(self, response):
        logging.error(response.body)


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl proxy_test'.split())
