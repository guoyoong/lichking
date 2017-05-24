# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
from lichking.settings import MONGODB_URI
import re
from lichking.util.time_util import *
from lichking.util.str_clean import *
from bs4 import BeautifulSoup


class IthomeSpider(scrapy.Spider):
    name = "ithome"
    allowed_domains = ["ithome.com"]
    start_urls = ['ithome.com']
    source_name = "IT之家"
    source_short = "ithome"
    connect('yuqing', host=MONGODB_URI['host'], port=MONGODB_URI['port'],
            username=MONGODB_URI['username'], password=MONGODB_URI['password'])
    break_point_file_name = "ithome_break_point"
    start_page_num = 1
    page_num = 100  # 2

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

    # 断点
    def __init__(self):
        self.start_page_num = 1

    # scrapy start and check page num
    def start_requests(self):
        for i in range(self.start_page_num, self.page_num):
            url = 'http://win10.ithome.com/ithome/getajaxdata.aspx?categoryid=0&type=pccategorypage&page=' + str(i)
            yield scrapy.Request(
                url,
                dont_filter='true',
                callback=self.generate_article_url
            )

    def generate_article_url(self, response):
        for h1a_forum_url in response.xpath('//li//div//h2//a//@href').extract():
            yield scrapy.Request(
                h1a_forum_url,
                dont_filter='true',
                callback=self.generate_article_page
            )

    def generate_article_page(self, response):
        ithome_item = YIthomeItem()
        article_id = re.search(u'[\d]+', response.url.split("/")[5])
        try:
            article_id = article_id.group(0)
        except:
            article_id = ''
        ithome_item._id = article_id
        ithome_item.url = response.url
        ithome_item.source = self.source_name
        ithome_item.source_short = self.source_short
        ithome_item.title = self.get_item_value(response.xpath('//div[@class="post_title"]//h1/text()').extract())
        ithome_item.category = self.get_item_value(
            response.xpath('//div[@class="current_nav"]//a[2]//text()').extract())
        author = self.get_item_value(response.xpath('//span[@id="author_baidu"]//strong//text()').extract())
        editor = self.get_item_value(response.xpath('//span[@id="editor_baidu"]//strong//text()').extract())
        ithome_item.author = "作者：" + author + ",责编：" + editor
        ithome_item.time = self.get_item_value(response.xpath('//span[@id="pubtime_baidu"]//text()').extract())
        ithome_item.time = TimeUtil.transfer_date(ithome_item.time)
        soup = BeautifulSoup(response.xpath('//div[@class="post_content"]').extract()[0], 'lxml')
        ithome_item.content = StrClean.clean_comment(soup.get_text())
        MongoClient.save_ithome_article(ithome_item)

        com_url = \
            "http://dyn.ithome.com/ithome/getajaxdata.aspx?newsID=" + article_id + "&type=commentpage&order=false&page="
        yield scrapy.Request(
            com_url + str(1),
            dont_filter='true',
            callback=self.generate_article_comment
        )

        com_sum_url = "http://dyn.ithome.com/comment/" + str(article_id)
        yield scrapy.Request(
            com_sum_url,
            dont_filter='true',
            callback=self.generate_article_comment_sum
        )

    def generate_article_comment_sum(self, response):
        com_sum_script = response.xpath("//html//script[1]//text()").extract()
        com_sum = 0
        if len(com_sum_script) > 1:
            com_sum_script = re.search(u'[\d]+', com_sum_script[1])
            try:
                com_sum = com_sum_script.group(0)
            except:
                com_sum = ''
        ithome_item = YIthomeItem()
        ithome_item._id = re.search(u'[\d]+', response.url).group(0)
        ithome_item.replies = str(com_sum)
        MongoClient.save_ithome_com_sum(ithome_item)

    def generate_article_comment(self, response):
        if response.body:
            ithome_item = YIthomeItem()
            ithome_item._id = re.search(u'[\d]+', response.url).group(0)
            comment = []
            new_comment = []
            for index, reply_content in enumerate(
                    response.xpath('//div[@class="comm"]').extract()):
                new_comment.append(BeautifulSoup(reply_content, 'lxml').get_text())
            for index, reply_content in enumerate(
                    response.xpath('//div[@class="re_comm"]').extract()):
                new_comment.append(BeautifulSoup(reply_content, 'lxml').get_text())
            new_comment.append(response.url)
            comment.append(new_comment)
            ithome_item.comment = comment
            MongoClient.save_ithome_article(ithome_item)

            com_url = response.url.split("page=")[0]
            pn = int(response.url.split("page=")[1])
            yield scrapy.Request(
                com_url + "page=" + str(pn + 1),
                dont_filter='true',
                meta={'com_url': com_url, 'pn': pn+1},
                callback=self.generate_article_comment
            )

    def parse(self, response):
        pass

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''
