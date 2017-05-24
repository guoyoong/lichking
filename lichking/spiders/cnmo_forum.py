# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
from lichking.settings import MONGODB_URI
import re
import logging
from lichking.util.time_util import *
from lichking.util.str_clean import *
from bs4 import BeautifulSoup
import fileinput

reload(sys)
sys.setdefaultencoding('utf-8')


class CnmoSpider(scrapy.Spider):
    name = "cnmo_forum"
    allowed_domains = ["bbs.cnmo.com"]
    start_urls = ['http://bbs.cnmo.com/']
    source_name = "手机中国论坛"
    source_short = "cnmo_forum"
    dic_file_path = "forum_dict"
    connect('yuqing', host=MONGODB_URI['host'], port=MONGODB_URI['port'],
            username=MONGODB_URI['username'], password=MONGODB_URI['password'])

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
        print 'init'

    # scrapy start and check page num
    def start_requests(self):
        # 进入论坛
        for line in fileinput.input(self.dic_file_path):
            logging.log(logging.ERROR, line)
            if not line:
                break
            if line.find('#') == -1:
                forum_url = 'http://bbs.cnmo.com/forum-' + line.split(":")[0] + '-1.html'
                forum_category = line.split(":")[1]
                logging.log(logging.ERROR, forum_url+':'+forum_category)
                yield scrapy.Request(
                    forum_url,
                    dont_filter='true',
                    meta={'url_pre': 'http://bbs.cnmo.com/forum-' + line.split(":")[0], "page_num": 1},
                    callback=self.get_record_list
                )

    def get_record_list(self, response):
        flag = -1
        # check 是否有新帖
        rep_time = response.xpath('//span[@class="fea-time"]/text()').extract()
        if len(rep_time) > 0:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            if rep_time[0] == today or rep_time[0] == yestday:
                flag = 1
                page_num = response.meta['page_num']
                url = response.meta['url_pre'] + str(page_num) + ".html"
                yield scrapy.Request(
                    url,
                    dont_filter='true',
                    meta={'url_pre': response.meta['url_pre'], "page_num": int(page_num) + 1},
                    callback=self.get_record_list
                )
        # 爬取当页数据
        if flag != -1:
            for cnmo_url in response.xpath(
                    '//div[@class="wrap2 feaList"]//p[@class="fea-tit"]//a[@target="_blank"]/@href').extract():
                yield scrapy.Request(
                    cnmo_url,
                    dont_filter='true',
                    callback=self.generate_forum_page
                )

    def generate_forum_page(self, response):
        forum_url = re.search(u'[\d]+', response.url.split("/")[3])
        try:
            forum_url = forum_url.group(0)
        except:
            forum_url = ''
        forum_item = YCnmoForumItem()
        forum_item._id = forum_url
        forum_item.url = response.url
        forum_item.source = self.source_name
        forum_item.source_short = self.source_short

        if response.url[len(response.url) - 9:] == '-1-1.html':
            forum_item.category = self.get_item_value(response.xpath('//div[@class="bcrumbs"]//a[1]/text()').extract())
            forum_item.time = self.get_item_value(response.xpath('//div[@class="b_detail"]//span[1]/text()').extract())
            forum_item.views = self.get_item_value(response.xpath('//div[@class="b_detail"]//span[2]/text()').extract())
            forum_item.replies = \
                self.get_item_value(response.xpath('//div[@class="b_detail"]//span[3]//em[2]/text()').extract())
            forum_item.title = StrClean.clean_comment(
                BeautifulSoup(response.xpath('//div[@class="b_title"]//p[1]').extract()[0], 'lxml').get_text())
            forum_item.content = BeautifulSoup(response.xpath(
                '//div[@class="b_article"]').extract()[0], 'lxml').get_text()
            forum_item.content = StrClean.clean_comment(forum_item.content)
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_cnmo_forum(forum_item)
            if len(response.xpath('//span[@class="bornone"]')) > 0:
                page_num = response.xpath('//div[@class="List-pages fr"]//a/text()').extract()[-3]
                page_num = int(page_num.replace('.', ''))
                # 回复太多的帖子 大部分为水贴或者活动帖子，每天只爬最后二十页
                start_page = 2
                if page_num > 50:
                    start_page = page_num - 20
                for page in range(start_page, page_num):
                    cnmo_url = response.url[:len(response.url) - 8] + str(page) + '-1.html'
                    yield scrapy.Request(
                        cnmo_url,
                        dont_filter='true',
                        callback=self.generate_forum_page
                    )
        else:
            forum_item.title = ''
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_cnmo_forum(forum_item)

    @staticmethod
    def gen_item_comment(response):
        comment = []
        new_comment = []
        for indexi, content in enumerate(response.xpath('//div[@class="bcom_text"]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            c = StrClean.clean_unicode(soup.get_text())
            if c != '':
                new_comment.append(c)
        for indexi, content in enumerate(response.xpath('//div[@class="br_Ltext"]/text()').extract()):
            soup = BeautifulSoup(content, 'lxml')
            c = StrClean.clean_unicode(soup.get_text())
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
