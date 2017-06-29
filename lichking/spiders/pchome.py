# -*- coding: utf-8 -*-

import scrapy
import re
from lichking.util.str_clean import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging
import json


class PchomeSpider(scrapy.Spider):
    name = "pchome"
    start_urls = ['http://www.pchome.net/']
    source_name = '电脑之家'
    source_short = 'pchome'
    max_reply = 400

    custom_settings = {
        'COOKIES_ENABLED': False,
        # 是否追踪referer
        'REFERER_ENABLED': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 2,
        'DOWNLOAD_DELAY': 0.5,
    }

    def __init__(self):
        print 123

    def start_requests(self):
        return [scrapy.http.FormRequest(url="http://10.100.124.226:9200/test/test/_bulk",
                            formdata={'': 'John Doe'},
                            callback=self.after_post)]

