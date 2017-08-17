# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
from lichking.util.time_util import *
from lichking.util.str_clean import *
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')


class CnmoSpider(scrapy.Spider):
    name = "cnmo_forum"
    allowed_domains = ["cnmo.com"]
    start_urls = ['http://bbs.cnmo.com/boardmap/']
    source_name = "手机中国论坛"
    source_short = "cnmo_forum2"
    # 有几个版块特殊，有单独域名
    forum_url = ['http://dopodbbs.cnmo.com/forum-6-1.html', 'http://htcbbs.cnmo.com/forum-12788-1.html',
                 'http://elifebbs.cnmo.com/forum-16198-1.html', 'http://lenovobbs.cnmo.com/forum-14788-1.html',
                 'http://motobbs.cnmo.com/forum-11122-1.html', 'http://nubiabbs.cnmo.com/forum-16193-1.html',
                 'http://iphonebbs.cnmo.com/forum-6975-1.html', 'http://sebbs.cnmo.com/forum-4-1.html',
                 'http://samsungbbs.cnmo.com/forum-5338-1.html', 'http://sonybbs.cnmo.com/forum-15504-1.html',
                 'http://oneplusbbs.cnmo.com/forum-16153-1.html', 'http://wpbbs.cnmo.com/forum-2138-1.html',
                 'http://androidbbs.cnmo.com/forum-15207-1.html', 'http://padbbs.cnmo.com/forum-15019-2.html']

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.8,
    }

    def __init__(self):
        print 'init'

    # 爬取版块地址
    def start_requests(self):
        yield scrapy.Request(
            'http://bbs.cnmo.com/boardmap/',
            dont_filter='true',
            callback=self.generate_forum_url_list
        )
        # 供测试版块
        # yield scrapy.Request(
        #     'http://bbs.cnmo.com/forum-16313-1.html',
        #     meta={"page_key": 1},
        #     callback=self.get_record_list
        # )

    def generate_forum_url_list(self, response):
        all_a_tags = response.xpath('//a/@href').extract()
        forum_dict = {}
        for a_tag in all_a_tags:
            if a_tag.find("forum") != -1:
                if a_tag in forum_dict:
                    forum_dict[a_tag] += 1
                else:
                    forum_dict[a_tag] = 1
        for a_href in forum_dict:
            yield scrapy.Request(
                a_href,
                meta={"page_key": 1},
                dont_filter='true',
                callback=self.get_record_list
            )
        # 单独域名的版块
        for a_href in self.forum_url:
            yield scrapy.Request(
                a_href,
                meta={"page_key": 1},
                dont_filter='true',
                callback=self.get_record_list
            )

    def get_record_list(self, response):
        flag = -1
        # check 是否有新帖
        rep_time_list = response.xpath('//span[@class="fea-time"]/text()').extract()
        if len(rep_time_list) > 0:
            # if 1 == 1:
            rep_time = rep_time_list[0].strip()
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            page_key = int(response.meta['page_key'])
            # 只爬第一页 或者有新回复的帖子
            if rep_time == today or rep_time == yestday or page_key == 1:
                flag = 1
                # 请求下一页
                page_box = response.xpath('//div[contains(@class, "pagebox")]//a/@title').extract()
                page_href = response.xpath('//div[contains(@class, "pagebox")]//a/@href').extract()
                if len(page_box) > 0:
                    if page_box[-1] == '下一页':
                        cnmo_url_pre = response.url.split('forum')[0]
                        yield scrapy.Request(
                            cnmo_url_pre + page_href[-1],
                            meta={"page_key": -1},
                            callback=self.get_record_list
                        )
        # 爬取当页数据
        if flag != -1:
            for cnmo_url in response.xpath(
                    '//div[@class="wrap2 feaList"]//p[@class="fea-tit"]//a[@target="_blank"]/@href').extract():
                yield scrapy.Request(
                    cnmo_url,
                    callback=self.generate_forum_page
                )

    def generate_forum_page(self, response):
        forum_url = re.search(u'[\d]+', response.url.split("/")[3])
        try:
            forum_url = forum_url.group(0)
        except:
            forum_url = ''
        forum_item = YCnmoForum2Item()
        forum_item._id = forum_url
        forum_item.url = response.url
        forum_item.source = self.source_name
        forum_item.source_short = self.source_short

        if response.url[len(response.url) - 9:] == '-1-1.html':
            category1 = self.get_item_value(response.xpath('//div[@class="bcrumbs"]//a[1]/text()').extract())
            category2 = self.get_item_value(response.xpath('//div[@class="bcrumbs"]//a[2]/text()').extract())
            category3 = self.get_item_value(response.xpath('//div[@class="bcrumbs"]//a[3]/text()').extract())
            forum_item.category = category1 + '-' + category2 + '-' + category3
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
            rep_time_list = response.xpath('//div[@class="bcom_detail"]//span[2]/text()').extract()
            if len(rep_time_list) > 0:
                forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            MongoClient.save_common_forum(forum_item, YCnmoForum2Item)
            if len(response.xpath('//span[@class="bornone"]')) > 0:
                page_num = response.xpath('//div[@class="List-pages fr"]//a/text()').extract()[-3]
                page_num = int(page_num.replace('.', ''))
                # 回复太多的帖子 大部分为水贴或者活动帖子，每天只爬最后二十页
                start_page = 2
                if page_num > 40:
                    start_page = page_num - 20
                for page in range(start_page, page_num + 1):
                    cnmo_url = response.url[:len(response.url) - 8] + str(page) + '-1.html'
                    yield scrapy.Request(
                        cnmo_url,
                        callback=self.generate_forum_page
                    )
        else:
            forum_item.title = ''
            forum_item.comment = self.gen_item_comment(response)
            rep_time_list = response.xpath('//div[@class="bcom_detail"]//span[2]/text()').extract()
            if len(rep_time_list) > 0:
                forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            MongoClient.save_common_forum(forum_item, YCnmoForum2Item)

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return ''

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return ''

    def gen_item_comment(self, response):
        comment = []
        new_comment = {}
        comments_data = []
        rep_time_list = response.xpath('//div[@class="bcom_detail"]//span[2]/text()').extract()
        for indexi, content in enumerate(response.xpath('//div[@class="bcom_text"]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            c = StrClean.clean_unicode(soup.get_text())
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
