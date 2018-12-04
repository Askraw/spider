import random 
import docx
import sys
import os
import json
import io
import glob
import codecs
path='C:\\Users\\72499\\Downloads\\jiaocaiDownloads\\basics\\978-7-117-17314-8\\xml\\1.txt'
f=open(path,'r',encoding='ansi')
lines=f.readlines();
str='\n'.join(lines)
print(str.encode('utf-8'))