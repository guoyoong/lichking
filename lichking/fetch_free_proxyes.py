#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib2
import logging
from lichking.mongo.mongo_client import *
from lichking.util.md5_util import *
from apscheduler.schedulers.blocking import BlockingScheduler


logger = logging.getLogger(__name__)


def get_html(url):
    request = urllib2.Request(url)
    request.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.99 Safari/537.36")
    html = urllib2.urlopen(request)
    return html.read()


def get_soup(url):
    soup = BeautifulSoup(get_html(url), "lxml")
    return soup


def fetch_kxdaili(page):
    """
    从www.kxdaili.com抓取免费代理
    """
    proxyes = []
    try:
        url = "http://www.kxdaili.com/dailiip/1/%d.html" % page
        soup = get_soup(url)
        table_tag = soup.find("table", attrs={"class": "segment"})
        trs = table_tag.tbody.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            ip = tds[0].text
            port = tds[1].text
            latency = tds[4].text.split(" ")[0]
            if float(latency) < 0.5: # 输出延迟小于0.5秒的代理
                proxy = "%s:%s" % (ip, port)
                proxyes.append(proxy)
    except:
        logger.warning("fail to fetch from kxdaili")
    return proxyes


def img2port(img_url):
    """
    mimvp.com的端口号用图片来显示, 本函数将图片url转为端口, 目前的临时性方法并不准确
    """
    code = img_url.split("=")[-1]
    if code.find("AO0OO0O") > 0:
        return 80
    elif code.find("4vMpDgw") > 0:
        return 8080
    elif code.find("zvMpTI4") > 0:
        return 3128
    elif code.find("5vOpTk5") > 0:
        return 9999
    elif code.find("4vMpDgx") > 0:
        return 8081


def fetch_mimvp():
    """
    从http://proxy.mimvp.com/free.php抓免费代理
    """
    proxyes = []
    try:
        url = "http://proxy.mimvp.com/free.php?proxy=in_tp"
        soup = get_soup(url)
        table = soup.find("div", attrs={"class": "free-list"}).table
        tds = table.tbody.find_all("td")
        for i in range(0, len(tds), 10):
            ip = tds[i + 1].text
            port = img2port(tds[i + 2].img["src"])
            response_time = tds[i + 7]["title"][:-1]
            if port is not None and float(response_time) < 1:
                proxy = "%s:%s" % (ip, port)
                proxyes.append(proxy)
    except:
        logger.warning("fail to fetch from mimvp")
    return proxyes


def fetch_xici():
    """
    http://www.xicidaili.com/nn/
    """
    proxyes = []
    try:
        url = "http://www.xicidaili.com/nn/"
        soup = get_soup(url)
        table = soup.find("table", attrs={"id": "ip_list"})
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tr = trs[i]
            tds = tr.find_all("td")
            ip = tds[1].text
            port = tds[2].text
            speed = tds[6].div["title"][:-1]
            latency = tds[7].div["title"][:-1]
            if float(speed) < 3 and float(latency) < 1:
                proxyes.append("%s:%s" % (ip, port))
    except:
        logger.warning("fail to fetch from xici")
    return proxyes


def fetch_ip181():
    """
    http://www.ip181.com/
    """
    proxyes = []
    try:
        url = "http://www.ip181.com/"
        soup = get_soup(url)
        table = soup.find("table")
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            tds = trs[i].find_all("td")
            ip = tds[0].text
            port = tds[1].text
            latency = tds[4].text[:-2]
            if float(latency) < 1:
                proxyes.append("%s:%s" % (ip, port))
    except Exception as e:
        logger.warning("fail to fetch from ip181: %s" % e)
    return proxyes


def fetch_httpdaili():
    """
    http://www.httpdaili.com/mfdl/
    更新比较频繁
    """
    proxyes = []
    try:
        url = "http://www.httpdaili.com/mfdl/"
        soup = get_soup(url)
        table = soup.find("div", attrs={"kb-item-wrap11"}).table
        trs = table.find_all("tr")
        for i in range(1, len(trs)):
            try:
                tds = trs[i].find_all("td")
                ip = tds[0].text
                port = tds[1].text
                type = tds[2].text
                if type == u"匿名":
                    proxyes.append("%s:%s" % (ip, port))
            except:
                pass
    except Exception as e:
        logger.warning("fail to fetch from httpdaili: %s" % e)
    return proxyes


def check(proxy):
    import urllib2
    url = "http://www.baidu.com/js/bdsug.js?v=1.0.3.0"
    proxy_handler = urllib2.ProxyHandler({'http': "http://" + proxy})
    opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
    try:
        response = opener.open(url, timeout=1)
        return response.code == 200 and response.url == url
    except Exception:
        return False


def fetch_all():
    proxyes = []
    proxyes += fetch_mimvp()
    proxyes += fetch_xici()
    proxyes += fetch_ip181()
    proxyes += fetch_httpdaili()
    valid_proxyes = []
    logger.info("checking proxyes validation")
    for p in proxyes:
        if check(p):
            valid_proxyes.append(p)
            print p

    return valid_proxyes


def trigger_proxy_job():
    import sys
    root_logger = logging.getLogger("")
    stream_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(name)-8s %(asctime)s %(levelname)-8s %(message)s', '%a, %d %b %Y %H:%M:%S', )
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    proxyes = fetch_all()
    for p in proxyes:
        proxy_item = FreeProxyItem()
        proxy_item._id = Md5Util.generate_md5(p)
        proxy_item.ip = str(p).split(":")[0]
        proxy_item.port = str(p).split(":")[1]
        proxy_item.save()

    items = MongoClient.get_all_proxy()
    for p_item in items:
        if not check(str(p_item.ip) + ":" + str(p_item.port)):
            FreeProxyItem.objects(_id=p_item._id).delete()


if __name__ == '__main__':
    trigger_proxy_job()
    # bscheduler = BlockingScheduler()
    # bscheduler.add_job(trigger_proxy_job, 'interval', minutes=8)
    # bscheduler.start()






