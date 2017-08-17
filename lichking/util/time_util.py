# coding=utf-8

import time
import datetime
import re


class TimeUtil:

    def __init__(self):
        print 'init'

    @staticmethod
    def transfer_date(date_source):
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def format_date(date_source):
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d %H:%M:%S'))
            return time.strftime('%Y-%m-%d', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def format_date_short(date_source):
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d'))
            return time.strftime('%Y-%m-%d', time.localtime(timestamp))
        except:
            return datetime.datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def compare_date_short(date1, date2):
        try:
            timestamp1 = time.mktime(time.strptime(date1, '%Y-%m-%d %H:%M:%S'))
            timestamp2 = time.mktime(time.strptime(date2, '%Y-%m-%d %H:%M:%S'))
            if timestamp1 > timestamp2:
                return date1
            return date2
        except:
            if date1 == '':
                return date2
            return date1

    @staticmethod
    def check_date_is_new(date_source):
        date_source = re.search(u'\d{4}-\d{1,2}-\d{1,2}', date_source).group(0)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        yestday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        try:
            timestamp = time.mktime(time.strptime(date_source, '%Y-%m-%d'))
            date_source = time.strftime('%Y-%m-%d', time.localtime(timestamp))
            if date_source == today or date_source == yestday:
                return True
        except:
            return False
        return False

    @staticmethod
    def get_date_diff_seconds(date1, date2):
        timestamp1 = time.mktime(time.strptime(date1, '%Y-%m-%d %H:%M:%S'))
        timestamp2 = time.mktime(time.strptime(date2, '%Y-%m-%d %H:%M:%S'))
        return int(timestamp2 - timestamp1)

    @staticmethod
    def timestamp_to_format_date(time_st):
        try:
            date_source = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time_st))
            return date_source
        except:
            return ''
