from multiprocessing import Process
import os
from urllib import request
from bs4 import BeautifulSoup
import random 
import docx
import json
import io
import glob
import requests
import string
from queue import Queue

import threading
import time

base='https://baike.baidu.com/item/'
writeinPath=r'E:\Code\words.txt'
url=r'阿尔茨海默病'
urlStart={r'阿尔茨海默病',r'上海交通大学',r'刀塔2'}
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}

base='https://baike.baidu.com/item/'
s=set()

fo=open(writeinPath,"ab+")

class myThread (threading.Thread):
    def __init__(self, threadID, url):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.url=url
    def run(self):
        q = Queue()
        q.put(self.url)
        i=0
        while not q.empty():
            try:
                self.url=q.get()
                self.url=base+self.url
                #url=quote(url,safe=string.printable)
                #print(url)
                response= requests.get(self.url, headers=headers)

                response.encoding = response.apparent_encoding
                soup = BeautifulSoup(response.text, 'html.parser')
                aHrefs = soup.find_all('a', target='_blank')
                for href in aHrefs:
                    str=href.get('href')
                    if str[0:6]=='/item/' :
                        if i>4 :
                            if str[6:] not in s:
                                s.add(str[6:])
                                q.put(str[6:])
                                #print(str)
                        i+=1
                #print(s)
                    
                keywords=soup.find_all('title')
                for keyword in keywords:
                    
                    s1 = keyword.get_text()
                    s1 = s1.strip('\n')
                    s1=s1[:-5]
                    print("title:"+s1)
                    output=s1

                    
                body_flag = False
                for element in soup.find_all(['dd', ['dt']]):
                    if element.string=='别称':
                        body_flag = True
                    if body_flag is True and element.name == 'dd':
                        s2 = element.get('title')
                        s2 = s2.strip('\n')
                        print("thesaurus:"+s2)
                        output+='\t'+s2

                        body_flag=False
                fo.write((output).encode('UTF-8'))
                fo.write(('\n').encode('UTF-8'))
                i=0


            except Exception as e:
                print(e)
                continue





threadLock = threading.Lock()
threads = []

# 创建新线程
thread1 = myThread(1,r'阿尔茨海默病' )
thread2 = myThread(2,r'上海交通大学')
thread3 = myThread(3,r'刀塔2' )

# 开启新线程
thread1.start()
thread2.start()
thread3.start()

# 添加线程到线程列表
threads.append(thread1)
threads.append(thread2)
threads.append(thread3)
# 等待所有线程完成
for t in threads:
    t.join()
print ("退出主线程")
fo.close()