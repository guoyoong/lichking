# -*- coding: utf-8 -*-
import scrapy
from lichking.util.str_clean import *
from bs4 import BeautifulSoup
from lichking.mongo.mongo_client import *
import logging
import json


class PcpopSpider(scrapy.Spider):
    name = "pcpop"
    allowed_domains = ["pcpop.com","changyan.sohu.com"]
    start_urls = ['http://www.pcpop.com/']
    source_name = '泡泡网'
    source_short = 'pcpop'
    max_reply = 200
    # 过滤掉一些新闻、广告版块
    channel_list = [1, 2, 3, 4, 5, 6, 7, 9, 10, 12, 13, 14]
    # channel_list = [1]
    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.8,
    }

    def start_requests(self):
        for channel in self.channel_list:
            yield scrapy.Request(
                'http://www.pcpop.com/pcpop-api/article/articlelist_artset/?channel=' + str(channel) + '&index=1',
                callback=self.generate_articlelist,
                meta={"page_key": "1"}
            )

    def generate_articlelist(self, response):
        if response.body.find("list") == -1:
            return
        articlelist = json.loads(response.body)
        page_key = int(response.meta['page_key'])
        # if 1 == 1:
        if page_key == 1 or self.check_rep_time(response.body):
            yield scrapy.Request(
                response.url.replace(re.search(u'index=[\d]+', response.url).group(0), 'index='+str(page_key+1)),
                callback=self.generate_articlelist,
                meta={"page_key": str(page_key+1)}
            )
            # scrapy all article
            for artUrl in articlelist['list']:
                yield scrapy.Request(
                    artUrl['ArtUrl'],
                    callback=self.generate_article_detail
                )

    def generate_article_detail(self, response):
        article_item = YPcpopItem()
        article_id = re.search(u'/([\d]+).shtml', response.url)
        try:
            article_id = article_id.group(1)
        except:
            return
        article_item._id = article_id
        article_item.source = self.source_name
        article_item.source_short = self.source_short
        article_item.url = response.url
        article_item.category = ''
        for i in range(0, len(response.xpath('//div[@class="crumbs"]/a').extract())):
            if i == 0:
                article_item.category = response.xpath('//div[@class="crumbs"]/a/text()').extract()[i]
            else:
                article_item.category = article_item.category + '-' + \
                                        response.xpath('//div[@class="crumbs"]/a/text()').extract()[i]
        article_item.time = self.format_rep_time(response.xpath('//div[@class="chuchu"]').extract())
        article_item.title = StrClean.clean_comment(response.xpath('//div[@class="l1"]/h1/text()').extract()[0])
        c_soup = BeautifulSoup(response.xpath(
            '//div[@class="main"]').extract()[0], 'lxml')
        [s.extract() for s in c_soup('script')]  # remove script tag
        if c_soup.find('div', class_='attach_nopermission attach_tips') is not None:
            c_soup.find('div', class_='attach_nopermission attach_tips').clear()
        article_item.content = c_soup.get_text()
        article_item.content = StrClean.clean_comment(article_item.content)
        article_item.comment = []
        article_item.last_reply_time = article_item.time
        article_item.replies = "0"
        article_item.views = "0"

        yield scrapy.Request(
            'http://changyan.sohu.com/api/2/topic/load?client_id=cyrYYYfxG&topic_url=' + response.url,
            meta={"article_id": article_id},
            callback=self.get_changyan_topic_id
        )

        MongoClient.save_common_forum(article_item, YPcpopItem)

    def get_changyan_topic_id(self, response):
        article_item = YPcpopItem()
        article_item._id = response.meta['article_id']
        comment_all = json.loads(response.body)
        if 'cmt_sum' in comment_all:
            article_item.replies = str(comment_all['cmt_sum'])
        if 'participation_sum' in comment_all:
            article_item.views = str(comment_all['participation_sum'])
        MongoClient.save_forum_views(article_item, YPcpopItem)
        MongoClient.save_forum_replies(article_item, YPcpopItem)
        if 'topic_id' in comment_all:
            yield scrapy.Request(
                'http://changyan.sohu.com/api/2/topic/comments?&client_id=cyrYYYfxG&page_size=100&page_no=1&topic_id='+
                str(comment_all['topic_id']),
                meta={"article_id": article_item._id, "page_no":1, "topic_id":str(comment_all['topic_id'])},
                callback=self.get_changyan_comment
            )

    def get_changyan_comment(self, response):
        comments_list = json.loads(response.body)
        if 'comments' in comments_list:
            comments_list = comments_list['comments']
            comment = []
            new_comment = {}
            comments_data = []
            if len(comments_list) > 0:
                for comment_item in comments_list:
                    c = StrClean.clean_comment(comment_item['content'])
                    rep_time = self.format_rep_date_from_stamp(comment_item['create_time'])
                    comments_data.append({'content': c, 'reply_time': rep_time})
                new_comment['url'] = response.url
                new_comment['comments_data'] = comments_data
                comment.append(new_comment)

                article_item = YPcpopItem()
                article_item._id = response.meta['article_id']
                article_item.title = ''
                article_item.last_reply_time = self.format_rep_date_from_stamp(comments_list[0]['create_time'])
                article_item.comment = comment
                MongoClient.save_common_forum(article_item, YPcpopItem)

                new_page_no = str(int(response.meta['page_no']) + 1)
                yield scrapy.Request(
                    'http://changyan.sohu.com/api/2/topic/comments?&client_id=cyrYYYfxG&page_size=100&page_no='+
                    new_page_no +'&topic_id=' + str(response.meta['topic_id']),
                    meta={"article_id": article_item._id, "page_no": new_page_no, "topic_id": str(response.meta['topic_id'])},
                    callback=self.get_changyan_comment
                )

    @staticmethod
    def check_rep_time(articlelist):
        try:
            date_source = articlelist
            date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2}', date_source).group(0)
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d'))
            date_source = time.strftime('%Y-%m-%d', time.localtime(timestamp))
            logging.error(date_source)
            if date_source == today or date_source == yestday:
                return True
        except:
            return False
        return False

    @staticmethod
    def format_rep_time(rep_time_source):
        if len(rep_time_source) <= 0:
            return ''
        try:
            rep_time_source = rep_time_source[0]
            rep_time_source = rep_time_source.replace(u'年', u'-')
            rep_time_source = rep_time_source.replace(u'月', u'-')
            rep_time_source = rep_time_source.replace(u'日', u'')
            rep_time_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', rep_time_source).group(0)
            timestamp = time.mktime(time.strptime(rep_time_source, '%Y-%m-%d %H:%M'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return ''

    @staticmethod
    def format_rep_date_from_stamp(rep_time_source):
        try:
            rep_time_source = int(rep_time_source) / 1000
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rep_time_source))
        except:
            return ''
