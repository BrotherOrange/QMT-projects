"""qmtquant -- a backtrader-based quant backtesting toolkit.

This package root defines the version and re-exports a small, curated public
API so callers can write, e.g.::

    from qmtquant import run_backtest, save_plot, SmaCross, generate_ohlcv

The dependency direction inside the package is strictly one-way::

    data -> strategies -> backtest -> plotting

with ``live/`` as an independent, future-facing sibling.
"""
from __future__ import annotations

__version__: str = "0.1.0"

from .backtest.engine import run_backtest, build_cerebro, BacktestResult
from .backtest.analyzers import Metrics
from .plotting.plot import save_plot
from .strategies.sma_cross import SmaCross
from .data.sources.synthetic import generate_ohlcv, SyntheticDataSource
from .data.sources.base import DataSource, OHLCV_COLUMNS
from .config import BrokerConfig, BacktestConfig

__all__ = [
    "__version__",
    "run_backtest",
    "build_cerebro",
    "BacktestResult",
    "Metrics",
    "save_plot",
    "SmaCross",
    "generate_ohlcv",
    "SyntheticDataSource",
    "DataSource",
    "OHLCV_COLUMNS",
    "BrokerConfig",
    "BacktestConfig",
]
