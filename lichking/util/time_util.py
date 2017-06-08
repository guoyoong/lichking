# coding=utf-8

import time
import datetime


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
