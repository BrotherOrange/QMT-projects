"""Data-source abstraction and the canonical OHLCV column contract.

This module is the OWNER of :data:`OHLCV_COLUMNS` (the normalized column order
that every data source must produce) and defines the :class:`DataSource`
abstract base class. Concrete sources (synthetic / csv / xtquant) implement
:meth:`DataSource.get_dataframe` and inherit :meth:`DataSource.to_feed`.

Dependency note
---------------
The backtest engine depends ONLY on this abstraction, never on a concrete
source. ``feeds`` is imported lazily inside :meth:`DataSource.to_feed` to avoid
an import cycle (``feeds`` imports ``OHLCV_COLUMNS`` from here, while sources
import ``feeds`` only when actually building a backtrader feed).
"""

from __future__ import annotations

import abc
from datetime import datetime

import backtrader as bt
import pandas as pd

# The single source of truth for the normalized OHLCV column order. 所有数据源
# 必须输出这五列、且为 DatetimeIndex。feeds.py 从这里导入此常量做校验。
OHLCV_COLUMNS: tuple[str, ...] = ("open", "high", "low", "close", "volume")


class DataSource(abc.ABC):
    """Abstract market-data source returning normalized OHLCV frames.

    Subclasses implement :meth:`get_dataframe` to fetch / generate bars for a
    symbol and return a :class:`pandas.DataFrame` with a
    :class:`~pandas.DatetimeIndex` and exactly the :data:`OHLCV_COLUMNS`.
    The concrete :meth:`to_feed` turns that frame into a backtrader feed.
    """

    @abc.abstractmethod
    def get_dataframe(
        self,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """Return a normalized OHLCV frame for ``symbol`` in ``[start, end]``.

        Implementations MUST return a frame whose index is a
        :class:`~pandas.DatetimeIndex` and whose columns are exactly
        :data:`OHLCV_COLUMNS`. Validation is performed downstream in
        :func:`qmtquant.data.feeds.make_pandas_feed`.
        """

    def to_feed(
        self,
        symbol: str,
        *,
        start: datetime | None = None,
        end: datetime | None = None,
        **feed_kwargs,
    ) -> bt.feeds.PandasData:
        """Build a validated backtrader :class:`~backtrader.feeds.PandasData`.

        Fetches the frame via :meth:`get_dataframe` and wraps it through
        :func:`qmtquant.data.feeds.make_pandas_feed`, which validates the shape
        before backtrader ever sees it. ``make_pandas_feed`` is imported lazily
        to keep this module free of any dependency on ``feeds`` at import time.
        """
        df = self.get_dataframe(symbol, start, end)
        from ..feeds import make_pandas_feed  # lazy import: avoid import cycle

        return make_pandas_feed(df, name=symbol, **feed_kwargs)


__all__ = ["DataSource", "OHLCV_COLUMNS"]
