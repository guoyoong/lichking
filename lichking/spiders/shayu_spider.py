# -*- coding: utf-8 -*-
import scrapy
# import fileinput
import re
from lichking.util.str_clean import *
from lichking.util.time_util import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging


class Shayu_Spider(scrapy.Spider):
    name = "shayu"
    allowed_domains = ["18095.com"]
    start_urls = ['http://www.18095.com/forum.php']
    source_name = '鲨鱼手机论坛'
    source_short = 'shayu_forum'
    forum_dict = {}

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.1,
        'AUTOTHROTTLE_MAX_DELAY': 0.3,
        'DOWNLOAD_DELAY': 0.3,
    }

    def start_requests(self):
        # get into the bbs
        yield scrapy.Request(
            self.start_urls[0],
            meta={"page_key": 1},
            callback=self.generate_forum_list
        )
        # yield scrapy.Request(
        #     'http://www.18095.com/forum-81-1.html',
        #     dont_filter='true',
        #     callback=self.generate_forum_page_list
        # )

    def generate_forum_list(self, response):
        forum_list = response.xpath('//a/@href').extract()
        if len(forum_list) > 0:
            for forum_url in forum_list:
                url = re.search(u'http://www.18095.com/forum-\d{1,10}-1.html', forum_url)
                if url is not None:
                    yield scrapy.Request(
                        forum_url,
                        meta={"page_key": 1},
                        callback=self.generate_forum_list
                    )

        page_key = int(response.meta['page_key'])
        rep_time_list = response.xpath('//tr/td[@class="by"]/em/a').extract()
        if len(response.xpath('//span[@id="fd_page_bottom"]//a[@class="nxt"]/@href').extract()) != 0:
            if page_key == 1 or self.check_rep_date(rep_time_list):
                nxt_page = \
                    response.xpath('//span[@id="fd_page_bottom"]//a[@class="nxt"]/@href').extract()[0]
                yield scrapy.Request(
                    nxt_page,
                    meta={"page_key": -1},
                    callback=self.generate_forum_list
                )

                thread_list = response.xpath('//a[contains(@class,"xst")]/@href').extract()
                if len(thread_list) > 0:
                    logging.error(len(thread_list))
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
        forum_item = YShayuForumItem()
        forum_item._id = forum_id
        forum_item.v = '0.1'
        rep_time_list = response.xpath('//td[@class="plc"]//div[@class="authi"]/em').extract()
        if len(response.xpath('//a[@class="prev"]').extract()) == 0:
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url
            forum_item.views = StrClean.clean_comment(
                response.xpath('//div[@class="hm ptn"]/span[@class="xi1"]/text()').extract()[0])
            forum_item.replies = StrClean.clean_comment(
                response.xpath('//div[@class="hm ptn"]/span[@class="xi1"]/text()').extract()[1])
            forum_item.category = ''
            for i in range(len(response.xpath('//div[@id="pt"]/div[@class="z"]/a/text()').extract())-1):
                forum_item.category = forum_item.category + '-' + response.xpath('//div[@id="pt"]/div[@class="z"]/a/text()').extract()[i]
            forum_item.time = self.format_rep_date(rep_time_list[0])
            forum_item.title = StrClean.clean_comment(response.xpath('//span[@id="thread_subject"]/text()').extract()[0])
            if len(response.xpath(
                '//td[@class="t_f"]').extract())!= 0:
                c_soup = BeautifulSoup(response.xpath('//td[@class="t_f"]').extract()[0],'lxml')
                if c_soup.find('div', class_='attach_nopermission') is not None:
                    c_soup.find('div', class_='attach_nopermission').clear()
                [s.extract() for s in c_soup('script')]
                forum_item.content = StrClean.clean_comment(c_soup.get_text())
                forum_item.comment = self.gen_item_comment(response)
                forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            MongoClient.save_common_forum(forum_item, YShayuForumItem)

            if response.xpath('//div[@class="pg"]//span/text()').extract():
                page_num = response.xpath('//div[@class="pg"]//span/text()').extract()[0]
                page_num = int(re.search(' / ([\d]+) ', page_num).group(0)[3])
            else:
                page_num = 1

            if page_num > 40:
                start_page = page_num - 20
                for i in range(start_page, page_num + 1):
                    page_url = 'http://www.18095.com/thread-' + forum_id + '-' + str(i) + '-1.html'
                    yield scrapy.Request(
                        page_url,
                        dont_filter='true',
                        callback=self.generate_forum_thread
                    )
            else:
                for i in range(2, page_num + 1):
                    page_url = 'http://www.18095.com/thread-' + forum_id + '-' + str(i) + '-1.html'
                    yield scrapy.Request(
                        page_url,
                        dont_filter='true',
                        callback=self.generate_forum_thread
                    )

        else:
            forum_item.title = ''
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_common_forum(forum_item, YShayuForumItem)

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def gen_item_comment(self, response):
        comment = []
        new_comment = {}
        comments_data = []
        rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
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
