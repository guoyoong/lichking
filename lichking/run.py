# coding=utf-8

from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.crawler import CrawlerRunner
from apscheduler.triggers.interval import *
from twisted.internet import reactor
from scrapy.utils.log import configure_logging

from lichking.spiders.ithome import *
from lichking.spiders.cnmo_forum import *
from lichking.spiders.ihei5 import *
from lichking.spiders.lenovo_forum import *
from lichking.spiders.lenovo_mobile import *
from lichking.spiders.tieba import *


def other_method():
    logging.error(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':::   otherMethod')


configure_logging()
runner = CrawlerRunner()
date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def trigger_spider_job(spider, start_seconds=5):
    scheduler = TwistedScheduler()
    start_time = datetime.datetime.now() + datetime.timedelta(seconds=start_seconds)
    trigger = IntervalTrigger(minutes=1,
                              start_date=start_time)
    scheduler.add_job(runner.crawl, trigger, args=[spider])
    scheduler.start()


if __name__ == '__main__':
    trigger_spider_job(IthomeSpider, 2)
    trigger_spider_job(CnmoSpider, 3)
    trigger_spider_job(Ihei5Spider, 4)
    trigger_spider_job(LenovoClub, 5)
    trigger_spider_job(LenovoMobile, 6)
    trigger_spider_job(TiebaSpider, 7)

    reactor.run()

