# coding=utf-8

from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from apscheduler.triggers.interval import *
import sys
sys.path.append("..")
from lichking.spiders.ithome import *


configure_logging()
runner = CrawlerRunner()


def trigger_spider_job(spider, seconds=10):
    scheduler = TwistedScheduler()
    start_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    trigger = IntervalTrigger(hours=8,
                              start_date=start_time)
    scheduler.add_job(runner.crawl, trigger, args=[spider])
    scheduler.start()


if __name__ == '__main__':
    trigger_spider_job(IthomeSpider, 2)

    reactor.run()

