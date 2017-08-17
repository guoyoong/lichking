# -*- coding: utf-8 -*-
import scrapy
import json
from lichking.mongo.mongo_client import *
from bs4 import BeautifulSoup


def generate_product_category(response):
    category1 = response.xpath("//a[@id='category1']/text()").extract()[0]
    category_list = response.xpath('//span[@class="dropdown-text"]').extract()
    for i in range(len(category_list)):
        category1 += ('-' + BeautifulSoup(category_list[i], 'lxml').get_text())
    return category1


class SuningSpider(scrapy.Spider):

    def parse(self, response):
        pass

    name = "suning"
    allowed_domains = ["suning.com"]
    start_urls = ['https://list.suning.com/0-20006-0.html', 'https://list.suning.com/0-258003-0.html']
    source_name = '苏宁网'
    source_short = 'suning'
    list_url_pre = 'https://list.suning.com'
    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.8,
    }

    def start_requests(self):
        for part_url in self.start_urls:
            yield scrapy.Request(
                part_url,
                meta={"page_key": 0},
                callback=self.generate_productlist
            )

    # 说明 每个品类最多可以看前100页商品
    def generate_productlist(self, response):
        product_list = response.xpath("//a[@class='sellPoint']/@href").extract()
        for product_url in product_list:
            yield scrapy.Request(
                'http:' + product_url,
                callback=self.generate_product_detail
            )
        # 判断下一页
        # next_page = response.xpath("//a[@class='cur']/following-sibling::*[1]/@href").extract()[0]
        page_key = int(response.meta['page_key'])
        if page_key < 100:
            yield scrapy.Request(
                response.url.replace('-' + str(page_key) + '.html', '-' + str(page_key + 1) + '.html'),
                meta={"page_key": page_key+1},
                callback=self.generate_productlist
            )

    def generate_product_detail(self, response):
        product_id1 = re.search('/([\d]+)/', response.url).group(1)
        product_id2 = re.search('/([\d]+).html', response.url).group(1)
        category = generate_product_category(response)
        yield scrapy.Request(
            'http://review.suning.com/ajax/review_lists/general-000000000' + product_id2 +
                '-' + product_id1 + '-total-1-default-10-----reviewList.htm',
            callback=self.generate_product_comment,
            meta={"page_key": 1, "category": category, "url": response.url}
        )

    def generate_product_comment(self, response):
        page_key = int(response.meta['page_key'])
        next_url = response.url.replace('total-' + str(page_key), 'total-' + str(page_key + 1))
        commodity_reviews = json.loads(re.search('reviewList\((.*)\)', response.body).group(1)).get('commodityReviews')
        if len(commodity_reviews) > 0:
            # 增量抓取前3页评论
            if page_key < 3:
                yield scrapy.Request(
                    next_url,
                    callback=self.generate_product_comment,
                    meta={"page_key": page_key + 1, "category": response.meta['category'], "url": response.meta['url']}
                )
            for commodity_review in commodity_reviews:
                suning_item = YSuningItem()
                suning_item._id = str(commodity_review.get('commodityReviewId'))
                suning_item.content = commodity_review.get('content')
                suning_item.user_client = commodity_review.get('sourceSystem')
                suning_item.category = response.meta['category']
                suning_item.url = response.meta['url']
                suning_item.content_url = response.url
                suning_item.score = str(commodity_review.get('qualityStar'))
                suning_item.goods_score_name = self.generate_goods_score_name(suning_item.score)
                suning_item.source = self.source_name
                suning_item.source_short = self.source_short
                suning_item.title = commodity_review.get('commodityInfo').get('commodityName')
                suning_item.product_detail = suning_item.title
                suning_item.itemId = commodity_review.get('commodityInfo').get('commodityCode')
                suning_item.time = commodity_review.get('publishTime')
                suning_item.last_reply_time = commodity_review.get('publishTime')
                if 'againReview' in commodity_review:
                    suning_item.replies_comment = self.generate_reply_list(commodity_review, response.url)
                else:
                    suning_item.replies_comment = []
                suning_item.hotTags = self.generate_hot_tag(commodity_review)

                # 取得有用数和回复数
                yield scrapy.Request(
                    'https://review.suning.com/ajax/useful_count/' + str(commodity_review.get('commodityReviewId'))
                        + '-usefulCnt.htm',
                    callback=self.generate_comment_usefulcnt
                )

                MongoClient.save_common_onlineshop(suning_item, YSuningItem)

    def generate_comment_usefulcnt(self, response):
        review_userful = json.loads(re.search('usefulCnt\((.*)\)', response.body).group(1))
        if 'reviewUsefuAndReplylList' in review_userful:
            useful_dict = review_userful.get('reviewUsefuAndReplylList')
            suning_item = YSuningItem()
            c_id = str(useful_dict[0].get('commodityReviewId'))
            suning_item._id = c_id
            suning_item.useful_vote_count = str(useful_dict[0].get('usefulCount'))
            suning_item.replies = str(useful_dict[0].get('replyCount'))
            if useful_dict[0].get('replyCount') > 0:
                yield scrapy.Request(
                    'https://review.suning.com/ajax/reply_list/' + c_id + '--1-replylist.htm',
                    callback=self.generate_comment_replylist
                )
            MongoClient.save_suning_usefulcnt(suning_item, YSuningItem)

    @staticmethod
    def generate_comment_replylist(response):
        replylist = json.loads(re.search('replylist\((.*)\)', response.body).group(1)).get('replyList')[0]
        if 'replyList' in replylist:
            suning_item = YSuningItem()
            suning_item._id = str(replylist.get('commodityReviewId'))
            replylist = replylist.get('replyList')
            comments = []
            new_comment = {}
            comments_data = []
            for reply_detail in replylist:
                comments_data.append({'content': reply_detail.get('replyContent'),
                                      'reply_time': reply_detail.get('replyTime')})
            new_comment['url'] = response.url
            new_comment['comments_data'] = comments_data
            comments.append(new_comment)
            suning_item.replies_comment = comments
            suning_item.last_reply_time = comments_data[0]['reply_time']
            MongoClient.save_common_onlineshop(suning_item, YSuningItem)

    # 获取hot tag
    @staticmethod
    def generate_hot_tag(commodity_review):
        label_arr = []
        label_names = commodity_review.get('labelNames')
        for label_name in label_names:
            label_arr.append(label_name.get('labelName'))
        return label_arr

    # 获取评价str
    @staticmethod
    def generate_goods_score_name(star):
        if star == '1':
            return '差评'
        if star == '2' or star == '3':
            return '中评'
        return '好评'

    # 获取追加的评价
    @staticmethod
    def generate_reply_list(c_r, c_url):
        comments = []
        if 'againReview' in c_r:
            new_comment = {}
            comments_data = [{'content': c_r.get('againReview').get('againContent'),
                              'reply_time': c_r.get('againReview').get('publishTime')}]
            new_comment['url'] = c_url
            new_comment['comments_data'] = comments_data
        comments.append(new_comment)
        return comments
