# -*- coding: utf-8 -*-
import scrapy


class PconlineSpider(scrapy.Spider):
    name = "pconline"
    allowed_domains = ["pconline.com"]
    start_urls = ['http://pconline.com/']

    news_url = ['http://news.pconline.com.cn/it/', 'http://news.pconline.com.cn/mobile/',
                'http://news.pconline.com.cn/office/', 'http://news.pconline.com.cn/digital/']