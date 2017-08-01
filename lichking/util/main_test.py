# coding=utf-8

from apscheduler.schedulers.twisted import TwistedScheduler
from apscheduler.triggers.cron import *
from apscheduler.triggers.interval import *
from lichking.mongo.mongo_item import *
from lichking.settings import MONGODB_URI
from mongoengine.queryset.visitor import Q
import logging
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
import datetime
from lichking.util.time_util import *

connect('yuqing', host='10.100.2.225', username='yuqing', password='123456')
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
crawl_pages = YLenovoForum2Item.objects(Q(insert_time__gte="2017-06-01 00:00:00") & Q(insert_time__lte="2017-07-01 00:00:00"))
if len(crawl_pages) > 0:
    date1 = crawl_pages.order_by('insert_time')[0].insert_time
    date2 = crawl_pages.order_by('-insert_time')[0].insert_time
    print TimeUtil.get_date_diff_seconds(date1, date2)

