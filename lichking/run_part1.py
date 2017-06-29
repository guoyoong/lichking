# coding=utf-8

from apscheduler.schedulers.twisted import TwistedScheduler
from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from apscheduler.triggers.interval import *
from lichking.spiders.ithome import *
from lichking.spiders.cnmo_forum import *
from lichking.spiders.ihei5 import *
from lichking.spiders.lenovo_forum import *
from lichking.spiders.lenovo_mobile import *
from lichking.spiders.tieba import *
from lichking.spiders.it168 import *
from lichking.spiders.zhiyoo import *
from lichking.spiders.shayu_spider import *
from lichking.spiders.hiapk import *
from lichking.spiders.gfan import *
from lichking.spiders.angeeks import *
from lichking.spiders.imobile import *
from lichking.spiders.pconline import *


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
    trigger_spider_job(AngeeksSpider, 2)
    trigger_spider_job(CnmoSpider, 4)
    trigger_spider_job(GfanSpider, 6)
    trigger_spider_job(HiapkSpider, 8)
    trigger_spider_job(Ihei5Spider, 10)
    trigger_spider_job(ImobileSpider, 12)
    trigger_spider_job(It168Spider, 14)
    trigger_spider_job(IthomeSpider, 16)
    trigger_spider_job(LenovoClub, 18)
    trigger_spider_job(LenovoMobile, 20)
    trigger_spider_job(PconlineSpider, 22)
    trigger_spider_job(Shayu_Spider, 24)
    trigger_spider_job(TiebaSpider, 26)
    trigger_spider_job(ZhiyooSpider, 28)

    reactor.run()

