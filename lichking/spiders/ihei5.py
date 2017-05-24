# -*- coding: utf-8 -*-
import scrapy
import logging
import fileinput
import re
from lichking.mongo.mongo_client import *
from lichking.util.time_util import *
from lichking.util.str_clean import *
from bs4 import BeautifulSoup


class Ihei5Spider(scrapy.Spider):
    name = "ihei5"
    allowed_domains = ["bbs.ihei5.com"]
    start_urls = ['http://bbs.ihei5.com/']
    forum_list_file = 'ihei5_forum_list_file'
    source_name = '爱黑武'
    source_short = 'ihei5'

    def start_requests(self):
        # enter forum
        for line in fileinput.input(self.forum_list_file):
            if not line:
                break
            if line.find('#') == -1:
                yield scrapy.Request(
                    line.strip(),
                    dont_filter='true',
                    callback=self.generate_forum_page_list
                )

    def update_forum_group(self):
        url = 'http://bbs.ihei5.com/forum.php?gid='
        for i in range(1, 250):
            yield scrapy.Request(
                url + str(i),
                dont_filter='true',
                callback=self.generate_forum_group
            )

    def generate_forum_group(self, response):
        forum_list = response.xpath('//td[@class="fl_g"]//dt//a/@href').extract()
        if len(forum_list) > 0:
            all_url = ''
            for forum_url in forum_list:
                all_url += forum_url+'\n'
            with open(self.forum_list_file, 'a') as f:
                f.write(all_url)
        forum_list = response.xpath('//td[@class="fl_icn"]//a/@href').extract()
        if len(forum_list) > 0:
            all_url = ''
            for forum_url in forum_list:
                all_url += forum_url+'\n'
            with open(self.forum_list_file, 'a') as f:
                f.write(all_url)

    def generate_forum_page_list(self, response):
        flag = -1
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        rep_time = response.xpath('//th[contains(@class,"new")]//div[@class="foruminfo"]//i[@class="y"]').extract()
        thread_list = response.xpath('//th[contains(@class,"new")]//a[@onclick="atarget(this)"]/@href').extract()
        for i in range(0, len(rep_time)):
            r_time = re.search(u'\d{4}-\d{1,2}-\d{1,2}', rep_time[i])
            if r_time is not None:
                r_time = TimeUtil.format_date_short(r_time.group(0))
                timestamp = time.mktime(time.strptime(r_time, '%Y-%m-%d'))
                r_time = time.strftime('%Y-%m-%d', time.localtime(timestamp))
                # 是否有新回帖
                if r_time == today or r_time == yestday:
                    yield scrapy.Request(
                        thread_list[i],
                        callback=self.generate_forum_thread
                    )
                    # 是否有下一页
                    if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0 and flag == -1:
                        flag = 1
                        r_url = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
                        yield scrapy.Request(
                            r_url,
                            callback=self.generate_forum_page_list
                        )

    def generate_forum_thread(self, response):
        forum_id = re.search(u'thread-[\d]+', response.url)
        try:
            forum_id = forum_id.group(0).replace('thread-', '')
        except:
            forum_id = ''
        forum_item = YIhei5Item()
        forum_item._id = forum_id

        # 是否是第一页
        if len(response.xpath('//span[@class="ico_see"]/text()').extract()) > 0:
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url
            forum_item.category = self.get_item_value(
                response.xpath('//div[@id="pt"]//div[@class="z"]//a[3]/text()').extract())
            forum_item.time = self.get_item_value(
                response.xpath('//span[@class="time"]/text()').extract())
            forum_item.time = self.format_rep_date(forum_item.time)
            forum_item.views = self.get_item_value(response.xpath('//span[@class="ico_see"]/text()').extract())
            forum_item.replies = \
                self.get_item_value(response.xpath('//span[@class="ico_reply"]/text()').extract())
            forum_item.title = StrClean.clean_comment(
                BeautifulSoup(response.xpath('//a[@id="thread_subject"]').extract()[0], 'lxml').get_text())

            c_soup = BeautifulSoup(response.xpath(
                '//div[@class="t_fsz"]//table[1]').extract()[0], 'lxml')
            if c_soup.find('div', class_='attach_nopermission') is not None:
                c_soup.find('div', class_='attach_nopermission').clear()
            [s.extract() for s in c_soup('script')]  # remove script tag
            forum_item.content = c_soup.get_text()
            forum_item.content = StrClean.clean_comment(forum_item.content)
            forum_item.comment = self.gen_item_comment(response)

            MongoClient.save_ihei5_forum(forum_item)

            if len(response.xpath('//div[@class="pg"]').extract()) > 0:
                last_page = response.xpath('//a[@class="last"]/text()').extract()
                if len(last_page) > 0:
                    last_page = last_page[0].replace('.', '')
                else:
                    last_page = 10
                c_url = response.url[:len(response.url) - 8]
                for i in range(1, int(last_page)):
                    yield scrapy.Request(
                        c_url + str(i) + '-1.html',
                        callback=self.generate_forum_thread
                    )
        else:
            forum_item.title = ''
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_ihei5_forum(forum_item)

        # 是否有下一页
        if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0:
            r_url = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
            yield scrapy.Request(
                r_url,
                callback=self.generate_forum_thread
            )

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def gen_item_comment(response):
        comment = []
        new_comment = []
        for indexi, content in enumerate(response.xpath('//div[@class="t_fsz"]//table[1]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            if soup.find('div', class_='attach_nopermission') is not None:
                soup.find('div', class_='attach_nopermission').clear()
            [s.extract() for s in soup('script')]     # remove script tag
            c = StrClean.clean_unicode(soup.get_text())
            if c != '':
                new_comment.append(c)
        new_comment.append(response.url)
        comment.append(new_comment)
        return comment

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''
