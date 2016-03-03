#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import datetime
import simplejson
import urllib2
import MySQLdb

import jieba
import jieba.analyse

def get_keyword(content, top_k=10):
    tags = jieba.analyse.extract_tags(content, topK=top_k)
    return " ".join(tags)

def get_id_num_content(someday):
    sql = """
          select id, num, content from news_xwlb where `day` = '%s'
          """ % someday.strftime("%Y-%m-%d")
    C.execute(sql)
    return C.fetchall()


def update_keyword(_id, _keyword):
    global DB, C

    sql = """update news_xwlb set keyword = "%s"
             where id = %s """
    C.execute(sql, (_keyword, _id))
    DB.commit()  # this line is important.


def get_daylist(startday, endday):
    daylist = []
    while startday <= endday:
        daylist.append(startday)
        startday = startday + datetime.timedelta(days=1)
    return daylist


def main(someday):
    id_num_content_list = get_id_num_content(someday)
    total_content = u""
    for _id, _num, _content in id_num_content_list[1:]:
        keyword = get_keyword(_content)
        update_keyword(_id, keyword.encode("utf8"))
        #print keyword
        total_content += _content
    keyword = get_keyword(total_content, 20)
    #print keyword
    update_keyword(id_num_content_list[0][0], keyword)


DB = None
C = None


def init_db(user, passwd, db, host="112.124.39.18", charset="utf8"):
    global DB, C

    DB = MySQLdb.connect(user=user, passwd=passwd, db=db, host=host, charset=charset)
    C = DB.cursor()


def close_db():
    global DB, C

    C.close()
    DB.close()


USER = "yhyan"
PASSWD = "yhyanP@55word"
DB = "dosite"


if __name__ == "__main__":
    if len(sys.argv) == 2:
        someday = datetime.datetime.strptime(sys.argv[1], "%Y%m%d")
        daylist = [someday]
    elif len(sys.argv) == 3:
        startday = datetime.datetime.strptime(sys.argv[1], "%Y%m%d")
        endday = datetime.datetime.strptime(sys.argv[2], "%Y%m%d")
        daylist = get_daylist(startday, endday)
    else:
        someday = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        daylist = [someday]

    init_db(USER, PASSWD, DB)
    for someday in daylist:
        main(someday)
    close_db()

