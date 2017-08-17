# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
import json
from bs4 import BeautifulSoup


class SanliukrSpider(scrapy.Spider):
    name = "36kr"
    allowed_domains = ["36kr.com"]
    start_urls = ['36kr.com']
    source_name = "36氪"
    source_short = "sanliukr"
    url_36kr_pre = "http://36kr.com"

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 1.2,
    }

    def __init__(self):
        self.source_name = "36氪"

    # scrapy start and check page num
    def start_requests(self):
        yield scrapy.Request(
            "http://36kr.com/",
            callback=self.generate_article_url
        )

    def generate_article_url(self, response):
        article_hrefs = re.findall(u'/p/[\d]+.html', response.body)
        for a_href in article_hrefs:
            yield scrapy.Request(
                self.url_36kr_pre + a_href,
                callback=self.generate_article_content
            )

        if re.search(u'/p/[\d]+.html', response.url) is None:
            return

    def generate_article_content(self, response):
        article_hrefs = re.findall(u'/p/[\d]+.html', response.body)
        for a_href in article_hrefs:
            yield scrapy.Request(
                self.url_36kr_pre + a_href,
                callback=self.generate_article_content
            )

        if re.search(u'/p/[\d]+.html', response.url) is None:
            return

        item = YSanliukrItem()
        item._id = re.search(u'/p/([\d]+).html', response.url).group(1)
        item.url = response.url
        item.source = self.source_name
        item.source_short = self.source_short
        # 文章内容在script标签内
        item = self.article_detail(item, response)
        MongoClient.save_common_article(item, YSanliukrItem)

        time_str = str(int(time.time()))
        url = 'http://36kr.com/api/comment?ctype=post&per_page=50&b_id=&_=' + time_str + '&cid=' + str(item._id)
        yield scrapy.Request(
            url,
            callback=self.generate_article_comment
        )

        yield scrapy.Request(
            'http://36kr.com/api/post/' + str(item._id) +'/next?_=' + time_str,
            callback=self.generate_article_next
        )

    def generate_article_next(self, response):
        next_json = json.loads(response.body)
        if next_json.get('code') != 0:
            return
        article_id = str(next_json.get('data').get('id'))
        yield scrapy.Request(
            self.url_36kr_pre + '/p/' + article_id + '.html',
            callback=self.generate_article_content
        )

    @staticmethod
    def generate_article_comment(response):
        a_comment = json.loads(response.body)
        if a_comment.get('code') != 0:
            return
        y_item = YSanliukrItem()
        comment = []
        new_comment = {}
        comments_data = []
        c_items = a_comment.get('data').get('items')
        if c_items is None or len(c_items) <= 0:
            return
        y_item._id = str(c_items[0].get('commentable_id'))
        y_item.last_reply_time = c_items[0].get('created_at')
        for c_item in a_comment.get('data').get('items'):
            comments_data.append({'content': c_item.get('content'),
                                  'reply_time': c_item.get('created_at')})
        new_comment['url'] = response.url
        new_comment['comments_data'] = comments_data
        comment.append(new_comment)
        y_item.comment = comment
        MongoClient.save_common_article(y_item, YSanliukrItem)

    @staticmethod
    def article_detail(aitem, response):
        for a_content in response.xpath('//script').extract():
            if a_content.find("detailArticle|post") == -1:
                continue
            a_content = a_content.split("props=")[1]
            a_content = a_content.split(",location")[0]
            a_content = json.loads(a_content).get("detailArticle|post")
            aitem.content = BeautifulSoup(a_content.get("content"), 'lxml').get_text()
            aitem.time = a_content.get('published_at')
            aitem.last_reply_time = aitem.time
            aitem.views = a_content.get('counters').get('view_count')
            aitem.replies = a_content.get('counters').get('comment')
            aitem.author = a_content.get('user').get('name')
            aitem.title = a_content.get('title')
            category_tags = json.loads(a_content.get('extraction_tags'))
            category = ''
            for category_tag in category_tags:
                category += category_tag[0] + ' '
            aitem.category = category

        return aitem


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl 36kr'.split())
