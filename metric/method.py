import numpy as np
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import photovoltaic as pv
from pytz import timezone

# 1 注意光伏进行功率评价的计算方法和一般评价方法不同，考虑了装机容量的影响。
# 2 不同地区的评价和考核标准都不同，目前参考国内的评价标准
# 3 不同之处在于
# 1）合格率和准确率，以及各自的衡量值
# 2）对于预测值和实际值 之间的值的准确率计算公式，常用rmse,还有自用。

""" 均方根误差 """
def cap_RMSR(pred, real, cap):
    n = len(pred)
    pred = np.array(pred)
    real = np.array(real)

    return np.sqrt(np.sum((pred - real) ** 2)) / (cap * np.sqrt(n))

""" 平均绝对误差"""
def cap_MAE(pred, real, cap):
    return np.average(np.abs(pred - real) / cap)

def cap_maxMaE(pred,real):
    return np.max(abs(pred-real))

""" 平均误差"""
def cap_ME(pred, real, cap):
    return np.average(real-pred)/cap

""" 相关系数 """
def cap_corr(pred, real):
    meanp, meanr = np.average(pred), np.average(real)
    f1 = np.sum((pred-meanp )*(real - meanr))
    f2 = np.sum( (pred-meanp)**2 )
    f3 = np.sum( (real-meanr)**2 )
    return  f1/np.sqrt( f2*f3)

"""准确率 一般85，超短期95%，短期90%，长期渐变从90%-80% """
def cap_accuracy(pred,real, cap):
    rmse = cap_RMSR(pred, real ,cap)
    return 1-rmse

"""合格率  样本中准确率"""
def cap_passrate(ac, standard ):
    if standard is None:
        standard = 0.85 # 判断预测结果是否满足该标准，满足为1, 风电场是0.75
    ac = [1 if i >= standard else 0 for i in ac ]
    return np.average(ac)

# ============ 其他参考评估指标 ==========
def score_rmse(real, pred ):
    # 参考 https: // www.dcic - china.com / competitions / 10097 / datasets
    rmse = np.sqrt(np.mean( ( real-pred)**2 ))
    score = 1 / (1 + rmse)
    return score
