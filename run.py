from flask import Flask
from flask_cors import *
from config import config
from src import pvPred
from config import Config
# from core import scheduler
# import logging

def func_job():
    pvPred().do()

def create_app(config_name):
    """
    Create APP by config name
    """
    # new app by Flask
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app=app)
    """
    set configuration for logging
    """
    config[config_name].setup_logging()
    # register blueprint for app
    app.register_blueprint(switch_version("v1"))
    return app

def switch_version(version):

    """
    Import different blueprint according to version from app.config

    :param version:
    :return:
    """

    if version == "v1":
        from api import pv_power as blueprint
        return blueprint


# def create_app(config_name):
#     """
#     定时触发任务
#     Create APP by config name
#     """
#     # new app by Flask
#     app = Flask(__name__)
#     CORS(app, supports_credentials=True)
#     app.config.from_object(config[config_name])
#     config[config_name].init_app(app=app)
#     app.config.update(
#         {"SCHEDULER_API_ENABLED": True,
#          "JOBS": [
#              {"id": "job_weather",  # 任务ID
#               "func": func_job,     # 任务位置
#               "trigger": "cron",    # 触发器
#               "hour": Config.TIME_HOUR ,  # 小时
#               "minute": str(int(Config.TIME_MINUTE))  # 分钟
#               },
#                   ]
#          }
#     )
#     """
#     set configuration for logging
#     """
#     config[config_name].setup_logging()
#     # register blueprint for app
#     app.register_blueprint(switch_version("v1"))
#     scheduler.init_app(app)
#     scheduler.start()
#     logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)
#     return app
