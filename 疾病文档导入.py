#coding=utf-8
# author luojin 18/5/23 ver 2.0
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

    id=0
    mark=1

    actions = []
    
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
            if '。' in para.text:
                content=para.text
                self.id+=1   #id++
                action={
                    "_index": self.index,
                    "_type": self.type,
                    "_id": str(self.id),      #id是string类型
                    "_source": {
                    "content":content,

                    "type": "content",   #还是要剔除title
                    "timestamp": datetime.now()
                    }
                }
                self.actions.append(action)
                self.j+=1
                if self.j%50==0:
                    helpers.bulk(self.es, self.actions)
                    self.actions=[]
        helpers.bulk(self.es, self.actions)
        self.actions=[]
        self.id=0
    
     #处理病历的文件名 修改成合适的id
    def filenToId(self,filename):
        index=filename.index('_')
        index2=filename.index('.')
        str=filename[index+2:index2]+'.'+filename[0:index]
        return str
    
    #导入病历到es
    def depositMediHist(self,url,_index,_type):
        
        self.index=_index
        self.type=_type
        
        _index_mappings = {"mappings": {self.type:{"properties":{"content":{"type":"text","analyzer":"ik_smart"},"pred":{"type":"keyword"},"succ":{"type":"keyword"},"type":{"type":"keyword"}}}}}

        if self.es.indices.exists(index=self.index) is not True:
            self.es.indices.create(index=self.index, body=_index_mappings)
        
        os.chdir(url)
        self.files=glob.glob('*.txt')
        for filename in self.files:
            self.url=url+'\\'+filename
            self.f=open(self.url,'r',encoding="utf-8")
            self.lines=self.f.readlines()
            self.output='\n'.join(self.lines)
            self.id=self.filenToId(filename)
            action={
                "_index": self.index,
                "_type": self.type,
                #"_id": self.mark,
                "_id":self.id,
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
            self.mark+=1
        helpers.bulk(self.es, self.actions)
        self.actions=[]
        self.mark=1
   
        
            
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
    #reIndex es的iudex  reType es的type minMatch 最低匹配数  limit 输出的doc数 arr 关键词数组
    def retrieveText(self,reIndex,reType,minMatch,limit,arr=[]):
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
    
        # if mode==1:
            # tot_str='"query":{"bool":{'+should_str+',"minimum_should_match":'+str(minMatch)+'}}}'
        # elif mode==2:
            # tot_str='"query":{"bool":{"must":{"term":{"type":"content"}},"must_not":{"term":{"succ":""}},'+should_str+',"minimum_should_match":'+str(minMatch)+'}}}'
        # elif mode==3:
            # tot_str='"query":{"bool":{"must":[{"term":{"type":"content"}},{"term":{"succ":""}],'+should_str+',"minimum_should_match":'+str(minMatch)+'}}}'
        # else:
            # print("mode error!")
            # return;
        tot_str='"query":{"bool":{'+should_str+',"minimum_should_match":'+str(minMatch)+'}}}'
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
        



#通过flask服务器 不同机器之前发起post请求，调用接口类传输json
#代码还有个发起结构化存储文档的post请求，待补全
app = Flask(__name__)

@app.route('/',methods=['GET','POSt'])
def home():
    return '<h1>Home</h1>'

 #另一种传参方式，可以在浏览器进行传参

@app.route('/deposit',methods=['GET'])
def deposit_form():
    docurl='C:\\Users\\72499\\Desktop\\basics\\病理学 王恩华.docx'
    pindex='病理学v2'
    ptype='WangEnHua'
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    esIntF.depositText(docurl,pindex,ptype)
    return '<h1>OK</h1>'
    
@app.route('/depositMediHist',methods=['GET'])
def deposit_medihist():
    #histUrl='C:\\Users\\72499\\Desktop\\MediHist\\short\\review'
    #histUrl2='C:\\Users\\72499\\Desktop\\MediHist\\short\\diagnose'
    #histIndex='medihistrev'
   # histIndex2='medihistdia'
   # histType='txt'
    histUrl='C:\\Users\\72499\\Desktop\\txt\\zh-cn'
    ESurl="localhost:9200"   
    histIndex='bmj'
    histType='bmj'
    esIntF=ESinterface(ESurl)
    esIntF.depositMediHist(histUrl,histIndex,histType)
    #esIntF.depositMediHist(histUrl2,histIndex2,histType)
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
    return '''<form action="/retrieveTest" method="post">
    <p>index:<input name="index" ></p>
    <p>type:<input name="type" ></p>
    <p>minMatch:<input name="minMatch"></p>
    <p>array:<input name="array" ></p>
    <p>limit:<input name="limit" ></p>
    <p>json:<input name="json" ></p>
    <p><button type="submit">Sign In </button></p>
    </form>
    '''
#测试路由 用来本机自身测试模拟http post请求
@app.route('/retrieveTest',methods=['POST'])
def retrievetest():
    reIndex='病理学v2'
    reType='WangEnHua'
    minMatch=2
    arr1=['咳嗽','气急','呼吸困难','胸闷']
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    limit=5
    resDic=esIntF.retrieveText(reIndex,reType,minMatch,limit,arr1)
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
    
    limit=reqJson['limit']
    
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    resDic=esIntF.retrieveText(reIndex,reType,minMatch,limit,arrstr)
    
    js1=json.dumps(resDic)
    return js1
    
    
@app.route('/retrieve',methods=['POST'])
def retrieve():
    reqBody=(request.data).decode()
    reqJson=json.loads(reqBody)   #json 格式转成python字典
    arrstr=reqJson['keywords']
    minMatch=reqJson['minmatch']
    reIndex=reqJson['index']
    reType=reqJson['type']
    limit=reqJson['limit']
    
    ESurl="localhost:9200"   
    esIntF=ESinterface(ESurl)
    resDic=esIntF.retrieveText(reIndex,reType,minMatch,limit,arrstr)
    
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