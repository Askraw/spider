import random 
import docx
import sys
import os
import json
import io
import glob

url='C:\\Users\\72499\\Desktop\\basics\\病理学 王恩华.docx'
document=docx.Document(url)
fo=open('D:\\1.txt', "ab+")
for para in document.paragraphs:
    if '。' in para.text:
        fo.write((para.text+'\n').encode('UTF-8'))  
fo.close()        #关闭小说文件
