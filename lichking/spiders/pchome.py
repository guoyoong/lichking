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
        # get into the bbs
        for forum_group in self.start_urls:
            yield scrapy.Request(
                forum_group,
                meta={"page_key": 1},
                callback=self.generate_forum_list
            )
        # yield scrapy.Request(
        #     'http://itbbs.pconline.com.cn/mobile/f769405.html',
        #     meta={"page_key": 1},
        #     callback=self.generate_forum_list
        # )

