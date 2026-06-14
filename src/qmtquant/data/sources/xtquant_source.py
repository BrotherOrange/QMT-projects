"""EMPTY SHELL xtquant (miniQMT) market-data source.

This is a placeholder so an xtquant-backed market-data source can slot in beside
:class:`~qmtquant.data.sources.synthetic.SyntheticDataSource` and
:class:`~qmtquant.data.sources.csv.CsvDataSource` without touching the engine.
The real implementation is deferred until QMT trading qualification is granted.

IMPORTANT: there is intentionally NO top-level ``import xtquant`` so the package
builds and imports cleanly on machines without the miniQMT SDK installed. When
implemented, import ``xtdata`` lazily inside :meth:`get_dataframe`.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from .base import DataSource


class XtQuantDataSource(DataSource):
    """Stub market-data source backed by xtquant / miniQMT (not yet implemented).

    Parameters
    ----------
    period:
        Bar period string understood by xtquant (e.g. ``"1d"``, ``"1m"``).
    """

    def __init__(self, *, period: str = "1d") -> None:
        self.period = period

    def get_dataframe(
        self,
        symbol: str,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> pd.DataFrame:
        """Not implemented yet -- see the TODO for the post-qualification plan."""
        raise NotImplementedError(
            "TODO: implement via xtquant.xtdata after QMT qualification: "
            "import xtdata inside this method (no top-level import); "
            "xtdata.download_history_data(symbol, period=self.period, "
            "start_time=..., end_time=...) to cache bars locally; "
            "xtdata.get_market_data_ex([], [symbol], period=self.period, "
            "start_time=..., end_time=...) to pull them back; "
            "then map the time / open / high / low / close / volume fields to an "
            "OHLCV_COLUMNS DataFrame with a DatetimeIndex (sorted, sliced to "
            "[start, end])."
        )


__all__ = ["XtQuantDataSource"]
