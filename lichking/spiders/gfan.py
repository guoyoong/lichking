# -*- coding: utf-8 -*-
import scrapy
import re
from lichking.util.str_clean import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging


class GfanSpider(scrapy.Spider):
    name = 'gfan'
    allowed_domains = ['gfan.com']
    start_urls = ['http://bbs.gfan.com/forum.php']
    source_name = '机锋论坛'
    source_short = 'gfan_forum'
    max_reply = 6000
    forum_dict = {}

    custom_settings = {
        'COOKIES_ENABLED': False,
        # 是否追踪referer
        'REFERER_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.1,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
        'DOWNLOADER_MIDDLEWARES': {
            'lichking.middlewares.RandomUserAgent_pc': 1,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
    }

    def __init__(self):
        print 123

    def start_requests(self):
        # get into the bbs
        yield scrapy.Request(
            self.start_urls[0],
            callback=self.generate_forum_list
        )
        # yield scrapy.Request(
        #     'http://bbs.gfan.com/forum-1686-1.html',
        #     callback=self.generate_forum_page_list
        # )

    def generate_forum_list(self, response):
        forum_list = re.findall(u'http://bbs.gfan.com/forum-[\d]+-1.html', response.body)
        for forum_url in forum_list:
            if forum_url in self.forum_dict:
                self.forum_dict[forum_url] += 1
            else:
                logging.error(forum_url)
                self.forum_dict[forum_url] = 1
                yield scrapy.Request(
                    forum_url,
                    dont_filter='true',
                    callback=self.generate_forum_list
                )

                yield scrapy.Request(
                    forum_url,
                    dont_filter='true',
                    callback=self.generate_forum_page_list
                )

    def generate_forum_page_list(self, response):
        pg_bar = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()
        if len(pg_bar) > 0:
            yield scrapy.Request(
                pg_bar[0],
                dont_filter='true',
                callback=self.generate_forum_page_list
            )

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
        forum_item = YGfanForumItem()
        forum_id = re.search(u'android-([\d]+)', response.url)
        try:
            forum_id = forum_id.group(1)
        except:
            forum_id = re.search(u'tid=([\d]+)', response.url).group(1)
        forum_item._id = forum_id
        crawl_next = True
        rep_time_list = response.xpath('//div[@class="authi"]//em/text()').extract()
        if len(response.xpath('//span[@class="xi1"]/text()').extract()) != 0:
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url
            forum_item.views = StrClean.clean_comment(response.xpath('//span[@class="xi1"]/text()').extract()[0])
            forum_item.replies = \
                StrClean.clean_comment(response.xpath('//span[@class="xi1"]/text()').extract()[1])
            forum_item.category = ''
            for i in range(len(response.xpath('//div[@id="pt"]/div[@class="z"]/a/text()').extract())-1):
                forum_item.category = forum_item.category + '-' + response.xpath('//div[@id="pt"]/div[@class="z"]/a/text()').extract()[i]
            forum_item.time = self.format_rep_date(rep_time_list[0])
            forum_item.title = StrClean.clean_comment(response.xpath('//a[@id="thread_subject"]/text()').extract()[0])
            if len(response.xpath('//td[@class="t_f"]').extract()) != 0:
                c_soup = BeautifulSoup(response.xpath('//td[@class="t_f"]').extract()[0],'lxml')
                if c_soup.find('div', class_='attach_nopermission') is not None:
                    c_soup.find('div', class_='attach_nopermission').clear()
                [s.extract() for s in c_soup('script')]
                forum_item.content = StrClean.clean_comment(c_soup.get_text())
                forum_item.comment = self.gen_item_comment(response)
                forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])

            if int(forum_item.replies) > self.max_reply:
                crawl_next = False
            MongoClient.save_gfan_forum(forum_item)

        else:
            forum_item.title = ''
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_gfan_forum(forum_item)

        if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0 and crawl_next:
            next_page = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
            logging.error(next_page)
            yield scrapy.Request(
                next_page,
                callback=self.generate_forum_thread
            )

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def gen_item_comment(self, response):
        comment = []
        new_comment = {}
        comments_data = []
        rep_time_list = response.xpath('//div[@class="authi"]//em/text()').extract()
        for indexi, content in enumerate(response.xpath('//td[@class="t_f"]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            if soup.find('div', class_='attach_nopermission') is not None:
                soup.find('div', class_='attach_nopermission').clear()
            [s.extract() for s in soup('script')]  # remove script tag
            c = StrClean.clean_unicode(soup.get_text())
            comments_data.append({'content': c, 'reply_time': self.format_rep_date(rep_time_list[indexi])})
        new_comment['url'] = response.url
        new_comment['comments_data'] = comments_data
        comment.append(new_comment)
        return comment
