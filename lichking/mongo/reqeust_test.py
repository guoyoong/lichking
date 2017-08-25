# coding=utf-8

import requests
from lxml import etree

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

r = requests.get(url="http://www.ifanr.com/").content
response = etree.HTML(r)
print response
print response.xpath("//div[@class='post_title']//h1/text()")[0]
