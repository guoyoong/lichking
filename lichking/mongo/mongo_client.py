# coding=utf-8

from mongo_item import *
import datetime
import sys
from lichking.util.time_util import *

reload(sys)
sys.setdefaultencoding('utf-8')

# connect('yuqing', host='10.100.2.225', username='yuqing', password='123456')
# item.save()

# for pos in range(1, 213):
#     items = YLenovoMobileItem.objects.order_by("+_id")[(pos-1):(pos+1)]
#     print items[0]._id
# comment = items[0].comment
# n_comment = []
# items.update_one(set__title="mytitle1")
# items.update_one(set__insert_time="my_inserttime1")

# item.title = 'title123'
# comment = item.comment
# comment.append(item2.comment[0])
# item2.comment = comment
# item2.save()
# item.save()
# print hasattr(item, 'title1')
# YLenovoForumItem.objects(_id="thread-2783010").update(set__comment=comment)

# source_comments = remove_duplicate_comment(item.comment, new_comment)
# item.comment = source_comments
# item.save()


class MongoClient:
    def __init__(self):
        print 123

    @staticmethod
    def save_forum_item(forum_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if forum_item.title != '':
            forum_item.save()   # fisrt
        else:
            items = YLenovoForum2Item.objects(_id=forum_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, forum_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                last_rtime = TimeUtil.compare_date_short(items[0].last_reply_time, forum_item.last_reply_time)
                items.update_one(set__last_reply_time=last_rtime)
                items.update_one(set__comment=n_comment)

    @staticmethod
    def save_mobile_item(forum_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if forum_item.title != '':
            forum_item.save()   # fisrt
        else:
            items = YLenovoMobile2Item.objects(_id=forum_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, forum_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                last_rtime = TimeUtil.compare_date_short(items[0].last_reply_time, forum_item.last_reply_time)
                items.update_one(set__last_reply_time=last_rtime)
                items.update_one(set__comment=n_comment)

    @staticmethod
    def save_ithome_article(article_item):
        article_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        article_item.flag = '-1'
        if article_item.title != '':
            article_item.save()
        else:
            items = YIthome2Item.objects(_id=article_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, article_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                if article_item.last_reply_time != '':
                    items.update_one(set__last_reply_time=article_item.last_reply_time)
                items.update_one(set__comment=n_comment)

    @staticmethod
    def save_ithome_com_sum(article_item):
        if article_item.replies != '':
            items = YIthome2Item.objects(_id=article_item._id)
            if len(items) > 0:
                items.update_one(set__replies=article_item.replies)

    @staticmethod
    def save_tieba_item(tieba_item):
        tieba_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tieba_item.flag = '-1'
        if tieba_item.title != '':
            tieba_item.save()
        else:
            items = YBaiduTieba2Item.objects(_id=tieba_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, tieba_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                last_rtime = TimeUtil.compare_date_short(items[0].last_reply_time, tieba_item.last_reply_time)
                items.update_one(set__last_reply_time=last_rtime)
                items.update_one(set__insert_time=insert_time)
                items.update_one(set__comment=n_comment)

    @staticmethod
    def save_cnmo_forum(forum_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forum_item.flag = '-1'
        if forum_item.title != '':
            forum_item.save()
        else:
            items = YCnmoForum2Item.objects(_id=forum_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, forum_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                items.update_one(set__last_reply_time=forum_item.last_reply_time)
                items.update_one(set__comment=n_comment)

    @staticmethod
    def save_ihei5_forum(forum_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forum_item.flag = '-1'
        if forum_item.title != '':
            forum_item.save()
        else:
            items = YIhei52Item.objects(_id=forum_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, forum_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                last_rtime = TimeUtil.compare_date_short(items[0].last_reply_time, forum_item.last_reply_time)
                items.update_one(set__last_reply_time=last_rtime)
                items.update_one(set__comment=n_comment)

    @staticmethod
    def save_it168_forum(forum_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forum_item.flag = '-1'
        if forum_item.title != '':
            forum_item.save()
        else:
            items = YIt168Item.objects(_id=forum_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, forum_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                items.update_one(set__last_reply_time=forum_item.last_reply_time)
                items.update_one(set__comment=n_comment)

    @staticmethod
    def save_zhiyoo_forum(forum_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forum_item.flag = '-1'
        if forum_item.title != '':
            forum_item.save()
        else:
            items = YZhiyooItem.objects(_id=forum_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, forum_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                items.update_one(set__last_reply_time=forum_item.last_reply_time)
                items.update_one(set__comment=n_comment)

    @staticmethod
    def save_hiapk_forum(forum_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forum_item.flag = '-1'
        if forum_item.title != '':
            forum_item.save()
        else:
            items = YHiapkItem.objects(_id=forum_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, forum_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                items.update_one(set__last_reply_time=forum_item.last_reply_time)
                items.update_one(set__comment=n_comment)

    @staticmethod
    def save_angeeks_forum(forum_item):
        forum_item.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        forum_item.flag = '-1'
        if forum_item.title != '':
            forum_item.save()
        else:
            items = YAngeeksItem.objects(_id=forum_item._id)
            if len(items) > 0:  # not
                n_comment = \
                    MongoClient.remove_duplicate_comment(items[0].comment, forum_item.comment[0])
                insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                items.update_one(set__insert_time=insert_time)
                items.update_one(set__last_reply_time=forum_item.last_reply_time)
                items.update_one(set__comment=n_comment)

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

