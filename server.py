# -*- coding: utf-8 -*-

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.options
from settings import topic, port
from crawlerthread import CrawlerThread
import glob
from datetime import datetime

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html", topic = topic, data = glob.weiboPool[:20],
                    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        glob.newswall.register(self.callback)
        # glob.newswall.notifyCallbacks(glob.weiboPool[:5])

    def on_close(self):
        glob.newswall.unregister(self.callback)

    def callback(self, data):
        self.write_message(data)

class Application(tornado.web.Application):

    def __init__(self):

        handlers = [
            (r'/',MainHandler),
            (r'/update', WSHandler)
        ]
        settings = {
            'template_path': 'templates',
            'debug': True
        }
        tornado.web.Application.__init__(self, handlers, **settings)
        # 爬虫线程
        crawl_thread = CrawlerThread()
        try:
            crawl_thread.start()
        except:
            crawl_thread.stop()

if __name__ == '__main__':
    app = Application()
    server = tornado.httpserver.HTTPServer(app)
    server.listen(port)
    tornado.ioloop.IOLoop.instance().start()