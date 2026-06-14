"""Backtest subpackage.

Re-exports the cerebro engine entry points and the analyzer helpers so callers
can ``from qmtquant.backtest import run_backtest, Metrics`` directly.
"""
from __future__ import annotations

from .analyzers import Metrics, add_standard_analyzers, extract_metrics
from .engine import BacktestResult, build_cerebro, run_backtest

__all__ = [
    "run_backtest",
    "build_cerebro",
    "BacktestResult",
    "Metrics",
    "add_standard_analyzers",
    "extract_metrics",
]
