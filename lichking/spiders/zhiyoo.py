# -*- coding: utf-8 -*-
import scrapy
import fileinput
import re
from lichking.util.str_clean import *
from lichking.util.time_util import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging


class ZhiyooSpider(scrapy.Spider):
    name = "zhiyoo"
    allowed_domains = ["zhiyoo.com"]
    start_urls = ['http://zhiyoo.com/']
    source_name = '安智智友论坛'
    source_short = 'zhiyoo'
    forum_arr = [2044, 1822, 82, 71, 55, 201, 1692, 204, 659, 843, 1958, 707, 4]
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
        'DOWNLOAD_DELAY': 0.2,
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
            'http://bbs.zhiyoo.com/',
            callback=self.generate_forum
        )
        for index in self.forum_arr:
            yield scrapy.Request(
                'http://bbs.zhiyoo.com/source/module/forum/tab_ajax.php?index=nav_' + str(index),
                callback=self.generate_forum
            )
        # yield scrapy.Request(
        #     'http://bbs.zhiyoo.com/forum-401-1.html',
        #     callback=self.generate_forum_page_list
        # )

    def generate_forum(self, response):
        forum_list = response.xpath('//td[@class="fl_g"]//dl//dt//a/@href').extract()
        if len(forum_list) > 0:
            for forum_url in forum_list:
                f_url = forum_url
                if forum_url.find('bbs.zhiyoo.com') == -1:
                    f_url = 'http://bbs.zhiyoo.com/' + forum_url
                yield scrapy.Request(
                    f_url,
                    callback=self.generate_forum
                )

                if f_url in self.forum_dict:
                    self.forum_dict[forum_url] += 1
                else:
                    self.forum_dict[f_url] = 1
                    yield scrapy.Request(
                        f_url,
                        dont_filter='true',
                        callback=self.generate_forum_page_list
                    )

    def generate_forum_page_list(self, response):
        # check 是否有下一页
        pg_bar = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()
        if len(pg_bar) > 0:
            yield scrapy.Request(
                pg_bar[0],
                callback=self.generate_forum_page_list
            )

        # scrapy all tie url
        thread_list = response.xpath('//a[@class="xst"]/@href').extract()
        logging.error(response.url)
        logging.error(len(thread_list))
        if len(thread_list) > 0:
            for thread_url in thread_list:
                yield scrapy.Request(
                    thread_url,
                    callback=self.generate_forum_thread
                )

    def generate_forum_thread(self, response):
        forum_id = re.search(u'thread-([\d]+)', response.url)
        try:
            forum_id = forum_id.group(1)
        except:
            forum_id = re.search(u'tid=([\d]+)', response.url).group(1)
        forum_item = YZhiyooItem()
        forum_item._id = forum_id
        crawl_next = True
        if len(response.xpath('//span[@class="xi1"]/text()').extract()) > 1:
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url
            forum_item.views = StrClean.clean_comment(response.xpath('//span[@class="xi1"]/text()').extract()[0])
            forum_item.replies = \
                StrClean.clean_comment(response.xpath('//span[@class="xi1"]/text()').extract()[1])
            category1 = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[2]/text()').extract())
            category2 = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[3]/text()').extract())
            category3 = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[4]/text()').extract())
            category4 = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[5]/text()').extract())
            forum_item.category = category1 + '-' + category2 + '-' + category3 + '-' + category4

            rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
            forum_item.time = self.format_rep_date(rep_time_list[0])
            forum_item.title = StrClean.clean_comment(
                response.xpath('//a[@id="thread_subject"]/text()').extract()[0])
            c_soup = BeautifulSoup(response.xpath(
                '//div[@class="pct"]//table[1]').extract()[0], 'lxml')
            [s.extract() for s in c_soup('script')]  # remove script tag
            forum_item.content = c_soup.get_text()
            forum_item.content = StrClean.clean_comment(forum_item.content)
            forum_item.comment = self.gen_item_comment(response)
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            if int(forum_item.replies) > self.max_reply:
                crawl_next = False

            MongoClient.save_zhiyoo_forum(forum_item)
        else:
            forum_item.title = ''
            rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_zhiyoo_forum(forum_item)

        # 是否有下一页
        if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0 and crawl_next:
            r_url = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
            yield scrapy.Request(
                r_url,
                callback=self.generate_forum_thread
            )

    def gen_item_comment(self, response):
        comment = []
        new_comment = {}
        comments_data = []
        rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
        for indexi, content in enumerate(response.xpath('//div[@class="t_fsz"]//table[1]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            [s.extract() for s in soup('script')]  # remove script tag
            c = StrClean.clean_comment(soup.get_text())
            if indexi >= len(rep_time_list):
                rep_time = self.format_rep_date(rep_time_list[-1])
            else:
                rep_time = self.format_rep_date(rep_time_list[indexi])
            comments_data.append({'content': c, 'reply_time': rep_time})
        new_comment['url'] = response.url
        new_comment['comments_data'] = comments_data
        comment.append(new_comment)
        return comment

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''
