#!/usr/bin/env python
# @Time    : 2024/1/8 12:39
# @Author  : Will
# @Email   : 864311352@qq.com
# @File    : creaters.py
# @Software: PyCharm

from contextlib import contextmanager
from typing import Optional

from pydantic import Field, BaseModel, field_validator
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from libs.enums import TextChoices
from utils.encryption import Encryption


class DialectEnum(TextChoices):
    mysql = 'mysql'
    sqlite = 'sqlite3'


class SqlConfig(BaseModel):
    host: Optional[str] = Field(default=None, title="地址")
    user: Optional[str] = Field(default=None, title="用户")
    port: Optional[str] = Field(default=None, title="端口号")
    pwd: str = Field(default=None, title="密码")
    db: str = Field(title="数据库")
    max_connections: int = Field(default=15, title="最大连接数")
    echo: bool = Field(default=False, title="显示SQL")
    dialect: DialectEnum = Field(title="数据库方言")
    charset: str = Field(default="utf8", title="字符编码")

    @field_validator('pwd', mode="before")
    def decrypt_password(v):
        if v is not None:
            return Encryption().decrypt(v)
        return v


class SqlBase:

    def __init__(self, config: SqlConfig):
        self.config = config
        self.engine = create_engine(self.connect_url(), echo=self.config.echo)

    def __enter__(self):
        self.con = self.engine.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            self.con.rollback()
        self.con.commit()
        self.engine.dispose()
        self.con.close()

    @contextmanager
    def connection(self):
        try:
            conn = self.engine.connect()
            yield conn
            conn.commit()
        except SQLAlchemyError as e:
            conn.rollback()
            raise SQLAlchemyError(f"事务失败: {e}") from e
        finally:
            conn.close()

    def connect_url(self):
        raise NotImplementedError("Subclasses must implement this method")

    def execute(self, sql, params=None):
        """Simple passthrough to SQLAlchemy connectable"""
        args = [] if params is None else [params]
        with self.connection() as conn:
            if isinstance(sql, str):
                return conn.exec_driver_sql(sql, *args)
            return conn.execute(sql, *args)

    def ping_wilcards(self, cols, jon=""):
        raise NotImplementedError("Subclasses must implement this method")


class MysqlBase(SqlBase):

    def connect_url(self):
        """ url = "mysql+pymysql://用户名：密码@主机名：端口号/数据库名" """
        url = f"mysql+pymysql://{self.config.user}:{self.config.pwd}@{self.config.host}:{self.config.port}/{self.config.db}"
        return url

    def ping_wilcards(self, cols, jon=""):
        wildcards = f"{jon}".join([f"{col}=%({col})s" for col in cols])
        return wildcards

    def __str__(self):
        return f'msyql: {self.config.host}:{self.config.db}'


class Sqlite3Base(SqlBase):

    def connect_url(self):
        """ url = "sqlite:///example.db" """
        url = f"sqlite:///{self.config.db}.db"
        return url

    def ping_wilcards(self, cols, jon=","):
        wildcards = f"{jon}".join([f"{col}=:{col}" for col in cols])
        return wildcards

    def __str__(self):
        return f'sqlite: {self.config.db}'
