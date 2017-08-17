# -*- coding: utf-8 -*-

from mongo_item import *
import sys
from lichking.util.time_util import *
from lichking.settings import MONGODB_URI

reload(sys)
sys.setdefaultencoding('utf-8')


class MongoClient:
    connect('yuqing', host=MONGODB_URI['host'], port=MONGODB_URI['port'],
            username=MONGODB_URI['username'], password=MONGODB_URI['password'])

    def __init__(self):
        print 123

    @staticmethod
    def save_common_forum(forum_item, object_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forum_item.flag = '-1'
        if forum_item.title != '':
            forum_item.save()
        else:
            items = object_item.objects(_id=forum_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, forum_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                last_rtime = TimeUtil.compare_date_short(items[0].last_reply_time, forum_item.last_reply_time)
                items.update_one(set__last_reply_time=last_rtime)
                items.update_one(set__comment=n_comment)
                items.update_one(set__flag=forum_item.flag)

    @staticmethod
    def save_common_article(article_item, object_item):
        article_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        article_item.flag = '-1'
        if article_item.title != '':
            article_item.save()
        else:
            items = object_item.objects(_id=article_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, article_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                if article_item.last_reply_time != '':
                    last_rtime = TimeUtil.compare_date_short(items[0].last_reply_time, article_item.last_reply_time)
                    items.update_one(set__last_reply_time=last_rtime)
                items.update_one(set__comment=n_comment)
                items.update_one(set__flag=article_item.flag)

    @staticmethod
    def save_forum_views(forum_item, object_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forum_item.flag = '-1'
        items = object_item.objects(_id=forum_item._id)
        if len(items) > 0:  # not
            items.update_one(set__insert_time=forum_item.insert_time)
            items.update_one(set__flag=forum_item.flag)
            items.update_one(set__views=forum_item.views)

    @staticmethod
    def save_forum_replies(forum_item, object_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forum_item.flag = '-1'
        items = object_item.objects(_id=forum_item._id)
        if len(items) > 0:  # not
            items.update_one(set__insert_time=forum_item.insert_time)
            items.update_one(set__flag=forum_item.flag)
            items.update_one(set__replies=forum_item.replies)

    @staticmethod
    def save_ithome_com_sum(article_item):
        if article_item.replies != '':
            items = YIthome2Item.objects(_id=article_item._id)
            if len(items) > 0:
                items.update_one(set__replies=article_item.replies)

    @staticmethod
    def save_common_onlineshop(shop_item, object_item):
        shop_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        shop_item.flag = '-1'
        if shop_item.title != '':
            shop_item.save()
        else:
            items = object_item.objects(_id=shop_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].replies_comment, shop_item.replies_comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                last_rtime = TimeUtil.compare_date_short(items[0].last_reply_time, shop_item.last_reply_time)
                items.update_one(set__last_reply_time=last_rtime)
                items.update_one(set__replies_comment=n_comment)
                items.update_one(set__flag=shop_item.flag)

    @staticmethod
    def save_suning_usefulcnt(shop_item, object_item):
        shop_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        shop_item.flag = '-1'
        items = object_item.objects(_id=shop_item._id)
        if len(items) > 0:  # not
            items.update_one(set__insert_time=shop_item.insert_time)
            items.update_one(set__useful_vote_count=shop_item.useful_vote_count)
            items.update_one(set__replies=shop_item.replies)

    # 评论去重
    @staticmethod
    def remove_duplicate_comment(source_comments, new_comment):
        index = sys.maxint
        for i in range(0, len(source_comments)):
            if source_comments[i]['url'] == new_comment['url']:
                index = i
        # modify
        if index != sys.maxint:
            source_comments[index] = new_comment
        else:
            source_comments.append(new_comment)
        return source_comments

