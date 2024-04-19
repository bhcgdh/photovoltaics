import os
import yaml
from application_configuration import GetConfig
# from config_properties import data
import logging.config

class Config:
    # 链接应用配置
    clf = GetConfig()
    # data = clf.get_ac() # 没有acm数据

    # 2 实时数据库数据
    # data = {}
    # data['DATA'] = {}
    # data['DATA']['PORT'] = 21111
    # # 基础开发测试 mysql
    # data['MysqlBASE'] = {}
    # data['MysqlBASE']['charset'] = 'utf8'
    # data['MysqlBASE']['host'] = "223.223.223.248"
    # data['MysqlBASE']['user'] = "dbadmin"
    # data['MysqlBASE']['passwd'] = "zhyjy@DB123"
    # data['MysqlBASE']['port'] = 3306
    # data['MysqlBASE']['database'] = "algorithm_data"
    # data['MysqlBASE']['TableDataID'] = "t_statist_data"
    # data['MysqlBASE']['TableDataSave'] = "t_statist_result"
    # # 测试库
    # data['MysqlBASE']['TableDataId'] = "t_statist_data2"
    # data['MysqlBASE']['TableDataSave'] = "t_statist_result2"
    #
    # # ==========================================
    # # 基础开发库 mysql
    # data['MysqlBASE'] = {}
    # data['MysqlBASE']['charset'] = 'utf8'
    # data['MysqlBASE']['host'] = "10.1.180.133"
    # data['MysqlBASE']['user'] = "sys3000sa"
    # data['MysqlBASE']['passwd'] = "sys3000"
    # data['MysqlBASE']['port'] = 3306
    # data['MysqlBASE']['database'] = "algorithm_data"
    # data['MysqlBASE']['TableDataID'] = "t_statist_data"
    # data['MysqlBASE']['TableDataSave'] = "t_statist_result"
    #
    # # ==========================================
    # data['TDengineBASE'] = {}
    # data['TDengineBASE']['charset'] = 'utf8'
    # data['TDengineBASE']['host'] = "10.1.180.133"
    # data['TDengineBASE']['user'] = "root"
    # data['TDengineBASE']['passwd'] = "taosdata"
    # data['TDengineBASE']['port'] = 3306
    # data['TDengineBASE']['database'] = "sys3000sa"
    # data['TDengineBASE']['config'] = r"C:\TDengine\cfg\taos.cfg"
    # data['TDengineBASE']['TableDataId'] = "ai_data"

    # 测试库
    # data['TDengineBASE']['host'] = "223.223.223.248"
    # data['TDengineBASE']['database'] = "sys3000sa_test"
    # Type = data['TYPE']
    # # 1 原始真实的光伏，负荷，储能点号数据
    # API_DATA = data['API_DATA']
    #
    # SQL_DATA = data['SQL_DATA']
    #
    # # 2 节假日数据，数据库信息
    # Holiday_DATA = data['Holiday_DATA']
    # Div_Holiday = data['Div_Holiday']
    #
    # # 3 防逆流初始值
    # Integrity = data["Thory_DATA"]['Integrity_DATA']
    # SOC_INIT = data["Thory_DATA"]['SOC_INIT_DATA']
    # Counter_Currents = data["Thory_DATA"]['Counter_Currents_DATA']
    #
    #
    # TDengineBASE = data['TDengineBASE']
    # MysqlBASE = data['MysqlBASE']
    # TableSave = MysqlBASE['TableDataSave']
    #
    # DATA = data['DATA']
    # PORT = DATA['PORT']

    # # 定时每日执行任务时间设置
    # TIMING = data['TIMING']['Daily']
    # TIME_HOUR = TIMING['HOUR']
    # TIME_MINUTE = TIMING['MINUTE']
    # # 每日进行循环获取的数据字段信息,
    # INFOS = data['INFOS']['Daily'][0]

    @staticmethod
    def init_app(app):
        pass

    @staticmethod
    def setup_logging(
            default_path='logging.yaml',
            default_level=logging.INFO,
            env_key='LOG_CFG'
    ):
        """
        Setup logging configuration
        """
        path = default_path

        """
        Get environment config file for logging config
        """
        value = os.getenv(env_key, None)
        if value:
            path = value

        """
        Set config for logging
        """
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)


class DevelopmentConfig(Config):
    DEBUG = True


class StagingConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

# 不同的环境，设置日志的记录方式
config = {
    'dev': DevelopmentConfig,
    'stg': StagingConfig,
    'pro': ProductionConfig,
    'default': DevelopmentConfig,
}

