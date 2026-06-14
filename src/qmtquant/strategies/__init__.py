"""Strategies subpackage.

Holds backtrader strategy implementations. Currently exposes the
:class:`SmaCross` double moving-average crossover strategy migrated from the
original smoke test.
"""
from __future__ import annotations

from .sma_cross import SmaCross

__all__ = ["SmaCross"]
