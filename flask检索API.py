#coding=utf-8
# author luojin 2018/4/9 ver1.0
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import random 
import docx
import sys
import os
import json
import io
import glob
from datetime import datetime 
from flask import Flask
from flask import request

#ES接口类
class ESinterface:
    
    i=0
    j=0  #用于批量bulk计数的 也是为了防止内存占用过多
    k=0  #用来计数句子的

    id=""
    level=0
    epiId="" #episode id
    chId="" #chapter id

    contId=""
    paraId=""
    sentId=""

    lv0Num=0
    lv1Num=1   #节 都是从1开始的 因为有内容
    lv2Num=0
    lv3Num=0

    str_epi="章"
    str_ch="节"
    str_start="标题: "

    title=""
    outputs=[]
    actions = []

    pg=""
    tag=0   #用于标记是节内跳转 还是标题跳节
    
    keyWordsArr=[]
    hits=[]
    resDoc=[]
    resDocScore=[]
    resDic={'documents':[]}
    
    def __init__(self,url):
        self.es=Elasticsearch(url)
    
    #导入书籍的方法
    #index不能有大写字母
    def depositText(self,url,_index,_type):
        self.url=url
        self.index=_index
        self.type=_type
        self.document=docx.Document(self.url)
        _index_mappings = {"mappings": {self.type:{"properties":{"content":{"type":"text","analyzer":"ik_smart"},"pred":{"type":"keyword"},"succ":{"type":"keyword"},"type":{"type":"keyword"}}}}}

        if self.es.indices.exists(index=self.index) is not True:
            self.es.indices.create(index=self.index, body=_index_mappings) 
        for para in self.document.paragraphs:
            if self.i>132:
                if self.str_epi in para.text and self.str_start in para.text:  #如果是章
                    self.level=0
                    if self.tag==0 and self.contId!="":   #处理章下没有节只有内容的情形 这里append 内容节点 章内容到章
                        action={
                            "_index": self.index,
                            "_type": self.type,
                            "_id": self.contId,
                            "_source": {
                            "content":"",
                            "pred":self.epiId,
                            "succ":hex(self.lv2Num),
                            "type": "content",
                            "timestamp": datetime.now()
                            }
                        }
                        self.actions.append(action)
                        self.j+=1
                        if self.j%50==0:
                            helpers.bulk(self.es, self.actions)
                            self.actions=[]
                
                
                    if  self.tag==1 and self.contId!="":  #处理 节内容 到章
                        action={
                            "_index": self.index,
                            "_type": self.type,
                            "_id": self.contId,
                            "_source": {
                            "content":"",
                            "pred":self.chId,
                            "succ":hex(self.lv3Num),
                            "type": "content",
                            "timestamp": datetime.now()
                            }
                        }
                        self.actions.append(action)
                        self.j+=1
                        if self.j%50==0:
                            helpers.bulk(self.es, self.actions)
                            self.actions=[]
                
                
                        self.lv3Num=0
                        self.tag=0     #这是从上一章的节 过渡到本章 所以需要把tag重新赋值为1
                
                    self.lv2Num=0             #清空段落数 和句子数
                              
                    if self.lv0Num!=0:        #对章进行append  在代码最后缺一个 对最后一章（节）的节点的append
                        self.contId=self.epiId+hex(0)
                        action={
                            "_index": self.index,
                            "_type": self.type,
                            "_id": self.epiId,
                            "_source": {
                            "content":self.title,
                            "pred":"",
                            "succ":self.contId,
                            "type": "title",
                            "timestamp": datetime.now()
                            }
                        }
                        self.actions.append(action)
                        self.j+=1
                        if self.j%50==0:
                            helpers.bulk(self.es, self.actions)
                            self.actions=[]
                
                    self.lv1Num=1   #清空章下 节点数  第一个节点是内容 所以节是从1开始的！！！
            
                    self.title=para.text.split()[2] #确定本章节的title和epiId
                    self.epiId=hex(self.lv0Num)
                    self.contId=self.epiId+hex(0)
            
                    self.lv0Num+=1
                elif self.str_ch in para.text and self.str_start in para.text:  #如果是chapter
                    self.level=1
            
                    if  self.tag==1 and self.contId!="":  #处理 节内容到节
                        action={
                            "_index": self.index,
                            "_type": self.type,
                            "_id": self.contId,
                            "_source": {
                            "content":"",
                            "pred":self.chId,
                            "succ":hex(self.lv3Num),
                            "type": "content",
                            "timestamp": datetime.now()
                            }
                        }
                        self.actions.append(action)
                        self.j+=1
                        if self.j%50==0:
                            helpers.bulk(self.es, self.actions)
                            self.actions=[]
                   
                        self.lv3Num=0
                    if self.tag==0 and self.contId!="":   #处理 章内容到节
                        action={
                            "_index": self.index,
                            "_type": self.type,
                            "_id": self.contId,
                            "_source": {
                            "content":"",
                            "pred":self.epiId,
                            "succ":hex(self.lv2Num),
                            "type": "content",
                            "timestamp": datetime.now()
                            }
                        }
                        self.actions.append(action)
                        self.j+=1
                        if self.j%50==0:
                            helpers.bulk(self.es, self.actions)
                            self.actions=[]
                        
                        self.tag=1  #过渡到节以后 这个tag就要改成1
                
                    self.lv2Num=0   #清空段落数 和句子数
                    self.lv3Num=0
           
                    self.title=para.text.split()[2] #确定本节的title和chId
                    self.chId=self.epiId+hex(self.lv1Num)
                    self.contId=self.chId+hex(0)
            
                    action={                       #append节
                        "_index": self.index,
                        "_type": self.type,
                        "_id": self.chId,
                        "_source": {
                        "content":self.title,
                        "pred":self.epiId,
                        "succ":self.contId,     #k个子句 从1开始
                        "type": "title",
                        "timestamp": datetime.now()
                        }
                    }
                    self.actions.append(action)
                    self.j+=1
                    if self.j%50==0:
                        helpers.bulk(self.es, self.actions)
                        self.actions=[]
            
                    self.lv1Num+=1               #节数 自增
            
                elif self.tag==0 and para.text!="":  #章后内容
                    self.paraId=self.contId+hex(self.lv2Num)
                    self.outputs=para.text.split("。")
                    self.k=0
                    for output in self.outputs:   #对句子遍历
                        self.sentId=self.paraId+hex(self.k)   #章下的句子id为章id+内容id（0）+段落id+句子id
                        self.pg+=output
                        self.pg+="。"
                        action={
                            "_index": self.index,
                            "_type": self.type,
                            "_id": self.sentId,
                            "_source": {
                            "content":output,
                            "pred":self.paraId,
                            "succ":"",
                            "type": "content",
                            "timestamp": datetime.now()
                            }
                        }
                        self.actions.append(action)
                        self.j+=1
                        if self.j%50==0:
                            helpers.bulk(self.es, self.actions)
                            self.actions=[]
                        self.k+=1
            
                    action={                 #append段落
                        "_index": self.index,
                        "_type": self.type,
                        "_id": self.paraId,
                        "_source": {
                        "content":self.pg,
                        "pred":self.contId,
                        "succ":hex(self.k),     #k个子句 从1开始
                        "type": "content",
                        "timestamp": datetime.now()
                        }
                    }
                    self.actions.append(action)
                    self.j+=1
                    if self.j%50==0:
                        helpers.bulk(self.es,self.actions)
                        self.actions=[]
                    self.pg=""
                    self.lv2Num+=1 #段num++
                elif self.tag==1 and para.text!="":  #节后内容
                    self.paraId=self.contId+hex(self.lv3Num)
                    self.outputs=para.text.split("。")
                    self.k=0
                    for output in self.outputs:   #对句子遍历
                        self.sentId=self.paraId+hex(self.k)   #章下的句子id为章id+内容id（0）+段落id+句子id
                        self.pg+=output
                        self.pg+="。"
                        action={
                            "_index": self.index,
                            "_type": self.type,
                            "_id": self.sentId,
                            "_source": {
                            "content":output,
                            "pred":self.paraId,
                            "succ":"",
                            "type": "content",
                            "timestamp": datetime.now()
                            }
                        }
                        self.actions.append(action)
                        self.j+=1
                        if self.j%50==0:
                            helpers.bulk(self.es,self.actions)
                            self.actions=[]
                    
                        self.k+=1
            
                    action={       #对para进行append
                        "_index": self.index,
                        "_type": self.type,
                        "_id": self.paraId,
                        "_source": {
                        "content":self.pg,
                        "pred":self.contId,
                        "succ":hex(self.k),     #k个子句 从1开始
                        "type": "content",
                        "timestamp": datetime.now()
                        }
                    }
                    self.actions.append(action)
                    self.j+=1
                    if self.j%50==0:
                        helpers.bulk(self.es, self.actions)
                        self.actions=[]
            
                    self.pg=""
                    self.lv3Num+=1 #段num++
            self.i+=1

        if self.tag==0 and self.contId!="":   #处理章下没有节只有内容的情形 这里append 内容节点
            action={
                "_index": self.index,
                "_type": self.type,
                "_id": self.contId,
                "_source": {
                "content":"",   
                "pred":self.epiId,
                "succ":hex(self.lv2Num),
                "type": "content",
                "timestamp": datetime.now()
                }
            }
            self.actions.append(action)
            self.j+=1
            if self.j%50==0:
                helpers.bulk(self.es, self.actions)
                self.actions=[]
    
        if  self.tag==1 and self.contId!="":  #处理章有节的情况下 最后一个节的内容节点
            action={
                "_index": self.index,
                "_type": self.type,
                "_id": self.contId,
                "_source": {
                "content":"",
                "pred":self.chId,
                "succ":hex(self.lv3Num),
                "type": "content",
                "timestamp": datetime.now()
                }
            }
            self.actions.append(action)
            self.j+=1
            if self.j%50==0:
                helpers.bulk(self.es, self.actions)
                self.actions=[]
              
        self.lv3Num=0
        self.tag=0     #这是从上一章的节 过渡到本章 所以需要把tag重新赋值为1
                
        self.lv2Num=0             #清空段落数 和句子数
                              
        if self.lv0Num!=0:        #对章进行append  在代码最后缺一个 对最后一章（节）的节点的append
            action={
                "_index": self.index,
                "_type": self.type,
                "_id": self.epiId,
                "_source": {
                "content":self.title,
                "pred":"",
                "succ":self.contId,
                "type": "title",
                "timestamp": datetime.now()
                }
            }
            self.actions.append(action)
            self.j+=1
            if self.j%50==0:
                helpers.bulk(self.es, self.actions)
                self.actions=[]
    
    #导入病历到es
    def depositMediHist(self,url,_index,_type):
        
        self.index=_index
        self.type=_type
        
        _index_mappings = {"mappings": {self.type:{"properties":{"content":{"type":"text","analyzer":"ik_smart"},"pred":{"type":"keyword"},"succ":{"type":"keyword"},"type":{"type":"keyword"}}}}}

        if self.es.indices.exists(index=self.index) is not True:
            self.es.indices.create(index=self.index, body=_index_mappings)
        mark=1
        os.chdir(url)
        self.files=glob.glob('*.txt')
        for filename in self.files:
            self.url=url+'\\'+filename
            self.f=open(self.url,'r',encoding="utf-8")
            self.lines=self.f.readlines()
            self.output='\n'.join(self.lines)
            action={
                "_index": self.index,
                "_type": self.type,
                "_id": mark,
                "_source": {
                    "content":self.output,
                    "type": "content",
                    "timestamp": datetime.now()
                    }
                }
            self.actions.append(action)
            self.j+=1
            if self.j%50==0:
                helpers.bulk(self.es, self.actions)
                self.actions=[]
            mark+=1
        helpers.bulk(self.es, self.actions)
        self.actions=[]
            
    #获取输入的关键字数组
    def getArr(self,arr):
        if arr==[]:
            str=input("输入关键词(词之间请加空格)：")
            for word in str.split():
                self.keyWordsArr.append(word)
        else:
            self.keyWordsArr=arr

    #输出文档数组，并按相关度排序
    def printDocs(self):
        
        for hit in self.hits:
            self.resDoc.append(hit['_source']['content'])
        print(resDoc)
    
    #返回文档数组，并按相关度排序
    def reDocs(self):
        self.resDoc=[]
        for hit in self.hits:
            self.resDoc.append(hit['_source']['content'])
        return self.resDoc
    
    #输出得分数组 文档相关度的评分数组
    def printScores(self):
        
        for hit in self.hits:
            self.resDocScore.append(hit['_score'])
        print(resDocScore)
    
    #返回得分数组 文档相关度的评分数组
    def reScores(self):
        self.resDocScore=[]
        for hit in self.hits:
            self.resDocScore.append(hit['_score'])
        return self.resDocScore
    
    #返回一个结果数组其中每一个item都是形如{"id":,"text":,"score":}
    def resArray(self):   #得到结果数组即 [{"id":,"text":,"score":},…,]
        self.resArr=[]
        #itemDic={} 如果写在这一行 会出bug 即resArr的每个item都是最后那个item
        #引起这个bug的原因可能跟作用域有关 由于每个append的item都是itemDic 而itemDic是外部变量 所有每次修改每个item都被修改了
        for hit in self.hits:
            itemDic={}
            itemDic['id']=hit['_id']
            itemDic['text']=hit['_source']['content']
            itemDic['score']=hit['_score']
            self.resArr.append(itemDic)
        return self.resArr
            
    #根据 （关键词数组、粒度、最低match词语数限制）获得结果并通过2个print函数完成输出 5/15添加输出的文档数量限制
    #mode=1,2,3对应 段句、段、句
    def retrieveText(self,reIndex,reType,mode,minMatch,limit,arr=[]):
        wordSum=0
        self.getArr(arr)
        should_str='"should":['
        for word in self.keyWordsArr:
            if wordSum!=0:
                should_str+=','
            wordSum+=1
            str1='{"match":{"content":"'+word+'"}}'
            should_str+=str1
        should_str+=']'
    
        if mode==1:
            tot_str='"query":{"bool":{'+should_str+',"minimum_should_match":'+str(minMatch)+'}}}'
        elif mode==2:
            tot_str='"query":{"bool":{"must":{"term":{"type":"content"}},"must_not":{"term":{"succ":""}},'+should_str+',"minimum_should_match":'+str(minMatch)+'}}}'
        elif mode==3:
            tot_str='"query":{"bool":{"must":[{"term":{"type":"content"}},{"term":{"succ":""}],'+should_str+',"minimum_should_match":'+str(minMatch)+'}}}'
        else:
            print("mode error!")
            return;
        query_str='{'+tot_str
        res=self.es.search(index=reIndex,doc_type=reType,body=query_str) #es查询文档的index，type
        total=res['hits']['total']     #这一步是获取doc的数量 使得下一步能够输出指定limit的doc数
        
        if total<=limit:  #limit大于所有符合条件的doc数量，则输出所有doc
            query_str='{"from":0,"size":'+str(total)+','+tot_str
        else:     #否则输出limit数量的doc
            query_str='{"from":0,"size":'+str(limit)+','+tot_str
        res=self.es.search(index=reIndex,doc_type=reType,body=query_str) #es查询文档的index，type 这次是输出所有结果
        self.hits=res['hits']['hits']
        self.resDic['documents']=self.resArray()
        return self.resDic
            # self.printDocs()
            # self.printScores()
            # self.resDic['docs']=self.reDocs()
            # self.resDic['scores']=self.reScores()
            # return self.resDic
        

#直接调用接口类 进行检索        
# url="localhost:9200"   
# int=ESinterface(url)

#int.retrieveText(1,1)
# arr1=['咳嗽','气急','呼吸困难','胸闷']
# dic=int.retrieveText(2,3,arr1)

# print(dic)

# docurl="C:\\Users\\Administrator\\Desktop\\basics\\病理学 王恩华.docx"
# apiindex="apiindex"
# apitype="apitype"
# int.depositText(docurl,apiindex,apitype)

#通过flask服务器 不同机器之前发起post请求，调用接口类传输json
#代码还有个发起结构化存储文档的post请求，待补全
app = Flask(__name__)

@app.route('/',methods=['GET','POSt'])
def home():
    return '<h1>Home</h1>'

 #另一种传参方式，可以在浏览器进行传参

@app.route('/deposit',methods=['GET'])
def deposit_form():
    docurl='C:\\Users\\72499\\Desktop\\病理学 王恩华.docx'
    pindex='病理学v2'
    ptype='WangEnHua'
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    esIntF.depositText(docurl,pindex,ptype)
    return '<h1>OK</h1>'
    
@app.route('/depositMediHist',methods=['GET'])
def deposit_medihist():
    histUrl='C:\\Users\\72499\\Desktop\\MediHist\\short'
    histIndex='medihist'
    histType='txt'
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    esIntF.depositMediHist(histUrl,histIndex,histType)
    return '<h1>OK</h1>'
    
@app.route('/deposit',methods=['POST'])
def deposit():
    reqBody=request.data
    
    #获取url里的参数
    filename=request.args.get('fname')
    pindex=request.args.get('index')
    ptype=request.args.get('type')
    docurl=r'D:\cont.txt'
    fo=open(docurl,"wb")    
    fo.write(reqBody)    
    fo.close()
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    esIntF.depositText(docurl,pindex,ptype)
    return '<h1>OK</h1>'
    
@app.route('/retrieve',methods=['GET'])
def retrieve_form():
    return '''<form action="/retrieveTest2" method="post">
    <p><input name="mode"></p>
    <p><input name="minMatch"></p>
    <p><input name="array" ></p>
    <p><input name="json" ></p>
    <p><button type="submit">Sign In </button></p>
    </form>
    '''
#测试路由 用来本机自身测试模拟http post请求
@app.route('/retrieveTest',methods=['POST'])
def retrievetest():
    mode=int(request.form['mode'])
    minMatch=int(request.form['minMatch'])
    arr1=['咳嗽','气急','呼吸困难','胸闷']
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    limit=5
    resDic=esIntF.retrieveText(mode,minMatch,limit,arr1)
    js1=json.dumps(resDic)
    return js1

@app.route('/retrieveTest2',methods=['POST'])
def retrievetest2():
    reqBody=request.form['json']
    reqJson=json.loads(reqBody)   #json 格式转成python字典
    reIndex=reqJson['index']
    reType=reqJson['type']
    arrstr=reqJson['keywords']
    minMatch=reqJson['minmatch']
    mode=reqJson['mode']
    limit=reqJson['limit']
    
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    resDic=esIntF.retrieveText(reIndex,reType,mode,minMatch,limit,arrstr)
    
    js1=json.dumps(resDic)
    return js1
    
    
@app.route('/retrieve',methods=['POST'])
def retrieve():
    reqBody=(request.data).decode()
    reqJson=json.loads(reqBody)   #json 格式转成python字典
    arrstr=reqJson['keywords']
    minMatch=reqJson['minmatch']
    mode=reqJson['type']
    limit=reqJson['limit']
    
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    resDic=esIntF.retrieveText(mode,minMatch,limit,arrstr)
    
    js1=json.dumps(resDic)
    return js1

# @app.route('/retrieveBytes',methods=['POST'])
# def retrieveBytes():
    #flask服务器是基于socket实现的，socket传输的信息是bytes流所以这里需要decode()将byptes类型转成str类型
    # reqBody=(request.data).decode()  #将其他编码的字符串转换成unicode编码
    
    #这里讲读取的数据分割存入各个变量
    # reqBodies=reqBody.split('\n')
    # mode=int(reqBodies[0])
    # minMatch=int(reqBodies[1])
    # arrstr=reqBodies[2]
    
    
    # 用于读取传输信息，调试用  此段
    # fo=open(r'D:\log.txt',"w")
    # fo.write('start:\n')
    # fo.write(str(mode))
    # fo.write('\r\n')
    # fo.write(str(minMatch))
    # fo.write('\r\n')
    # fo.write(arrstr)
    # fo.write('\nend')
    # fo.close()
    
    # 另一种读取多行string的方法，未尝试
    # buf=io.StringIO(reqBody)
    # mode=int(buf.readline())
    # minMatch=int(buf.readline())
    # arrstr=buf.readline()
    
    # arritems=arrstr.split(',')
    # arr1=[]
    # for item in arritems:
        # arr1.append(item)
    
    # ESurl="localhost:9200"   
    # esIntF=ESinterface(ESurl)
    # resDic=esIntF.retrieveText(mode,minMatch,arr1)
    # k=0
    # fo.open(r'D:\cont.txt',"w")
    # for word in resDic['docs']:
        # k+=1
        # fo.write(word)
        # fo.write('\t')
    # fo.write('\r\n')
    # fo.write(k)
    # fo.close()
    # js1=json.dumps(resDic)
    
    #flask返回值也就是视图模块的response必须是json 所以最后需要一个json.dumps
    # return js1
    
#这里host必须设为0,0,0,0 否则外部浏览器没法通过本机IP访问flask服务器
if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 56788,debug=True)