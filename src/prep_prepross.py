# 1 获取数据，根据其有的数据，进行不同的处理方式，如只有天气，只有功率，或两者都有。
# 2 对获取的数据，同训练时的处理方式（ 大部分 ）
# 3 对处理后的数据，进行特征构造
# 4 获取模型所在的位置
# 5 返回预测的结果，

import pandas as pd
# import sys
# sys.path.append('/Users/cc/Documents/资料/hx/prepross')
try:
    from utils  import get_time_feature
except:
    from ..utils import get_time_feature


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# 不同预测长短周期的数据预处理，不同的字段，可能处理方式不同
# 训练集》可能传入的是多个数据，判断删除条件空值 》时间处理 》数据填充 》
# 测试集》

# 1 删除空值 默认时间字段是t, 一个样本有一半是空值则删除
def drop_nan(df, tn='t'):
    num = int(df.shape[1] * 0.5)
    df['nan'] = df.isna().sum(axis=1)
    n1 = list(df[df['nan'] >= num].index)  # 样本中空值的个数占比大于50%的
    n2 = list(df[df[tn].isna()].index)  # 样本中时间未知的样本
    n3 = n1 + n2
    df = df.drop(index=n3)
    del df['nan']
    return df.reset_index(drop=True)

# 2 时间处理
def time_feat(df,tn='t'):
    return get_time_feature(df, tn=tn)

# 3 空值填充 数值vs类别
def fill_nan_num(df,col):
    # 不同周的96个点，一年的第几周》不同月份的96个点》不同季节的96个点》不同的96个点
    # df[col] = df.groupby(['weekofyear', 'hourms'], sort=False)[col].apply(lambda x: x.fillna(x.mean()))
    # df[col] = df.groupby(['month', 'hourms'], sort=False)[col].apply(lambda x: x.fillna(x.mean()))
    # df[col] = df.groupby(['season', 'hourms'], sort=False)[col].apply(lambda x: x.fillna(x.mean()))
    df[col] = df[col].fillna(df.groupby('hourms')[col].transform('mean'))
    return df

def fill_nan_cate(df):
    # 使用前后数据进行填充》再用
    df['wea'].fillna(method='ffill', inplace=True)
    df['wea'].fillna(method='bfill', inplace=True)
    df['wea'] = df['wea'].fillna(df['wea'].mode()[0])
    return df

def fill_nan_train(df):
    # num = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    # col_num = [i for i in df.columns if df[i].dtypes  in num]
    col_num = ['pw', 'temp', 'windspeed', 'ir', 'humidity']
    df = fill_nan_num(df,col_num)
    if 'wea' in df.columns:
        df = fill_nan_cate(df)
    return df

def fill_nan_pred(df):
    df.fillna(method='ffill', inplace=True)
    df.fillna(method='bfill', inplace=True)
    if df.isna().sum().sum()>0:
        raise Exception('predict data has too much Nan value !')
    return df

# 4 聚合处理，数值用均值的方法，这里默认都是均值
# def agg_15Min(df,tn='t'):
#     df.index = df[tn]
#     df = df.resample('15Min').mean().reset_index()
#     return df

# 异常功率处理
def abnormal(df,scale):
    scales = scale*1.1
    df.loc[df['pw'] >= scales, 'pw'] = scales
    df.loc[df['pw'] <= 0, 'pw'] = 0
    return df

# 类别数据处理
def change_cate(df):
    def change(i):
        if '雨' in i or '雪' in i or '冰' in i:
            return "雨"
        elif '阴' in i:
            return '阴'
        else:
            return '晴'

    # 不同天气类型，分为，晴，阴，雨三个大类，对天气描述类别数据进行转换
    df['wea'] = df['wea'].apply(lambda x: change(x))
    df = pd.get_dummies(df, columns=['wea'])
    df = df.rename(columns={'wea_晴': 'sun', 'wea_阴': 'cloudy', 'wea_雨': 'rain'})
    return df

def train_prepross(df,scale, tn='t'):
    # 1 数据聚合为间隔15分钟 》2 空值处理 》3 时间计算 》4 空值填充 》5 连续、类别型数据处理
    # df = agg_15Min(df,tn=tn)       # 1 聚合为均值
    df = drop_nan(df, tn=tn)       # 2 删除空值
    df = time_feat(df, tn=tn)      # 3 时间计算
    df = abnormal(df,scale)        # 4 异常值处理
    df = fill_nan_train(df)        # 5 空值填充
    # if 'wea' in df.columns:
    #     df = change_cate(df)            # 6 数据转换？
    return df

def pred_prepross(df,tn='t'):
    # 1 预测值空值和训练集的空值填充方式不同，一个有多个数据，一个没有，
    # df = drop_nan(df, tn=tn)   # 1 数据不足96个点则补齐，空值大于50%的告警，否则填充空值未知的 》先使用前后填充
    # df = time_feat(df, tn=tn)  # 2 时间计算
    df = drop_nan(df, tn=tn)     # 1 预测值空值填充，只对时间，
    df = time_feat(df, tn=tn)    # 2
    df = fill_nan_pred(df)  # 5 数据转换
    return df

def prepross_ultra_pw(df,scale):
    irmax = df['ghi'].max()
    df['pw_his_95'] = df['pw'].shift(95)
    df['pw_his_96'] = df['pw'].shift(96)
    df['pw_his_97'] = df['pw'].shift(97)
    df['pw_his_94'] = df['pw'].shift(94)
    df['pw_his_15'] = df['pw'].shift(15)
    df['pw_his_93'] = df['pw'].shift(93)

    df['pw_his_192'] = df['pw'].shift(192)
    df['pw_his_288'] = df['pw'].shift(288)
    df['pw_his_max_d123'] = df[['pw_his_96','pw_his_192','pw_his_288']].max(axis=1)
    for i in range(96 - 1 - 15 * 1, 96 - 1):
        df[f'pw_his_{i}'] = df['pw'].shift(i)
    df['pw_his_mean_d1_p11'] = df[[f'pw_his_{i}' for i in range(96 - 1 - 15 * 1, 96 - 1)]].mean(axis=1)
    df['pw2'] = df['ir'] * scale/irmax
    df['pw3'] = df['ghi'] * df['pw_his_max_d123'] / irmax
    df['pw4'] = 0.6 * df['pw2'] + 0.4 * df['pw3']
    return df

# 考虑是曲线较为平滑地方的功率，
# 找一个时间段落的功率 》 此处的时间，功率的变化，反推出最大功率值
# def prepross_short_pw(df, scale):
# def prepross_medium_pw(df,scale):

def prepross(df, param ):
    # 训练和测试是不同的预处理方式，超短期，使用天气和功率则是不同的处理方式，其他是相同的处理方式，
    if param['train'] == 1:
        df = train_prepross(df, param['scale'] )
    else:
        df = pred_prepross(df)

    if param['ftperiod']=='ultra' and param['predtype_value'] in ['pred_pw','pred_pw_wea']:
        df = prepross_ultra_pw(df, param['scale'])
    return df

# json={}
# json['name'] = 'd1_changyuan'
# json['longitude'] = 113.772097
# json['latitude'] = 29.11
# json['altitude'] = 200
# json['scale'] = 758.7
# json['freq'] = '15Min' # 时间间隔
# json['timezone'] = 'Asia/Shanghai'
# json['type'] = 1  # 表示只获取辐照度数据
#
# json['ftperiod'] = 'short' # ultra, medium
# json['mode'] = 'train'
#
# dfs = pd.read_csv("/Users/cc/Documents/资料/A3_光伏探索/Data/测试4个地区数据_v1/长园电力.csv", encoding='utf-8')
# from pred_only_basic.c1_pred_only_basic import PredOnlyBasic
#
#
#
# dfs.rename(columns={'time':'t'}, inplace=True)
# dfs['t'] = pd.to_datetime(dfs['t'])
#
#
# dfb = PredOnlyBasic( json,  dfs[['t']],'t' ).get_pred_only_basic()
# print(dfb.head())
# print(dfs.head())
# dfs = pd.merge(dfs, dfb.rename(columns={'time':'t'}), how='left')
#
# # df = dfs.head(1000)
# # df = prepross(df, json)
# # print(df.shape)
# # print(df.head())
# print(json['mode'])
# json['ftperiod'] = 'ultra' # ultra, medium
# json['predtype_value'] ='pred_pw'
#
# df = dfs.head(1000)
# df = prepross(df, json)
# print(df.shape)
# print(df.head())
#
# json['predtype_value'] ='pred_pw_wea'
#
# df = dfs.head(1000)
# df = prepross(df, json)
# print(df.shape)
# print(df.head())



# #  后续可以改进的地方： 不同周期，不同的输入字段，处理方式不同
# # * * * * * * * * * * * * * * * * * * * * * * * * * 中期 * * * * * * * * * * * * * * * * * * * * * * * * * *
# def prepross_medium_pw(df):
#     return df
# def prepross_medium_wea(df):
#     return df
# def prepross_medium_pw_wea(df):
#     return df
# # * * * * * * * * * * * * * * * * * * * * * * * * *  短期 * * * * * * * * * * * * * * * * * * * * * * * * * *
# def prepross_short_pw(df):
#     return df
# def prepross_short_wea(df):
#     return df
# def prepross_short_pw_wea(df):
#     return df
# # * * * * * * * * * * * * * * * * * * * * * * * * * *  超短期 * * * * * * * * * * * * * * * * * * * * * * * * *
# def prepross_ultra_pw(df):
#     return df
# def prepross_ultra_wea(df):
#     return df
# def prepross_ultra_pw_wea(df):
#     return df
