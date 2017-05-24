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
