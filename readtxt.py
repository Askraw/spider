import random 
import docx
import sys
import os
import json
import io
import glob
url='C:\\Users\\72499\\Desktop\\MediHist\\1.txt'
f=open(url,'r',encoding="utf-8")
lines=f.readlines()
str='\n'.join(lines)
print(str)
path='C:\\Users\\72499\\Desktop\\MediHist'
os.getcwd()
os.chdir(path)
files=glob.glob('*.txt')

for filename in files:
    print(filename)