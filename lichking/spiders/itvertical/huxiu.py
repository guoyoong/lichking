# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
import json
from bs4 import BeautifulSoup
from lichking.util.str_clean import *
from lxml import etree


class HuXiuSpider(scrapy.Spider):
    name = "huxiu"
    allowed_domains = ["huxiu.com"]
    start_urls = ['huxiu.com']
    source_name = "虎嗅"
    source_short = "huxiu"
    url_huxiu_pre = "https://www.huxiu.com"

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 1.2,
    }

    def __init__(self):
        self.source_name = "虎嗅"

    # scrapy start and check page num
    def start_requests(self):
        yield scrapy.Request(
            "http://www.huxiu.com/",
            callback=self.generate_article_url
        )

    def generate_article_url(self, response):
        article_hrefs = re.findall(u'/article/[\d]+.html', response.body)
        for a_href in article_hrefs:
            yield scrapy.Request(
                self.url_huxiu_pre + a_href,
                callback=self.generate_article_content
            )

    def generate_article_content(self, response):
        if re.search(u'/article/[\d]+.html', response.url) is None:
            return

        aitem = YHuxiuItem()
        aitem._id = re.search(u'/article/([\d]+).html', response.url).group(1)
        aitem.url = response.url
        aitem.source = self.source_name
        aitem.source_short = self.source_short
        # 生成文章内容   //span[contains(@class,"threadlist_reply_date")
        aitem.time = response.xpath('//span[contains(@class, "article-time")]/text()').extract()[0] + ":00"
        aitem.last_reply_time = aitem.time
        aitem.replies = response.xpath('//span[contains(@class, "article-pl")]/text()').extract()[0].split("评论")[1]
        aitem.views = response.xpath('//span[contains(@class, "article-share")]/text()').extract()[0].split("收藏")[1]
        aitem.author = response.xpath(
            '//div[@class="article-author"]//span[@class="author-name"]//a/text()').extract()[0]
        aitem.title = StrClean.clean_comment(response.xpath('//h1[@class="t-h1"]/text()').extract()[0])
        aitem.content = BeautifulSoup(response.xpath('//div[contains(@class, "article-content-wrap")]').extract()[0],
                                      'lxml').get_text()
        category = ''
        for category_tag in response.xpath('//div[@class="tag-box "]//li[@class="transition"]/text()').extract():
            category += category_tag + ' '
        aitem.category = category

        MongoClient.save_common_article(aitem, YHuxiuItem)

        yield scrapy.Request(
            'https://www.huxiu.com/relatedArticle/' + str(aitem._id),
            callback=self.generate_related_article
        )

        url = 'https://www.huxiu.com/v2_action/comment_list?page=1&type=dateline&aid=' + aitem._id
        yield scrapy.Request(
            url,
            callback=self.generate_article_comment
        )

    def generate_related_article(self, response):
        a_ids = re.findall(u'data-id=\\\\\"([\d]+)\\\\\"', response.body)
        for a_id in a_ids:
            yield scrapy.Request(
                'https://www.huxiu.com/article/'+str(a_id)+'.html',
                callback=self.generate_article_content
            )

    def generate_article_comment(self, response):
        a_comment = json.loads(response.body)
        if a_comment.get('result') != 1:
            return
        y_item = YHuxiuItem()
        comment = []
        new_comment = {}
        comments_data = []
        c_items = a_comment.get('data')
        if c_items is None or len(c_items) <= 0:
            return
        y_item._id = re.search(u'aid=([\d]+)', response.url).group(1)
        r = etree.HTML(c_items)

        time_items = r.xpath('//span[@class="time"]//text()')
        pl_items = r.xpath('//div[@class="pl-content"]//text()')
        for i in range(len(pl_items)):
            pl_time = ''
            if i < len(time_items):
                if time_items[i].find("前") != -1:
                    pl_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
                else:
                    pl_time = time_items[i]
            comments_data.append({'content': pl_items[i],
                                  'reply_time': pl_time + ' 00:00:00'})
        new_comment['url'] = response.url
        new_comment['comments_data'] = comments_data
        comment.append(new_comment)
        y_item.comment = comment
        MongoClient.save_common_article(y_item, YHuxiuItem)
        if a_comment.get('cur_page') < a_comment.get('total_page'):
            url = 'https://www.huxiu.com/v2_action/comment_list?page=' + str(a_comment.get('cur_page'))\
                  + '&type=dateline&aid=' + str(y_item._id)
            yield scrapy.Request(
                url,
                callback=self.generate_article_comment
            )

if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl huxiu'.split())
