# -*- coding: utf-8 -*-
import scrapy
import re
from lichking.util.str_clean import *
from lichking.util.time_util import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging


class It168Spider(scrapy.Spider):
    name = "it168"
    allowed_domains = ["it168.com"]
    start_urls = ['http://bbs.it168.com/']
    forum_list_file = 'it168_forum_list_file'
    source_name = 'it168'
    source_short = 'it168'
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
        # enter forum
        yield scrapy.Request(
            'http://jiyouhui.it168.com/forum.php',
            meta={"page_key": 1},
            callback=self.generate_forum_url_list
        )
        yield scrapy.Request(
            'http://benyouhui.it168.com/forum.php',
            meta={"page_key": 1},
            callback=self.generate_forum_url_list
        )

        # yield scrapy.Request(
        #     'http://benyouhui.it168.com/forum-962-1.html',
        #     meta={"page_key": 1},
        #     callback=self.generate_forum_page_list
        # )

    def generate_forum_url_list(self, response):
        forum_list = response.xpath('//td[@class="fl_g"]//dl//dt//a/@href').extract()
        if len(forum_list) > 0:
            it168_url_pre = response.url.split('forum')[0]
            if it168_url_pre[-1] != '/':
                it168_url_pre += '/'
            for forum_url in forum_list:
                if forum_url is not None:
                    if forum_url.find("http") == -1:
                        forum_url = it168_url_pre + forum_url
                    yield scrapy.Request(
                        forum_url,
                        meta={"page_key": 1},
                        callback=self.generate_forum_url_list
                    )

        # scrapy all tie url
        thread_list = response.xpath('//a[@class="xst"]/@href').extract()
        rep_time_list = response.xpath('//p[@class="replyer"]').extract()
        it168_url_pre = response.url.split('forum')[0]
        if it168_url_pre[-1] != '/':
            it168_url_pre += '/'
        if len(thread_list) > 0:
            rep_time = self.format_rep_date_short(rep_time_list[0].strip())
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            page_key = int(response.meta['page_key'])
            logging.error("page_key:" + str(page_key))
            if rep_time == today or rep_time == yestday or page_key == 1:
                for thread_url in thread_list:
                    yield scrapy.Request(
                        it168_url_pre + thread_url,
                        callback=self.generate_forum_thread
                    )
                # check 是否有下一页
                pg_bar = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()
                if len(pg_bar) > 0:
                    yield scrapy.Request(
                        it168_url_pre + pg_bar[0],
                        meta={"page_key": -1},
                        callback=self.generate_forum_url_list
                    )

    def generate_forum_thread(self, response):
        forum_id = re.search(u'thread-([\d]+)', response.url)
        try:
            forum_id = forum_id.group(1)
        except:
            forum_id = ''
        forum_item = YIt168Item()
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
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[1]/text()').extract())
            category2 = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[2]/text()').extract())
            category3 = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[3]/text()').extract())
            forum_item.category = category1 + '-' + category2 + '-' + category3

            rep_time_list = response.xpath('//div[@class="authi"]//em/text()').extract()
            forum_item.time = self.format_rep_date(rep_time_list[0])
            forum_item.title = StrClean.clean_comment(
                response.xpath('//span[@id="thread_subject"]/text()').extract()[0])
            content_div = response.xpath('//div[@class="t_fsz"]//table[1]').extract()
            if len(content_div) == 0:
                content_div = response.xpath('//div[@class="pcb"]').extract()
            c_soup = BeautifulSoup(content_div[0], 'lxml')
            [s.extract() for s in c_soup('script')]  # remove script tag
            forum_item.content = c_soup.get_text()
            forum_item.content = StrClean.clean_comment(forum_item.content)
            forum_item.comment = self.gen_item_comment(response)
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])

            if int(forum_item.replies) > self.max_reply:
                crawl_next = False
            MongoClient.save_common_forum(forum_item, YIt168Item)
        else:
            forum_item.title = ''
            rep_time_list = response.xpath('//div[@class="authi"]//em/text()').extract()
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_common_forum(forum_item, YIt168Item)

        # 是否有下一页
        if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0 and crawl_next:
            it168_url_pre = response.url.split('thread')[0]
            r_url = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
            yield scrapy.Request(
                it168_url_pre + r_url,
                callback=self.generate_forum_thread
            )

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_rep_date_short(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d'))
            return time.strftime('%Y-%m-%d', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d")

    def gen_item_comment(self, response):
        comment = []
        new_comment = {}
        comments_data = []
        rep_time_list = response.xpath('//div[@class="authi"]//em/text()').extract()
        for indexi, content in enumerate(response.xpath('//div[@class="pcb"]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            [s.extract() for s in soup('script')]  # remove script tag
            c = StrClean.clean_comment(soup.get_text())
            comments_data.append({'content': c, 'reply_time': self.format_rep_date(rep_time_list[indexi])})
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
