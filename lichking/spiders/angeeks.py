# -*- coding: utf-8 -*-
import scrapy
import scrapy
import fileinput
import re
from lichking.util.str_clean import *
from lichking.util.time_util import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging


class AngeeksSpider(scrapy.Spider):
    name = "angeeks"
    allowed_domains = ["angeeks.com"]
    start_urls = ['http://angeeks.com/']
    source_name = '安极论坛'
    source_short = 'angeeks'
    max_reply = 200
    forum_dict = {}

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.5,
    }

    def start_requests(self):
        yield scrapy.Request(
            'http://bbs.angeeks.com/forum.php',
            meta={"page_key": 1},
            callback=self.generate_forum
        )
        # yield scrapy.Request(
        #     'http://bbs.angeeks.com/forum-328-1.html',
        #     meta={"page_key": 1},
        #     callback=self.generate_forum_page_list
        # )

    def generate_forum(self, response):
        forum_list = response.xpath('//td[@class="fl_g"]//dl//dt//a/@href').extract()
        if len(forum_list) > 0:
            for forum_url in forum_list:
                f_url = forum_url
                yield scrapy.Request(
                    f_url,
                    meta={"page_key": 1},
                    callback=self.generate_forum
                )

        # check 是否有下一页
        rep_time_list = response.xpath('//tr/td[@class="by"]/em/a').extract()
        page_key = int(response.meta['page_key'])
        pg_bar = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()
        if page_key == 1 or self.check_rep_date(rep_time_list):
            if len(pg_bar) > 0:
                yield scrapy.Request(
                    pg_bar[0],
                    meta={"page_key": -1},
                    callback=self.generate_forum
                )

            # scrapy all tie url
            thread_list = response.xpath('//a[contains(@class,"xst")]/@href').extract()
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
        forum_item = YAngeeksItem()
        forum_item._id = forum_id
        crawl_next = True
        if len(response.xpath('//a[@class="prev"]').extract()) == 0:
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url
            forum_item.views = StrClean.get_safe_value(response.xpath('//span[@class="xi1"]/text()').extract())
            forum_item.replies = \
                StrClean.get_safe_value(response.xpath('//span[@class="xi1"]/text()').extract(), index=1)
            category1 = StrClean.get_safe_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[2]/text()').extract())
            category2 = StrClean.get_safe_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[3]/text()').extract())
            category3 = StrClean.get_safe_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[4]/text()').extract())
            forum_item.category = category1 + '-' + category2 + '-' + category3

            rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
            forum_item.time = self.format_rep_date(StrClean.get_safe_value(rep_time_list))
            forum_item.title = StrClean.get_safe_value_and_clean(
                response.xpath('//span[@id="thread_subject"]/text()').extract())
            c_soup = BeautifulSoup(StrClean.get_safe_value(response.xpath(
                '//div[@class="pct"]//table[1]').extract()), 'lxml')
            [s.extract() for s in c_soup('script')]  # remove script tag
            forum_item.content = c_soup.get_text()
            forum_item.content = StrClean.clean_comment(forum_item.content)
            forum_item.comment = self.gen_item_comment(response)
            if len(rep_time_list) > 0:
                forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            if int(forum_item.replies) > self.max_reply:
                crawl_next = False

            MongoClient.save_common_forum(forum_item, YAngeeksItem)
        else:
            forum_item.title = ''
            rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
            forum_item.last_reply_time = self.format_rep_date(StrClean.get_safe_value(rep_time_list, index=-1))
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_common_forum(forum_item, YAngeeksItem)

        # 是否有下一页
        if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0 and crawl_next:
            try:
                r_url = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
                yield scrapy.Request(
                    r_url,
                    callback=self.generate_forum_thread
                )
            except:
                logging.error(response.url + ':' + r_url)

    @staticmethod
    def format_rep_date(date_source):
        try:
            date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', date_source).group(0)
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return ''

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
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''

    @staticmethod
    def check_rep_date(rep_time_list):
        try:
            date_source = rep_time_list[0]
            date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2}', date_source).group(0)
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d'))
            date_source = time.strftime('%Y-%m-%d', time.localtime(timestamp))
            if date_source == today or date_source == yestday:
                return True
        except:
            return False
        return False
