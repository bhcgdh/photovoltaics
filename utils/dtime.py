# 1 时间转为时间戳，秒级, 这里没有时区的要求
import time
import holidays
import datetime
import pandas as pd
from chinese_calendar import is_holiday, is_in_lieu
from dateutil.relativedelta import relativedelta
import numpy as np

"""
时间转换
time_to_stamp：时间转为时间戳，单值
times_to_stamps：时间列表转为时间戳列表 
stamp_to_time：时间戳转为时间，需要时间和时区 单值 
stamps_to_times：时间戳转为时间，需要时间和时区 列表
data_to_time: 单个数据转为时间格式数据 单值
datas_to_times: 单个数据转为时间格式数据 列表
pandas_str_to_time: pandas时间转为时间格式

时间特征
get_time_feature: 获取时间的基本特征，年月日时季节等，
get_time_first_end：判断时间是否第一天或者最后一天
get_time_holiday: 判断该国家是否节假日
get_time_holiday_china：判断中国是否节假日

时间计算
get_time_calculation: 单个时间加减，输入正数为加，负数为减
get_time_calculations：时间列表的加减计算
get_time interval: 两个单值时间间隔，可以设置返回的间隔 日，分钟,秒  即 d, m, s 
get_time intervals: 两个时间列表时间间隔，

时间连续
judge_time_continuous：判断时间是否连续，

当前时间
get_now ： 获取当前时间，到秒
get_now_day 获取当前时间，到日
get_now_stamp13 获取当前时间，时间戳13位
get_now_stamp10 获取当前时间，时间戳10位

"""
# ==============   时间转换
# 时间列表转为时间戳列表
def times_to_stamps(t, type=13):
    # 返回serise格式的数据列
    return [int( (10 ** ( type - 10 ) ) * time.mktime(time.strptime(str(i), "%Y-%m-%d %H:%M:%S"))) for i in t]

# 单个时间转为单个时间戳
def time_to_stamp(t, type=13):
    return int( (10 ** ( type - 10 ) ) * time.mktime(time.strptime(str(t), "%Y-%m-%d %H:%M:%S")) )

# 时间戳列表转为时间列表
def stamps_to_times(t, timezone):
    num = len(str(int(t[0])))
    if num == 10:
        unit = 's'
    else:
        unit = 'ms'
    # return [pd.Timestamp(i, unit=unit, tz=timezone) for i in t]
    return [datetime.datetime.strftime(pd.Timestamp(int(i), unit=unit, tz=timezone), "%Y-%m-%d %H:%M:%S") for i in t]


# 单个时间戳转为datetime64类型"""
def stamp_to_time(t, timezone):
    num = len(str(int(t)))
    if num == 10:
        unit = 's'
    else:
        unit = 'ms'
    return datetime.datetime.strftime(pd.Timestamp(int(t), unit=unit, tz=timezone), "%Y-%m-%d %H:%M:%S")

# Dataframe数据时间格式转换
def pandas_str_to_time(df, tn='t'):
    try:
        df[tn] = pd.to_datetime(df[tn])

    except ValueError:
        pass

def data_to_time(data, timezone=None):
    """
    :param data: 时间相关数据, 支持多种格式数据抓换
    :return: 将不同格式的数据转为标准的时间格式
    """
    # 1 10和13位的整数，时间戳 》时间
    if isinstance(data, (int, float)):
        data = stamp_to_time(data, timezone)

    # 2 字符类型数据,
    elif isinstance(data, str):
        if len(data)==19:
            data = datetime.datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
        elif len(data)==10:
            data = datetime.datetime.strptime(data, "%Y-%m-%d")
        else:
            raise Exception('wrong length of data')
    elif isinstance(data, datetime.datetime):
        pass
    else:
        raise Exception('unknow data type ')
    return data

def datas_to_times(datas, timezone=None):
    """
    :param datas: 时间相关列表
    :param timezone: 当前时区，默认空
    :return: 时间列别
    """
    tmp1, tmp2 = datas[0], len(str(datas[0]))

    # 1 10和13位的整数，时间戳 》时间
    if isinstance(tmp1, (int, float, np.int8, np.int32, np.int64,np.float16, np.float32,np.float64 )):
        datas = [stamp_to_time(data, timezone) for data in datas]

    # 2 字符类型数据,
    elif isinstance(tmp1, str):
        if tmp2==19:
            datas =[datetime.datetime.strptime(data, "%Y-%m-%d %H:%M:%S") for data in datas ]
        elif tmp2==10:
            datas =[ datetime.datetime.strptime(data, "%Y-%m-%d") for data in datas]
        else:
            raise Exception('wrong length of data')
    elif isinstance(tmp1, datetime.datetime):
        pass
    else:
        raise Exception('unknow data type ')
    return datas

# ==============   获取时间的特征，不同颗粒度，不同节假日。
def get_time_feature(df, tn='t'):
    """
    :param t: 字符格式，如果是
    :return: 所有时间特征，
    """
    try:
        df[tn] = datas_to_times(df[tn])
    except:
        raise Exception('cannot change time data to datetime type')

    df['year'] = df[tn].dt.year
    df['month'] = df[tn].dt.month
    df['day'] = df[tn].dt.date
    df['day'] = pd.to_datetime(df['day'])
    df['hour'] = df[tn].dt.hour
    df['minute'] = df[tn].dt.minute
    df['hourms'] = [datetime.datetime.strftime(i, '%H-%M-%S')for i in df[tn]] # 小时分钟秒
    df['hourms2'] = df['hour']*4 + df['minute']//15
    df['dayofyear'] = df[tn].dt.dayofyear # 一年的第几天
    df['dayofweek'] = df[tn].dt.dayofweek+1 # 一周的第几天
    df['dayofmonth'] = df[tn].dt.day # 一个月的第几天
    df['weekofyear'] = df[tn].dt.weekofyear # 一年中的第几周
    df['season'] = df[tn].dt.quarter # 季节
    return df

def get_time_first_end(df, tn='t'):
    """ 判断是否时间的第一天或者最后一天  """
    df['t_is_year_start'] = df[tn].dt.is_year_start
    df['t_is_year_end'] = df[tn].dt.is_year_end
    df['t_is_quarter_start'] = df[tn].dt.is_quarter_start
    df['t_is_quarter_end'] = df[tn].dt.is_quarter_end
    df['t_is_month_start'] = df[tn].dt.is_month_start
    df['t_is_month_end'] = df[tn].dt.is_month_end
    return df

def get_time_holiday(df, tn='t',country='CN'):
    """ 判断是否国外节假日 """
    country_holidays = holidays.country_holidays(country)  # this is a dict
    if isinstance(df, str):
        return df in country_holidays
    else:
        df['t_is_holiday'] = [i in country_holidays for i in df[tn]]
        return df

def get_time_holiday_china(df, tn='t'):
    df['t_is_holiday'] = [ is_holiday(i) for i in df[tn]]   # 是否节假日
    df['t_is_tiaoxiu'] = [ is_in_lieu(i) for i in df[tn]]   # 是否调优
    return df

# ==============   时间数据的加减计算
def get_time_calculation(data,timezone=None, years=0, months=0, weeks=0, hours=0, days=0,minutes=0, seconds=0):
    # 1 数据转为时间格式，方便后续计算
    data = data_to_time(data, timezone)

    # 2 时间加减，注意，用s ,hour表示将小时转为hour,22:00:00 > 10:00:00
    data = data + relativedelta( years=years, months=months, days=days, weeks=weeks,
                                 hours=hours, minutes=minutes, seconds=seconds)
    return data


def get_time_calculations(datas, timezone=None, years=0, months=0,
                          weeks=0, hours=0, days=0,minutes=0, seconds=0):
    # datas是时间列表列表 timezone是在输入的时间是时间戳才需要"""
    datas = datas_to_times(datas, timezone)
    datas = [data + relativedelta( years=years, months=months, days=days, weeks=weeks,
                                 hours=hours, minutes=minutes, seconds=seconds) for data in datas]
    return datas

def get_time_interval(data1, data2, type='m',timezone=None):
    """
    type: 返回时间的类型，
       - s: 两个时间相差的总秒数
       - m: 两个时间相差的总分钟，默认该值
       - d: 两个时间相差的日数据,不足一天为0
    """
    data1 = data_to_time(data1, timezone)
    data2 = data_to_time(data2, timezone)
    delta = data1 - data2
    if type=='m':
        return delta.total_seconds()/60
    elif type=='s':
        return delta.total_seconds()
    elif type=='d':
        return delta.days

def get_time_intervals(datas1, datas2, type='m',timezone=None):
    datas1 = datas_to_times(datas1,timezone)
    datas2 = datas_to_times(datas2,timezone)
    deltas = [datas1[i]-datas2[i] for i in range(len( datas1 ))]
    if type=='m':
        return [delta.total_seconds()/60 for delta in deltas]
    elif type=='s':
        return [delta.total_seconds() for delta in deltas]
    elif type=='d':
        return [delta.days for delta in deltas]


# ==============   时间连续性判断
def judge_time_continuous(df, tn='t', freqs='15Min', lack=0.3):
    """
    时间完整性判断，根据输入的dataframe数据，指定时间列名称
    :param df: 要进行判断的dataframe
    :param tn: 时间列名称
    :param freqs:时间间隔
    :param lack:缺失率，超过这个值，不建议继续进行计算
    :return: 是否
    """
    df[tn] = pd.to_datetime(df[tn])
    m1 = df[tn].min()
    m2 = df[tn].max()
    if 'D' in freqs:
        m3 = get_time_calculation( m2, days=1)
        df_time = pd.date_range(m1, m3, freq=freqs, closed='left')
    else:
        df_time = pd.date_range(m1, m2, freq=freqs)
    df_miss = len(df_time) - len(df)
    per = df_miss/len(df)
    if df_miss > 0:
        print('从{} 到 {}共计 {} 条数据，间隔{} 缺失{}条数据'.format(m1, m2, len(df),freqs ,df_miss))
    if per>lack:
        print(f'缺失率高于{lack}, 不建议继续进行计算 ')
    else:
        print('没有确实值')

# ==============   获取不同格式的当前时间
def get_now():
    return datetime.datetime.today().replace(microsecond=0) # 返回当前时间，秒级 now

def get_now_day( ):
    return datetime.datetime.now().date() # 返回当前日时间，日级

def get_now_stamp13():
    return time_to_stamp(get_now(), type=13)

def get_now_stamp10():
    return time_to_stamp(get_now(), type=10)

