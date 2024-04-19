import json
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
# try:
#     from config import Config
# except:
#     try:
#         from ..config import Config
#     except:
#         from .config import Config
import os
import pandas as pd
#
try:
    from utils import Databases
    from utils import datas_to_times
    from utils import get_files_mkdir
except:
    from ..utils import Databases
    from ..utils import datas_to_times
    from ..utils import get_files_mkdir

try:
    from .pred_only_basic import PredOnlyBasic
except:
    from pred_only_basic import PredOnlyBasic

import logging
logger = logging.getLogger(__name__)

""" 解构电站基本信息数据 》 根据输入的数据，定义预测或者训练的类型 》获取时段数据 》 获取模型所在位置，没有则新建
1 电站的基本数据解构
2 电站功率、天气数据的解构
3 预测的类型，超短，短期，中长期，
"""
def get_predtype(col):
    name = ['ir', 'temp', 'windspeed','wea']
    counts = len(set(col).intersection(name))
    if 'pw' in col and counts>1:
        return 3
    elif counts>0:
        return 2
    elif 'pw' in col:
        return 1
    else:
        return 0


class Base:
    def __init__(self, json_data):
        # 1 基本数据单值
        self.df = None
        self.json_data = json_data
        # self.station_name = self.json_data["station_name"]

        # 2 判断必须输入的数据，没有则 报错
        keys = ['name', 'longitude', 'latitude', 'altitude', 'scale', 'ftperiod',  'train', 'model_path', 'data_colname'] # 'timezone',
        real_keys = json_data.keys()
        lack = list( set(keys).difference(set(real_keys)) )
        if len(lack) > 0:
            logger.error(f'base - Missing required information: {lack}')
            # raise Exception("Missing required information")

        self.station_name = self.json_data['name']  # 'd1_changyuan' 电站的名称
        self.name = self.json_data['name']
        self.ftperiod = self.json_data['ftperiod'] # 预测时间周期，超短期，短期，中长期, Forecast time period, ultra,short,medium
        self.longitude = self.json_data['longitude']  # 113.772097
        self.latitude = self.json_data['latitude']  # 29.11
        self.altitude = self.json_data['altitude']  # 200
        self.scale = self.json_data['scale']  # 758.7
        self.timezone = self.json_data['timezone']  # 'Asia/Shanghai'
        self.train = self.json_data['train']  # 1：表示训练，0：表示预测, 一定要给定的
        try:
            self.model_path = self.json_data['model_path']
        except:
            self.model_path ='../models'

        try:
            self.train_split = self.json_data['train_split'] # 训练模型，是否进行分割，使用测试集进行验证
        except:
            self.train_split = 0 # 默认对所有的数据集进行训练, 可能本地训练时使用

        try:
            self.freq = self.json_data['freq']  # '15Min'  时间间隔
        except:
            self.freq = "15Min" # 默认间隔15分钟

        try:
            self.type = self.json_data['type']  # 1 表示只获取辐照度数据，否则会返回天顶角等数据，空则默认为1
        except:
            self.type = 1

        try:
            self.save_model = self.json_data['save_model']
        except:
            self.save_model = 1  # 默认保存新训练的模型

        # 模型文件所在的位置
        self.model_path = self.json_data['model_path'] # 模型所在的位置
        self.model_path_name = os.path.join(self.model_path, self.station_name) # 模型所在的位置/电站名称
        self.model_path_period = os.path.join(self.model_path_name, self.ftperiod)  # 模型所在的位置/电站名称/短期预测
        self.json_data['model_path_period'] = self.model_path_period


        # 2 根据输入的数据，判断进行哪一种类型的预测，如只有天气，只有基本，只有功率，以及有功率和天气的数据
        # 预测的类型，0:只用基础数据，1：只有历史功率，2：只有预测天气，3：有历史功率和天气
        # 当前指定输入的数据字段，
        self.predtype_val = {0: 'pred_base', 1: 'pred_pw', 2: 'pred_wea', 3: 'pred_pw_wea'} # 每个预测所在的的位置

        try:
            self.data_colname = self.json_data['data_colname']  # 指定字段名称, 不论是字典，文件，数据库保存
            # print(self.data_colname)
            self.predtype = get_predtype(self.data_colname.keys())
        except:
            self.predtype = 0


        # 3 注意这里需要指定特征列名称，预测和训练需要的数据，sql和path都是读取的dataframe格式的数据
        if 'data_path' in self.json_data.keys():
            file = self.json_data['data_path']['filepath']
            self.df = pd.read_csv(file, encoding='utf-8')

        elif 'data_sql' in self.json_data.keys():
            self.sql = self.json_data['data_sql']['sql']
            self.sql_base = self.json_data['data_sql']['sql_base']
            con = Databases(self.sql_base)
            self.df = con.get_sql_data(self.sql)

        elif 'data' in self.json_data.keys():
            tmp = self.json_data['data']
            if isinstance(self.json_data['data'], str):
                tmp = eval(tmp)
            self.df = pd.DataFrame.from_dict(tmp)  # 字典转为dataframe 格式数据
        else:
            pass

        # 4 字段改为常用的，方便使用，如果输入数据指定了，则将数据转为默认字段名称，
        if self.df is not None:
            if self.data_colname is not None :
                tmp = {self.data_colname[i] : i for i in self.data_colname.keys()}
                self.df = self.df.rename(columns=tmp)
            else:
                # 如果没有输入列名称，但是有表格数据，则根据表格数据计算
                self.predtype = get_predtype(self.df.columns)
            self.df['t'] = datas_to_times(self.df['t'].tolist(), timezone=self.timezone)
            self.df['t'] = pd.to_datetime(self.df['t'])

        # 5 获取利率的辐照度，不论是训练还是预测，都是需要的， 时间可能没有，读取当前时间
        self.df_pred_basic = PredOnlyBasic(self.json_data, self.df[['t']], 't').get_pred_only_basic()
        if self.type == 1:
            col_pv = ['time', 'ghi', 'pred']
        else:
            col_pv = ['Eot', 'Declination', 'TimeCorrection', 'LocalSolorTime', 'Elevation', 'Azimuth', 'Sunrise', 'Sunset', 'Zenith', 'Air_Mass'] + ['time','pred','ghi']

        # 理论值是ghi
        if self.df is not None:
            self.df = pd.merge(self.df, self.df_pred_basic[col_pv].rename(columns={"time":'t','pred':'pred_theory'}), how ='left', on='t')

        # 6 模型所在的位置/电站名称/短期预测/只有天气数据的预测
        self.predtype_value = self.predtype_val[self.predtype] # 预测的字段范围，只有功率，只有天气，天气+功率
        self.model_path_predtype = os.path.join(self.model_path_period, self.predtype_value)
        self.json_data['predtype_value'] = self.predtype_value
        self.json_data['model_path_predtype'] = self.model_path_predtype

        # 判断是否有该文件地址，没有则新建、path/name/period/predtype
        # python manage 时，文件。。相当于是
        value = {
            'ultra': '超短期',
            'short': '短期',
            'medium': '中期',
            'train_pred': {1: f'训练 模型保存:{self.save_model}', 0: '预测'}
        }
        info = f"进行{value[self.ftperiod]} {value['train_pred'][self.train]}"
        logger.info(info)

        # 预测的电站 > 的所有模型在的位置 > 不同周期的预测 > 不同方法的预测
        files = [self.model_path,self.model_path_name,self.model_path_period,self.model_path_predtype]
        get_files_mkdir(files)


