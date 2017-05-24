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
