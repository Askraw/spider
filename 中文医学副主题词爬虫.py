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
import re

sys.setrecursionlimit(1000000) #括号中的值为递归深度
headers = {'Content-Type': 'json;charset=UTF-8;charset=UTF-8',
'Cookie': 'JSESSIONID=82F41F8DEE45C9842D421833CD098C3A',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
'X-Requested-With': 'XMLHttpRequest'
}
writeinPath=r'E:\Code\spider2.txt'
def spiderUrl(url):
    postCont={'node': 'source'}
    reply=requests.post(url,headers=headers,data=postCont)
    output=json.loads(reply.text)
    
    baseurl=r'http://cmesh.imicams.ac.cn/quli.action?action=extTreeQuli&ids='
    addurl=r'&pnode='
    idList=[]
    
    for jsonObj in output:
        print(jsonObj['id']+'\t'+jsonObj['pcode']+'\t'+jsonObj['text'])
        #print(jsonObj['id']+'\t'+jsonObj['pcode'])
        idList.append(jsonObj['id'])
        if jsonObj['leaf']== False:
            xhrUrl1=baseurl+jsonObj['id']+addurl+jsonObj['pcode']
            postContLevel1={'node': jsonObj['id']}
            replyLevel1=requests.post(xhrUrl1,headers=headers,data=postContLevel1)
            outputLevel1=json.loads(replyLevel1.text)
            
            for jsonObj2 in outputLevel1:
                print(jsonObj2['id']+'\t'+jsonObj2['pcode']+'\t\t'+jsonObj2['text'])
                #print(jsonObj2['id']+'\t'+jsonObj2['pcode'])
                idList.append(jsonObj2['id'])
                if jsonObj2['leaf']==False:
                    xhrUrl2=baseurl+jsonObj2['id']+addurl+jsonObj2['pcode']
                    postContLevel2={'node': jsonObj2['id']}
                    replyLevel2=requests.post(xhrUrl2,headers=headers,data=postContLevel2)
                    outputLevel2=json.loads(replyLevel2.text)
                    for jsonObj3 in outputLevel2:
                        print(jsonObj3['id']+'\t'+jsonObj3['pcode']+'\t'+jsonObj3['text'])
                        idList.append(jsonObj3['id'])
    return idList
                
def func():
    #url=r'http://cmesh.imicams.ac.cn/index.action?action=extTreeMesh&ids=source&pnode='
    url=r'http://cmesh.imicams.ac.cn/quli.action?action=extTreeQuli&ids=source&pnode='
    idList=spiderUrl(url)
    print(idList)
    read(idList)
    # s=set()
    # for keyid in keyidList:
        # dfs(keyid,s)



def find_last(string,str):
    last_position=-1
    while True:
        position=string.find(str,last_position+1)
        if position==-1:
            return last_position
        last_position=position

def read(idList): #mode=1 parentNode mode=2 leafNode
    detailUrlFront=r'http://cmesh.imicams.ac.cn/index.action?action=mainWordView&beanName=com.tbs.dictweb.bean.QuliBean&fztc_tree=fztc&keyid='
    for keyid in idList:
        url=detailUrlFront+keyid
        response= requests.get(url, headers=headers)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        tables=soup.find_all('table')
        trs = tables[1].find_all('tr')
        fo=open(writeinPath,"ab+")
        for tr in trs:
            tds=tr.find_all('td')
            output=re.sub(r'\r\n|\t|\n|\r', '', tds[0].text).strip()
            output+='\t'
            output+=re.sub(r'\r\n|\t|\n|\r', '', tds[1].text).strip()
            fo.write((output).encode('UTF-8'))
            fo.write(('\n').encode('UTF-8'))
            #print(output)
            #print(tds[1].text.replace(' ',''))
        fo.write(('\n').encode('UTF-8'))
        fo.close()
    

if __name__ == '__main__':
    func()


