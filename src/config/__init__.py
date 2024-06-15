#!/usr/bin/env python
# @Time    : 2020/1/19 20:29
# @Author  : Will
# @Email   : 864311352@qq.com
# @File    : __init__.py
# @Software: PyCharm

try:
    from .prod_config import default_config
except:
    from .dev_config import default_config
