# -*- coding: utf-8 -*-
import json
from datetime import datetime

weiboPool = []

class Newswall():

    callbacks = []

    def register(self, callback):
        self.callbacks.append(callback)

    def unregister(self, callback):
        self.callbacks.remove(callback)

    def getJson(self, data):
        return json.dumps({'content': data, 'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

    def notifyCallbacks(self, data):
        print str(len(weiboPool)) + " weibos in total storage"
        for callback in self.callbacks:
            callback(self.getJson(data))

newswall = Newswall()