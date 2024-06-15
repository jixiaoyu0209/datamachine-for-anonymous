#!/usr/bin/env python
# @Time    : 2024/1/24 16:38
# @Author  : Will
# @Email   : 864311352@qq.com
# @File    : 6.py
# @Software: PyCharm


import pandas as pd

from config import default_config
from utils import SqlHelper, SqlConfig

sqlinstance_info = SqlHelper(SqlConfig(**default_config.INFO))

df = pd.DataFrame([{"id": 1, "a": None, "b": None},
                   {"id": 2, "a": None, "b": {"a": 1}, },
                   {"id": 3, "a": None, "b": {"a": 1}, },
                   {"id": 4, "a": pd.Timestamp(year=2024, month=1, day=31, hour=12, minute=30), "b": {"a": 1}},
                   ])

sqlinstance_info.insert(df, tb="example")

df = pd.DataFrame({
    'id': 1,
    'b': {"a": 666}
})

sqlinstance_info.update(df, tb="example", wheres=["id"])
