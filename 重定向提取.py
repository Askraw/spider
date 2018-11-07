#coding:utf-8
import random 
import docx
import sys
import os
import json
import io
import glob
readPath=r'E:\Code\wiki.txt'
writePath=r'E:\Code\wiki2.txt'
dict={}
s=set()
fo=open(readPath,'r',encoding='UTF-8')
lines=fo.readlines()
for line in lines:
    line=line.strip('\n')
    baseword=line.split(',')[1]  #本词
    otherword=line.split(',')[0]  #重定向的词
    if baseword not in s:
        s.add(baseword)
        dict[baseword]=otherword
    else:
        dict[baseword]+='\t'+otherword
fo.close()
fo=open(writePath,"ab+")
for key in dict:
    fo.write((key).encode('UTF-8'))
    fo.write(('\t').encode('UTF-8'))
    fo.write((dict[key]).encode('UTF-8'))
    fo.write(('\n').encode('UTF-8'))
fo.close()