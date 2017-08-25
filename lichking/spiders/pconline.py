# -*- coding: utf-8 -*-

import scrapy
from lichking.util.str_clean import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging
import json


class PconlineSpider(scrapy.Spider):
    name = "pconline"
    start_urls = ['http://itbbs.pconline.com.cn/mobile/', 'http://android.pconline.com.cn/',
                  'http://itbbs.pconline.com.cn/wp/', 'http://mobile.pconline.com.cn/mobilebbs/xt/iphone/',
                  'http://itbbs.pconline.com.cn/notebook/', 'http://itbbs.pconline.com.cn/diy/']
    category_list = ['mobile/', 'bbs/', 'diy/', 'notebook/', '']
    source_name = '太平洋电脑网'
    source_short = 'pconline'
    max_reply = 200
    max_page = 3

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 1.2,
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

    def generate_forum_list(self, response):
        for cate in self.category_list:
            forum_list = re.findall(u'http://itbbs.pconline.com.cn/' + cate + 'f[\d]+.html', response.body)
            if len(forum_list) > 0:
                for forum_url in forum_list:
                    yield scrapy.Request(
                        forum_url,
                        meta={"page_key": 1},
                        callback=self.generate_forum_list
                    )

        pg_next = response.xpath('//a[@class="btn-next"]/@href').extract()
        page_key = int(response.meta['page_key'])
        if len(pg_next) > 0:
            # 论坛 没有展示回复时间抓取前3页
            if page_key < self.max_page:
                yield scrapy.Request(
                    'http:' + pg_next[0],
                    meta={"page_key": page_key + 1},
                    callback=self.generate_forum_list
                )

        thread_list = response.xpath('//span[@class="topic-tit"]/a[2]/@href').extract()
        logging.error(len(thread_list))
        if len(thread_list) > 0:
            for thread_url in thread_list:
                yield scrapy.Request(
                    'http:' + thread_url,
                    callback=self.generate_forum_thread
                )

    def generate_forum_thread(self, response):
        forum_item = YPconlineItem()
        forum_id = re.search(u'([\d]+)', response.url)
        try:
            forum_id = forum_id.group(1)
        except:
            forum_id = re.search(u'tid=([\d]+)', response.url).group(1)
        forum_item._id = forum_id
        crawl_next = True
        rep_time_list = response.xpath('//span[@class="date"]/text()').extract()
        if len(response.xpath('//em[@id="Jtopicvcount"]/text()').extract()) != 0:
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url
            forum_item.views = StrClean.get_safe_value(response.xpath('//em[@id="Jtopicvcount"]/text()').extract())
            forum_item.replies = \
                StrClean.get_safe_value(response.xpath('//em[@id="Jreplycount"]/text()').extract())
            forum_item.category = ''
            for i in range(len(response.xpath('//div[@class="crumb"]/a/text()').extract())-2):
                forum_item.category = forum_item.category + '-' + \
                                      response.xpath('//div[@class="crumb"]/a/text()').extract()[i]
            forum_item.time = self.format_rep_date(rep_time_list[0])
            forum_item.title = StrClean.clean_comment(response.xpath('//div[@class="tit"]/a/text()').extract()[0])
            c_soup = BeautifulSoup(response.xpath(
                '//div[@class="topiccontent"]').extract()[0], 'lxml')
            forum_item.content = c_soup.get_text()
            forum_item.content = StrClean.clean_comment(forum_item.content)
            forum_item.comment = self.gen_item_comment(response, is_first=True)
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])

            if int(forum_item.replies) > self.max_reply:
                crawl_next = False
            MongoClient.save_common_forum(forum_item, YPconlineItem)

            yield scrapy.Request(
                'http://itbbs.pconline.com.cn/forum/async/listUserInfoAndTopicViews.ajax?tids=' + forum_id,
                meta={'tid': forum_id},
                callback=self.gen_item_views
            )
        else:
            forum_item.title = ''
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_common_forum(forum_item, YPconlineItem)

        if len(response.xpath('//a[@class="btn-next"]/@href').extract()) > 0 and crawl_next:
            next_page = response.xpath('//a[@class="btn-next"]/@href').extract()[0]
            yield scrapy.Request(
                'http:' + next_page,
                callback=self.generate_forum_thread
            )

    @staticmethod
    def gen_item_views(response):
        forum_id = response.meta['tid']
        forum_item = YPconlineItem()
        forum_item._id = forum_id
        forum_item.views = str(json.loads(response.body)['topicViews'][0]['views'])
        MongoClient.save_forum_views(forum_item, YPconlineItem)

    def gen_item_comment(self, response, is_first=False):
        comment = []
        new_comment = {}
        comments_data = []
        rep_time_list = response.xpath('//span[@class="date"]/text()').extract()
        for indexi, content in enumerate(response.xpath('//div[@class="replycontent"]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            [s.extract() for s in soup('script')]  # remove script tag
            c = StrClean.clean_comment(soup.get_text())
            time_index = indexi
            if is_first:
                time_index += 1
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
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return ''
