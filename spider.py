# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import cookielib
from datetime import datetime, date, timedelta
from settings import topic, username, password, search_address, max_size
import glob

# 比较微博是否为同一条
# def isthesame(a, b):
#     return a["author"] == b["author"] and a["content"] == b["content"] \
#         and a["tool"] == b["tool"]

# 计算时间
# def calcu_time(time_text):
#     if re.match('今天.+', time_text):
#         return time_text.replace('今天', str(date.today().month) + '月' + str(date.today().day) + '日')
#     elif re.match('\d+分钟前', time_text):
#         tominus = int(re.match('\d+',time_text).group(0))
#         time = datetime.now() - timedelta(seconds=tominus*60)
#         return time.strftime('%m月%d日 %H:%M')
#     else:
#         return time_text

# 清理字符串
def clean(str):
    return re.sub(u'<.+?>','',str)\
        .replace('&nbsp;', '')

# 抽取有用信息
def extract(str):
    info = {}
    # 抽作者
    info["author"] = str.split(':')[0]
    str = str[len(info["author"])+1:]
    # 抽微博内容（仅文本）
    try:
        info["content"] = re.search('^.+?赞', str).group(0).replace('赞', '')
    except:
        info["content"] = "未知"
    # 抽时间
    # try:
    #     time = re.search('((\d{2}月\d{2}日|今天) \d{2}:\d{2})|\d+分钟前', str).group(0)
    #     # info["time"] = time
    #     info["time"] = calcu_time(time)
    # except:
    #     info["time"] = "未知"
    # 抽工具
    try:
        info["tool"] = re.search('来自.+', str).group(0)
    except:
        info["tool"] = '未知'

    return info

# 获取页面html代码
def getHtml(url, data=None):
    headers = {'User-Agent':'Mozilla/5.0 (SymbianOS/9.2; U; Series60/3.1 NokiaN82/31.0.016;Profile/MIDP-2.0 Configuration/CLDC-1.1 ) AppleWebKit/413 (KHTML, like Gecko) Safari/413',
                        'Referer':'','Content-Type':'application/x-www-form-urlencoded'}
    req = urllib2.Request(url, data, headers)
    return urllib2.urlopen(req).read()

# 假设不可能有连续五条微博消失掉
def figureout(weibos, obj_list):
    for w in weibos:
        if w in obj_list:
            return w
    return False

class Spider(object):

    def __init__(self):

        self.cj = cookielib.LWPCookieJar()
        self.cookie_processor = urllib2.HTTPCookieProcessor(self.cj)
        self.opener = urllib2.build_opener(self.cookie_processor, urllib2.HTTPHandler)
        urllib2.install_opener(self.opener)
        self.login_succeed = self.login()
        if(self.login_succeed):
            glob.weiboPool = self.search(page_num=1)
        else:
            print """Incorrect username or password!
            Please recheck your username and password and restart the server!"""

    def update(self):
        new_stuff = []
        i = 1
        weibos = self.search(page_num=i)
        # shit happens sometimes.
        if weibos[0] in glob.weiboPool:
            return []
        tails = []

        # head可能出于一些原因（被删了）找不到了，然后就会一直找下去！其实tail也可能消失掉。
        # 这里，假设不会有5条微博消失掉
        heads = glob.weiboPool[:5]
        while True:

            index_of_head = figureout(weibos, heads)

            if index_of_head:
                index_of_tail = figureout(weibos, tails)
                if index_of_tail:
                    new_stuff += weibos[weibos.index(index_of_tail)+1:weibos.index(index_of_head)]
                else:
                    new_stuff += weibos[:weibos.index(index_of_head)]
                glob.weiboPool = new_stuff + glob.weiboPool
                glob.weiboPool = glob.weiboPool[:max_size]
                break

            else:
                print "I've got something"
                index_of_tail = figureout(weibos, tails)
                if index_of_tail:
                    new_stuff += weibos[weibos.index(index_of_tail)+1:]
                else:
                    new_stuff += weibos
                tails = new_stuff[-5:]
                i += 1

            # 如果爬的速度赶不上发的速度，那爬50条就返回
            if len(new_stuff) >= 50:
                glob.weiboPool = new_stuff + glob.weiboPool
                glob.weiboPool = glob.weiboPool[:max_size]
                break
            weibos = self.search(page_num=i)

        # print "length of new stuff: " + str(len(new_stuff))
        return new_stuff

    def login(self):
        # 模拟登陆
        if re.search("<a href='(.*?)'>登录</a>", getHtml('http://weibo.cn/pub/')):
            loginHtml = getHtml('http://login.weibo.cn/login/')
            actionUrl = re.search('<form action="(.+?)" method="post">', loginHtml).group(1)
            pswFieldName = re.search('<input type="password" name="(.+?)" size="30" value=""/>', loginHtml).group(1)
            vkValue = re.search('<input type="hidden" name="vk" value="(.+?)" />', loginHtml).group(1)
            formData = urllib.urlencode({
                'mobile': username,
                 pswFieldName: password,
                'remember': 'on',
                'backURL': 'http://weibo.cn/',
                'backTitle': '手机新浪网',
                'tryCount': '',
                'vk': vkValue,
                'submit': '登录', })
            result = getHtml('http://login.weibo.cn/login/' + actionUrl, data=formData)

            return not re.search("<a href='(.*?)'>登录</a>", result)

    def extract_per_page(self, content):
        news = re.findall('<a class="nk".+?来自.+?</div>', content)
        if len(news) == 11:
            news = news[1:]
        return map(extract, map(clean, news))

    #搜微博
    def search(self, keyword=topic, page_num=1):
        result = []
        url = search_address.replace("@keyword", keyword).replace("@page", str(page_num+1))
        # print url
        content = getHtml(url)
        result += self.extract_per_page(content)

        return result

if __name__ == '__main__':
    print "shit happens"

    # f = open('shit.txt', 'w')
    # for n in res:
    #     f.write(n['author'] + '\n')
    #     f.write(n['content'] + '\n')
    #     f.write(n['time'] + '\n')
    #     f.write(n['tool'] + '\n')
    #     f.write('\n')
