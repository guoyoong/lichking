# -*- coding: utf-8 -*-
import scrapy
import logging


class AngeeksTestSpider(scrapy.Spider):
    name = "angeeks_test"
    allowed_domains = ["angeeks.com"]
    start_urls = ['http://angeeks.com/']
    source_name = '安极论坛'
    source_short = 'angeeks'
    all_thread = 0
    max_reply = 6000
    forum_dict = {}

    custom_settings = {
        'COOKIES_ENABLED': False,
        # 是否追踪referer
        'REFERER_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
        'DOWNLOADER_MIDDLEWARES': {
            'lichking.middlewares.RandomUserAgent_pc': 1,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
    }

    def start_requests(self):
        yield scrapy.Request(
            'http://bbs.angeeks.com/forum.php',
            callback=self.generate_forum
        )

    def generate_forum(self, response):
        forum_list = response.xpath('//td[@class="fl_g"]//dl//dt//a/@href').extract()
        t_sum = response.xpath('//h1[@class="xs2"]//strong[@class="xi1"]/text()').extract()
        if len(t_sum) > 0:
            self.all_thread += int(t_sum[1])
            logging.error(self.all_thread)
        if len(forum_list) > 0:
            for forum_url in forum_list:
                f_url = forum_url
                if forum_url.find('angeeks.com') == -1:
                    f_url = 'http://bbs.angeeks.com/' + forum_url
                yield scrapy.Request(
                    f_url,
                    callback=self.generate_forum
                )

