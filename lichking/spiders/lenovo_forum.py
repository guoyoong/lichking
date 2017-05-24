# coding=utf-8

import scrapy
import re
import logging
from lichking.mongo.mongo_client import *
from bs4 import BeautifulSoup
from lichking.util.str_clean import *
from lichking.settings import MONGODB_URI
from lichking.util.time_util import *


reload(sys)
sys.setdefaultencoding('utf-8')


class LenovoClub(scrapy.Spider):

    name = "lenovo_club"
    page_num = 100
    start_page_num = 0
    # 将论坛的url地址都存储到文本
    url_file_name = "lenovo_forum_url_list"
    allowed_domains = ["club.lenovo.com.cn"]
    source_name = "联想社区"
    source_short = "lenovo_forum"
    connect('yuqing', host=MONGODB_URI['host'], port=MONGODB_URI['port'],
            username=MONGODB_URI['username'], password=MONGODB_URI['password'])
    custom_settings = {
        'DOWNLOAD_DELAY': 0.01,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.01,
        'AUTOTHROTTLE_MAX_DELAY': 2.0
    }

    # 断点
    def __init__(self):
        self.start_page_num = 1

    # scrapy start and check page num
    def start_requests(self):
        url = 'http://club.lenovo.com.cn/forum-all-reply_time-0-1'
        yield scrapy.Request(
            url,
            meta={"page_key": 1},
            callback=self.generate_forum_url
        )

    # filter all forum url and store
    def generate_forum_url(self, response):
        for h1a_forum_url in response.xpath('//div[@class="Forumhome_listbox"]//dd//h1//a//@href').extract():
            yield scrapy.Request(
                h1a_forum_url,
                dont_filter='true',
                callback=self.generate_forum_page
            )
        # check last forum time 只抓取一天前的数据
        rep_time = response.xpath('//div[@class="Forumhome_listbox"]//dl//dd//p/text()').extract()
        if rep_time[2].find('前') != -1:
            page_key = int(response.meta['page_key'])+1
            url = 'http://club.lenovo.com.cn/forum-all-reply_time-0-' + str(page_key)
            yield scrapy.Request(
                url,
                meta={"page_key": page_key},
                callback=self.generate_forum_url
            )

    def generate_forum_page(self, response):
        forum_url = response.url[:len(response.url) - 8] + '1-1.html'
        forum_page_bar = response.xpath('//div[@class="pg"]').extract()
        if len(forum_page_bar) > 0:
            last_page = response.xpath('//div[@class="pg"]//label//span/text()').extract()[0]
            last_page = re.search(u'[\d]+', last_page).group(0)
            if int(last_page) > 500:
                last_page = 500
            for i in range(1, int(last_page) + 1):
                url = response.url[:len(response.url) - 8] + str(i) + '-1.html'
                forum_url += '\n' + url
                yield scrapy.Request(
                    url,
                    callback=self.generate_forum_content,
                    dont_filter='true'
                )
        else:
            yield scrapy.Request(
                forum_url,
                callback=self.generate_forum_content,
                dont_filter='true'
            )
        with open(self.url_file_name, 'a') as f:
            f.write('\n'+forum_url)

    # parse forum content and store
    def generate_forum_content(self, response):

        if 'thread' not in response.url:
            logging.log(logging.WARNING, response.url)
            return
        forum_url = re.search(u'[\d]+', response.url)
        try:
            forum_url = forum_url.group(0)
        except:
            forum_url = ''
        forum_item = YLenovoForumItem()
        forum_item._id = forum_url
        if response.url[len(response.url) - 9:] == '-1-1.html':
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url

            self.save_item_value(forum_item, 'category',
                                 response.xpath('//div[@class="lt_single_left_toptwo"]//h1/text()').extract())
            self.save_item_value(forum_item, 'views',
                                 response.xpath('//p[@id="view_title_look"]//span[1]/text()').extract())
            self.save_item_value(forum_item, 'replies',
                                 response.xpath('//p[@id="view_title_look"]//span[2]/text()').extract())
            self.save_item_value(forum_item, 'title',
                                 response.xpath('//span[@id="thread_subject"]//text()').extract())
            forum_type = response.xpath('//h1[@id="view_title_01"]//a/text()').extract()
            if len(forum_type) > 0:
                forum_item.title = forum_type[0].strip() + forum_item.title

            forum_time = response.xpath('//div[@class="pti"]/div[@class="authi"]/em/text()').extract()
            try:
                forum_item.time = forum_time[0].split(' ')[1] + ' '+forum_time[0].split(' ')[2]
            except:
                forum_item.time = \
                    TimeUtil.transfer_date(
                        response.xpath('//div[@class="pti"]//div[@class="authi"]//span[1]//@title').extract()[0])
                if forum_item.time == '':
                    # 最近的回复日期 需要特殊处理。默认日期格式：2017-5-3 12:1:1
                    forum_item.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            forum_item.flag = '-1'

            # content
            comments = []
            content_comment = []
            for indexi, content in enumerate(response.xpath('//div[@class="t_fsz"]').extract()):
                soup = BeautifulSoup(content, 'lxml')
                if indexi == 0:
                    forum_item.content = StrClean.clean_comment(soup.get_text())
                else:
                    content_comment.append(StrClean.clean_comment(soup.get_text()))
            content_comment.append(response.url)
            comments.append(content_comment)
            forum_item.comment = comments

            if response.url.find('thinkworld') != -1:
                forum_item.category = "ThinkPad"
                self.save_item_value(forum_item, 'views',
                                     response.xpath('//div[@class="thinktitleleft"]//span[1]//text()').extract())
                self.save_item_value(forum_item, 'replies',
                                     response.xpath('//div[@class="thinktitleright"]//span[1]//text()').extract())

            MongoClient.save_forum_item(forum_item)
        else:
            comments = []
            content_comment = []
            for indexi, content in enumerate(response.xpath('//div[@class="t_fsz"]').extract()):
                soup = BeautifulSoup(content, 'lxml')
                content_comment.append(StrClean.clean_comment(soup.get_text()))
            content_comment.append(response.url)
            comments.append(content_comment)
            forum_item.comment = comments
            MongoClient.save_forum_item(forum_item)

    def get_other_comment_page(self, forum_url, last_page):
        logging.log(logging.WARNING, last_page)
        if last_page.isdigit():
            for i in range(2, int(last_page) + 1):
                url = "http://club.lenovo.com.cn/" + forum_url + '-' + str(i) + '-1.html',
                logging.log(logging.WARNING, url)
                yield scrapy.Request(
                    url,
                    dont_filter='true',
                    callback=self.generate_forum_content
                )

    @staticmethod
    def save_item_value(forum_item, forum_key, forum_arr):
        if len(forum_arr) > 0:
            forum_item[forum_key] = forum_arr[0].strip()
        else:
            forum_item[forum_key] = ''

