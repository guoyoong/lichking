# -*- coding: utf-8 -*-
import scrapy
import logging
import random
from lichking.mongo.mongo_client import *
from lichking.settings import MONGODB_URI
import re
from lxml import etree
from lichking.util.time_util import *
from lichking.util.str_clean import *
from bs4 import BeautifulSoup
import time

reload(sys)
sys.setdefaultencoding('utf-8')


class TiebaSpider(scrapy.Spider):
    name = "baidu_tieba"
    allowed_domains = ["tieba.baidu.com"]
    start_urls = ['http://tieba.baidu.com/']
    source_name = '百度贴吧'
    source_short = 'baidu_tieba'
    connect('yuqing', host=MONGODB_URI['host'], port=MONGODB_URI['port'],
            username=MONGODB_URI['username'], password=MONGODB_URI['password'])
    category = '联想'

    custom_settings = {
        'COOKIES_ENABLED': False,
        # 是否追踪referer
        'REFERER_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.01,
        'AUTOTHROTTLE_MAX_DELAY': 0.08,
        'SCHEDULER_DISK_QUEUE': 'scrapy.squeues.PickleFifoDiskQueue',
        'SCHEDULER_MEMORY_QUEUE': 'scrapy.squeues.FifoMemoryQueue',
        'DOWNLOADER_MIDDLEWARES': {
            'lichking.middlewares.RandomUserAgent_pc': 1,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
    }

    def __init__(self):
        print "init"

    def start_requests(self):
        # 进入贴吧
        url = 'http://tieba.baidu.com/f?ie=utf-8&kw=' + self.category + '&fr=search&pn=0'
        yield scrapy.Request(
            url,
            meta={"page_key": 0},
            callback=self.get_record_list
        )

    def get_record_list(self, response):
        content = response.body
        content = content.replace('<!--', '')
        content = content.replace('-->', '')
        tree = etree.HTML(content)
        url_list = tree.xpath('//*[@id="thread_list"]//a/@href')

        for i in url_list:
            if '/p/' in i and 'http://' not in i:
                tie_url = 'http://tieba.baidu.com' + i
                yield scrapy.Request(
                    tie_url,
                    callback=self.get_record_page_num
                )
        # check last reply time, 昨天回复的帖子时间格式： 12:12
        rep_time = tree.xpath('//span[contains(@class,"threadlist_reply_date")]/text()')
        if rep_time[0].find(':') != -1:
            page_key = int(response.meta['page_key']) + 50
            url = 'http://tieba.baidu.com/f?ie=utf-8&kw=' + self.category + '&fr=search&pn=' + str(page_key)
            yield scrapy.Request(
                url,
                meta={"page_key": page_key},
                callback=self.get_record_list
            )

    def get_record_page_num(self, response):
        page_num = re.search('<a(.*?)pn=(.*?)"(.*?)>尾页</a>', response.body)
        if page_num:
            page_num = int(page_num.group(2))
        else:
            page_num = 1

        tieba_item = YBaiduTiebaItem()
        tie_id = response.url.split('/p/')[1].split('?')[0]
        tieba_item['_id'] = tie_id
        # 帖子标题
        tieba_item.title = self.get_item_value(response.xpath('//title/text()').extract())
        tieba_item.category = self.category

        # 帖子时间
        tie_time = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', response.body)
        if tie_time:
            tie_time = tie_time.group(0)
        else:
            tie_time = ''
        tieba_item.time = tie_time
        tieba_item.source = self.source_name
        tieba_item.source_short = self.source_short
        tieba_item.replies = self.get_item_value(
            response.xpath('//li[@class="l_reply_num"]//span[1]/text()').extract())
        tieba_item.url = response.url
        tieba_item.content = BeautifulSoup(response.xpath(
            '//div[contains(@class,"d_post_content_firstfloor")]').extract()[0], 'lxml').get_text()
        tieba_item.content = StrClean.clean_unicode(tieba_item.content)
        comment = []
        new_comment = []
        for indexi, content in enumerate(response.xpath('//div[contains(@class,"j_d_post_content ")]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            new_comment.append(StrClean.clean_unicode(soup.get_text()))
        new_comment.append(response.url)
        comment.append(new_comment)
        tieba_item.comment = comment
        MongoClient.save_tieba_item(tieba_item)

        for indexi, content_id in \
                enumerate(response.xpath('//div[contains(@class,"j_d_post_content ")]/@id').extract()):
            c_id = re.search(u'[\d]+', content_id).group(0)
            tamp = int(time.time())
            c_url = 'https://tieba.baidu.com/p/comment?tid=' + str(tie_id) + '&pid=' + str(c_id) + '&t=' + str(
                tamp) + '&pn=1'
            yield scrapy.Request(
                c_url,
                callback=self.get_comment
            )

        start_page = 2
        # 水帖，只爬最后40页
        if page_num > 50:
            start_page = page_num - 40
        for i in range(start_page, page_num + 1):
            yield scrapy.Request(
                response.url + '?pn=' + str(i),
                meta={
                    'pageNumber': str(i)
                },
                callback=self.get_content
            )

    def get_content(self, response):
        tieba_item = YBaiduTiebaItem()
        tie_id = response.url.split('/p/')[1].split('?')[0]
        tieba_item['_id'] = tie_id

        if response.meta["pageNumber"] == '1':
            print 'page 1'
        # other page
        else:
            comment = []
            new_comment = []
            for indexi, content in enumerate(response.xpath('//div[contains(@class,"j_d_post_content ")]').extract()):
                soup = BeautifulSoup(content, 'lxml')
                new_comment.append(StrClean.clean_unicode(soup.get_text()))
            new_comment.append(response.url)
            comment.append(new_comment)
            tieba_item.comment = comment
            MongoClient.save_tieba_item(tieba_item)

            for indexi, content_id in \
                    enumerate(response.xpath('//div[contains(@class,"j_d_post_content ")]/@id').extract()):
                c_id = re.search(u'[\d]+', content_id).group(0)
                tamp = int(time.time())
                c_url = 'https://tieba.baidu.com/p/comment?tid='+str(tie_id)+'&pid='+str(c_id)+'&t='+str(tamp)+'&pn=1'
                yield scrapy.Request(
                    c_url,
                    callback=self.get_comment
                )

    def get_comment(self, response):
        if len(response.xpath('//span[@class="lzl_content_main"]').extract()) > 0:
            tieba_item = YBaiduTiebaItem()
            tieba_item._id = re.search(u'[\d]+', response.url).group(0)
            comment = []
            new_comment = []
            for index, reply_content in enumerate(
                    response.xpath('//span[@class="lzl_content_main"]').extract()):
                new_comment.append(StrClean.clean_comment(BeautifulSoup(reply_content, 'lxml').get_text()))

            new_comment.append(response.url)
            comment.append(new_comment)
            tieba_item.comment = comment
            MongoClient.save_tieba_item(tieba_item)

            com_url = response.url.split("pn=")[0]
            pn = int(response.url.split("pn=")[1])
            yield scrapy.Request(
                com_url + "pn=" + str(pn + 1),
                dont_filter='true',
                callback=self.get_comment
            )

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''
