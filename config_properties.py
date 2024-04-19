
# OriginDATA 原始数据的来源，先从api获取,后续可能是数据库中读取
data = {
    "TYPE":"api",
    'DATA': {'PORT': 26617}
}
# data ={
#     'DATA': {'PORT': 26617},
#     "TYPE":"api",
#     'API_DATA':{
#         "url": "http://10.1.176.22:25507/",
#         "point_elec" : "162824509383765",
#         "point_pv" : "162824509381721",
#         "point_pw" : "162824509383764",
#     },
#
#     "SQL_DATA":{
#         'charset': "utf8",
#         'host': "223.223.223.248",
#         'user': "dbadmin",
#         'passwd': "zhyjy@DB123",
#         'port': 3306,
#         'database': "algorithm_data",
#         'TableDataID': "t_statist_data",
#         'TableDataSave': "t_statist_result"
#     },
#     "Holiday_DATA":{
#         'charset': 'utf8',
#         'host': "10.1.176.26",
#         'user': "ynyquery",
#         'passwd': "ZH@Ynydb123",
#         'port': 3306,
#         'database': "algorithm_data",
#         'TableHoliday': "tb_holiday",
#     },
#     "Div_Holiday": False,
#     "Thory_DATA": {"Integrity_DATA": [0.8],
#                   "SOC_INIT_DATA": [6.5],
#                   "Counter_Currents_DATA": [50, 150]
#                   },
#
#     'MysqlBASE': {
#          'charset': 'utf8',
#          'host': "223.223.223.248",
#          'user': "dbadmin",
#          'passwd': "zhyjy@DB123",
#          'port': 3306,
#          'database': "algorithm_data",
#          'TableDataID': "t_statist_data",
#          'TableDataSave': "t_statist_result",
#                   },
#     'TDengineBASE': {
#         "charset" : 'utf8',
#         "host" : "10.1.180.133",
#         "user" : "root",
#         "passwd" : "taosdata",
#         "port" : 3306,
#         "database" : "sys3000sa",
#         "config" : r"C:\TDengine\cfg\taos.cfg",
#         "TableDataId" : "ai_data",
#         # "host": "223.223.223.248", 测试库
#         # "database": "sys3000sa_test",
#     },
#     "TIMING":{
#         'Daily':
#             # {'HOUR': 19,
#             #  "MINUTE": 7 }
#             {'HOUR': 2,
#              "MINUTE": 30 }
#         },
#
#
# }

# from Nacos_information import nacos
# data = {'SELECT_TYPE' : 'ACM',
#         'SERVER_ADDRESSES' : nacos.SERVER_ADDRESSES,
#         'NAMESPACE' : nacos.NAMESPACE,
#         'AK' : '0f0c7aebabc14fba8c235e5e248c44e2',
#         'SK' : 'h7apLnc8OsZ95eW9Qa1QXL7q1Jg=',
#         'GROUP' : 'algorithm',
#         'DATA_ID' : 'business_power'
#         }
# data = {'SELECT_TYPE' : 'NACOS',
#         'SERVER_ADDRESSES' : nacos.SERVER_ADDRESSES,
#         'NAMESPACE' : nacos.NAMESPACE,
#         'GROUP' : 'algorithm',
#         'DATA_ID' : 'energy_storage_benefits'
#         }
