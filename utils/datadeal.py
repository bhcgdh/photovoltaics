import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import os
import time
from contextlib import contextmanager

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                                         一般的代码中工具处理
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

# 时间记录，记录执行该程序需要耗费的时间
@contextmanager
def timer(title):
    t0 = time.time()
    yield
    print("{} - done in {:.0f}s".format(title, time.time() - t0))
# example:
# with timer('train'):
#     df = train(df,)

# 内存释放，对dataframe格式数据进行处理，减少所占用的内存，可以对大量的训练集进行处理。
def reduce_mem_usage(df, verbose=True):
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    start_mem = df.memory_usage().sum() / 1024 ** 2
    for col in df.columns:
        col_type = df[col].dtypes
        if col_type in numerics:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)

    end_mem = df.memory_usage().sum() / 1024 ** 2
    print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))

    return df

# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                                      文件的处理，读取，加载，保存等
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *


# 读取当前的目录路径》新建文件读取层级时使用
def get_file_mkdir(file):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if os.path.exists(file):
        pass
    else:
        os.mkdir(file)

def get_files_mkdir(files):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    for file in files:
        if os.path.exists(file):
            pass
        else:
            os.mkdir(file)
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                                         字典数据的转换
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

# 1 dataframe转为字典，包含时间数据，返回时间对数值数据
def frame_t_dictt(df, col, tn='t',type=1):
    """
    :param df:
    :param col:指定的特征列进行转换，如果没有则是转换所有的数据， 例如['a','b']
    :param tn:时间列名称,要求是时间格式，
    :return:字典格式数据，即data里保存每个列的字段格式的数据值
    类型1 {data:
            {
            name1:{t1:v1,t2:v2....},
            name2:{t1:v1,t2:v2....},
            ....
            }}
    类型2
          {data:
            [
            {name1: a1, name2:b1, name3:c1},
            {name1: a2, name2:b2, name3:c2},
            {name1: a3, name2:b3, name3:c3}
            ]
            ....
            }}
    """
    # 1 是否传入时间列，没有这个列，则不能进行带有时间字典的数据转换。
    if tn is None:
        raise Exception('need datetime column name ')
    if col is None:
        col = list(df.columns)
        col.remove(tn)
    # df[tn] = times_to_stamps(df[tn]) # 不用转为时间戳格式
    # 2 是否是时间格式数据，不是则进行转换。
    if isinstance(df[tn][0], pd.datetime):
        pass
    else:
        df[tn] = pd.to_datetime((df[tn]))

    # 3 转为需要的字典格式,data是字符串 ，需要eval转为字典数据
    df.index = df[tn]  # 转为时间索引
    data = {}
    if type==1:
        data['data'] = df[col].to_json() # 时间是字符格式
    else:
        col = col+[tn]
        # df[tn] = times_to_stamps(df[tn])
        data['data'] = df[col].to_json(orient='records') # 时间是数值格式
    return data

# 2 dataframe转为字典，不包含时间数据，直接返回数值数据
def frame_t_dictls(df, col,type=1):
    """
    :param col:指定的特征列进行转换，如果没有则是转换所有的数据， 例如['a','b']
    :return:
    类型1
           {data:
            {
            name1: [1,2,3,4],
            name2: [1,2,3,4],
            ....
            }}
    类型2
          {data:
            [
            {name1: a1, name2:b1, name3:c1},
            {name1: a2, name2:b2, name3:c2},
            {name1: a3, name2:b3, name3:c3},
            ....,
            ]
            }}
    """
    if col is None:
        raise Exception('need datetime column name ')
    if type == 1:
        data = {"data":{m: df[m].tolist() for m in col}}
    else:
        data = {"data":df[col].to_dict(orient='records')}
    return data


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
#                                         数据的分割
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *

# 1 数据分割，正常分割，不打乱顺序 ==================================================
# 2 根据不同月份》按比例选择每个月的日数据，如1月31天，随机选择20天为训练，10天为预测
def get_train_test_byday(df, label, split='month', size=0.7):
    """
    根据不同的时间内，随机选择不同的日数据作为不同的训练和测试集
    :param df: 待分割数据，dataframe格式数据
    :param label: 目标特征名称
    :param split: 分割的特征依据，可选{month, season, week }, 如month,则根据不同的month，
    :param size: 训练集比例
    :return:分割后的数据，训练集特征和目标，测试集特征和目标
    """
    if 'week' in split:
        split = 'weekofyear'
    day_train = []
    for month, dfs in df.groupby(split):
        tmp1 = dfs['day'].astype(str).unique()
        tmp2 = list(np.random.choice(tmp1, replace=False, size=int(len(tmp1) * size)))
        day_train += tmp2

    train = df[df['day'].isin(day_train)]
    test = df[~df['day'].isin(day_train)]
    train_y, test_y = train[label],test[label]
    train_x, test_x = train.drop(columns=[label]), test.drop(columns=[label])
    return train_x, test_x, train_y, test_y

def get_train_test(df, label='pw', types='common1',size=0.7):
    """
    :param df: dataframe数据
    :param label: 目标值
    :param types: 分割的类型，
    :param size: 参考的 type_ls = ['common1', 'common2', 'month', 'season', 'week']
                common1是打乱顺，common2按时间顺序
    :return: 分割后的数据
    """

    if types == 'common1':
        train_x, test_x, train_y, test_y = train_test_split( df.drop(columns=[label]),  df[label], shuffle=True )  # 打乱顺序
    if types == 'common2': #
        train_x, test_x, train_y, test_y = train_test_split( df.drop(columns=[label]),  df[label], shuffle=False ) # 按顺序
    elif types == 'month':
        train_x, test_x, train_y, test_y = get_train_test_byday(df, label, split='month',size=size)
    elif types == 'season':
        train_x, test_x, train_y, test_y = get_train_test_byday(df, label, split='season',size=size)
    elif types == 'week':
        train_x, test_x, train_y, test_y = get_train_test_byday(df, label, split='week',size=size)
    return train_x, test_x, train_y, test_y