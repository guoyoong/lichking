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


class YPcpopItem(Document):
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


class YJdItem(Document):
    _id = StringField(default='')
    title = StringField(default='')
    url = StringField(default='')
    content_url = StringField(default='')
    itemId = StringField(default='')
    insert_time = StringField(default='')
    source = StringField(default='')
    source_short = StringField(default='')
    category = StringField(default='')
    flag = StringField(default='')
    views = StringField(default='')
    replies = StringField(default='')
    goods_score_name = StringField(default='')
    score = StringField(default='')
    product_detail = ListField()
    content = StringField(default='')
    time = StringField(default='')
    order_time = StringField(default='')
    comment_guid = StringField(default='')
    comment_id = StringField(default='0.1')
    user_level_name = StringField(default='0.1')
    useless_vote_count = StringField(default='0.1')
    useful_vote_count = StringField(default='0.1')
    nick_name = StringField(default='0.1')
    user_client = StringField(default='0.1')
    last_reply_time = StringField(default='0.1')
    v = StringField(default='0.1')
    parse_time = StringField(default='')
    hotTags = ListField()
    replies_comment = ListField()


class YZolItem(Document):
    _id = StringField(default='')
    tid = StringField(default='')
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
    info = ListField()
    content = StringField(default='')
    time = StringField(default='')
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YSuningItem(Document):
    _id = StringField(default='')
    title = StringField(default='')
    url = StringField(default='')
    content_url = StringField(default='')
    insert_time = StringField(default='')
    source = StringField(default='')
    source_short = StringField(default='')
    itemId = StringField(default='')
    category = StringField(default='')
    flag = StringField(default='')
    views = StringField(default='0')
    replies = StringField(default='')
    goods_score_name = StringField(default='')
    score = StringField(default='')
    product_detail = StringField(default='')
    content = StringField(default='')
    time = StringField(default='')
    useful_vote_count = StringField(default='')
    user_client = StringField(default='')
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')
    parse_time = StringField(default='')
    hotTags = ListField()
    replies_comment = ListField()


class YSanliukrItem(Document):
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
    views = StringField(default='0')

    comment = ListField()
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YHuxiuItem(Document):
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
    views = StringField(default='0')

    comment = ListField()
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YToutiaoItem(Document):
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
    views = StringField(default='0')

    comment = ListField()
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YIfanrItem(Document):
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
    views = StringField(default='0')

    comment = ListField()
    insert_time = StringField(default='')
    flag = StringField(default='')
    parse_time = StringField(default='')
    last_reply_time = StringField(default='')
    v = StringField(default='0.1')


class YQichachaItem(Document):
    _id = StringField(default='')
    name = StringField(default='')
    base_info = ListField()
    susong = ListField()
    firm_run = ListField()
    touzi = ListField()
    report = ListField()
    assets = ListField()
    yuqing = ListField()
    insert_time = StringField(default='')


class YuqingSpiderMonitor(Document):
    _id = StringField(default='')
    key = StringField(default='')
    crawl_pages = StringField(default='')
    new_pages = StringField(default='')
    source_type = StringField(default='')
    duration = StringField(default='')
    date_stat = StringField(default='')


class FreeProxyItem(Document):
    _id = StringField(default='')
    ip = StringField(default='')
    port = StringField(default='')
    time = StringField(default='')

