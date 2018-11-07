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
'Cookie': 'JSESSIONID=1043CE90337DB5F820C291D48D595CF7',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
'X-Requested-With': 'XMLHttpRequest'
}
writeinPath=r'E:\Code\spider.txt'
def spiderUrl(url):
    
    postCont={'node': 'source'}
    reply=requests.post(url,headers=headers,data=postCont)
    output=json.loads(reply.text)

    baseurl=r'http://cmesh.imicams.ac.cn/index.action?action=extTreeMesh&ids='
    #+id
    addurl=r'&pnode='
    #+pcode


    i=0  #sum of url
    keyidList=[]
    for jsonObj in output:
        reUrl=baseurl+jsonObj['id']+addurl+jsonObj['pcode']
        postContLevel2={'node': jsonObj['id']}
        replyLevel2=requests.post(reUrl,headers=headers,data=postContLevel2)
        outputLevel2=json.loads(replyLevel2.text)
        for item in outputLevel2:
            keyidList.append(item['id'])
            i+=1
    print(i)
    print(keyidList)
    return keyidList
def spiderUrl2(url):
    
    postCont={'node': 'source'}
    reply=requests.post(url,headers=headers,data=postCont)
    output=json.loads(reply.text)
    keyidList=[]
    for jsonObj in output:
        keyidList.append(jsonObj['id'])
    print(keyidList)
    return keyidList

def func():
    url=r'http://cmesh.imicams.ac.cn/index.action?action=extTreeMesh&ids=source&pnode='
    keyidList=spiderUrl(url)
    s=set()
    for keyid in keyidList:
        dfs(keyid,s)
    addUrl=r'http://cmesh.imicams.ac.cn/tzc.action?action=extTreeTzc&ids=source&pnode='
    addIdList=spiderUrl2(addUrl)
    for id in addIdList:
        dfs2(id,s)
def dfs2(keyid,s):
    if keyid not in s:
        try:
            s.add(keyid)
            detailUrlFront=r'http://cmesh.imicams.ac.cn/index.action?action=mainWordView&keyid='
            detailUrlBack=r'&beanName=com.tbs.dictweb.bean.ZtcKmcPage'
            url=detailUrlFront+keyid+detailUrlBack
            print(url)
            response= requests.get(url, headers=headers)
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            tables=soup.find_all('table')
            print(len(tables))

            trs = tables[2].find_all('tr')
            fo=open(writeinPath,"ab+")
            for tr in trs:
                tds=tr.find_all('td')
                output=(re.sub(r'\r\n|\t|\n|\r', '', tds[0].text)).strip()
                output+='\t'
                output+=re.sub(r'\r\n|\t|\n|\r', '', tds[1].text).strip()
                fo.write((output).encode('UTF-8'))
                fo.write(('\n').encode('UTF-8'))
                #print(output)
                #print(tds[1].text.replace(' ',''))
            fo.write(('\n').encode('UTF-8'))
            fo.close()
            iframeUrls=soup.find_all('iframe')
            if iframeUrls!=[]:
                treeUrl=r'http://cmesh.imicams.ac.cn/'+iframeUrls[0].attrs['src']
                response2= requests.get(treeUrl, headers=headers)
                response2.encoding = response.apparent_encoding
                soup2 = BeautifulSoup(response2.text, 'html.parser')
                ahrefs=soup2.find_all('a')

                for ahref in ahrefs:
                    #print(ahref.text)
                    index=find_last(ahref.attrs['href'],'=')
                    dfs2(ahref.attrs['href'][index+1:],s)
        except Exception as e:
            print(e)
            
    else:
        return

        
def dfs(keyid,s):
    if keyid not in s:
        try:
            s.add(keyid)
            detailUrlFront=r'http://cmesh.imicams.ac.cn/index.action?action=mainWordView&beanName=com.tbs.dictweb.bean.ZtcKmcPage&keyid='
            url=detailUrlFront+keyid
            print(url)
            response= requests.get(url, headers=headers)
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            tables=soup.find_all('table')
            print(len(tables))

            trs = tables[2].find_all('tr')
            fo=open(writeinPath,"ab+")
            for tr in trs:
                tds=tr.find_all('td')
                output=(re.sub(r'\r\n|\t|\n|\r', '', tds[0].text)).strip()
                output+='\t'
                output+=re.sub(r'\r\n|\t|\n|\r', '', tds[1].text).strip()
                fo.write((output).encode('UTF-8'))
                fo.write(('\n').encode('UTF-8'))
                #print(output)
                #print(tds[1].text.replace(' ',''))
            fo.write(('\n').encode('UTF-8'))
            fo.close()
            iframeUrls=soup.find_all('iframe')
            if iframeUrls!=[]:
                treeUrl=r'http://cmesh.imicams.ac.cn/'+iframeUrls[0].attrs['src']
                response2= requests.get(treeUrl, headers=headers)
                response2.encoding = response.apparent_encoding
                soup2 = BeautifulSoup(response2.text, 'html.parser')
                ahrefs=soup2.find_all('a')

                for ahref in ahrefs:
                    #print(ahref.text)
                    index=find_last(ahref.attrs['href'],'=')
                    dfs(ahref.attrs['href'][index+1:],s)
        except Exception as e:
            print(e)
            
    else:
        return

def find_last(string,str):
    last_position=-1
    while True:
        position=string.find(str,last_position+1)
        if position==-1:
            return last_position
        last_position=position


def read(keyid): #mode=1 parentNode mode=2 leafNode
    detailUrlFront=r'http://cmesh.imicams.ac.cn/index.action?action=mainWordView&beanName=com.tbs.dictweb.bean.ZtcKmcPage&keyid='
    url=detailUrlFront+keyid
    response= requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')
    tables=soup.find_all('table')
    trs = tables[2].find_all('tr')
    fo=open(writeinPath,"ab+")
    for tr in trs:
        tds=tr.find_all('td')
        output=re.sub(r'\r\n|\t| |&nbsp|&ensp|&emsp|&thinsp|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020|\n|\r', '', tds[0].text)
        output+='\t'
        output+=re.sub(r'\r\n|\t| |&nbsp|&ensp|&emsp|&thinsp|\xa0|\\xa0|\u3000|\\u3000|\\u0020|\u0020|\n|\r', '', tds[1].text)
        fo.write((output).encode('UTF-8'))
        fo.write(('\n').encode('UTF-8'))
        #print(output)
        #print(tds[1].text.replace(' ',''))
    fo.write(('\n').encode('UTF-8'))
    fo.close()
    treeUrls=soup.find_all('iframe')
    print(treeUrls[0].attrs['src'])
    iframeUrls=soup.find_all('iframe')
    treeUrl=r'http://cmesh.imicams.ac.cn/'+iframeUrls[0].attrs['src']
    response2= requests.get(treeUrl, headers=headers)
    response2.encoding = response.apparent_encoding
    soup2 = BeautifulSoup(response2.text, 'html.parser')
    ahrefs=soup2.find_all('a')
    i=0
    for ahref in ahrefs:
        if i>1:
            print(ahref.text)
            print(ahref.attrs['href'][-7:])
        i+=1

if __name__ == '__main__':
    func()


