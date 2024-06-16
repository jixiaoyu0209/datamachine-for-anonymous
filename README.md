# datamachine-for-anonymous

## 概述

dataMachine-for-anonymous 是一个多功能的数据处理和分析工具，旨在高效地进行pandas与数据库之间的ETL。

## 功能

- **数据库配置**：独立数据库配置管理。
- **数据转换**：便捷的数据转换功能，适应所需格式和结构。


## 先决条件
- `requirements.txt` 中列出的必要 Python 包

## 安装步骤

1. 克隆仓库：
   ```bash
   git clone https://github.com/jixiaoyu0209/dataMachine-for-anonymous.git
   cd datamachine_for_anonymous
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 用法

以下是使用 dataMachine-for-anonymous 处理数据的基本示例，具体代码见 `example/6.py`。

### 示例代码

```python
import pandas as pd

from src.config import default_config
from src.utils import SqlHelper, SqlConfig

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
```


## 贡献

欢迎任何形式的贡献！如果您有改进建议或发现问题，请提交 Issue 或 Pull Request。

## 许可证

该项目基于 MIT 许可证，详情请参阅 LICENSE 文件。