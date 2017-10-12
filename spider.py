#! /usr/bin/env python
#-*- coding:UTF-8 -*-
#大众点评-分类爬虫
import re
from bs4 import BeautifulSoup
import threading#多线程爬虫
import urllib2
from urllib2 import urlopen
from requests import Session
import requests
import xlsxwriter
import time
import random
import getPositions
import returnProxy
import returnRandHeader
import codecs
import csv
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')

class Crawler_dianping:

    def __init__(self,category):#初始化参数
        self.baseUrl='http://www.dianping.com'
        self.bgurl=category[0]
        self.typename1=category[1]
        self.typename2=category[2]
        self.page=1
        self.count=0
        self.pagenum=50 #设置最大页面数目，大众点评每个条目下最多有50页
        self.Json=list()#定义一个字典用以存储数据
        self.Host='www.dianping.com'
        #self.Referer='https://www.dianping.com/guangzhou'
        self.headers={
            "Host":"www.dianping.com",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW 64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.3228.1 Safari/537.36",
            "Referer":"http://www.dianping.com/guangzhou",
            }

    def start(self):#函数的主要入口
        self.s=Session() #定义一个Session对象
        print self.bgurl,self.typename1.encode('gb2312'),self.typename2.encode('gb2312')
        print "please wait ..."    
        self.proxies=returnProxy.getproxy() 
        Crawler_dianping.__parseHtml(self,self.bgurl) #调用__parseHtml函数
        print 'get data downloaded'

    def __parseHtml(self,preurl):#爬取数据的主函数
        header=returnRandHeader.randHeader()#产生一个随机头部user-agent
        proxie=self.proxies[int(random.uniform(1,100))]#产生一个IP池中1-100编号的随机ip
        print preurl

        html=self.s.post(preurl,headers=header).text #发送请求，获取html
        #html=requests.get(preurl,headers=header,proxies=proxie,timeout=10).text
        soup=BeautifulSoup(html,'lxml') #进行解析
        name=['名称','地址','评论数','综合星级','综合人均','综合口味','综合环境','综合服务','纬度','经度','地址分类','菜品分类','用户名','用户评星级','用户人均','用户评口味','用户评环境','用户服务','评论详情']
        
        for li in soup.find('div',class_="shop-wrap").find('div',id="shop-all-list").ul.find_all('li'):
            _json=list()
            info=li.find('div',class_='txt')#实际上网页中最重要的信息都包含在这个txt里

            #店名称
            shopname=info.find('div',class_='tit').a.h4.get_text().encode('utf-8')
            #print shopname
            _json.append(shopname)#抓取名称

            #地址
            _json.append(info.find('div',class_='tag-addr').find('span',class_='addr').get_text().encode('utf-8'))#抓取地址
            #评论数
            try:
                lis1=int(info.find('div',class_='comment').find('a',class_="review-num").b.get_text().encode('utf-8'))#点评数
                _json.append(lis1)
            except:
                _json.append('-')

            #综合星级
            try:
                lis1=info.find('div',class_='comment').span['title']#点评数
                _json.append(lis1)
            except:
                _json.append('-')
            #人均
            try:
                lis2=int(re.sub('￥','',info.find('div',class_='comment').find('a',class_="mean-price").b.get_text().encode('utf-8')))#人均
                _json.append(lis2)
            except :
                _json.append('-') 
            #口味
            try:
                lis3=float( info.find('span',class_='comment-list').find_all('b')[0].get_text()) #口味
                _json.append(lis3) 
            except:
                _json.append('-') 
            #环境
            try:
                lis4=float( info.find('span',class_='comment-list').find_all('b')[1].get_text()) #环境
                _json.append(lis4) 
            except:
                _json.append('-') 
            #服务
            try:
                lis5=float( info.find('span',class_='comment-list').find_all('b')[2].get_text()) #服务
                _json.append(lis5) 
            except:
                _json.append('-') 

            #经纬度
            try:
                opera= li.find('div',class_='operate J_operate Hide')#要找到网址信息，包含的元素有部分隐藏
                str=opera.find('a',class_='o-map J_o-map').encode('utf-8')
                poiloc=re.search('data.poi=".*"',str,flags=0).span()
                poop=str[poiloc[0]+10:poiloc[0]+24]
                (longitude,latitude)=getPositions.getPosition(poop)
                _json.append(longitude)#经度
                _json.append(latitude)#维度
            except:
                _json.append('-')#经度
                _json.append('-')#维度

            _json.append(self.typename1)#地址分类
            _json.append(self.typename2)#菜品分类  
           
            #接下去进行用户评价的爬取
            
            ulss=li.find('div',class_='tit').a['href']+'/review_more' 
            self.urlss=ulss.replace(':','s:')
            print self.urlss
            Crawler_dianping.usercomment(self,self.urlss,li,header,proxie,_json,self.count)
            #self.Json.append(_json)    
            
        self.page+=1
        time.sleep(random.uniform(1,4))#表示设置一个随机数作为停顿时间，为１～４之间的一个数.
        if self.page<self.pagenum:
            try:
                tmphref=soup.find('div',class_='page').find('a',class_='next')['href']#获得下一页的链接
                self.nexturl=self.baseUrl+tmphref#获得下一页的链接
                print self.nexturl
                Crawler_dianping.__parseHtml(self,self.nexturl)     
            except:
                with open (self.typename2.encode('gb2312').replace('/','') +self.typename1.encode('gb2312').replace('/','')+'.csv','w') as csvfile:
                    csvfile.write(codecs.BOM_UTF8)
                    f_csv=csv.writer(csvfile,dialect='excel')
                    f_csv.writerow(name)
                    for j in self.Json:
                        f_csv.writerow(j)
                return    
        else:
            with open (self.typename2.encode('gb2312').replace('/','')+self.typename1.encode('gb2312').replace('/','')+'.csv','w') as csvfile:
                csvfile.write(codecs.BOM_UTF8)
                f_csv=csv.writer(csvfile,dialect='excel')
                f_csv.writerow(name)
                for j in self.Json:
                    f_csv.writerow(j.rstrip())
            return



    def usercomment(self,nurl,li,header,proxie,_json,count):
        #利用两种方法进行html请求，一种是session，另一种则是request
        #try:           

        htmlss=requests.get(nurl,headers=header,proxies=proxie,timeout=10).text
        #except:
        #ss=Session()
        htmlss=ss.post(nurl,headers=self.headers).text #发送请求，获取html
        soupss=BeautifulSoup(htmlss,'lxml')#进行解析

        #f = open("text.txt",'wb')
        #f.write(soupss.encode('utf-8'))
        #f.close()

        try:
            moreinfo=soupss.find('div',class_='comment-list').ul.find_all('li',id=True)#id=True就是找到所有有id标签的节点
        except:
            self.Json.append(_json)
            return
        count=count+1
  
        if count>50:
            self.Json.append(_json)
            return

        
        for ili in moreinfo:          
           
            #用户名
            try:
                username=ili.find('p',class_='name').get_text()
                _json.append(username)
                #print username
            except:
                _json.append('-')
                #print username
            
            #用户评星级    
            try:
                userstar=ili.find('div',class_='content').find('div',class_='user-info').span.encode('utf-8')
                isnum=int(re.sub('\D','',userstar).strip())/10.0
                #print isnum
                _json.append(isnum)
            except:
                _json.append('-')

            #用户人均
            try:
                userprice=ili.find('div',class_='content').find('div',class_='user-info').find('span',class_='comm-per').get_text()
                #print userprice
                _json.append(userprice)
            except:
                _json.append('-')

            try:
                userinfo=ili.find('div',class_='content').find('div',class_='comment-rst').find_all('span',class_='rst')
                
            except:
                _json.append('-')
              
                
            #用户评口味
            try:
                usertaste=userinfo[0].get_text()
                #print usertaste
                _json.append(usertaste)
            except:
                _json.append('-')

            #用户评环境
            try:
                userenvir=userinfo[1].get_text()
                #print userenvir
                _json.append(userenvir)
            except:
                _json.append('-')
            #用户评服务
            try:
                userservi=userinfo[2].get_text()
                #print userservi
                _json.append(userservi)
            except:
                _json.append('-')         

            #评论详情             
            try:
                usertxt=ili.find('div',class_='comment-txt').find('div',class_='J_brief-cont').get_text().encode('utf-8')
                #print usertxt
                _json.append(usertxt)
            except:
                _json.append('-')

            #time.sleep(random.uniform(1,2))

            
            self.Json.append(_json)
            _json=list()
            _json=['','','','','','','','','','','','']

        time.sleep(random.uniform(1,4))#表示设置一个随机数作为停顿时间，为１～４之间的一个数.
        try:
            nexturl=self.urlss+soupss.find('div',class_='Pages').find('a',class_='NextPage')['href']
            print nexturl
            newjson=['','','','','','','','','','','','']
            Crawler_dianping.usercomment(self,nexturl,li,header,proxie,newjson,count) 
        except:
           # with open ('data.csv','w') as csvfile:
           ##     csvfile.write(codecs.BOM_UTF8)
            #    f_csv=csv.writer(csvfile,dialect='excel')
            #    for j in self.Json:
            #        f_csv.writerow(j) 
            return   


if __name__=='__main__':
    obj=list()
    sitestr=r'http://www.dianping.com'
    rawstr=r'http://www.dianping.com/search/category/4/85'
    headers1={
            "Host":"www.dianping.com",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW 64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/50.0.2661.102 UBrowser/6.1.3228.1 Safari/537.36",
            'Cookie': 'PHOENIX_ID=0a650c81-154a0633f47-a97843; _hc.v="\"e27e18eb-3a3d-4b40-b06a-cbe624c96048.1462979739\""; s_ViewType=10; JSESSIONID=877B00919AD417544F72F5A9953E54B4; aburl=1; cy=2; cye=guangzhou',
            "Referer":"http://www.dianping.com/guangzhou"
            }
    
    ss=Session() #定义一个Session对象
    html1=ss.post(rawstr,headers=headers1).text #发送请求，获取html
    #proxies=returnProxy.getproxy()
    #proxie=proxies[int(random.uniform(1,100))]
    #html1=requests.get(rawstr,headers=returnRandHeader.randHeader(),proxies=proxie,timeout=10).text
    soup1=BeautifulSoup(html1,'lxml') #进行解析
    tmps=soup1.find('div',class_="nc-items").find_all('a')
    

    for line in tmps:#先按着菜品分类
        catename=line.find('span').get_text().encode('utf-8')   

        caturl=line['href']
        html2=ss.post(caturl,headers=headers1).text #发送请求，获取html
        soup2=BeautifulSoup(html2,'lxml') #进行解析
        items=soup2.find('div',class_='nav-category nav-tabs J_filter_region').find('div',class_='nc-items').find_all('a')
        for region in items:      #进一步按着地区    
            precatename=region.get_text()
            precaturl=region['href']
            #loc=re.search('/r.*',precaturl,flags=0).span()
            #r=caturl+precaturl[loc[0]+1:loc[1]]

            cat=[precaturl,precatename,catename]
            obj.append(Crawler_dianping(cat))                  
        
    [threading.Thread(target=foo.start(),args=()).start for foo in obj] #多线程执行obj任务
    
    






