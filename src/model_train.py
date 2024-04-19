import os
import joblib
# from model_configs import config_read
from sklearn.ensemble import GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

# 当前模型训练策略： 重新训练数据 》读取已有的模型参数 》 保存训练后的模型 》更新模型
# 后续可以优化 1： 重新训练数据 》读取已有的模型参数 》 保存训练后的模型 》不新模型，保留之前的模型
#                对比之前的模型，哪个效果好，取模型效果较好的一个，更复杂了
# 后续可以优化 2： 不同的长短周期，不同的字段数据，使用的是不同的参数
# 后续可以优化 3： 样本的多少，过多，gbdt训练慢，lightgbm是可以应用于大量样本

seed_cv = 123

def train_GBDG(x, y, path, params=None, save=True):
    if params is None:
        gbdt = GradientBoostingRegressor(
            learning_rate=0.05,
            n_estimators=200,
            max_depth=5,
            random_state=seed_cv
        )
    else:
        gbdt = GradientBoostingRegressor(
            learning_rate=params['learning_rate'],
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            # min_samples_split=params['min_samples_split'],
            # min_samples_leaf=params['min_samples_leaf'],
            random_state=seed_cv
        )

    gbdt.fit(x,y)
    if save is True:
        joblib.dump(gbdt, path)

def train_XGBoost(x, y, path, params=None, save=True):
    if params is None:
        xgb = XGBRegressor(
            objective="reg:squarederror",
            learning_rate=0.01,
            n_estimators=300,
            max_depth=5,
            random_state=seed_cv
        )
    else:
        xgb = XGBRegressor(
            objective="reg:squarederror",
            learning_rate=params['learning_rate'],
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            # max_features=params['max_features'],
            random_state=seed_cv
        )

    xgb.fit(x,y)
    if save is True:
        joblib.dump(xgb, path)

def train_lightGBM(x, y, path, params=None, save=True):
    if params is None:
        lgb = LGBMRegressor(
            learning_rate=0.01,
            n_estimators=500,
            max_depth=5,
            random_state=seed_cv
        )
    else:
        lgb = LGBMRegressor(
            learning_rate=params['learning_rate'],
            n_estimators=params['n_estimators'],
            max_depth=params['max_depth'],
            max_features=params['max_features'],
            random_state=seed_cv
        )

    lgb.fit(x, y)
    if save is True:
        joblib.dump(lgb, path)

# def get_confg():
#     fun = ['GBDT', 'XGBoost', 'lightGBM']
#     # data = config_read(fun)
#     return data

def train_pw(df, params, save=True):

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if save == 1:
        save = True
    col_wea = ['temp', 'windspeed', 'ir', 'humidity','pred_theory']
    col_medium_wea = col_wea
    col_short_wea = col_wea
    col_ultra_wea = col_wea

    col_pw = ['pw_his_max_d123', 'pw3', 'pw_his_95', 'pw_his_96', 'pw_his_94', 'pw_his_15', 'pw4', 'pw_his_93', 'pw_his_mean_d1_p11', 'pw_his_97']
    col_medium_pw = col_wea
    col_short_pw = col_wea
    col_ultra_pw = col_pw

    col_pw_wea = col_wea + col_pw
    col_short_pw_wea = col_wea
    col_medium_pw_wea = col_wea
    col_ultra_pw_wea = col_pw_wea

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
    df.fillna(0,inplace=True)
    x = df[col]
    y = df['pw']

    # 2 模型所在的位置，电站名称/短期预测/只有天气数据的预测， 实际可以考虑，所有电站共用一套模型
    path = params['model_path_predtype']
    path_gbdt = os.path.join(path, 'gbdt.pkl')
    path_xgboost = os.path.join(path, 'xgboost.pkl')
    path_lgb = os.path.join(path, 'lgb.pkl', )
    # print(path_gbdt )

    # params_clf = get_confg()
    #
    # train_GBDG(x, y, path_gbdt, params_clf['GBDT'], save=save)
    # train_XGBoost(x, y, path_xgboost, params_clf['XGBoost'], save=save)
    # train_lightGBM(x, y, path_lgb, params_clf['lightGBM'], save=save)

    train_GBDG(x, y, path_gbdt,  save=save)
    train_XGBoost(x, y, path_xgboost, save=save)
    train_lightGBM(x, y, path_lgb,  save=save)


# * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
# 不同预测周期的数据特征提取，不同的字段，数据特征提取的内容不同
# 不同周期，可能用到的模型个数，特征名称都不相同
# # * * * * * * * * * * * * * * * * * * * * * * * * * * 中期 * * * * * * * * * * * * * * * * * * * * * * * *
# def train_medium_pw(df, path, save):
#     col = []
#     x = df[col]
#     y = df['pw']
#     params_clf = get_confg()
#
#     # path： 电站/预测周期/预测模式
#     path_gbdt = os.path.join(path, 'gbdt.pkl', )
#     path_xgboost = os.path.join(path, 'xgboost.pkl', )
#     path_lgb = os.path.join(path, 'lgb.pkl', )
#
#     train_GBDG(x, y, path_gbdt, params_clf['GBDT'], save=save)
#     train_XGBoost(x, y, path_xgboost, params_clf['XGBoost'], save=save)
#     train_lightGBM(x, y, path_lgb, params_clf['lightGBM'], save=save)
#
# def train_medium_wea(df, path, save):
#     col = []
#     x = df[col]
#     y = df['pw']
#     params = get_confg()
#
#     # path： 电站/预测周期/预测模式
#     path_gbdt = os.path.join(path, 'gbdt.pkl', )
#     path_xgboost = os.path.join(path, 'xgboost.pkl', )
#     path_lgb = os.path.join(path, 'lgb.pkl', )
#
#     train_GBDG(x, y, path_gbdt, params['GBDT'], save=save)
#     train_XGBoost(x, y, path_xgboost, params['XGBoost'], save=save)
#     train_lightGBM(x, y, path_lgb, params['lightGBM'], save=save)
#
#     return df
#
# def train_medium_pw_wea(df, path, save):
#     col = []
#     x = df[col]
#     y = df['pw']
#     params = get_confg()
#
#     # path： 电站/预测周期/预测模式
#     path_gbdt = os.path.join(path, 'gbdt.pkl', )
#     path_xgboost = os.path.join(path, 'xgboost.pkl', )
#     path_lgb = os.path.join(path, 'lgb.pkl', )
#
#     train_GBDG(x, y, path_gbdt, params['GBDT'], save=save)
#     train_XGBoost(x, y, path_xgboost, params['XGBoost'], save=save)
#     train_lightGBM(x, y, path_lgb, params['lightGBM'], save=save)
#
#     return df
# # * * * * * * * * * * * * * * * * * * * * * * * * *  短期 * * * * * * * * * * * * * * * * * * * * * * * * * *
#
# def train_short_pw(df, path, save):
#     col = []
#     x = df[col]
#     y = df['pw']
#     params = get_confg()
#
#     # path： 电站/预测周期/预测模式
#     path_gbdt = os.path.join(path, 'gbdt.pkl', )
#     path_xgboost = os.path.join(path, 'xgboost.pkl', )
#     path_lgb = os.path.join(path, 'lgb.pkl', )
#
#     train_GBDG(x, y, path_gbdt, params['GBDT'], save=save)
#     train_XGBoost(x, y, path_xgboost, params['XGBoost'], save=save)
#     train_lightGBM(x, y, path_lgb, params['lightGBM'], save=save)
#
#     return df
#
# def train_short_wea(df, path, save):
#     col = []
#     x = df[col]
#     y = df['pw']
#     params = get_confg()
#
#     # path： 电站/预测周期/预测模式
#     path_gbdt = os.path.join(path, 'gbdt.pkl', )
#     path_xgboost = os.path.join(path, 'xgboost.pkl', )
#     path_lgb = os.path.join(path, 'lgb.pkl', )
#
#     train_GBDG(x, y, path_gbdt, params['GBDT'], save=save)
#     train_XGBoost(x, y, path_xgboost, params['XGBoost'], save=save)
#     train_lightGBM(x, y, path_lgb, params['lightGBM'], save=save)
#
#     return df
#
# def train_short_pw_wea(df, path, save):
#     col = []
#     x = df[col]
#     y = df['pw']
#     params = get_confg()
#
#     # path： 电站/预测周期/预测模式
#     path_gbdt = os.path.join(path, 'gbdt.pkl', )
#     path_xgboost = os.path.join(path, 'xgboost.pkl', )
#     path_lgb = os.path.join(path, 'lgb.pkl', )
#
#     train_GBDG(x, y, path_gbdt, params['GBDT'], save=save)
#     train_XGBoost(x, y, path_xgboost, params['XGBoost'], save=save)
#     train_lightGBM(x, y, path_lgb, params['lightGBM'], save=save)
#
#     return df
#
# # * * * * * * * * * * * * * * * * * * * * * * * * *  超短期 * * * * * * * * * * * * * * * * * * * * * * * * * *
#
# def train_ultra_pw(df, path, save):
#     col = []
#     x = df[col]
#     y = df['pw']
#     params = get_confg()
#
#     # path： 电站/预测周期/预测模式
#     path_gbdt = os.path.join(path, 'gbdt.pkl', )
#     path_xgboost = os.path.join(path, 'xgboost.pkl', )
#     path_lgb = os.path.join(path, 'lgb.pkl', )
#
#     train_GBDG(x, y, path_gbdt, params['GBDT'], save=save)
#     train_XGBoost(x, y, path_xgboost, params['XGBoost'], save=save)
#     train_lightGBM(x, y, path_lgb, params['lightGBM'], save=save)
#
#     return df
#
# def train_ultra_wea(df, path, save):
#     col = []
#     x = df[col]
#     y = df['pw']
#     params = get_confg()
#     # path： 电站/预测周期/预测模式
#     path_gbdt = os.path.join(path, 'gbdt.pkl', )
#     path_xgboost = os.path.join(path, 'xgboost.pkl', )
#     path_lgb = os.path.join(path, 'lgb.pkl', )
#
#     train_GBDG(x, y, path_gbdt, params['GBDT'], save=save)
#     train_XGBoost(x, y, path_xgboost, params['XGBoost'], save=save)
#     train_lightGBM(x, y, path_lgb, params['lightGBM'], save=save)
#     return df
#
# def train_ultra_pw_wea(df, path, save):
#     col = []
#     x = df[col]
#     y = df['pw']
#     params = get_confg()
#
#     # path： 电站/预测周期/预测模式
#     path_gbdt = os.path.join(path, 'gbdt.pkl', )
#     path_xgboost = os.path.join(path, 'xgboost.pkl', )
#     path_lgb = os.path.join(path, 'lgb.pkl', )
#
#     train_GBDG(x, y, path_gbdt, params['GBDT'], save=save)
#     train_XGBoost(x, y, path_xgboost, params['XGBoost'], save=save)
#     train_lightGBM(x, y, path_lgb, params['lightGBM'], save=save)
#
#     return df
