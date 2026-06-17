"""行情驱动：``Bar`` 数据载体、``Feed`` 抽象与历史回放 ``ReplayFeed``。

回测/模拟用 :class:`ReplayFeed` 把一只股票的 OHLCV ``DataFrame``（来自任意
:class:`~qmtquant.data.sources.base.DataSource`）逐根产出为 :class:`Bar`。
实时 ``RealtimeFeed`` 留待 v2（接口与 :class:`Feed` 一致，到时无缝接入）。
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from datetime import date
from typing import Iterator

import pandas as pd

from ..data.sources.base import OHLCV_COLUMNS, validate_ohlcv


@dataclass
class Bar:
    """单根 K 线。``up_limit`` / ``down_limit`` 为估算的涨跌停价（首根为 None）。"""

    ts: pd.Timestamp
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    up_limit: float | None = None
    down_limit: float | None = None

    @property
    def date(self) -> date:
        return self.ts.date()


class Feed(abc.ABC):
    """按时间顺序产出 :class:`Bar` 的行情源。"""

    @abc.abstractmethod
    def __iter__(self) -> Iterator[Bar]:
        ...


class ReplayFeed(Feed):
    """把一只股票的 OHLCV ``DataFrame`` 逐根回放为 :class:`Bar`。

    Parameters
    ----------
    df:
        OHLCV 帧（DatetimeIndex + :data:`OHLCV_COLUMNS`），如
        ``XtQuantDataSource(period="1d").get_dataframe(symbol, start, end)``。
    symbol:
        标的代码，写入每个 :class:`Bar`。
    limit_pct:
        涨跌停幅度估算（默认 0.10）。涨跌停按 ``round(前收 × (1 ± limit_pct), 2)`` 估算，
        **是近似**：ST(0.05)/创业板·科创板(0.20) 需自行调整。首根无前收，故不设涨跌停。
    """

    def __init__(self, df: pd.DataFrame, symbol: str, *, limit_pct: float = 0.10) -> None:
        self.df = validate_ohlcv(df).sort_index()
        self.symbol = symbol
        self.limit_pct = limit_pct

    def __iter__(self) -> Iterator[Bar]:
        prev_close: float | None = None
        for ts, row in self.df.iterrows():
            up = down = None
            if prev_close is not None:
                up = round(prev_close * (1 + self.limit_pct), 2)
                down = round(prev_close * (1 - self.limit_pct), 2)
            close = float(row["close"])
            yield Bar(
                ts=ts,
                symbol=self.symbol,
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=close,
                volume=float(row["volume"]),
                up_limit=up,
                down_limit=down,
            )
            prev_close = close


__all__ = ["Bar", "Feed", "ReplayFeed", "OHLCV_COLUMNS"]
