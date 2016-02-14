#!/usr/bin/env python

import urllib

import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import os.path
import uuid

from tornado import httpserver
from tornado.concurrent import Future
from tornado import gen
from tornado.options import define, options, parse_command_line
from tornado import template


from models import News


define("port", default=8880, help="run on the given port", type=int)

class MainHandler(tornado.web.RequestHandler):

    def get_more_page(self):
        self.render('more.html')

    def get_detail_page(self):

        self.render('detail.html')

    def get_index_page(self):
        page = int(self.get_argument('page', 1))
        page_obj = News.query.paginate(page=page, per_page=News.PER_PAGE)
        page_url = self.request.uri + "?%s" % urllib.urlencode(dict(page=page))
        self.render('index.html', page_obj, page_url)

    
    def get(self, *args):
        api_or_page = args[0]
        if api_or_page == 'more':
            self.get_more_page()
        elif api_or_page == 'detail':
            self.get_detail_page()
        else:
            self.get_index_page()
            
def main():
    tornado.options.parse_command_line()
    settings = dict(
        cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        template_path=os.path.join(os.path.dirname(__file__), "html"),
        static_path=os.path.join(os.path.dirname(__file__), "html"),
        xsrf_cookies=True,
        debug=False,
    )

    mapping = [
        (r"/xwlb/(\w+)(/.*)?", MainHandler),
    ]
    app = tornado.web.Application(
        mapping, **settings
    )

    http_server = httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()