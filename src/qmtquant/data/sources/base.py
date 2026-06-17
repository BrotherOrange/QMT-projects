"""数据源抽象与 OHLCV 列契约。

本模块拥有 :data:`OHLCV_COLUMNS`（每个数据源必须产出的归一化列），定义
:class:`DataSource` 抽象基类与形状校验 :func:`validate_ohlcv`。具体数据源
（synthetic / csv / xtquant）实现 :meth:`DataSource.get_dataframe`，产出带
:class:`~pandas.DatetimeIndex`、列恰为 :data:`OHLCV_COLUMNS` 的帧，供
:class:`~qmtquant.runtime.feed.ReplayFeed` 逐根回放。

本模块不依赖任何回测框架，处于依赖图底层、可被到处导入。
"""

from __future__ import annotations

import abc
from datetime import datetime

import pandas as pd

# 归一化 OHLCV 列顺序的唯一真源。所有数据源必须输出这五列、且为 DatetimeIndex。
OHLCV_COLUMNS: tuple[str, ...] = ("open", "high", "low", "close", "volume")


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    """校验 ``df`` 为合法 OHLCV 帧（DatetimeIndex + 含全部 :data:`OHLCV_COLUMNS`），否则抛 ValueError。

    返回原帧（不修改），便于链式调用。
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError(f"expected a pandas DataFrame, got {type(df).__name__!r}")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError(
            f"OHLCV frame must have a DatetimeIndex, got {type(df.index).__name__!r}"
        )
    missing = [c for c in OHLCV_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"OHLCV frame is missing required columns: {missing} "
            f"(expected all of {list(OHLCV_COLUMNS)}, got {list(df.columns)})"
        )
    return df


class DataSource(abc.ABC):
    """归一化 OHLCV 行情源抽象。

    子类实现 :meth:`get_dataframe`，返回索引为 :class:`~pandas.DatetimeIndex`、
    列恰为 :data:`OHLCV_COLUMNS` 的帧。
    """

    @abc.abstractmethod
    def get_dataframe(
        self,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """返回 ``symbol`` 在 ``[start, end]`` 的归一化 OHLCV 帧。"""


__all__ = ["DataSource", "OHLCV_COLUMNS", "validate_ohlcv"]
