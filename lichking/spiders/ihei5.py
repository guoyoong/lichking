# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
from lichking.util.time_util import *
from lichking.util.str_clean import *
from bs4 import BeautifulSoup


class Ihei5Spider(scrapy.Spider):
    name = "ihei5"
    allowed_domains = ["bbs.ihei5.com"]
    start_urls = ['http://bbs.ihei5.com/']
    source_name = '爱黑武'
    source_short = 'ihei52'

    custom_settings = {
        'COOKIES_ENABLED': False,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 0.5,
        'AUTOTHROTTLE_MAX_DELAY': 0.8,
        'DOWNLOAD_DELAY': 0.8,
    }

    def start_requests(self):
        yield scrapy.Request(
            'http://bbs.ihei5.com/',
            callback=self.generate_forum_url_list
        )
        # yield scrapy.Request(
        #     'http://bbs.ihei5.com/forum-39-1.html',
        #     meta={"page_key": 1},
        #     callback=self.generate_forum_page_list
        # )

    def generate_forum_url_list(self, response):
        all_a_tags = response.xpath('//a/@href').extract()
        for a_tag in all_a_tags:
            a_tag_re = re.search(u'forum.php\?gid=[\d]+', a_tag)
            if a_tag_re is not None:
                yield scrapy.Request(
                    a_tag,
                    callback=self.generate_forum_url_list
                )
            a_tag_re = re.search(u'forum-[\d]+-[\d]+.html', a_tag)
            if a_tag_re is not None:
                yield scrapy.Request(
                    a_tag,
                    meta={"page_key": 1},
                    callback=self.generate_forum_page_list
                )

    def generate_forum_page_list(self, response):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        rep_time = response.xpath('//th[contains(@class,"new")]//div[@class="foruminfo"]//i[@class="y"]').extract()
        thread_list = response.xpath('//th[contains(@class,"new")]//a[@onclick="atarget(this)"]/@href').extract()
        r_time = re.search(u'\d{4}-\d{1,2}-\d{1,2}', rep_time[0])
        if r_time is not None:
            r_time = TimeUtil.format_date_short(r_time.group(0))
            timestamp = time.mktime(time.strptime(r_time, '%Y-%m-%d'))
            r_time = time.strftime('%Y-%m-%d', time.localtime(timestamp))
            page_key = int(response.meta['page_key'])
            # 是否有新回帖
            if r_time == today or r_time == yestday or page_key == 1:
                for thread_url in thread_list:
                    yield scrapy.Request(
                        thread_url,
                        callback=self.generate_forum_thread
                    )
                # 是否有下一页
                if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0:
                    r_url = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
                    yield scrapy.Request(
                        r_url,
                        meta={"page_key": -1},
                        callback=self.generate_forum_page_list
                    )

    def generate_forum_thread(self, response):
        forum_id = re.search(u'thread-[\d]+', response.url)
        try:
            forum_id = forum_id.group(0).replace('thread-', '')
        except:
            forum_id = ''
        forum_item = YIhei52Item()
        forum_item._id = forum_id
        rep_time_list = response.xpath('//span[@class="time"]').extract()

        # 是否是第一页
        if len(response.xpath('//span[@class="ico_see"]/text()').extract()) > 0:
            forum_item.source = self.source_name
            forum_item.source_short = self.source_short
            forum_item.url = response.url
            category1 = self.get_item_value(response.xpath('//div[@id="pt"]//div[@class="z"]//a[1]/text()').extract())
            category2 = self.get_item_value(response.xpath('//div[@id="pt"]//div[@class="z"]//a[2]/text()').extract())
            category3 = self.get_item_value(response.xpath('//div[@id="pt"]//div[@class="z"]//a[3]/text()').extract())
            forum_item.category = category1 + '-' + category2 + '-' + category3
            forum_item.time = self.format_rep_date(rep_time_list[0])
            forum_item.views = self.get_item_value(response.xpath('//span[@class="ico_see"]/text()').extract())
            forum_item.replies = \
                self.get_item_value(response.xpath('//span[@class="ico_reply"]/text()').extract())
            forum_item.title = StrClean.clean_comment(
                BeautifulSoup(response.xpath('//a[@id="thread_subject"]').extract()[0], 'lxml').get_text())
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])

            c_soup = BeautifulSoup(response.xpath(
                '//div[@class="t_fsz"]').extract()[0], 'lxml')
            if c_soup.find('div', class_='attach_nopermission') is not None:
                c_soup.find('div', class_='attach_nopermission').clear()
            [s.extract() for s in c_soup('script')]  # remove script tag
            forum_item.content = c_soup.get_text()
            forum_item.content = StrClean.clean_comment(forum_item.content)
            forum_item.comment = self.gen_item_comment(response)
            MongoClient.save_common_forum(forum_item, YIhei52Item)

            if len(response.xpath('//div[@class="pg"]').extract()) > 0:
                last_page = response.xpath('//a[@class="last"]/text()').extract()
                if len(last_page) > 0:
                    last_page = last_page[0].replace('.', '')
                else:
                    last_page = 10
                c_url = response.url[:len(response.url) - 8]
                # 水帖，只爬最后10页
                start_page = 1
                last_page = int(last_page)
                if last_page > 40:
                    start_page = last_page - 10
                for i in range(start_page, last_page + 1):
                    yield scrapy.Request(
                        c_url + str(i) + '-1.html',
                        callback=self.generate_forum_thread
                    )
        else:
            forum_item.title = ''
            forum_item.comment = self.gen_item_comment(response)
            forum_item.last_reply_time = self.format_rep_date(rep_time_list[-1])
            MongoClient.save_common_forum(forum_item, YIhei52Item)

        # 是否有下一页
        # if len(response.xpath('//div[@class="pg"]//a[@class="nxt"]').extract()) > 0:
        #     r_url = response.xpath('//div[@class="pg"]//a[@class="nxt"]/@href').extract()[0]
        #     yield scrapy.Request(
        #         r_url,
        #         callback=self.generate_forum_thread
        #     )

    @staticmethod
    def format_rep_date(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{1,2}', date_source).group(0)
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def gen_item_comment(self, response):
        comment = []
        new_comment = {}
        comments_data = []
        rep_time_list = response.xpath('//span[@class="time"]').extract()
        for indexi, content in enumerate(response.xpath('//div[@class="t_fsz"]/table[1]').extract()):
            soup = BeautifulSoup(content, 'lxml')
            if soup.find('div', class_='attach_nopermission') is not None:
                soup.find('div', class_='attach_nopermission').clear()
            [s.extract() for s in soup('script')]     # remove script tag
            c = StrClean.clean_unicode(soup.get_text())
            comments_data.append({'content': c, 'reply_time': self.format_rep_date(rep_time_list[indexi])})
        new_comment['url'] = response.url
        new_comment['comments_data'] = comments_data
        comment.append(new_comment)
        return comment

    @staticmethod
    def get_item_value(forum_arr):
        if len(forum_arr) > 0:
            return forum_arr[0].strip()
        else:
            return ''
