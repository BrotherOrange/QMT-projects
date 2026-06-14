"""Data subpackage: sources + the backtrader feed adapter.

Convenience re-exports so callers can do ``from qmtquant.data import ...``:

* the :class:`~qmtquant.data.sources.base.DataSource` abstraction and the
  canonical :data:`~qmtquant.data.sources.base.OHLCV_COLUMNS`;
* the concrete sources (synthetic / csv / xtquant);
* the validation + feed adapter (:func:`~qmtquant.data.feeds.validate_ohlcv`,
  :func:`~qmtquant.data.feeds.make_pandas_feed`).
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
from .feeds import validate_ohlcv, make_pandas_feed

__all__ = [
    "DataSource",
    "OHLCV_COLUMNS",
    "generate_ohlcv",
    "SyntheticDataSource",
    "CsvDataSource",
    "XtQuantDataSource",
    "validate_ohlcv",
    "make_pandas_feed",
]
