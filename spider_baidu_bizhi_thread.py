# usr/bin/env python
# -*-coding:utf-8 -*-
import requests
import urllib
import os
import threading

gImageList=[]
gCondition=threading.Condition()

class Producer(threading.Thread):
    def run(self):
        global gImageList
        global gCondition
        print('%s started'%threading.currentThread())
        gImageList=download_wallpaper_urllist()
        gCondition.acquire()
        print('%s:produced%d urls.Left%d urls.'%(threading.currentThread(), len(gImageList), len(gImageList)))
        gCondition.notify_all()#t生产完了通知消费者
        gCondition.release()

class Consumer(threading.Thread):
    def run(self):
        global gImageList
        global gCondition
        print('%s started'% threading.currentThread())
        while True:
            gCondition.acquire()
            print('%s: trying to download image. Queue length is %d' % (threading.current_thread(), len(gImageList)))
            while len(gImageList)==0:
                gCondition.wait()
                print('%s: waken up. Queue length is %d' % (threading.current_thread(), len(gImageList)))
            url=gImageList.pop()#list.pop(index)移除列表中指定索引元素的值，默认是最后一个元素，并返回该元素的值。
            gCondition.release()
            _download_image(url,'wallpaperthread')

def _download_image(url,folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    #print('download%s' %url)
    def _fname(s):
        #os.path.split(p)返回一个路径的目录名与文件名
        return os.path.join(folder,os.path.split(url)[1])#连接路径与文件os.path.join

    urllib.urlretrieve(url,_fname(url))


def download_wallpaper_urllist():
    global urllist
    urllist=[]
    url='http://image.baidu.com/data/imgs'
    params={
        'pn':'0',
        'rn':18,
        'col':'壁纸',
        'tag':'国家地理',
        'tag3':'',
        'width':1366,
        'height':786,
        'ic':'0',
        'ie':'utf8',
        'oe':'utf - 8',
        'image_id':'',
        'fr':'channel',
        'p':'channel',
        'from':'1',
        'app':'img.browse.channel.wallpaper',
        't':'0.4931331318910932'
 }
    r=requests.get(url,params=params)
    imgs=r.json()['imgs']
    for i in imgs:
        if 'downloadUrl' in i:
            urllist.append(i['downloadUrl'])
        # if 'imageUrl' in i:
        #     urllist.append(i['imageUrl'])
    print('%s:totally get %d images'%(threading.current_thread(),len(urllist)))
    return urllist

if __name__=="__main__":
    Producer().start()
    for i in range(2):
        Consumer().start()