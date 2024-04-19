import nacos
import acm
import os
import shutil
import yaml
import configparser
from config_properties import data

class GetConfig(object):

    # 读取本地地址，以判断当前的环境，
    def get_filename(self):
        # 当前环境 这里不是完整路径
        pwd = os.path.dirname(__file__)
        properties_name = f'properties/config-{self.project}-{self.ide}.properties'

        # 使用完整路径
        properties_name = os.path.join(pwd, properties_name)

        # 判断路径是否存在
        if os.path.exists(properties_name):
            return properties_name
        else:
            raise Exception(f'完整路径的文件{properties_name}不存在')


    #  递归删除文件夹
    @staticmethod
    def remove_file():
        for name in ["nacos-data", 'acm-data']:
            if os.path.exists(name):
                shutil.rmtree(name)


    # 读取本地的配置文件内容，存放访问acm/nacos需要的访问数据
    def get_conf_value(self):
        # 读取环境中的访问数据
        ticket_config = configparser.ConfigParser()
        ticket_config.read( self.get_filename() )

        # 所有section
        sec = ticket_config.sections()
        # section1下所有的key
        opt = ticket_config.options(sec[0])

        # 配置文件转为key:value数据
        info = {}
        info['SELECT_TYPE'] = sec[0]
        for name in opt :
            info[name.upper()] = ticket_config.get(sec[0], name )

        print('已成功获取本地配置')

        return info


    # 根据参数，进行不同方法的配置获取 从acm还是从nacos读取文件
    def get_ac(self):
        # self.data = self.get_conf_value()
        self.data = data

        if self.data['SELECT_TYPE'] =='ACM':

            client = acm.ACMClient(endpoint=self.data['ENDPOINT'],
                                   namespace=self.data['NAMESPACE'],
                                   ak=self.data['AK'],
                                   sk=self.data['SK'])
            config = client.get( self.data['DATA_ID'], self.data['GROUP'])

        elif self.data['SELECT_TYPE'] =='NACOS':

            client = nacos.NacosClient(server_addresses=self.data['SERVER_ADDRESSES'],
                                       namespace=self.data['NAMESPACE']
                                       )
            config = client.get_config(self.data['DATA_ID'], self.data['GROUP'])

        self.remove_file()
        result = yaml.safe_load(config)

        return result