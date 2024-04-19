# -*- coding: utf-8 -*-
from flask_restplus import fields


class ModelInputFields(object):
    NAME = "ModelInputFields"
    # 必须给定的数据
    def __init__(self):
        self.freqs = fields.String( required=True , describe='时间间隔')
        self.aggtypes = fields.String( required=True , describe='聚合计算方式')
        self.station_name = fields.String(description='站点名称', required=True)
        self.algorithm_type = fields.String(description='功率训练预测的的周期', required=True) # 预测时间周期，超短期，短期，中长期, Forecast time period, ultra,short,medium
        # self.timezone = fields.String(description='时区', required=True) # 电站所在位置的时区
        # self.true = fields.List(fields.Float,description='真实数据', requested=True) #
        # self.pred = fields.List(fields.Float,description='预测数据', requested=True)
        self.longitude = fields.Float(description='经度', requested=True)
        self.latitude = fields.Float(description='纬度', requested=True)
        self.scale = fields.Float(description='装机容量', requested=True)

    def create_api_model(self, api):
        return api.model(self.NAME, self.__dict__)


class ModelOutputFields(object):
    NAME = "ModelOutputFields"

    def __init__(self):

        self.result = fields.Raw()

        self.status = fields.Integer()

        self.message = fields.String()

    def create_api_model(self, api):
        return api.model(self.NAME, self.__dict__)
