"""Data-source plugins subpackage.

Re-exports the :class:`~qmtquant.data.sources.base.DataSource` abstraction (and
the canonical :data:`~qmtquant.data.sources.base.OHLCV_COLUMNS`) plus every
concrete source: synthetic (seeded generator), csv (real saved bars), and the
xtquant empty shell (future miniQMT live data).
"""

from __future__ import annotations

from .base import DataSource, OHLCV_COLUMNS
from .synthetic import generate_ohlcv, SyntheticDataSource
from .csv import CsvDataSource
from .xtquant_source import XtQuantDataSource

__all__ = [
    "DataSource",
    "OHLCV_COLUMNS",
    "generate_ohlcv",
    "SyntheticDataSource",
    "CsvDataSource",
    "XtQuantDataSource",
]
