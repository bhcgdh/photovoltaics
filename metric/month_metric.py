import pandas as pd
from .method import cap_RMSR
import pandas as pd
import numpy as np

# 参考：《GBT51437-2021风光储联合发电站设计标准.pdf》，返回月平均准确率，月合格率，
# 超短期，每个小时的最后一小时
def month_ultra_metric(df, scale=None, sample='id'):
    passrate = 0.15
    vas = []
    for i, f in df.groupby(sample):
        f = f.tail(4)
        va = cap_RMSR(f['pred'], f['pw'], scale)
        vas.append([i,va])
    vas2 = np.array([i[1] for i in vas])
    va1 = round(vas2.mean(), 4)  # 月均方根误差
    va2 = np.mean(vas2 < passrate)  # 月合格率
    return va1, va2


# 短期3天  月均方根误差小于20%
def month_short_metric(df, scale=None, sample='id'):
    passrate = 0.2
    va = df.groupby(sample).apply(lambda x: cap_RMSR(x['pred'], x['pw'], scale))
    va1 = round(va.mean(),4)   # 月均方根误差
    va2 = np.mean(va<passrate) # 月合格率
    return va1, va2

# 中长期10天，没有合格率，而是预测的10天，返回月均精准度，和是否满足精准度指标。
def month_medium_metric(df, scale=None, sample='id'):
    passrate = 0.3
    passrates = np.array([round(passrate+0.01*i, 2) for i in list(range(9, -1, -1)) ])
    vas = []
    for i, f in df.groupby(sample):
        # 每个样本，预测的未来10天的功率
        va = df.groupby('day').apply(lambda x: cap_RMSR(x['pred'], x['pw'], scale)).values
        vas.append(va)
    vas = np.array(vas)

    va1 = vas.mean(axis=0) # 10天的准确度
    va2 = vas<passrates
    va2 = [i+0 for i in va2]
    return va1, va2


