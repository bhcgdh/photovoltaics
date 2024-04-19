try:
    from sklearn.externals import joblib
except:
    import joblib

import os
import pandas as pd
try:
    from prep_prepross import prepross
except:
    from .prep_prepross import prepross


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# 在训练过程中，需要对未来数据进行预测和验证，未来数据的


def train_pred_ultra_pw_wea(df_test, param, save=False):
    times = pd.date_range(df_test['t'].min(), freq='15Min', periods=len(df_test)-303)
    val = pd.DataFrame()
    for i, t in enumerate(times):
        ts = pd.date_range(t, freq='15Min', periods=288 + 15)
        df_ts = df_test[df_test['t'].isin(ts)]
        if len(df_ts)== 303:
            df_ts = prepross(df_ts, param)
            df_ts['id'] = i
            df_ts['train'] = 1
            df_ts.loc[df_ts.tail(15).index, 'train'] = 0
            # df_ts['pred'] = pred_pw(df_ts, param)
            pred = pred_pw(df_ts, param)
            val = val.append(pred.tail(15))
        else:
            pass
    if save is True:
        mode =  param['predtype_value'].split('pred_')[1]
        pathname = f'/Users/cc/Documents/资料/hx/prepross/Data/d1_changyuan/df_urltra_{mode}.csv'
        val.to_csv(pathname, index=False)
    return val

def train_pred_wea(df_test, param):
    # 常规的预测，
    if param['ftperiod'] == 'ultra':
        nums = 15
    elif param['ftperiod'] == 'short':
        nums = 96*3
    if param['ftperiod'] == 'medium':
        nums = 96*7
    val = pd.DataFrame()
    time_list= pd.date_range(df_test['t'].min(), df_test['t'].max(), freq='15Min')[:-nums]
    for i, t in enumerate(time_list):
        ts = pd.date_range(t, freq='15Min', periods=nums)
        df_ts = df_test[df_test['t'].isin(ts)]
        df_ts = prepross(df_ts, param)
        df_ts['id'] = i
        pred = pred_pw(df_ts, param)
        val = val.append(pred)
    # name = f'/Users/cc/Documents/资料/hx/prepross/Data/d1_changyuan/df_short_wea.csv'
    # val.to_csv(name, index=None)
    return val

def train_pred(df,param):
    if param['predtype_value']=='pred_pw_wea' and param['ftperiod']=='ultra':
        val = train_pred_ultra_pw_wea(df, param)

    elif param['predtype_value'] == 'pred_wea':
        val = train_pred_wea(df, param)
    else:
        val = None
    return val
# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# 不同预测周期的数据特征提取，不同的字段，数据特征提取的内容不同

# 1  获取预测的周期和字段信息 》 读取模型所在位置 》 加载模型 》
#    根据不同字段进行模型预测 》 根据不同模式模型聚合（也可以同一个模式）
# 2  待优化地方：预测结果聚合的方法需要更新。

import logging
# print('1 当前工作路径', os.getcwd())
# logger = logging.getLogger(__name__)
# os.chdir(os.path.dirname(os.path.abspath(__file__)))
#
# print('2 当前工作路径', os.getcwd())
# logger.info('1 进行了模型的预测测------- ')


def pred_pw(df, params):
    # logger.info('2 进行了模型的预测测------- ')
    col_wea = ['temp', 'windspeed', 'ir', 'humidity','pred_theory']

    col_medium_wea = col_wea
    col_short_wea = col_wea
    col_ultra_wea = col_wea

    col_pw = ['pw_his_max_d123', 'pw3', 'pw_his_95', 'pw_his_96', 'pw_his_94', 'pw_his_15', 'pw4', 'pw_his_93', 'pw_his_mean_d1_p11', 'pw_his_97']
    col_medium_pw = col_wea
    col_short_pw = col_wea
    col_ultra_pw = col_pw

    col_pw_wea = col_wea + col_pw
    col_ultra_pw_wea = col_pw_wea
    col_short_pw_wea = col_wea
    col_medium_pw_wea = col_wea
    cols = {
        "col_medium_pw":col_medium_pw,
        "col_medium_wea":col_medium_wea,
        "col_medium_pw_wea":col_medium_pw_wea,
        "col_short_pw":col_short_pw,
        "col_short_wea":col_short_wea,
        "col_short_pw_wea":col_short_pw_wea,
        "col_ultra_pw":col_ultra_pw,
        "col_ultra_wea":col_ultra_wea,
        "col_ultra_pw_wea":col_ultra_pw_wea
    }

    # 1 训练需要的字段
    period = params['ftperiod'] # 预测周期，长短超
    mode = params['predtype_value'].split('pred_')[1] # 预测类型
    colname = f"col_{period}_{mode}" # 模型预测需要的特征字段，
    col = cols[colname]
    x = df[col]

    # 2 模型所在的位置，电站名称/短期预测/只有天气数据的预测， 实际可以考虑，所有电站共用一套模型
    path = params['model_path_predtype']
    path_gbdt = os.path.join(path, 'gbdt.pkl')
    path_xgboost = os.path.join(path, 'xgboost.pkl')
    path_lgb = os.path.join(path, 'lgb.pkl', )

    # 3 加载模型
    gbdt = joblib.load(path_gbdt)
    xgb = joblib.load(path_xgboost)
    lgb = joblib.load(path_lgb)

    # 4 模型预测， 注意，不同周期，不同字段状况，模型融合的方法可能不同。
    df['pred_gbdt'] = gbdt.predict(x.fillna(0))
    df['pred_xgb'] = xgb.predict(x)
    df['pred_lgb'] = lgb.predict(x)

    #  5 聚合的方式，根据不同类型不同方式，自动化设置会复杂化模型 到没必要，可以先训练尝试。
    #  此处是对不同模式需要调用不同的方式
    df['pred'] = df[['pred_gbdt','pred_lgb']].mean(axis=1)

    # 6 人工干预，5点之前和8点之后，常规逻辑是0，
    df['pred'] = [i if i>0 else 0 for i in df['pred']]
    df.loc[df['pw'] > params['scale'] * 1.5, 'pw'] = df[df['pw'] <= params['scale'] * 1.5]['pw'].max()
    df.loc[ df[df['hour']<=5].index,'pred'] = 0
    df.loc[ df[df['hour']>=20].index,'pred'] = 0

    # df['t'].hour<=5)]
    # return df['pred']
    return df



# * * * * * * * * * * * * * * * * * * * * * * * * * * 中期 * * * * * * * * * * * * * * * * * * * * * * * *
def pred_medium_pw(df):
    return df

def pred_medium_wea(df):
    return df

def pred_medium_pw_wea(df):
    return df

# * * * * * * * * * * * * * * * * * * * * * * * * *  短期 * * * * * * * * * * * * * * * * * * * * * * * * * *

def pred_short_pw(df):
    return df

def pred_short_wea(df):
    return df

def pred_short_pw_wea(df):
    return df

# * * * * * * * * * * * * * * * * * * * * * * * * *  超短期 * * * * * * * * * * * * * * * * * * * * * * * * * *

def pred_ultra_pw(df):
    return df

def pred_ultra_wea(df):
    return df

def pred_ultra_pw_wea(df):
    return df


