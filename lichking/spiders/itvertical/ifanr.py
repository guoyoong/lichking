# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
import json
from bs4 import BeautifulSoup
from lichking.util.str_clean import *
from lxml import etree
import logging


class IfanrSpider(scrapy.Spider):
    name = "ifanr"
    allowed_domains = ["ifanr.com"]
    start_urls = ['ifanr.com']
    source_short = "ifanr"
    url_huxiu_pre = "https://www.ifanr.com"

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 1.2,
        'DEFAULT_REQUEST_HEADERS': {
            'user-agent':
                'Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
        }
    }

    def __init__(self):
        source_name = "爱范儿"

    # scrapy start and check page num
    def start_requests(self):
        yield scrapy.Request(
            "http://www.ifanr.com/",
            callback=self.generate_article_url
        )

    def generate_article_url(self, response):
        article_id = response.xpath("//div[contains(@class, 'article-item--card')]/@data-post-id").extract()
        for a_id in article_id:
            yield scrapy.Request(
                self.url_huxiu_pre + a_id,
                callback=self.generate_article_content
            )

    def generate_article_content(self, response):
        if re.search(u'/([\d]+)$', response.url) is None:
            return

        aitem = YIfanrItem()
        aitem._id = re.search(u'/([\d]+)$', response.url).group(1)
        aitem.url = response.url
        aitem.source = self.source_name
        aitem.source_short = self.source_short
        aitem.title = StrClean.get_safe_value_and_clean(
            response.xpath('//h1[@class="c-single-normal__title"]/text()').extract())
        aitem.author = StrClean.get_safe_value(
            response.xpath('//p[contains(@class, "c-card-author__name")]/text()').extract()[0])

        aitem.time = StrClean.get_safe_value(
            response.xpath("//meta[contains(@name, 'create_at')]/@content").extract()[0])
        aitem.last_reply_time = aitem.time
        aitem.content = StrClean.clean_comment(BeautifulSoup(
            response.xpath('//article[contains(@class, "c-article-content")]').extract()[0], 'lxml').get_text())

        category = ''
        for category_tag in response.xpath('//a[@class="c-article-tags__item"]/text()').extract():
            category += category_tag + ' '
        aitem.category = category

        MongoClient.save_common_article(aitem, YIfanrItem)

        # 请求评论数
        yield scrapy.Request(
            'https://www.huxiu.com/relatedArticle/' + str(aitem._id),
            callback=self.generate_related_article
        )

        url = 'https://www.huxiu.com/v2_action/comment_list?page=1&type=dateline&aid=' + aitem._id
        yield scrapy.Request(
            url,
            callback=self.generate_article_comment
        )


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl ifanr'.split())
