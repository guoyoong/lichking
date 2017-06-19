# coding=utf-8

from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from apscheduler.triggers.cron import *
from lichking.spiders.zhiyoo import *
from lichking.spiders.shayu_spider import *
from lichking.spiders.hiapk import *
from lichking.spiders.gfan import *
from lichking.spiders.angeeks import *


def other_method():
    logging.error(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+':::   otherMethod')


configure_logging()
runner = CrawlerRunner()
date_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def trigger_spider_job(spider, seconds=10):
    scheduler = TwistedScheduler()
    # 每天凌晨12点 开始执行
    trigger = CronTrigger(hour=0, minute=19, second=seconds)
    scheduler.add_job(runner.crawl, trigger, args=[spider])
    scheduler.start()


if __name__ == '__main__':
    trigger_spider_job(ZhiyooSpider, 2)
    trigger_spider_job(Shayu_Spider, 4)
    trigger_spider_job(HiapkSpider, 6)
    trigger_spider_job(GfanSpider, 8)
    trigger_spider_job(AngeeksSpider, 10)

    reactor.run()

