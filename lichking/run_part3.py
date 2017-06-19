# coding=utf-8

from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from apscheduler.triggers.interval import *
from lichking.spiders.shayu_spider import *
from lichking.spiders.gfan import *
from lichking.spiders.angeeks import *
from lichking.spiders.pconline import *
from lichking.spiders.imobile import *


def other_method():
    logging.error(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':::   otherMethod')


configure_logging()
runner = CrawlerRunner()
date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def trigger_spider_job(spider, seconds=10):
    scheduler = TwistedScheduler()
    start_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    trigger = IntervalTrigger(hours=8,
                              start_date=start_time)
    scheduler.add_job(runner.crawl, trigger, args=[spider])
    scheduler.start()

if __name__ == '__main__':
    trigger_spider_job(Shayu_Spider, 4)
    trigger_spider_job(GfanSpider, 8)
    trigger_spider_job(AngeeksSpider, 10)
    trigger_spider_job(PconlineSpider, 12)
    trigger_spider_job(ImobileSpider, 14)

    reactor.run()

