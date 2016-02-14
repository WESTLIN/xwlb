#!/usr/bin/env python

import sys
import datetime
import simplejson
import urllib2
import MySQLdb
from bs4 import BeautifulSoup  # pip install beautifulsoup4


S_TAG = '<div class="body" id="content_body">'
E_TAG = '</div>'

def get_soup(url):
    html = urllib2.urlopen(url).read()
    s = html.find(S_TAG)
    if s < 0:
        return None
    e = html.find(E_TAG, s)
    content = html[s:e+len(E_TAG)]
    soup = BeautifulSoup(content)
    return soup


def get_content(href):
    soup = get_soup(href)
    if not soup:
        return ""
    plist = soup.find_all("p")
    s = ""
    for p in plist:
        s += p.text
    return s

def get_id_and_href(someday):
    sql = """
          select id, url from news_xwlb where `day` = '%s'
          """ % someday.strftime("%Y-%m-%d")
    C.execute(sql)
    return C.fetchall()


def update_content(_id, _content):
    global DB, C

    sql = """update news_xwlb set content = "%s"
             where id = %s """
    #print sql %(_content, _id)
    C.execute(sql, (_content, _id))
    DB.commit()  # this line is important.


def get_daylist(startday, endday):
    daylist = []
    while startday <= endday:
        daylist.append(startday)
        startday = startday + datetime.timedelta(days=1)
    return daylist


def main(someday):
    id_href_list = get_id_and_href(someday)
    for _id, _href in id_href_list:
        content = get_content(_href)
        update_content(_id, content.encode("utf8"))


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
DB = "pypress"


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

