"""Plotting subpackage for qmtquant.

Re-exports :func:`save_plot`, the non-blocking helper around backtrader's
``cerebro.plot()`` that writes figures to disk instead of opening a GUI window.
"""
from __future__ import annotations

from .plot import save_plot

__all__ = ["save_plot"]
