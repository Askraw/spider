# -*- coding:utf-8 -*-
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

headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
'Cookie': 'HmHm_lvt_62d92d99f7c1e7a31a11759de376479f=1543834379; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2216773b3c270626-0cb871a46b4ade-6313363-2073600-16773b3c2715d%22%2C%22%24device_id%22%3A%2216773b3c270626-0cb871a46b4ade-6313363-2073600-16773b3c2715d%22%7D; ymt_pk_id=71c7811bd93c780a; ymtinfo=eyJ1aWQiOiIzNjIyNDQyIiwicmVzb3VyY2UiOiIiLCJhcHBfbmFtZSI6IiIsImV4dF92ZXJzaW9uIjoiMSJ9; _pk_ref.3.a971=%5B%22%22%2C%22%22%2C1543902803%2C%22https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DmkAdCoVf1sqA_aHwHlwSescjKeN2KqMJM1eWk5RPoCS%26wd%3D%26eqid%3Db5670efd0001f324000000035c061651%22%5D; s_history=%5B%22%E7%99%AB%E7%97%AB%22%2C%22%E8%8E%B7%E5%BE%97%E6%80%A7%E5%85%8D%E7%96%AB%E7%BC%BA%E9%99%B7%E7%BB%BC%E5%90%88%E5%BE%81%22%2C%22%E8%89%BE%E6%BB%8B%E7%97%85%22%2C%22%E5%8F%91%E7%83%A7%22%2C%22%E5%92%B3%E5%97%BD%22%2C%22%E8%82%BA%E7%BB%93%E6%A0%B8%22%2C%22%E9%98%BF%E5%85%B9%E6%B5%B7%E9%BB%98%E6%B0%8F%E7%97%87%22%2C%22%E5%A5%A5%E5%85%B9%E6%B5%B7%E9%BB%98%E7%97%87%22%5D; _pk_id.3.a971=71c7811bd93c780a.1543834393.2.1543905365.1543835349.; JSESSIONID=AC2258432C927086262AC9D01B37ED78; Hm_lpvt_62d92d99f7c1e7a31a11759de376479f=1543907935',
'Host': 'meddic.medlive.cn',
'Origin': 'http://meddic.medlive.cn',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
'X-Requested-With': 'XMLHttpRequest'
}
def test_ymt(url):#输出标准词和同义词列表
    add='word=癫痫'
    response= requests.get(url+add, headers=headers)
    response.encoding = response.apparent_encoding
    soup = BeautifulSoup(response.text, 'html.parser')  
    paras = soup.find_all('p') 
    tag=0
    for para in paras:
        if tag==1: 
            print(para.text)
            break
        if para.text=='疾病关联词典':
            tag=1
if __name__ == '__main__':
    url=r'http://meddic.medlive.cn/search/search.do?'
    test_ymt(url)