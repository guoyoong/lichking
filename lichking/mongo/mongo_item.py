# coding=utf-8

from mongoengine import *


class YLenovoForumItem(Document):
    _id = StringField(default='')
    url = StringField(default='')
    # forum
    source = StringField(default='')
    source_short = StringField(default='')
    views = StringField(default='')
    # forum part
    category = StringField(default='')
    replies = StringField(default='')
    title = StringField(default='')
    comment = ListField()
    content = StringField(default='')
    time = StringField(default='')
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')


class YLenovoMobileItem(Document):
    _id = StringField(default='')
    url = StringField(default='')
    # forum
    source = StringField(default='')
    source_short = StringField(default='')
    views = StringField(default='')
    category = StringField(default='')
    replies = StringField(default='')
    title = StringField(default='')
    comment = ListField()
    content = StringField(default='')
    time = StringField()
    insert_time = StringField(default='')
    parse_time = StringField(default='')
    flag = StringField(default='')


class YIthomeItem(Document):
    _id = StringField(default='')
    url = StringField(default='')
    title = StringField(default='')
    content = StringField(default='')
    source = StringField(default='')
    source_short = StringField(default='')
    author = StringField(default='')
    time = StringField(default='')
    category = StringField(default='')
    replies = StringField(default='')

    comment = ListField()
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')


class YBaiduTiebaItem(Document):
    _id = StringField(default='')
    url = StringField(default='')
    # forum
    source = StringField(default='')
    source_short = StringField(default='')
    # forum part
    category = StringField(default='')
    replies = StringField(default='')
    title = StringField(default='')
    comment = ListField()
    content = StringField(default='')
    time = StringField(default='')
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')


class YCnmoForumItem(Document):
    _id = StringField(default='')
    url = StringField(default='')
    # forum
    source = StringField(default='')
    source_short = StringField(default='')
    views = StringField(default='')
    # forum part
    category = StringField(default='')
    replies = StringField(default='')
    title = StringField(default='')
    comment = ListField()
    content = StringField(default='')
    time = StringField(default='')
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_rep_time = StringField(default='')


class YIhei5Item(Document):
    _id = StringField(default='')
    url = StringField(default='')
    # forum
    source = StringField(default='')
    source_short = StringField(default='')
    views = StringField(default='')
    # forum part
    category = StringField(default='')
    replies = StringField(default='')
    title = StringField(default='')
    comment = ListField()
    content = StringField(default='')
    time = StringField(default='')
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')


class YIt168Item(Document):
    _id = StringField(default='')
    url = StringField(default='')
    # forum
    source = StringField(default='')
    source_short = StringField(default='')
    views = StringField(default='')
    # forum part
    category = StringField(default='')
    replies = StringField(default='')
    title = StringField(default='')
    comment = ListField()
    content = StringField(default='')
    time = StringField(default='')
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_rep_time = StringField(default='')


class YZhiyooItem(Document):
    _id = StringField(default='')
    url = StringField(default='')
    # forum
    source = StringField(default='')
    source_short = StringField(default='')
    views = StringField(default='')
    # forum part
    category = StringField(default='')
    replies = StringField(default='')
    title = StringField(default='')
    comment = ListField()
    content = StringField(default='')
    time = StringField(default='')
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_rep_time = StringField(default='')


class YHiapkItem(Document):
    _id = StringField(default='')
    url = StringField(default='')
    # forum
    source = StringField(default='')
    source_short = StringField(default='')
    views = StringField(default='')
    # forum part
    category = StringField(default='')
    replies = StringField(default='')
    title = StringField(default='')
    comment = ListField()
    content = StringField(default='')
    time = StringField(default='')
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_rep_time = StringField(default='')


class YAngeeksItem(Document):
    _id = StringField(default='')
    url = StringField(default='')
    # forum
    source = StringField(default='')
    source_short = StringField(default='')
    views = StringField(default='')
    # forum part
    category = StringField(default='')
    replies = StringField(default='')
    title = StringField(default='')
    comment = ListField()
    content = StringField(default='')
    time = StringField(default='')
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_rep_time = StringField(default='')
