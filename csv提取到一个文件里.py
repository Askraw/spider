import random 
import docx
import sys
import os
import json
import io
import glob

base_path='E:\\Code\\github\\IntelligentHealthcare\\KnowledgeBaseSystem\\BKB\\KGv1.3(Release)'
list1=['陈旻宇','丁如江','Daniel','李璟旸','罗金','罗艺康','谭锦豪','王若愚','钟绿波','高敏']
url2='C:\\Users\\72499\\Desktop\\all.csv'
filesum=0
linesum=0
for name in list1:
	pathx=base_path+'\\'+name
	os.chdir(pathx)
	files=glob.glob('*.csv')
	for filename in files:
		filesum+=1
		url=pathx+'\\'+filename
		fo1=open(url,'rb')
		lines=fo1.readlines()
		
		fo2=open(url2,"ab+")
		for line in lines:
			fo2.write(line)
			linesum+=1
		fo2.close()
		fo1.close()
