"""
1 输入数据，字典，转为dataframeg格式，
    支持：字典，文件，数据库
2 字段包含必须的数值数据，以及长中短，明确指示，
3 数据值：电子基本信息，电站的功率，天气，
4 根据输入的数据，确定用哪个方式进行预测，只有基本信息，还是天气等
5 根据4确定模型的名字，和特征处理的方式
6 模型

预处理：
    训练：去除异常，可以不连续，可以填充，
    预测：
"""
import json
import warnings

warnings.filterwarnings('ignore')
try:
    from metric import month_short_metric, month_medium_metric, month_ultra_metric
except:
    from ..metric import month_short_metric, month_medium_metric, month_ultra_metric

try:
    from .base import Base
    from .prep_prepross import prepross
    from .model_train import train_pw
    from .model_pred import pred_pw, train_pred

except:
    from base import Base
    from prep_prepross import prepross
    from model_train import train_pw
    from model_pred import pred_pw, train_pred

import logging
logger = logging.getLogger(__name__)

# from metric.month_metric import month_ultra_metric

class pvPred(Base):

    def data_anlysis(self):
        self.param = self.json_data # 数据中各种有效字段
        try:
            self.df = self.df # 读取了原始数据，可能是空
        except:
            self.df = None

    @staticmethod
    def train_split_data(df, period):
        # 数据默认是按顺序 进行2，8 分割，
        # 1 数据多，保留最后一个月数据 8：2，7：2
        # 2 数据不够多，2，,8分
        # 3 数据极少，保证最后有至少一个样本作测试，，超短期，最后15个点，短期288个点，中期7*96个点
        n1 = len(df)
        n2 = 96 * 30

        n3 = int(n1 * 0.8)
        n4 = n1 - n3
        info = f"{n1 - n2} samples for training, {n2} samples for testing"
        # 1 如果是有至少6个月数据，则使用最后一个月进行测试
        if n1 // n2 >= 6:
            train = df.head(n1 - n2)
            test = df.tail(n2)
            info = f"至少有6个月的数据，{n1-n2} samples for training, {n2} samples for testing"
            logger.info(info)

        # 2 至少有一个月的数据
        elif n1 // n2 >= 1:
            train = df.head(n3)
            test = df.tail(n4)
            info = f"至少有1个月的数据，{n3} samples for training, {n4} samples for testing"
            logger.info(info)

        # 3 至少20天数据
        elif n1 > 96 * 20:
            train = df.head(n3)
            test = df.tail(n4)
            info = f"至少有20天的数据 {n3} samples for training, {n4} samples for testing"
            logger.info(info)

        # 4 超短期，至少10天的数据
        elif n1 > 96 * 10 and period == 'short':
            train = df.head(n3)
            test = df.tail(n4)
            info = f"至少有10天的数据，{n3} samples for training, {n4} samples for testing"
            logger.info(info)

        # 5 其他数据过少，不建议进行训练
        else:
            train, test = df, None
            info = f"{n1} samples for training. The amount of data is too small, all training is performed "
            logger.info(info)

        return train, test
    def train_pred_eval(self):
        if self.ftperiod=='short':
            self.test_rmse, self.test_mqr = month_short_metric(self.df_test,scale=self.scale )
        elif self.ftperiod=='ultra':
            self.test_rmse, self.test_mqr = month_ultra_metric(self.df_test,scale=self.scale )
        elif self.ftperiod=='medium':
            self.test_rmse, self.test_mqr = month_medium_metric(self.df_test,scale=self.scale )
        else:
            pass


    def train_data(self, train):
        # 所有数据用于训练，不返回其他数据，可以在logger中记录训练的数据，默认训练的模型都进行保存
        train = prepross(train, self.param)
        train_pw(train, self.param, save=self.save_model)

    def train_data_split(self):
        # 如果进行分割，返回预测的结果，预测结果按样本进行统计
        self.df_train, self.df_test = self.train_split_data(self.df, self.param['ftperiod'])
        self.train_data(self.df_train)
        if self.df_test is not None:
            self.test_pred = train_pred(self.df_test, self.param) # 训练中的测试集预测结果, 大量的预测结果，可以用月度评估
            # Month Qualified rate
            self.train_pred_eval()

    def predict(self):
        data = prepross(self.df, self.param)
        self.pred = pred_pw(data, self.param)


    def do(self):
        self.data_anlysis()
        # 判断 是否训练，是否预测，是否有数据，是否进行分割，
        if self.df is None and self.train == 0:  # 没有数据且不用训练，使用理论值

            pred = self.df_pred_basic
            pred.index = pred['t']
            val = json.loads(pred[['t','pred']].to_json(orient='records'))
            res = {'pred':val}

        elif self.df is not None and self.train == 0:  # 有数据，进行预测，需要调用模型，
            self.predict()
            pred = self.pred
            pred.index = pred['t']
            val = json.loads(pred[['t','pred']].to_json(orient='records'))
            res = {'pred': val}

        elif self.train == 1 and self.df is None: # 没有数据, 要求进行训练 需要log提示没有有效数据
            res = {"code":"No valid data for training"}
            pass

        elif self.train == 1 and self.train_split == 1: # 有数据，要求训练分割测试集, 默认不进行分割
            self.train_data_split()

            if self.test_rmse is not None:
                res={'code':f'Complete training. The average test accuracy is {self.test_rmse}. Monthly pass rate is {self.test_mqr}'}
            else:
                res={'code':'Complete training. Too little data, all used for training'}

        elif self.train == 1 and self.train_split == 0:
            self.train_data(self.df)
            res={'code':'Complete training'}
        else:
            res={'code':'Nothing'}

        return res

# data['train_split'] = 1
# res = df.do()
# print(res)
