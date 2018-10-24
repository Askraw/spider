# -*- coding: utf-8 -*-
import sys
from urllib import request
from bs4 import BeautifulSoup
import random 
import docx
import os
import json
import io
import glob
import requests
import string
from queue import Queue

writeinPath=r'E:\Code\words.txt'
url=r'阿尔茨海默病'
#url=url.encode('utf-8')

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}

#page = request.Request(url, headers=headers)
#page_info = request.urlopen(page).read()
#page_info = page_info.decode('utf-8')

# 将获取到的内容转换成BeautifulSoup格式，并将html.parser作为解析器
#soup = BeautifulSoup(page_info, 'html.parser')  

# 以格式化的形式打印html
# print(soup.prettify())
#aHrefs = soup.find_all('a', target='_blank')  # 查找所有a标签中class='title'的语句
# 打印查找到的每一个a标签的href为接下来的dfs提供url list
#i的目的是排除item的前5个秒懂百科的广告环节，接下来的问题就是对最后一个url词条：百度百科：本人词条编辑服务的修改
i=0
#s 的set负责存所有的url
base='https://baike.baidu.com/item/'
s=set()
q = Queue()
q.put(url)


while not q.empty():
    try:
        fo=open(writeinPath,"ab+")
        url=q.get()
        url=base+url
        #url=quote(url,safe=string.printable)
        #print(url)
        response= requests.get(url, headers=headers)

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
            
        keywords=soup.find_all('h1')
        for keyword in keywords:
            
            s1 = keyword.get_text()
            s1 = s1.strip('\n')
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

        fo.close()
    except Exception as e:
        print(e)
        continue

