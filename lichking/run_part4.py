# coding=utf-8
# 统计每日的爬虫数据抓取数量


from apscheduler.schedulers.twisted import TwistedScheduler
from apscheduler.triggers.cron import *
from apscheduler.triggers.interval import *
from lichking.mongo.mongo_item import *
from lichking.settings import MONGODB_URI
from mongoengine.queryset.visitor import Q
import logging
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from lichking.util.time_util import *
from lichking.util.md5_util import *


configure_logging()
forum_source_arr = {
    "zhiyoo": YZhiyooItem,
    "baidu_tieba2": YBaiduTieba2Item,
    "shayu_forum": YShayuForumItem,
    "pconline": YPconlineItem,
    "lenovo_forum2": YLenovoForum2Item,
    "ithome2": YIthome2Item,
    "it168": YIt168Item,
    "imobile": YImobileItem,
    "ihei52": YIhei52Item,
    "hiapk": YHiapkItem,
    "gfan": YGfanForumItem,
    "cnmo_forum2": YCnmoForum2Item,
    "angeeks": YAngeeksItem,
    "zol": YZolItem,
    "pcpop": YPcpopItem,
    "suning": YSuningItem
}
online_shop_source_arr = {
    "jd": YJdItem,
}
media_source_arr = {
    
}


def print_time(source_type, source_name, document_item):
    today = datetime.datetime.now().strftime("%Y-%m-%d") + " 00:00:00"
    yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d') + " 00:00:00"
    connect('yuqing', host=MONGODB_URI['host'], port=MONGODB_URI['port'],
            username=MONGODB_URI['username'], password=MONGODB_URI['password'])
    crawl_pages = document_item.objects(Q(insert_time__gte=yestday) & Q(insert_time__lte=today))
    new_pages = document_item.objects(Q(time__gte=yestday) & Q(time__lte=today)).count()
    ymonitor = YuqingSpiderMonitor()
    ymonitor.key = source_name
    logging.error(source_name)
    ymonitor.crawl_pages = str(len(crawl_pages))
    ymonitor.new_pages = str(new_pages)
    ymonitor.source_type = source_type
    ymonitor.date_stat = today
    if len(crawl_pages) > 0:
        date1 = crawl_pages.order_by('insert_time')[0].insert_time
        date2 = crawl_pages.order_by('-insert_time')[0].insert_time
        ymonitor.duration = str(TimeUtil.get_date_diff_seconds(date1, date2))
    else:
        ymonitor.duration = str(0)
    ymonitor._id = Md5Util.generate_md5(source_name+today)
    ymonitor.save()


def trigger_spider_job(seconds=10, source_type="1", source_key="jd", document_item=YJdItem):
    scheduler = TwistedScheduler()
    trigger = CronTrigger(hour=10, minute=42, second=seconds)
    scheduler.add_job(print_time, trigger, args=[source_type, source_key, document_item]
                      , misfire_grace_time=120)

    scheduler.start()


if __name__ == '__main__':
    new_seconds = 1
    for key in forum_source_arr:
        new_seconds += 1
        trigger_spider_job(new_seconds, "1", key, forum_source_arr[key])
    
    for key in online_shop_source_arr:
        new_seconds += 1
        trigger_spider_job(new_seconds, "2", key, online_shop_source_arr[key])

    reactor.run()
