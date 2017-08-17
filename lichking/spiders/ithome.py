# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
from lichking.util.time_util import *
from lichking.util.str_clean import *
from bs4 import BeautifulSoup


class IthomeSpider(scrapy.Spider):
    name = "ithome"
    allowed_domains = ["ithome.com"]
    start_urls = ['ithome.com']
    source_name = "IT之家"
    source_short = "ithome2"
    break_point_file_name = "ithome_break_point"
    start_page_num = 1
    page_num = 20  # 11789

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.8,
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
        ithome_item = YIthome2Item()
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
        ithome_item.time = self.format_rep_date(ithome_item.time)
        soup = BeautifulSoup(response.xpath('//div[@class="post_content"]').extract()[0], 'lxml')
        ithome_item.content = StrClean.clean_comment(soup.get_text())
        ithome_item.last_reply_time = self.format_rep_date(ithome_item.time)

        MongoClient.save_common_article(ithome_item, YIthome2Item)

        com_sum_url = "http://dyn.ithome.com/comment/" + str(article_id)
        yield scrapy.Request(
            com_sum_url,
            dont_filter='true',
            meta={'article_id': str(article_id)},
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
        ithome_item = YIthome2Item()
        ithome_item._id = re.search(u'[\d]+', response.url).group(0)
        ithome_item.replies = str(com_sum)
        MongoClient.save_ithome_com_sum(ithome_item)

        hash_key = response.xpath('//input[@id="hash"]/@value').extract()
        if len(hash_key) > 0:
            com_url = \
                "http://dyn.ithome.com/ithome/getajaxdata.aspx?newsID=" + response.meta['article_id']
            com_url += "&type=commentpage&order=false&hash="+hash_key[0]+"&page="
            yield scrapy.Request(
                com_url + str(1),
                dont_filter='true',
                callback=self.generate_article_comment
            )

    def generate_article_comment(self, response):
        if response.body:
            ithome_item = YIthome2Item()
            ithome_item._id = re.search(u'[\d]+', response.url).group(0)
            comment = []
            new_comment = {}
            comments_data = []
            rep_time_list = response.xpath('//div[starts-with(@class,"info")]/span[@class="posandtime"]').extract()
            for index, reply_content in enumerate(
                    response.xpath('//div[@class="comm"]').extract()):
                c = BeautifulSoup(reply_content, 'lxml').get_text()
                comments_data.append({'content': c, 'reply_time': self.format_rep_date(rep_time_list[index])})
            re_rep_time_list = response.xpath(
                '//div[starts-with(@class,"re_info")]/span[@class="posandtime"]').extract()
            for index, reply_content in enumerate(
                    response.xpath('//div[@class="re_comm"]').extract()):
                c = BeautifulSoup(reply_content, 'lxml').get_text()
                comments_data.append({'content': c, 'reply_time': self.format_rep_date(re_rep_time_list[index])})
            new_comment['url'] = response.url
            new_comment['comments_data'] = comments_data
            comment.append(new_comment)
            ithome_item.comment = comment
            pn = int(response.url.split("page=")[1])
            if pn == 1:
                ithome_item.last_reply_time = self.format_rep_date(rep_time_list[0])
            MongoClient.save_common_article(ithome_item, YIthome2Item)

            com_url = response.url.split("page=")[0]
            yield scrapy.Request(
                com_url + "page=" + str(pn + 1),
                dont_filter='true',
                meta={'com_url': com_url, 'pn': pn+1},
                callback=self.generate_article_comment
            )

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return ''

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''
