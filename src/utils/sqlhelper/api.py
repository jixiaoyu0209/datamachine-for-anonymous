#!/usr/bin/env python
# @Time    : 2024/1/8 11:23
# @Author  : Will
# @Email   : 864311352@qq.com
# @File    : api.py
# @Software: PyCharm

import concurrent.futures
import inspect
import json
import time
from typing import Any, Dict, List, Union, Literal

import pandas as pd
from ColorInfo import ColorLogger
from pandas.io.sql import DatabaseError

from utils.sqlhelper.creaters import (MysqlBase, Sqlite3Base, SqlBase, SqlConfig)


class SqlHelper:
    logger = ColorLogger()
    logger.set_format(filename_on=False, class_on=False, fun=False, line=False)

    def __init__(self, config: SqlConfig):
        self.config = config
        self.creater = self.get_creater()

    def get_creater(self, ) -> SqlBase:
        """获取数据库连接创建器

        根据配置文件中指定的数据库方言，创建相应的数据库连接创建器。
        目前支持 'mysql' 和 'sqlite3'。

        :return: SqlBase: 数据库连接创建器的实例。
        :raises NotImplementedError: 如果不支持指定的数据库方言。
        """

        dialect = self.config.dialect

        creators = {
            "mysql": MysqlBase,
            "sqlite3": Sqlite3Base
        }

        try:
            return creators[dialect](self.config)
        except KeyError:
            self.logger.error(f"Unsupported dialect: {dialect}")
            raise NotImplementedError(f"Unsupported dialect: {dialect}")

    def _read_sql(self, sql: str) -> pd.DataFrame:
        """私有方法：执行SQL查询并返回DataFrame

        :param sql: 要执行的SQL查询。
        :param sql_name: SQL查询的名称，用于日志记录。
        :return: pd.DataFrame: SQL查询结果。
        :raises DatabaseError: 如果数据库操作失败。
        """

        calling_frame_locals = inspect.currentframe().f_back.f_locals
        try:
            sql_name = [var_name for var_name, var_val in calling_frame_locals.items() if var_val is sql][0]
        except Exception as e:
            sql_name = 'unknown'

        engine = self.creater.engine
        try:
            start_time = time.time()
            df = pd.read_sql(sql, engine)
            end_time = time.time()
            time_eclipse = round((end_time - start_time), 2)
            self.logger.info(f"    {sql_name}：获取原始数据shape:{df.shape}; 耗时：{time_eclipse}s")
        except DatabaseError as e:
            self.logger.error(f"数据库错误：{e}")
            raise Exception(e)
        return df

    def get_df(self, *args) -> Union[List[pd.DataFrame], pd.DataFrame]:
        """查询数据"""

        calling_frame_locals = inspect.currentframe().f_back.f_locals
        fback_filename = calling_frame_locals.get("__file__") or calling_frame_locals.get("__session__")
        fback_lineno = inspect.currentframe().f_back.f_lineno

        self.logger.info(f"    执行文件名：{fback_filename}， 行号：{fback_lineno}")

        def execute_query(sql):
            df = self._read_sql(sql)
            return df

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            dfs = list(executor.map(execute_query, args))
        return dfs if len(dfs) > 1 else dfs[0]

    def _json_serialize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        对DataFrame中的列进行JSON序列化。

        参数:
        df (pd.DataFrame): 包含要处理数据的DataFrame。

        返回:
        pd.DataFrame: 处理后的DataFrame。
        """
        for col in df.columns:
            if df[col].dropna().apply(lambda x: isinstance(x, (list, dict))).all():
                df[col] = df[col].apply(lambda x: json.dumps(x) if pd.notnull(x) else None)
        return df

    def insert(self, df: pd.DataFrame, tb: str, if_exists: Literal["replace", "append"] = "append",
               index: bool = False, chunksize: int = None, method: Any = None, **kwargs) -> int:
        """
        将数据插入数据库表中。

        参数:
        df (pd.DataFrame): 要插入的数据的DataFrame。
        tb (str): 表名。
        if_exists (Literal["replace", "append"]): 如果表已存在，采取的行动。默认是"append"。
        index (bool): 是否写入索引。默认是False。
        chunksize (int, 可选): 分块大小。默认是None。
        method (Any, 可选): 插入方法。默认是None。

        返回:
        int: 插入的行数。
        """

        engine = self.creater.engine
        if "." in tb:
            kwargs["schema"] = tb.split(".")[0]
            tb = tb.split(".")[1]

        # JSON序列化列
        df = self._json_serialize_columns(df)

        try:
            row = df.to_sql(tb, engine, if_exists=if_exists, index=index, chunksize=chunksize, method=method, **kwargs)
        except Exception as e:
            self.logger.error(f"插入数据时发生错误: {e}")
            raise

        return row

    def update(self, df: pd.DataFrame, tb: str, wheres: List[str], sets: List[str] = None) -> int:
        """
        使用DataFrame中的数据更新数据库表中的记录。

        参数:
        df (pd.DataFrame): 包含要更新的数据的DataFrame。
        tb (str): 要更新的表名。
        wheres (List[str]): 用于WHERE子句的列列表。
        sets (List[str], 可选): 用于SET子句的列列表。默认为None。

        返回:
        int: 更新的行数。

        Example:
        sql = "update table_name set A=%(A)s where B=%(B)s;"
        params = (200, "c") or params = {"A": 200, "B": "c"}
        """

        if df.empty:
            return 0

        if not wheres:
            raise ValueError("数据库更新过滤条件不能为空")

        if isinstance(wheres, str):
            wheres = [wheres]

        set_cols = sets or list(set(df.columns) - set(wheres))

        set_sql_txt = self.creater.ping_wilcards(set_cols, ",")
        where_sql_txt = self.creater.ping_wilcards(wheres, " ")
        if where_sql_txt:
            where_sql_txt = "and " + where_sql_txt

        update_sql = f'''
        update {tb}
        set {set_sql_txt}
        where 1 = 1
            {where_sql_txt};
        '''

        self.logger.info(f"更新sql：{update_sql}")

        # 处理缺失值
        df = df.replace({pd.NA: None}).where(df.notnull(), None)

        # JSON序列化列
        df = self._json_serialize_columns(df)

        params = df.to_dict(orient='records')

        try:
            row = self.creater.execute(update_sql, params)
        except Exception as e:
            self.logger.error(f"更新数据时发生错误: {e}")
            raise

        return row

    def execute(self, sql: str, params: Union[List, Dict] = None) -> Any:
        row = self.creater.execute(sql, params)
        return row

    def __repr__(self):
        return f'{str(self.creater)}客户端应用'
