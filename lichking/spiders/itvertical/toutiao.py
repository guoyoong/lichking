# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
import json
from lichking.util.time_util import *
from bs4 import BeautifulSoup
import random
import string


class ToutiaoSpider(scrapy.Spider):
    name = "toutiao"
    allowed_domains = ["toutiao.com"]
    start_urls = ['toutiao.com']
    source_name = "今日头条"
    source_short = "toutiao"
    toutiao_url_pre = 'http://www.toutiao.com'

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 1.2,
    }

    def __init__(self):
        self.source_name = "今日头条"

    # scrapy start and check page num
    def start_requests(self):
        yield scrapy.Request(
            "http://www.toutiao.com/api/pc/feed/?category=news_tech&" +
                "tadrequire=true&as=A1E559C9D4812DE&cp=599411522D1E6E1",
            callback=self.generate_article_url
        )

    def generate_article_url(self, response):
        as_id = ''.join(random.sample(string.ascii_letters + string.digits, 15))
        cp_id = ''.join(random.sample(string.ascii_letters + string.digits, 15))
        yield scrapy.Request(
            "http://www.toutiao.com/api/pc/feed/?category=news_tech&" +
            "tadrequire=true&as=" + as_id + "&cp=" + cp_id + "&t=" + str(time.time()),
            callback=self.generate_article_url
        )
        article_list = json.loads(response.body)
        if article_list.get("message") != "success":
            return
        for article_detail in article_list.get('data'):
            # wenda gallery ad 图
            # news_tech and news_finance
            tag_url = article_detail.get('tag_url')
            if article_detail.get('article_genre') == 'article'\
                    and (tag_url == 'news_tech' or tag_url == 'news_finance'):
                yield scrapy.Request(
                    self.toutiao_url_pre + article_detail.get('source_url'),
                    callback=self.generate_article_content
                )

    def generate_article_content(self, response):

        item = YToutiaoItem()
        item.url = response.url
        item.source = self.source_name
        item.source_short = self.source_short
        item._id = re.search(u"/?([\d]+)", response.url).group(1)
        # 文章内容在script标签内
        for a_content in response.xpath('//script').extract():
            if a_content.find("BASE_DATA") == -1:
                continue
            a_content = a_content.split("BASE_DATA =")[1]
            a_content = a_content.split(";</script>")[0]
            # 是一个js字面量，不是json
            item.title = re.search(u"title: \'(.*)\'", a_content).group(1)
            item.content = BeautifulSoup(re.search(u"content: \'(.*)\'\.replace\(", a_content).group(1),
                                          'lxml').get_text()
            item.content = BeautifulSoup(item.content, 'lxml').get_text()
            item.author = re.search(u"name: \'(.*)\'", a_content).group(1)
            item.time = re.search(u"time: \'(.*)\'", a_content).group(1) + ':00'
            item.last_reply_time = item.time
            item.category = re.search(u"chineseTag: \'(.*)\'", a_content).group(1)
            item.replies = re.search(u"comments_count: (.*),", a_content).group(1)
            group_id = re.search(u"groupId: \'(.*)\'", a_content).group(1)
            item_id = re.search(u"itemId: \'(.*)\'", a_content).group(1)
            MongoClient.save_common_article(item, YToutiaoItem)

            # 抓取回复内容
            yield scrapy.Request(
                'http://www.toutiao.com/api/comment/list/?group_id=' + group_id +
                    '&item_id=' + item_id + '&offset=0&count=500',
                callback=self.generate_article_comment,
                meta={"article_id": item._id}
            )

    def generate_article_comment(self, response):
        y_item = YToutiaoItem()
        y_item._id = response.meta['article_id']
        c_content = json.loads(response.body)
        if c_content.get("message") != "success":
            return
        comment = []
        new_comment = {}
        comments_data = []
        c_items = c_content.get('data').get('comments')
        if c_items is None or len(c_items) <= 0:
            return
        y_item.last_reply_time = TimeUtil.timestamp_to_format_date(c_items[0].get('create_time'))
        for c_item in c_items:
            comments_data.append({'content': c_item.get('text'),
                                  'reply_time': TimeUtil.timestamp_to_format_date(c_item.get('create_time'))})
            if c_item.get('reply_count') > 0:
                yield scrapy.Request(
                    'http://www.toutiao.com/api/comment/get_reply/?comment_id=' + str(c_item.get('id')) +
                        '&dongtai_id='+str(c_item.get('dongtai_id'))+'&offset=0&count=500',
                    callback=self.generate_article_recomment,
                    meta={"article_id": y_item._id}
                )
        new_comment['url'] = response.url
        new_comment['comments_data'] = comments_data
        comment.append(new_comment)
        y_item.comment = comment
        MongoClient.save_common_article(y_item, YToutiaoItem)

    @staticmethod
    def generate_article_recomment(response):
        y_item = YToutiaoItem()
        y_item._id = response.meta['article_id']
        c_content = json.loads(response.body)
        if c_content.get("message") != "success":
            return
        comment = []
        new_comment = {}
        comments_data = []
        c_items = c_content.get('data').get('data')
        if c_items is None or len(c_items) <= 0:
            return
        y_item.last_reply_time = TimeUtil.timestamp_to_format_date(c_items[0].get('create_time'))
        for c_item in c_items:
            comments_data.append({'content': c_item.get('text'),
                                  'reply_time': TimeUtil.timestamp_to_format_date(c_item.get('create_time'))})
        new_comment['url'] = response.url
        new_comment['comments_data'] = comments_data
        comment.append(new_comment)
        y_item.comment = comment
        MongoClient.save_common_article(y_item, YToutiaoItem)

if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl toutiao'.split())
