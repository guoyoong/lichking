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
    source_short = 'baidu_tieba2'
    category_arr = ["thinkpad", "拯救者游戏本", "联想", "联想小新"]
    # category_arr = ["thinkpad"]

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
        for category in self.category_arr:
            url = 'http://tieba.baidu.com/f?ie=utf-8&kw=' + category + '&fr=search&pn=0'
            yield scrapy.Request(
                url,
                meta={"page_key": 0, "category": category},
                callback=self.get_record_list
            )

    def get_record_list(self, response):
        content = response.body
        content = content.replace('<!--', '')
        content = content.replace('-->', '')
        tree = etree.HTML(content)
        url_list = tree.xpath('//*[@id="thread_list"]//a/@href')
        category = response.meta['category']
        for i in url_list:
            if '/p/' in i and 'http://' not in i:
                tie_url = 'http://tieba.baidu.com' + i
                yield scrapy.Request(
                    tie_url,
                    meta={"category": category},
                    callback=self.get_record_page_num
                )
        # check last reply time, 昨天回复的帖子时间格式： 12:12
        rep_time = tree.xpath('//span[contains(@class,"threadlist_reply_date")]/text()')
        if self.check_rep_date(rep_time[0]):
            next_page = tree.xpath('//a[contains(@class, "next")]/text()')
            if len(next_page) > 0:
                logging.error(next_page[0])
                page_key = int(response.meta['page_key']) + 50
                url = 'http://tieba.baidu.com/f?ie=utf-8&kw=' + category + '&fr=search&pn=' + str(page_key)
                yield scrapy.Request(
                    url,
                    meta={"page_key": page_key, "category": category},
                    callback=self.get_record_list
                )

    def get_record_page_num(self, response):
        page_num = re.search('<a(.*?)pn=(.*?)"(.*?)>尾页</a>', response.body)
        if page_num:
            page_num = int(page_num.group(2))
        else:
            page_num = 1

        tieba_item = YBaiduTieba2Item()
        tie_id = response.url.split('/p/')[1].split('?')[0]
        tieba_item['_id'] = tie_id
        # 帖子标题
        tieba_item.title = self.get_item_value(response.xpath('//title/text()').extract())
        tieba_item.category = response.meta['category']

        # 帖子时间
        tie_time = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', response.body)
        if tie_time:
            tie_time = self.format_rep_date(tie_time.group(0))
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

        rep_time_list = re.findall(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', response.body)
        tieba_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
        comment = []
        new_comment = {}
        comments_data = []
        for indexi, content in enumerate(response.xpath('//div[contains(@class,"j_d_post_content ")]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            c = StrClean.clean_unicode(soup.get_text())
            if indexi >= len(rep_time_list):
                rep_time = self.format_rep_date(rep_time_list[-1])
            else:
                rep_time = self.format_rep_date(rep_time_list[indexi])
            comments_data.append({'content': c, 'reply_time': rep_time})
        new_comment['url'] = response.url
        new_comment['comments_data'] = comments_data
        comment.append(new_comment)
        tieba_item.comment = comment
        MongoClient.save_common_forum(tieba_item, YBaiduTieba2Item)

        # 回复的回复
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
        # 水帖，只爬前10页，最后20页
        if page_num > 40:
            start_page = page_num - 10
            for i in range(2, 10):
                yield scrapy.Request(
                    response.url + '?pn=' + str(i),
                    meta={
                        'pageNumber': str(i)
                    },
                    callback=self.get_content
                )

        for i in range(start_page, page_num + 1):
            yield scrapy.Request(
                response.url + '?pn=' + str(i),
                meta={
                    'pageNumber': str(i)
                },
                callback=self.get_content
            )

    def get_content(self, response):
        tieba_item = YBaiduTieba2Item()
        tie_id = response.url.split('/p/')[1].split('?')[0]
        tieba_item['_id'] = tie_id

        if response.meta["pageNumber"] == '1':
            print 'page 1'
        # other page
        else:
            rep_time_list = re.findall(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', response.body)
            tieba_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            comment = []
            new_comment = {}
            comments_data = []
            for indexi, content in enumerate(response.xpath('//div[contains(@class,"j_d_post_content ")]').extract()):
                soup = BeautifulSoup(content, 'lxml')
                c = StrClean.clean_unicode(soup.get_text())
                if indexi >= len(rep_time_list):
                    rep_time = self.format_rep_date(rep_time_list[-1])
                else:
                    rep_time = self.format_rep_date(rep_time_list[indexi])
                comments_data.append({'content': c, 'reply_time': rep_time})
            new_comment['url'] = response.url
            new_comment['comments_data'] = comments_data
            comment.append(new_comment)
            tieba_item.comment = comment
            MongoClient.save_common_forum(tieba_item, YBaiduTieba2Item)

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
            tieba_item = YBaiduTieba2Item()
            tieba_item._id = re.search(u'[\d]+', response.url).group(0)

            rep_time_list = re.findall(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', response.body)
            comment = []
            new_comment = {}
            comments_data = []
            for index, reply_content in enumerate(
                    response.xpath('//span[@class="lzl_content_main"]').extract()):
                c = StrClean.clean_comment(BeautifulSoup(reply_content, 'lxml').get_text())
                if index >= len(rep_time_list):
                    rep_time = self.format_rep_date(rep_time_list[-1])
                else:
                    rep_time = self.format_rep_date(rep_time_list[index])
                comments_data.append({'content': c, 'reply_time': rep_time})
            new_comment['url'] = response.url
            new_comment['comments_data'] = comments_data
            comment.append(new_comment)
            tieba_item.comment = comment
            MongoClient.save_common_forum(tieba_item, YBaiduTieba2Item)

            com_url = response.url.split("pn=")[0]
            pn = int(response.url.split("pn=")[1])
            yield scrapy.Request(
                com_url + "pn=" + str(pn + 1),
                dont_filter='true',
                callback=self.get_comment
            )

    def check_rep_date(self, date_source):
        logging.error(date_source)
        if date_source.find(':') != -1:
            return True
        year = datetime.datetime.now().strftime("%Y")
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        date_source = re.search(u'\d{1,2}-\d{1,2}', date_source).group(0)
        date_source = self.format_rep_date(year + '-' + date_source)
        logging.error(date_source)
        if date_source == today or date_source == yestday:
            return True
        return False

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return ''

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''
