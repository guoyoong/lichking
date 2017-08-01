# coding=utf-8

import scrapy
import re
from lichking.util.str_clean import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging

class ImobileSpider(scrapy.Spider):
    name = "imobile"
    start_urls = ['http://lt.imobile.com.cn/forum.php']
    source_name = '手机之家'
    source_short = 'imobile'
    max_reply = 200

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
        #     'http://lt.imobile.com.cn/forum-673-1.html',
        #     meta={"page_key": 1},
        #     callback=self.generate_forum_list
        # )

    def generate_forum_list(self, response):
        forum_list = re.findall(u'http://lt.imobile.com.cn/forum-[\d]+-1.html', response.body)
        if len(forum_list) > 0:
            for forum_url in forum_list:
                yield scrapy.Request(
                    forum_url,
                    meta={"page_key": 1},
                    callback=self.generate_forum_list
                )

        # 版块分页下一页
        pg_next = response.xpath('//a[@class="nxt"]/@href').extract()
        rep_time_list = response.xpath('//p[@class="thread-author"]/a[2]').extract()
        page_key = int(response.meta['page_key'])
        if len(pg_next) > 0:
            # if 1 == 1:
            if page_key == 1 or self.check_rep_date(rep_time_list):
                yield scrapy.Request(
                    pg_next[0],
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
        forum_item = YImobileItem()
        forum_id = re.search(u'thread-([\d]+)', response.url)
        try:
            forum_id = forum_id.group(1)
        except:
            forum_id = re.search(u'tid=([\d]+)', response.url).group(1)
        forum_item._id = forum_id
        crawl_next = True
        rep_time_list = response.xpath('//div[@class="authi"]/em').extract()
        if re.search(u'thread-([\d]+)-1-([\d]+).html', response.url) is not None or response.url.find("tid") != -1:
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url
            forum_item.views = re.search(u'([\d]+) 次浏览',
                                         response.xpath('//div[@class="zhanzhuai_authi"]').extract()[0]).group(1)
            forum_item.replies = re.search(u'([\d]+) 位用户',
                                           response.xpath('//div[@class="zhanzhuai_authi"]').extract()[0]).group(1)
            forum_item.category = ''
            for i in range(2, len(response.xpath('//div[@id="pt"]/div[@class="z"]/a').extract())-1):
                forum_item.category = forum_item.category + '-' + \
                                      response.xpath('//div[@id="pt"]/div[@class="z"]/a/text()').extract()[i]
            forum_item.time = self.format_rep_date(response.xpath('//div[@class="zhanzhuai_authi"]').extract()[0])
            forum_item.title = StrClean.clean_comment(response.xpath('//span[@id="thread_subject"]/text()').extract()[0])
            c_soup = BeautifulSoup(response.xpath(
                '//div[@class="pct"]//table[1]').extract()[0], 'lxml')
            [s.extract() for s in c_soup('script')]  # remove script tag
            if c_soup.find('div', class_='attach_nopermission attach_tips') is not None:
                c_soup.find('div', class_='attach_nopermission attach_tips').clear()
            forum_item.content = c_soup.get_text()
            forum_item.content = StrClean.clean_comment(forum_item.content)
            forum_item.comment = self.gen_item_comment(response, is_first=True)
            if len(rep_time_list) > 0:
                forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            else:
                forum_item.last_reply_time = forum_item.time

            if int(forum_item.replies) > self.max_reply:
                crawl_next = False
            MongoClient.save_common_forum(forum_item, YImobileItem)

        else:
            forum_item.title = ''
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_common_forum(forum_item, YImobileItem)

        if len(response.xpath('//a[@class="nxt"]/@href').extract()) > 0 and crawl_next:
            next_page = response.xpath('//a[@class="nxt"]/@href').extract()[0]
            yield scrapy.Request(
                next_page,
                callback=self.generate_forum_thread
            )

    def gen_item_comment(self, response, is_first=False):
        comment = []
        new_comment = {}
        comments_data = []
        rep_time_list = response.xpath('//div[@class="authi"]/em').extract()
        if len(rep_time_list) == 0:
            return comment
        for indexi, content in enumerate(response.xpath('//div[@class="pct"]//table[1]').extract()):
            if is_first and indexi == 0:
                continue
            soup = BeautifulSoup(content, 'lxml')
            [s.extract() for s in soup('script')]  # remove script tag
            c = StrClean.clean_comment(soup.get_text())
            time_index = indexi
            if time_index >= len(rep_time_list):
                rep_time = self.format_rep_date(rep_time_list[-1])
            else:
                rep_time = self.format_rep_date(rep_time_list[time_index])
            comments_data.append({'content': c, 'reply_time': rep_time})
        new_comment['url'] = response.url
        new_comment['comments_data'] = comments_data
        comment.append(new_comment)
        return comment

    @staticmethod
    def check_rep_date(rep_time_list):
        for rep_time in rep_time_list:
            try:
                date_source = rep_time
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

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return ''
