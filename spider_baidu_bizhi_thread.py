# usr/bin/env python
# -*-coding:utf-8 -*-
import requests
import urllib
import os
import threading

gImageList=[]
gCondition=threading.Condition()
gCondition2=threading.Condition()
producerlist = []
gColumn='壁纸'
gTag='美女'
gWidth=1920
gHeight=1080

def isConsumerHungry():
    global gImageList
    return len(gImageList) < 20

class Producer(threading.Thread):
    def run(self):
        global gImageList
        global gCondition
        global producerlist
        global gConsumerHungry
        producerlist.append(threading.currentThread())
        print('%s started'%threading.currentThread())
        start=60
        count=60
        while True:
            if len(gImageList) > 10:
                gCondition2.acquire()
                gCondition2.wait_for(isConsumerHungry)
                gCondition2.release()
            gImageList += download_wallpaper_urllist(start, count)
            if len(gImageList) == 0:
                break
            gCondition.acquire()
            print('%s:produced%d urls.Left%d urls.'%(threading.currentThread(), len(gImageList), len(gImageList)))
            gCondition.notify_all()#t生产完了通知消费者
            gCondition.release()
            start += count
        producerlist.remove(threading.currentThread())
        gCondition.acquire()
        gCondition.notify_all()
        gCondition.release()
        print('%s stopped' % threading.currentThread())

class Consumer(threading.Thread):
    def run(self):
        global gImageList
        global gCondition
        global producerlist
        global gConsumerHungry
        print('%s started'% threading.currentThread())
        while True:
            gCondition.acquire()
            print('%s: trying to download image. Queue length is %d' % (threading.current_thread(), len(gImageList)))
            if len(gImageList)==0:
                if len(producerlist) == 0:
                    break
                gCondition.wait()
                if len(gImageList) == 0:
                    break
                print('%s: waken up. Queue length is %d' % (threading.current_thread(), len(gImageList)))
            url=gImageList.pop()#list.pop(index)移除列表中指定索引元素的值，默认是最后一个元素，并返回该元素的值。
            gCondition.release()

            gCondition2.acquire()
            gCondition2.notify_all()
            gCondition2.release()

            if 'downloadUrl' not in url:
                continue

            targetpath = 'wallpaperthread'
            targetpath = os.path.join(targetpath, str(gWidth) + 'x' + str(gHeight))
            targetpath = os.path.join(targetpath, gColumn)
            if not os.path.isdir(targetpath):
                os.makedirs(targetpath, exist_ok=True)
            targetpath2 = targetpath + '\\' + url['title']

            if not _download_image(url['downloadUrl'], targetpath2):
                targetpath2 = targetpath + '\\' + url['objTag']
                _download_image(url['downloadUrl'], targetpath2)

        print('%s stopped' % threading.currentThread())

def _download_image(url,folder):
    #print('download%s' %url)
    path = folder + '_' + os.path.split(url)[1]#连接路径与文件os.path.join
    if os.path.exists(path):
        return True

    print('download %s to %s', url, path)
    try:
        urllib.request.urlretrieve(url, path)
    except Exception as e:
        print(e)
    return True

def download_wallpaper_urllist(start='0', count='10'):
    url='http://image.baidu.com/data/imgs'
    params={
        'sort':1,
        'pn':start,
        'rn':count,
        'col':gColumn,
        'tag':gTag,
        'width':gWidth,
        'height':gHeight,
        'ie':'utf8',
        'oe':'utf - 8',
        'p':'channel',
        'from':'1'
    }
    #'ic':'0',
    #'fr':'channel',
    #'app':'img.browse.channel.wallpaper',
    #'t':'0.4931331318910932'
    r=requests.get(url,params=params)
    print('url: %s', r.request.url)
    #print("json: \n" + r.content)
    imgs=r.json()['imgs']
    #for i in imgs:
    #    if 'downloadUrl' in i:
    #        urllist.append(i['downloadUrl'])
        # if 'imageUrl' in i:
        #     urllist.append(i['imageUrl'])
    print('%s:totally get %d images'%(threading.current_thread(),len(imgs)))
    return imgs

if __name__=="__main__":
    Producer().start()
    for i in range(2):
        Consumer().start()