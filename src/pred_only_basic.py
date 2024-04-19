"""
1)根据基本信息获取不同时间的光伏功率，
2)必须输入的信息：经纬度，电站装机容量，时间，时区,
3)不考虑长度等信息，只是单纯作为功能输出
后续可以优化的方向：不同季节、不同使用年限、不同品牌下，理论的光伏功率
"""
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
try:
    from utils import PVs
except:
    from ..utils import PVs



class PredOnlyBasic():
    def __init__(self, json_data, df, tn):
        self.json = json_data
        self.df = df
        self.tn = tn
        # self.json['type'] = 1  # 表示只获取辐照度数据 默认值是1

    def deal_json(self):
        if 'name' not in self.json.keys():
            self.json['name'] = 'd1_changyuan'

        must = ['longitude', 'latitude', 'scale', 'timezone']
        n1 = list(set(must).difference(set(self.json.keys()) ))
        if len(n1)>=1:
            raise Exception( f'missing data： {n1}')
        self.json['freq'] = '15Min'  # 时间间隔

    def deal_time(self):
        if self.df is not None:
            self.df[self.tn] = pd.to_datetime(self.df[self.tn])
            self.df['day'] = pd.to_datetime(self.df[self.tn].dt.date)
            self.json['timestart'] = str(self.df[self.tn].min().date())
            self.json['timeend'] = str(self.df[self.tn].max().date())

    def deal_pvs(self):
        try:
            dfp = PVs(self.json).do()
        except:
            raise Exception('Something wrong, cannot get pv ')
        if dfp['time'].dt.tz:
            dfp['time'] = dfp['time'].dt.tz_localize(None)  # 2020-11-01 00:00:00+08:00 》2020-11-01 00:00:00
        self.dfp = dfp

    # 获取理论功率,拼接理论辐照度》计算每天的最大辐照度效果相对一般，使用整体辐照度的最大值
    # deal_pws是可以进行
    def deal_pws(self):
        # df = pd.merge(df,df.groupby('day')['ghi'].max().reset_index().rename(columns={'ghi': 'ghi_max'}),how='left', on='day')
        self.dfp['pred'] = self.json['scale'] * self.dfp['ghi'] / self.dfp['ghi'].max()
        if self.json['type']==1:
            self.pred = self.dfp[['time','ghi','pred']]
        else:
            self.pred = self.dfp # 包含一些天体理论值，如方位角，仰角等信息。

    def get_pred_only_basic(self):
        self.deal_json()
        self.deal_time()
        self.deal_pvs()
        self.deal_pws()
        return self.pred

def pred():
    json={}
    json['longitude'] = 113.772097
    json['latitude'] = 29.11
    json['altitude'] = 200
    json['scale'] = 758.7
    json['timezone'] = 'Asia/Shanghai'
    json['timestart'] = '2022-02-22'
    json['timeend'] = '2022-02-27'
    # df = pd.read_csv("/Users/cc/Documents/资料/A3_光伏探索/Data/测试4个地区数据_v1/长园电力.csv", encoding='utf-8')
    dfs = PredOnlyBasic(json, None,tn=None)
    # dfs = PredOnlyBasic(json, df,tn='time')
    pred = dfs.get_pred_only_basic()
    return pred
#
# df = pred()
# print(df)

