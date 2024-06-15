# -*- coding: utf-8 -*-
# @Time    : 2019/5/13 18:11
# @Author  : Will
# @Email   : 864311352@qq.com
# @File    : fm_config.py
# @Software: PyCharm


class BaseConfig(object):
    """
    Base configuration with default settings.
    """
    FOR_PROJECT = 'anonymous'

    def __init__(self, ):
        pass


class ProductionConfig(BaseConfig):
    """
    Production-specific configuration.
    """
    ...


class DevelopmentConfig(BaseConfig):
    """
    Development-specific configuration.
    """
    ...


class TestConfig(BaseConfig):
    """
    Test-specific configuration.
    """
    ...