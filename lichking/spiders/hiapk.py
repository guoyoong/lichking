# -*- coding: utf-8 -*-
import scrapy
from lichking.util.str_clean import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging


class HiapkSpider(scrapy.Spider):
    name = "hiapk"
    allowed_domains = ["hiapk.com"]
    start_urls = ['http://bbs.hiapk.com/']
    forum_list_file = 'hiapk_forum_list_file'
    source_name = '安卓论坛'
    source_short = 'hiapk'
    max_reply = 200
    forum_dict = {"http://bbs.hiapk.com/forum-183-1.html", "http://bbs.hiapk.com/forum-10-1.html",
                  "http://games.hiapk.com/forum-65-1.html","http://bbs.hiapk.com/forum-86-1.html" }

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 1.2,
    }

    def start_requests(self):
        yield scrapy.Request(
            'http://bbs.hiapk.com/',
            meta={"page_key": 1},
            callback=self.generate_forum
        )
        # yield scrapy.Request(
        #     'http://bbs.hiapk.com/forum-1378-1.html',
        #     dont_filter='true',
        #     callback=self.generate_forum_page_list
        # )

    def generate_forum(self, response):
        forum_list = response.xpath('//td[@class="fl_g"]//dl//dt//a/@href').extract()
        if len(forum_list) > 0:
            for forum_url in forum_list:
                f_url = forum_url
                if forum_url.find('bbs.hiapk.com') == -1:
                    f_url = 'http://bbs.hiapk.com/' + forum_url
                if f_url not in self.forum_dict:
                    yield scrapy.Request(
                        f_url,
                        meta={"page_key": 1},
                        callback=self.generate_forum
                    )

        hiapk_url_pre = response.url.split('forum')[0]
        # check 是否有下一页
        pg_bar = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()
        page_key = int(response.meta['page_key'])
        rep_time_list = response.xpath('//tr/td[@class="by"]/em/a').extract()
        if len(pg_bar) > 0:
            if page_key == 1 or self.check_rep_date(rep_time_list):
                yield scrapy.Request(
                    hiapk_url_pre + pg_bar[0],
                    meta={"page_key": -1},
                    callback=self.generate_forum
                )

                # scrapy all tie url
                thread_list = response.xpath('//a[@class="xst"]/@href').extract()
                logging.error(len(thread_list))
                if len(thread_list) > 0:
                    for thread_url in thread_list:
                        yield scrapy.Request(
                            hiapk_url_pre + thread_url,
                            callback=self.generate_forum_thread
                        )

    def generate_forum_thread(self, response):
        forum_id = re.search(u'thread-([\d]+)', response.url)
        try:
            forum_id = forum_id.group(1)
        except:
            forum_id = re.search(u'tid=([\d]+)', response.url).group(1)
        forum_item = YHiapkItem()
        forum_item._id = forum_id
        crawl_next = True
        if len(response.xpath('//a[@class="prev"]').extract()) == 0:
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url
            forum_item.views = StrClean.clean_comment(response.xpath('//span[@class="xi1"]/text()').extract()[0])
            forum_item.replies = \
                StrClean.clean_comment(response.xpath('//span[@class="xi1"]/text()').extract()[1])
            category1 = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[2]/text()').extract())
            category2 = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[3]/text()').extract())
            category3 = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[4]/text()').extract())
            forum_item.category = category1 + '-' + category2 + '-' + category3

            rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
            forum_item.time = self.format_rep_date(rep_time_list[0])
            forum_item.title = StrClean.clean_comment(
                response.xpath('//a[@id="thread_subject"]/text()').extract()[0])
            c_soup = BeautifulSoup(response.xpath(
                '//div[@class="pct"]//table[1]').extract()[0], 'lxml')
            [s.extract() for s in c_soup('script')]  # remove script tag
            forum_item.content = c_soup.get_text()
            forum_item.content = StrClean.clean_comment(forum_item.content)
            forum_item.comment = self.gen_item_comment(response)
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            if int(forum_item.replies) > self.max_reply:
                crawl_next = False

            MongoClient.save_common_forum(forum_item, YHiapkItem)
        else:
            forum_item.title = ''
            rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_common_forum(forum_item, YHiapkItem)

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
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def gen_item_comment(self, response):
        comment = []
        new_comment = {}
        comments_data = []
        rep_time_list = response.xpath('//div[@class="authi"]//em').extract()
        for indexi, content in enumerate(response.xpath('//div[@class="t_fsz"]//table[1]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            [s.extract() for s in soup('script')]  # remove script tag
            c = StrClean.clean_comment(soup.get_text())
            if indexi >= len(rep_time_list):
                rep_time = self.format_rep_date(rep_time_list[-1])
            else:
                rep_time = self.format_rep_date(rep_time_list[indexi])
            comments_data.append({'content': c, 'reply_time': rep_time})
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

    @staticmethod
    def check_rep_date(rep_time_list):
        try:
            date_source = rep_time_list[0]
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
