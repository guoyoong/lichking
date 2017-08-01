# coding=utf-8

import sys
import hashlib
reload(sys)
sys.setdefaultencoding('utf-8')


class Md5Util:

    def __init__(self):
        print 'init'

    @staticmethod
    def generate_md5(source):
        m1 = hashlib.md5(source)
        return m1.hexdigest()
