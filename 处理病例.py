import random 
import docx
import sys
import os
import json
import io
import glob

base_path='C:\\Users\\72499\\Desktop\\MediHist'
base_path2='C:\\Users\\72499\\Desktop\\MediHist\\short'
os.chdir(base_path)
files=glob.glob('*.txt')
for filename in files:
    url=base_path+'\\'+filename
    url2=base_path2+'\\'+filename
    fo1=open(url,'r',encoding="utf-8")
    lines=fo1.readlines()
    fo2=open(url2,"ab+")
    for line in lines:
        if '诊疗计划：' in line:
            break
        else:
            fo2.write((line).encode('UTF-8'))
    fo2.close()
    fo1.close()