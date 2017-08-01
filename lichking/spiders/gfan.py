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
    max_reply = 200
    forum_dict = {"http://bbs.gfan.com/forum-170-1.html", "http://bbs.gfan.com/forum-62-1.html"}

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.5,
    }

    def __init__(self):
        print 123

    def start_requests(self):
        # get into the bbs
        yield scrapy.Request(
            self.start_urls[0],
            meta={"page_key": 1},
            callback=self.generate_forum_list
        )
        # yield scrapy.Request(
        #     'http://bbs.gfan.com/forum-1686-1.html',
        #     callback=self.generate_forum_page_list
        # )

    def generate_forum_list(self, response):
        forum_list = re.findall(u'http://bbs.gfan.com/forum-[\d]+-1.html', response.body)
        if len(forum_list) > 0:
            for forum_url in forum_list:
                if forum_url not in self.forum_dict:
                    yield scrapy.Request(
                        forum_url,
                        meta={"page_key": 1},
                        callback=self.generate_forum_list
                    )

        pg_bar = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()
        rep_time_list = response.xpath('//tr/td[@class="by"]/em/a').extract()
        page_key = int(response.meta['page_key'])
        if len(pg_bar) > 0:
            if page_key == 1 or self.check_rep_date(rep_time_list):
                yield scrapy.Request(
                    pg_bar[0],
                    meta={"page_key": -1},
                    callback=self.generate_forum_list
                )

            thread_list = response.xpath('//a[@class="xst"]/@href').extract()
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
        rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
        if len(response.xpath('//a[@class="prev"]').extract()) == 0:
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
            MongoClient.save_common_forum(forum_item, YGfanForumItem)

        else:
            forum_item.title = ''
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_common_forum(forum_item, YGfanForumItem)

        if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0 and crawl_next:
            next_page = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
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