# # -*- coding: utf-8 -*-
# import datetime
# import os
# import re
# import time
# import urllib
# from time import sleep
# import base64
# import requests
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.support.ui import WebDriverWait
# from PIL import Image
# from PIL import ImageEnhance
# from pytesseract import *
#
#
# def getverify(name):
#     '''
#     图片识别模块
#     :param name:图片path
#     :return:
#     '''
#     # 打开图片
#     im = Image.open(name)
#     # 使用ImageEnhance可以增强图片的识别率
#     enhancer = ImageEnhance.Contrast(im)
#     image_enhancer = enhancer.enhance(4)
#     # 放大图像 方便识别
#     im_orig = image_enhancer.resize((image_enhancer.size[0] * 2, image_enhancer.size[1] * 2), Image.BILINEAR)
#     # 识别
#     text = image_to_string(im_orig)
#     im.close()
#     im_orig.close()
#     # 识别对吗
#     text = text.strip()
#     return text
#
#
# class BD_Crawler(object):
#     def __init__(self, userName, pwd, chromedriver, data_dir):
#         '''
#         初始化 driver
#         :param userName:账户
#         :param pwd: 密码
#         :param chromedriver:webdirver
#         '''
#         os.environ["webdriver.chrome.driver"] = chromedriver
#         options = webdriver.ChromeOptions()
#         options.add_argument('--user-data-dir=' + data_dir)  # 设置成用户自己的数据目录
#         # option.add_argument('--user-agent=iphone') #修改浏览器的User-Agent来伪装你的浏览器访问手机m站
#         # option.add_extension('d:\crx\AdBlock_v2.17.crx')  # 自己下载的crx路径
#         self.driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)
#         # self.driver = webdriver.Chrome(chromedriver)
#         self.userName = str(userName)
#         self.pwd = pwd
#
#     def login(self):
#         '''
#         判断是否需要登录
#         :return:
#         '''
#         try:
#             if self.driver.find_elements_by_class_name('compInfo'):
#                 return True
#
#             WebDriverWait(self.driver, 30).until(
#                 EC.presence_of_element_located((By.NAME, 'userName'))
#             )
#
#             userName = self.driver.find_element_by_name("userName")
#             userName.send_keys(self.userName)
#             password = self.driver.find_element_by_name("password")
#             password.send_keys(self.pwd)
#             submit = self.driver.find_element_by_xpath('//*[@class="pass-form-item pass-form-item-submit"]')
#             submit.submit()
#             print '请检查是否有验证码，手动输入'
#             sleep(10)
#             while self.driver.find_element_by_xpath('//*[@class="pass-verifyCode"]'):
#                 try:
#                     if self.driver.find_element_by_xpath(
#                             '//*[@class="pass-success pass-success-verifyCode" and @style="display: block; visibility: visible; opacity: 1;"]'):
#                         submit = self.driver.find_element_by_xpath('//*[@class="pass-form-item pass-form-item-submit"]')
#                         submit.submit()
#                         break
#                 except:
#                     pass
#                 sleep(6)
#             return True
#         except:
#             return False
#             pass
#         else:
#             return False
#
#     def getTimeSpan(self):
#         try:
#             self.driver.implicitly_wait(20)  # seconds
#             # 获取时间范围
#             time_span = self.driver.find_elements_by_class_name('compInfo')[4].text
#             from_day = time_span.split()[0]
#             to_day = time_span.split()[-1]
#             from_daytime = datetime.datetime.strptime(from_day, "%Y-%m-%d").date()
#             to_daytime = datetime.datetime.strptime(to_day, "%Y-%m-%d").date()
#             alldays = (to_daytime - from_daytime).days
#             self.driver.implicitly_wait(5)  # seconds
#             return from_daytime, alldays
#         except:
#             return -1
#
#     def downloadImageFile(self, keyword, imgUrl):
#         local_filename = '../photos/' + keyword + time.strftime('_%Y_%m_%d') + '.png'
#         print "Download Image File=", local_filename
#         r = requests.get(imgUrl, cookies=self.getCookieJson(),
#                          stream=True)  # here we need to set stream = True parameter
#         with open(local_filename, 'wb') as f:
#             for chunk in r.iter_content(chunk_size=1024):
#                 if chunk:  # filter out keep-alive new chunks
#                     f.write(chunk)
#                     f.flush()
#             f.close()
#         return local_filename
#
#     def getCookieJson(self):
#         cookie_jar = {}
#         for cookie in self.driver.get_cookies():
#             name = cookie['name']
#             value = cookie['value']
#             cookie_jar[name] = value
#         return cookie_jar
#
#     def webcrawler(self, keyword):
#         '''
#         百度指数控制函数
#         :return:
#         '''
#         self.driver.get('http://index.baidu.com/?tpl=trend&word=' + urllib.quote(keyword.encode('gb2312')))
#         # self.driver.maximize_window()
#
#         self.login()
#         try:
#             # 判断form表单ajax加载完成标记：id属性
#             WebDriverWait(self.driver, 20).until(
#                 EC.presence_of_element_located((By.ID, 'trend'))
#             )
#         except:
#             pass
#         try:
#             for i in range(1, 4):
#                 if self.driver.find_element_by_class_name('toLoading').get_attribute('style') != u'display: none;':
#                     break
#                 sleep(5)
#         except:
#             pass
#         for i in range(1, 4):
#             from_daytime, alldays = self.getTimeSpan()
#             if alldays < 0:
#                 self.driver.refresh()
#             else:
#                 break
#         sleep(2)
#         for i in range(1, 4):
#             try:
#                 # 获取所有的纵坐标的点
#                 svg_data = re.search(r'<path fill="none" stroke="#3ec7f5"(.*?)" stroke-width="2" stroke-opacity="1"',
#                                      self.driver.page_source).group(1)
#                 break
#             except:
#                 self.driver.refresh()
#                 sleep(2)
#                 pass
#
#         points = []
#         for line in re.split('C', svg_data):
#             tmp_point = re.split(',', line)[-1]
#             points.append(tmp_point)
#
#         # 判断时间天数差 与 points个数 是否一致
#         if len(points) != alldays + 1:
#             return
#
#         # self.driver.save_screenshot('aa.png')  # 截取当前网页
#         CaptchaUrl = self.driver.find_element_by_id('trendYimg').get_attribute('src')  # 定位坐标尺度
#
#         pic_path = self.downloadImageFile(urllib.quote(keyword.encode('gb2312')), CaptchaUrl)
#         reg_txt = getverify(pic_path)
#
#         MaxValue = float(reg_txt.split()[0].replace(',', ''))
#         MinValue = float(reg_txt.split()[-1].replace(',', ''))
#         kedu = (MaxValue - MinValue) / (len(reg_txt.split()) - 1)
#         indexValue = []
#         for index, point in enumerate(points):
#             day = from_daytime + datetime.timedelta(days=index)
#             Xvalue = MaxValue - (float(point) - 130) * (MaxValue - (MinValue - kedu)) / 207.6666666
#
#             indexValue.append({'day': day, 'value': Xvalue})
#         return indexValue
#
#
# def main():
#     bd_crawler = BD_Crawler('13141398441', base64.b64decode('gb1314LFHS@21!'),
#                             'D:\software\chromedriver_win32\chromedriver.exe',
#                             'D:\tmp\data')
#     values = bd_crawler.webcrawler(u'爱情')
#     print values
#     print 'end'
#
#
# if __name__ == '__main__':
#     main()
