import json
import datetime
import warnings
warnings.filterwarnings('ignore')
global graph
import pymysql
import requests
import pandas as pd
from urllib.parse import quote
# from config import Config
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
import logging
logger = logging.getLogger(__name__)

class Databases():
    def __init__(self,json):
        self.charset = 'utf8'
        # self.host = Config.SQL_HOST
        # self.user = Config.SQL_USER
        # self.passwd = Config.SQL_PASSWD
        # self.port = int(Config.SQL_PORT)
        # self.database = Config.SQL_DATABASE
        self.host = json['SQL_HOST']
        self.user = json['SQL_USER']
        self.passwd = json['SQL_PASSWD']
        self.port = json['Config.SQL_PORT)']
        self.database = json['SQL_DATABASE']

    def deal_sql(self, sql):
        db = pymysql.connect(host=self.host,
                             user=self.user,
                             port=self.port,
                             passwd=self.passwd,
                             database=self.database,
                             charset=self.charset)
        cursor = db.cursor()
        cursor.execute(sql)
        cursor.close()
        db.commit()
        db.close()

    def get_sql_data(self, sql):
        '''2 获得数据库数据'''
        db = pymysql.connect(host=self.host,
                             user=self.user,
                             port=self.port,
                             passwd=self.passwd,
                             database=self.database,
                             charset=self.charset)
        cursor = db.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        db.commit()
        db.close()
        col_name_list = [tuple[0] for tuple in cursor.description]
        data = list(data)
        data = [list(i) for i in data]
        datas = pd.DataFrame(data, columns=col_name_list)
        return datas

    '''    3 数据直接存入数据库'''
    def to_sql(self, df, to_filename):
        engine = create_engine( str(r'mysql+pymysql://%s:%s@%s:%s/%s?charset=%s' % (self.user, quote(self.passwd), self.host, self.port, self.database, self.charset)) )
        df.to_sql(to_filename, con=engine, if_exists='append', index=False)  # 增量入库

# con = Databases(json)
# con.deal_sql()


