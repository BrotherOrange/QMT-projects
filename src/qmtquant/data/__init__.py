"""数据子包：OHLCV 数据源 + 列契约 + 形状校验。

便捷再导出，使调用方可 ``from qmtquant.data import ...``：

* :class:`~qmtquant.data.sources.base.DataSource` 抽象与 :data:`OHLCV_COLUMNS`；
* 具体数据源（synthetic / csv / xtquant）；
* 形状校验 :func:`~qmtquant.data.sources.base.validate_ohlcv`。
"""

from __future__ import annotations

from .sources import (
    DataSource,
    OHLCV_COLUMNS,
    generate_ohlcv,
    SyntheticDataSource,
    CsvDataSource,
    XtQuantDataSource,
)
from .sources.base import validate_ohlcv

__all__ = [
    "DataSource",
    "OHLCV_COLUMNS",
    "validate_ohlcv",
    "generate_ohlcv",
    "SyntheticDataSource",
    "CsvDataSource",
    "XtQuantDataSource",
]
