# -*- coding: utf-8 -*-
import scrapy
from lichking.mongo.mongo_client import *
import json
from bs4 import BeautifulSoup
from lichking.util.str_clean import *
from lxml import etree
import logging

reload(sys)
sys.setdefaultencoding('utf-8')

class QichacahSpider(scrapy.Spider):
    name = "qichacha"
    allowed_domains = ["qichacha.com"]
    source_short = "qichacha"
    source_name = "企查查"
    url_qichacha_pre = "https://www.qichacha.com"

    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3,
        'AUTOTHROTTLE_MAX_DELAY': 3,
        'DOWNLOAD_DELAY': 3,
        'DEFAULT_REQUEST_HEADERS': {
            'user-agent':
                'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
        }
    }

    # cookie 有效期一个星期
    qicha_cookie = {'CNZZDATA1254842228': '1344262236-1504601048-https%253A%252F%252Fwww.qichacha.com%252F%7C1505873642',
                    'PHPSESSID': '0lr420dakp82uiba2u5qjae5c7',
                    # '_uab_collina': '150460169094577226831388',
                    # '_umdata': 'E2AE90FA4E0E42DEE59CBAC46561DF4B98DF99D138F0503931CFE50F8E388F249A899F453D98C08BCD43AD3E795C914C8BCC59DC29ED289D21B3E4E07D991E42',
                    # 'hasShow': '1',
                    # 'zg_did': '%7B%22did%22%3A%20%2215e513fd1a026d-05ea14c3726071-3a3e5f04-100200-15e513fd1a158c%22%7D',
                    # 'UM_distinctid': '15e513fd277465-0e8550552977f7-3a3e5f04-100200-15e513fd278337'
                    }

    def __init__(self):
        self.source_short = "qichacha"

    # scrapy start and check page num
    def start_requests(self):
        yield scrapy.Request(
            "http://www.qichacha.com/search?key=中国建筑股份有限公司",
            cookies=self.qicha_cookie,
            callback=self.generate_firm_url
        )

    def generate_firm_url(self, response):
        firm_hrefs = response.xpath('//a[@class="ma_h1"]/@href').extract()
        for a_id in firm_hrefs:
            yield scrapy.Request(
                self.url_qichacha_pre + a_id,
                cookies=self.qicha_cookie,
                encoding='utf-8',
                callback=self.generate_firm_content
            )

    def generate_firm_content(self, response):
        qitem = YQichachaItem()
        qitem._id = re.search(u'firm_(.*)(\.html)$', response.url).group(1)
        qitem.name = response.xpath("//div[contains(@class, 'company-top-name')]/text()").extract()[0]
        base_info = list()
        base_info.append({"基本信息": self.clean_content(response.xpath(
            "//span[contains(@class, 'm_comInfo')]").extract()[0])})

        qitem.base_info = base_info
        qitem.save()
        chacha_url_pre = self.url_qichacha_pre + '/company_getinfos?unique=' + qitem._id + '&companyname='+qitem.name
        yield scrapy.Request(
            chacha_url_pre +'&tab=base',
            callback=self.generate_firm_base,
            cookies=self.qicha_cookie,
            encoding='utf-8',
            meta={"item": qitem, "chacha_url_pre":chacha_url_pre}
        )

    def generate_firm_base(self, response):
        firm_hrefs = response.xpath("//a/@href").extract()
        for a_id in firm_hrefs:
            if a_id.find("firm_") == -1:
                continue
            if a_id.find(".html") != -1:
                yield scrapy.Request(
                    self.url_qichacha_pre + a_id,
                    cookies=self.qicha_cookie,
                    encoding='utf-8',
                    callback=self.generate_firm_content
                )
            else:
                yield scrapy.Request(
                    self.url_qichacha_pre + a_id + ".html",
                    encoding='utf-8',
                    cookies=self.qicha_cookie,
                    callback=self.generate_firm_content
                )

        qitem = response.meta["item"]
        base_info = qitem.base_info
        base_info.append({"工商信息": self.clean_content(response.body)})
        qitem.base_info = base_info

        yield scrapy.Request(
            response.meta["chacha_url_pre"] + '&tab=run',
            callback=self.generate_firm_firm_run,
            cookies=self.qicha_cookie,
            meta={"item": qitem, "chacha_url_pre": response.meta["chacha_url_pre"]}
        )

    def generate_firm_firm_run(self, response):
        qitem = response.meta["item"]
        firm_run = qitem.firm_run
        firm_run.append({"经营状况": self.clean_content(response.body)})
        qitem.firm_run = firm_run

        yield scrapy.Request(
            response.meta["chacha_url_pre"] + '&tab=touzi',
            callback=self.generate_firm_touzi,
            cookies=self.qicha_cookie,
            meta={"item": qitem, "chacha_url_pre": response.meta["chacha_url_pre"]}
        )

    def generate_firm_touzi(self, response):
        qitem = response.meta["item"]
        touzi = qitem.touzi
        touzi.append({"对外投资": self.clean_content(response.body)})
        qitem.touzi = touzi

        yield scrapy.Request(
            response.meta["chacha_url_pre"] + '&tab=report',
            callback=self.generate_firm_report,
            cookies=self.qicha_cookie,
            meta={"item": qitem, "chacha_url_pre": response.meta["chacha_url_pre"]}
        )

    def generate_firm_report(self, response):
        qitem = response.meta["item"]
        report = qitem.report
        report.append({"企业年报": self.clean_content(response.body)})
        qitem.report = report

        yield scrapy.Request(
            response.meta["chacha_url_pre"] + '&tab=assets',
            callback=self.generate_firm_assets,
            cookies=self.qicha_cookie,
            meta={"item": qitem, "chacha_url_pre": response.meta["chacha_url_pre"]}
        )

    def generate_firm_assets(self, response):
        qitem = response.meta["item"]
        assets = qitem.assets
        assets.append({"知识产权": self.clean_content(response.body)})
        qitem.firm_run = assets

        yield scrapy.Request(
            response.meta["chacha_url_pre"] + '&tab=job',
            callback=self.generate_firm_yuqing,
            cookies=self.qicha_cookie,
            meta={"item": qitem, "chacha_url_pre": response.meta["chacha_url_pre"]}
        )

    def generate_firm_yuqing(self, response):
        qitem = response.meta["item"]
        yuqing = qitem.yuqing
        yuqing.append({"新闻舆情": self.clean_content(response.body)})
        qitem.yuqing = yuqing
        qitem.insert_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        qitem.save()

        yield scrapy.Request(
            response.meta["chacha_url_pre"] + '&tab=susong',
            callback=self.generate_firm_susong,
            cookies=self.qicha_cookie,
            meta={"item": qitem, "chacha_url_pre": response.meta["chacha_url_pre"], "page_n": 1}
        )

    def generate_firm_susong(self, response):
        if len(response.body) < 10:
            return
        qitem = response.meta["item"]
        page_n = response.meta["page_n"]

        self.append_susong_detail({"法律诉讼": self.clean_content(response.body)}, qitem._id)

        anjian_list = response.xpath("//table[@class='m_changeList']//a[@class='c_a']/@onclick").extract()
        anjian_name = response.xpath("//table[@class='m_changeList']//tr//td[2]//a[@class='c_a']/text()").extract()
        for i in range(0, len(anjian_list)):
            yield scrapy.FormRequest(
                "http://www.qichacha.com/company_wenshuView",
                callback=self.generate_firm_anjian,
                cookies=self.qicha_cookie,
                method='POST',
                dont_filter="true",
                formdata={"id": self.generate_anjian_id(anjian_list[i])},
                meta={"item_id": qitem._id, "anjian_name": anjian_name[i]}
            )
        # 请求下一页
        yield scrapy.Request(
            response.meta["chacha_url_pre"] + '&tab=susong&box=wenshu&p=' + str(page_n),
            encoding='utf-8',
            callback=self.generate_firm_susong,
            cookies=self.qicha_cookie,
            meta={"item": qitem, "chacha_url_pre": response.meta["chacha_url_pre"], "page_n": int(page_n)+1}
        )

    def generate_firm_anjian(self, response):
        a_json = json.loads(response.body)
        a_detail = self.clean_content(a_json.get("data"))
        a_name = response.meta["anjian_name"]
        q_id = response.meta["item_id"]

        self.append_susong_detail({a_name: a_detail}, q_id)

    @staticmethod
    def append_susong_detail(susong_json, q_id):
        items = YQichachaItem.objects(_id=q_id)
        s_susong = items[0].susong
        s_susong.append(susong_json)
        items.update_one(set__susong=s_susong)

    @staticmethod
    def generate_anjian_id(anjian):
        return anjian.split("wsView(\"")[1].split("\"")[0]

    @staticmethod
    def clean_content(s_soup):
        s_soup = BeautifulSoup(s_soup, 'lxml', from_encoding='utf-8')
        [s.extract() for s in s_soup('script')]  # remove script tag
        [s.extract() for s in s_soup('style')]  # remove script tag
        s_soup_text = s_soup.get_text()
        s_soup_text = s_soup_text.replace('\n', '').replace('\r', '').strip()
        return ' '.join(s_soup_text.split())


if __name__ == '__main__':
    from scrapy import cmdline
    cmdline.execute('scrapy crawl qichacha'.split())
