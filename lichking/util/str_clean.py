# coding=utf-8

import sys
from bs4 import UnicodeDammit
reload(sys)
sys.setdefaultencoding('utf-8')


class StrClean:
    def __init__(self):
        print 'init'

    @staticmethod
    def clean_comment(comment_str):
        comment_str = comment_str.replace('\n', '').replace('\r', '').strip()
        return ' '.join(comment_str.split())

    @staticmethod
    def clean_unicode(comment_str):
        comment_str = comment_str.replace('\n', '').replace('\r', '').strip()
        comment_str = ' '.join(comment_str.split())
        return UnicodeDammit(comment_str).unicode_markup

    @staticmethod
    def get_safe_value(value_arr, index=0):
        new_index = index
        if index < 0:
            new_index = 0
        if len(value_arr) > new_index:
            return value_arr[index].strip()
        else:
            return ''

    @staticmethod
    def get_safe_value_and_clean(value_arr, index=0):
        new_index = index
        if index < 0:
            new_index = 0
        if len(value_arr) > new_index:
            return StrClean.clean_comment(value_arr[index])
        else:
            return ''

