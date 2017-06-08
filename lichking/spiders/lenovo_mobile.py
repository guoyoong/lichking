# coding=utf-8

import scrapy
from lichking.mongo.mongo_client import *
from lichking.settings import MONGODB_URI
from lichking.util.time_util import *
from lichking.util.str_clean import *
from bs4 import BeautifulSoup
import logging

import re

reload(sys)
sys.setdefaultencoding('utf-8')


class LenovoMobile(scrapy.Spider):

    name = "lenovo_mobile"
    # 将论坛的url地址都存储到文本
    allowed_domains = ["bbs.lenovomobile.cn"]
    source_name = "联想手机社区"
    source_short = "lenovo_mobile"
    connect('yuqing', host=MONGODB_URI['host'], port=MONGODB_URI['port'],
            username=MONGODB_URI['username'], password=MONGODB_URI['password'])
    custom_settings = {
        'DOWNLOAD_DELAY': 0.01,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.01,
        'AUTOTHROTTLE_MAX_DELAY': 5.8
    }

    forum_page_num = {
        'zukedge': 80,
        'zui': 135,
        'z2': 1014,
        'z1': 1092
    }

    def __init__(self):
        print 123

    # scrapy start and check page num
    def start_requests(self):
        for key in self.forum_page_num:
            for i in range(1, self.forum_page_num.get(key)):
                url = "http://bbs.lenovomobile.cn/" + key + "/" + str(i) + "/"
                yield scrapy.Request(
                    url,
                    meta={"page_key": 1,  "forum_key": key},
                    callback=self.generate_forum_url
                )

    def generate_forum_url(self, response):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        url_xpath = response.xpath(
            '//div[@class="threadlist"]//div[@class="threadlist_title"]//a[@onclick="atarget(this)"]/@href').extract()
        rep_time_path = response.xpath(
            '//div[@class="threadlist_info"]//div[@class="lastreply"]//span/@title').extract()
        if len(rep_time_path) > 0:
            for index in range(0, len(rep_time_path)):
                r_time = TimeUtil.format_date(rep_time_path[index])
                if r_time == today or r_time == yestday:
                    yield scrapy.Request(
                        # eg. /zui/t778232/
                        "http://bbs.lenovomobile.cn" + url_xpath[index] + '1/',
                        callback=self.generate_forum_content
                    )

        # check last forum time 只抓取一天前的数据
        # if len(rep_time_path) > 0:
        #     r_time = TimeUtil.format_date(rep_time_path[0])
        #     logging.log(logging.ERROR, r_time)
        #     if r_time == today or r_time == yestday:
        #         page_key = int(response.meta['page_key']) + 1
        #         forum_key = response.meta['forum_key']
        #         url = "http://bbs.lenovomobile.cn/" + forum_key + "/" + str(page_key) + "/"
        #         yield scrapy.Request(
        #             url,
        #             meta={"page_key": page_key, "forum_key": forum_key},
        #             callback=self.generate_forum_url
        #         )

    def generate_forum_content(self, response):
        forum_item = YLenovoMobile2Item()
        forum_item.url = response.url
        forum_item._id = forum_item.url.split("/")[4].replace('t', '')

        # first page
        if forum_item.url.split("/")[5] == '1':
            rep_time_list = response.xpath('//div[contains(@class,"main")]/div[2]//div[contains(@id, "post_")]'
                                           '//div[@class="viewthread_top"]/em').extract()
            try:
                forum_item.category = forum_item.url.split("/")[3]
            except:
                forum_item.category = \
                    self.get_safe_item_value(response.xpath('//*[@id="nv_forum"]/div[4]/a[3]/text()').extract())
            forum_item.views = response.xpath("//div[@class='viewthreadtop_storey right']/text()").extract()[0]
            forum_item.replies = response.xpath("//div[@class='viewthreadtop_storey right']/text()").extract()[1]
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            color_link = self.get_safe_item_value(response.xpath('//a[@class="colorlink"]/text()').extract())
            forum_item.title = color_link + "" + \
                self.get_safe_item_value(response.xpath('//*[@id="thread_subject"]/text()').extract())

            forum_item.time = self.format_rep_date(response.xpath('//div[@class="viewthread_top"]').extract()[0])

            soup = response.xpath('//div[@class="viewthread_table"]//table').extract()
            if len(soup) > 0:
                forum_item.content = StrClean.clean_comment(BeautifulSoup(soup[0], 'lxml').get_text())
            else:
                forum_item.content = ''
            forum_item.flag = '-1'

            comments = []
            new_comment = {}
            comments_data = []
            for index, reply_content in enumerate(
                    response.xpath('//div[contains(@class,"main")]/div[2]//div[contains(@id, "post_")]'
                                   '//div[@class="viewthread_content"]').extract()):
                c = BeautifulSoup(reply_content, 'lxml').get_text()
                if index >= len(rep_time_list):
                    rep_time = self.format_rep_date(rep_time_list[-1])
                else:
                    rep_time = self.format_rep_date(rep_time_list[index])
                comments_data.append({'content': StrClean.clean_comment(c), 'reply_time': rep_time})
            new_comment['url'] = response.url
            new_comment['comments_data'] = comments_data
            comments.append(new_comment)
            forum_item.comment = comments
            if len(rep_time_list) == 0:
                forum_item.last_reply_time = forum_item.time
            else:
                forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            MongoClient.save_mobile_item(forum_item)

            forum_url = response.url
            forum_page_bar = response.xpath('//div[@class="pg"]').extract()
            # exists more page
            if len(forum_page_bar) > 0:
                last_page = response.xpath('//div[@class="pg"]//label//span/text()').extract()[0]
                last_page = re.search(u'[\d]+', last_page).group(0)

                start_page = 2
                # 水帖，只爬最后40页
                if int(last_page) > 50:
                    start_page = int(last_page) - 30
                for i in range(start_page, int(last_page) + 1):
                    url = response.url[:len(response.url) - 2] + str(i) + '/'
                    forum_url += '\n' + url
                    yield scrapy.Request(
                        url,
                        callback=self.generate_forum_content,
                        dont_filter='true'
                    )
            # only one page

        else:
            rep_time_list = response.xpath('//div[contains(@id, "post_")]'
                                           '//div[@class="viewthread_top"]/em').extract()
            comments = []
            new_comment = {}
            comments_data = []
            for index, reply_content in enumerate(
                    response.xpath('//div[contains(@id, "post_")]'
                                   '//div[@class="viewthread_content"]').extract()):
                c = BeautifulSoup(reply_content, 'lxml').get_text()
                if index >= len(rep_time_list):
                    rep_time = self.format_rep_date(rep_time_list[-1])
                else:
                    rep_time = self.format_rep_date(rep_time_list[index])
                comments_data.append({'content': StrClean.clean_comment(c), 'reply_time': rep_time})
            new_comment['url'] = response.url
            new_comment['comments_data'] = comments_data
            comments.append(new_comment)
            forum_item.comment = comments
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            MongoClient.save_mobile_item(forum_item)

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return ''

    @staticmethod
    def get_safe_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ""
