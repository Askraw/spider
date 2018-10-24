import random 
import docx
import sys
import os
import json
import io
import glob

#base_path='C:\\Users\\72499\\Desktop\\MediHist'
base_path2='C:\\Users\\72499\\Desktop\\MediHist\\short'
base_path3='C:\\Users\\72499\\Desktop\\MediHist\\short\\review'
base_path4='C:\\Users\\72499\\Desktop\\MediHist\\short\\diagnose'
os.chdir(base_path2)
files=glob.glob('*.txt')
for filename in files:
    #url=base_path+'\\'+filename
    
    #基地址
    url2=base_path2+'\\'+filename
    #主述路径和 诊断路径
    url3=base_path3+'\\'+filename
    url4=base_path4+'\\'+filename
    #fo1=open(url,'r',encoding="utf-8")
    #lines=fo1.readlines()
    fo2=open(url2,'r',encoding="utf-8")
    lines=fo2.readlines()
    fo3=open(url3,"ab+")
    fo4=open(url4,"ab+")
    tag=1
    for line in lines:
        if tag==1:
            if '诊断：' not in line:
                fo3.write((line).encode('UTF-8'))
            else:
                fo4.write((line).encode('UTF-8'))
                tag=0
        else:
            fo4.write((line).encode('UTF-8'))
    fo2.close()
    fo3.close()
    fo4.close()