# -*- coding: utf-8 -*-
import scrapy
import fileinput
import re
from lichking.util.str_clean import *
from lichking.util.time_util import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging


class HiapkSpider(scrapy.Spider):
    name = "hiapk"
    allowed_domains = ["hiapk.com"]
    start_urls = ['http://bbs.hiapk.com/']
    forum_list_file = 'hiapk_forum_list_file'
    source_name = '安卓论坛'
    source_short = 'hiapk'

    custom_settings = {
        'COOKIES_ENABLED': False,
        # 是否追踪referer
        'REFERER_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.1,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
    }

    def generate_forum_start_requests(self):
        yield scrapy.Request(
            'http://bbs.hiapk.com/',
            callback=self.generate_forum
        )

    def generate_forum(self, response):
        forum_list = response.xpath('//td[@class="fl_g"]//dl//dt//a/@href').extract()
        if len(forum_list) > 0:
            all_url = ''
            for forum_url in forum_list:
                all_url += 'http://bbs.hiapk.com/' + forum_url + '\n'
            with open(self.forum_list_file, 'a') as f:
                f.write(all_url)

    def start_requests(self):
        # enter forum
        for line in fileinput.input(self.forum_list_file):
            if not line:
                break
            if line.find('#') == -1 and line.strip() != '':
                yield scrapy.Request(
                    line.strip(),
                    dont_filter='true',
                    callback=self.generate_forum_page_list
                )

    def generate_forum_page_list(self, response):
        # scrapy all tie url
        thread_list = response.xpath('//a[@class="xst"]/@href').extract()
        hiapk_url_pre = response.url.split('forum')[0]
        logging.error(response.url)
        logging.error(len(thread_list))
        if len(thread_list) > 0:
            for thread_url in thread_list:
                yield scrapy.Request(
                    hiapk_url_pre + thread_url,
                    callback=self.generate_forum_thread
                )
        # check 是否有下一页
        pg_bar = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()
        if len(pg_bar) > 0:
            yield scrapy.Request(
                hiapk_url_pre + pg_bar[0],
                callback=self.generate_forum_page_list
            )

    def generate_forum_thread(self, response):
        forum_id = re.search(u'thread-([\d]+)', response.url)
        try:
            forum_id = forum_id.group(1)
        except:
            forum_id = ''
        forum_item = YHiapkItem()
        forum_item._id = forum_id
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
            forum_item.category = category1 + '-' + category2 + '-' + category3

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
            forum_item.last_rep_time = self.format_rep_date(rep_time_list[-1])
            MongoClient.save_hiapk_forum(forum_item)
        else:
            forum_item.title = ''
            rep_time_list = response.xpath('//div[@class="authi"]//em/text()').extract()
            forum_item.last_rep_time = self.format_rep_date(rep_time_list[-1])
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_hiapk_forum(forum_item)

        # 是否有下一页
        if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0:
            it168_url_pre = response.url.split('thread')[0]
            r_url = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
            yield scrapy.Request(
                it168_url_pre + r_url,
                dont_filter='true',
                callback=self.generate_forum_thread
            )

    @staticmethod
    def format_rep_date(date_source):
        logging.log(logging.ERROR, date_source)
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def gen_item_comment(response):
        comment = []
        new_comment = []
        for indexi, content in enumerate(response.xpath('//div[@class="t_fsz"]//table[1]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            [s.extract() for s in soup('script')]  # remove script tag
            c = StrClean.clean_comment(soup.get_text())
            if c != '':
                new_comment.append(c)
        new_comment.append(response.url)
        comment.append(new_comment)
        return comment

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''
