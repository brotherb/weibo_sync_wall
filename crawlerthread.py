from spider import Spider
from threading import Thread
import time
import glob
from settings import crawl_interval

class CrawlerThread(Thread):
    def __int__(self):
        Thread.__init__(self)

    def run(self):
        sp = Spider()
        if not sp.login_succeed:
            self.stop()
        else:
            while True:
                new_stuff = sp.update()
                if len(new_stuff) > 0:
                    print str(len(new_stuff)) + " weibos to update"
                    glob.newswall.notifyCallbacks(new_stuff)
                time.sleep(crawl_interval)

    def stop(self):
        self.thread_stop = True