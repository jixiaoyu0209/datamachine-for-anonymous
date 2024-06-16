# -*- coding: utf-8 -*-
# @Time    : 2021/1/8 10:36 上午
# @Author  : Will
# @Email   : 864311352@@qq.com
# @File    : m_config.py
# @Software: PyCharm


from config.fm_config import (
    ProductionConfig as FmProductionConfig,
    DevelopmentConfig as FmDevelopmentConfig,
    TestConfig as FmTestConfig
)


class BaseConfig(object):
    SECRET_KEY = "FklfSOfNOkWawiCw"


class ProductionConfig(BaseConfig, FmProductionConfig):
    pass


class DevelopmentConfig(BaseConfig, FmDevelopmentConfig):
    INFO = {
        "db": "info",
        "dialect": "sqlite3"
    }


class TestConfig(BaseConfig, FmTestConfig):
    pass


CONFIG = {"development": DevelopmentConfig,
          "production": ProductionConfig,
          "test": TestConfig
          }

default_config = CONFIG["development"]()
