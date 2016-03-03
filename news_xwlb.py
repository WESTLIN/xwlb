#!/usr/bin/env python

import sys
import datetime
import simplejson
import urllib2
import MySQLdb
from bs4 import BeautifulSoup  # pip install beautifulsoup4

URL_FORMAT = "http://tv.cctv.com/lm/xwlb/day/%s.shtml"


def get_soup(url):
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html)
    return soup

def get_data_by_day(someday):
    url = URL_FORMAT % someday.strftime("%Y%m%d")
    soup = get_soup(url)


    a_list = soup.findAll("a")
    data = []
    num = 0
    for a in a_list:
        href = a["href"]
        title = a.text.encode("utf8")
        print title
        print href
        data.append([num, someday, href, title, datetime.datetime.now()])
        num = num + 1
    return data


def insert_to_db(iterdata):
    global DB, C

    sql = """INSERT INTO  news_xwlb (`num`, `day`, `url`, `title`, created_at)
           VALUES (%s, %s, %s, %s, %s)
            on duplicate key update updated_at = now()"""
    C.executemany(sql, iterdata)
    DB.commit()  # this line is important.


def get_daylist(startday, endday):
    daylist = []
    while startday <= endday:
        daylist.append(startday)
        startday = startday + datetime.timedelta(days=1)
    return daylist


def main(someday):
    data = get_data_by_day(someday)
    insert_to_db(data)


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

