import pymysql
import logging

class MySQLHelper:

    host="localhost"
    user="root"
    password="tostent@123456"
    db="cnblogdb"
    port=3306
    charset="utf8"

    def __init__(self):
        pass

    #插入数据
    #sqltext  插入数据的SQL语句
    def InsertData(self,sqltext):
        db= pymysql.connect(host=self.host,user=self.user,password=self.password,db=self.db,port=self.port,charset=self.charset)
        cur=db.cursor()
        try:
            cur.execute(sqltext)
            db.commit()
        except Exception as e:
            db.rollback()
            logging.basicConfig(filename='C:\myproject\python\mylog.log',format='%(asctime)s - %(levelname)s - %(message)s')
            logging.error('Mysql异常信息：{0},sqltext={1}'.format(repr(e),sqltext))
        db.close()