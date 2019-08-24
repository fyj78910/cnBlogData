import requests
from requests.exceptions import ReadTimeout,HTTPError,RequestException
import re
import json
import time
from bs4 import BeautifulSoup
from SqlHelper import MySQLHelper
import schedule
import time
import datetime
import threading
import hashlib
import logging
import logging.handlers

CNBLOG_URL="https://www.cnblogs.com/AggSite/AggSitePostList"
BLOGTAG_URL="https://www.cnblogs.com/chenyanbin/ajax/CategoriesTags.aspx?blogId=%d&postId=%d"
logging.basicConfig(filename='C:\myproject\python\mylog.log',format='%(asctime)s - %(levelname)s - %(message)s')
mysqlhelper=MySQLHelper()

#MD5加密
def MD5Encry(encrystr):
    return hashlib.md5(encrystr.encode(encoding='UTF-8')).hexdigest()

#爬取数据
def CrawlData(pageindex):
    resultdata=[]

    headers={"content-type":"application/json; charset=UTF-8"}
    
    databodys={
        "CategoryId": 808,
        "CategoryType": "SiteHome",
        "ItemListActionName": "AggSitePostList",
        "PageIndex":pageindex,
        "ParentCategoryId":0,
         "TotalPostCount":4000
    }

    try:
        res=requests.post(CNBLOG_URL,data=json.dumps(databodys),headers=headers,verify=False)
        if res.status_code==200:
            html=BeautifulSoup(res.text,"html.parser")
            #获取所有博客
            postItems=html.select(".post_item")
            for item in postItems:
                #博客postid和blogid
                blogdigg=item.select(".diggit")[0].attrs["onclick"]
                blogId=0
                postId=0
                if len(blogdigg)>0:
                    blogdigg_arr=blogdigg.split(',')
                    if len(blogdigg_arr)>=3:
                        blogId=int(blogdigg_arr[2])
                        postId=int(blogdigg_arr[1])
                #推荐数量
                blogdiggnum=int(item.select(".diggnum")[0].get_text())
                #博客标题
                blogTitle=item.select(".post_item_body h3 a")[0].get_text()
                #博客地址
                blogUrl=item.select(".post_item_body h3 a")[0].attrs["href"]
                #博客ID,由URL进行MD5加密得到
                blogFId=MD5Encry(blogUrl)
                #博客作者
                blogAuthor=item.select(".post_item_foot a")[0].get_text()
                #发布时间
                blogTime=item.select(".post_item_foot")[0].contents[2][11:27]+":00"
                #评论数量
                blogCommentNum=int(re.findall("\d+", item.select(".post_item_foot .article_comment a")[0].get_text())[0])
                #阅读数量
                blogViewNum=int(re.findall("\d+", item.select(".post_item_foot .article_view a")[0].get_text())[0])

                resultDic={
                    "blogdiggnum":blogdiggnum,
                    "blogtitle":blogTitle,
                    "blogurl":blogUrl,
                    "blogauthor":blogAuthor,
                    "blogtime":blogTime,
                    "blogcommentnum":blogCommentNum,
                    "blogviewnum":blogViewNum,
                    "blogFId":blogFId,
                    "blogId":blogId,
                    "postId":postId
                }
                resultdata.append(resultDic)
        else:
            logging.error('Http error:httpcode={0},data={1}'.format(res.status_code,json.dumps(databodys)))

    except ReadTimeout:
        logging.error('ReadTimeout:data={0}'.format(json.dumps(databodys)))
    except HTTPError:
        logging.error('HTTPError:data={0}'.format(json.dumps(databodys)))
    except RequestException:
        logging.error('RequestException:data={0}'.format(json.dumps(databodys))) 
    return resultdata

#获取分类、标签数据
def CrawlTagData(blogId,url):
    tagdata=[]
    try:
        res=requests.get(url)
        if res.status_code==200:
            html=BeautifulSoup(res.text,"html.parser")
            #获取所有分类
            allcatogerys=html.select("#BlogPostCategory a")
            #获取所有标签
            alltags=html.select("#EntryTag a")
            
            if len(allcatogerys)>0:
                for item in allcatogerys:
                    dataType=1
                    dataText=item.get_text().replace("\n","").strip()
                    dataDic={
                        "blogId":blogId,
                        "dataType":dataType,
                        "dataText":dataText
                    }
                    tagdata.append(dataDic)

            if len(alltags)>0:
                for item in alltags:
                    dataType=2
                    dataText=item.get_text()
                    dataDic={
                        "blogId":blogId,
                        "dataType":dataType,
                        "dataText":dataText
                    }
                    tagdata.append(dataDic)
        else:
            logging.error('http error:httpcode={0},url={1}'.format(res.status_code,url))

    except ReadTimeout:
        logging.error('ReadTimeout:url={1}'.format(url))
    except HTTPError:
        logging.error('HTTPError:url={1}'.format(url))
    except RequestException:
        logging.error('RequestException:url={1}'.format(url)) 
    return tagdata



#插入数据
def InsertData(data):
    sqltext="INSERT INTO tb_bloginfo(blogdiggnum,blogtitle,blogurl,blogauthor,blogtime,blogcommentnum,blogviewnum,AddTime,blogFId,blogId,postId)\
                VALUES(%d,'%s','%s','%s',str_to_date(\'%s\','%%Y-%%m-%%d %%H:%%i:%%s'),%d,%d,NOW(),'%s',%d,%d);" % \
                 (data["blogdiggnum"],data["blogtitle"],data["blogurl"],data["blogauthor"],data["blogtime"],data["blogcommentnum"],data["blogviewnum"],data["blogFId"],data["blogId"],data["postId"])
    mysqlhelper.InsertData(sqltext)

#插入明细数据
def InsertDetailData(data):
    sqltext="INSERT INTO tb_blogdetail(blogFId,dataType,dataText,AddTime) VALUES('%s',%d,'%s',NOW());" % \
        (data["blogId"],data["dataType"],data["dataText"])
    mysqlhelper.InsertData(sqltext)


def GetData():
    TotalPage =201
    for pageindex in range(1,TotalPage):
        cur_result=CrawlData(pageindex)
        if len(cur_result)>0:
            for item in cur_result:
                #添加到数据库中保存
                #print(item)
                InsertData(item)
                #爬取分类以及标签
                if (item["blogId"]>0 and item["postId"]>0):
                    cur_blogurl=BLOGTAG_URL %(item["blogId"],item["postId"])
                    cur_tagdata=CrawlTagData(item["blogFId"],cur_blogurl)
                    if len(cur_tagdata)>0:
                        for curtag in cur_tagdata:
                            InsertDetailData(curtag)

        print("已完成：%s/%s" % (pageindex,TotalPage-1))

def GetData_Task():
    threading.Thread(target=GetData).start()

def run():
    #每天22点执行
    schedule.every(1).days.at("02:00").do(GetData_Task)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    print("每天凌晨两点开始执行......")
    run()
    #GetData()