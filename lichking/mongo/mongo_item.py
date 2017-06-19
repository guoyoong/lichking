# coding=utf-8

from mongoengine import *


class YLenovoForum2Item(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YLenovoMobile2Item(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YIthome2Item(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YBaiduTieba2Item(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YCnmoForum2Item(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YIhei52Item(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YGfanForumItem(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YShayuForumItem(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YPconlineItem(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YImobileItem(Document):
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
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')
