"""Typed, immutable configuration for the backtest engine.

These dataclasses centralize the magic numbers that used to be scattered inline
in the original smoke test (initial cash 100000, commission 0.0003 / 万三,
fixed stake 100) so the engine, the CLI, and the tests all share a single
default plus a single override point.

This module is intentionally pure: no I/O and no framework imports
(no backtrader / pandas / numpy), so it stays at the bottom of the dependency
graph and is trivially importable everywhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class BrokerConfig:
    """Broker-level settings.

    Attributes:
        cash: Initial account cash.
        commission: Per-trade commission rate (0.0003 == 万三, i.e. 3bp).
    """

    cash: float = 100_000.0
    commission: float = 0.0003  # 万三


@dataclass(frozen=True, slots=True)
class BacktestConfig:
    """Top-level backtest configuration.

    Attributes:
        broker: Broker settings (cash + commission).
        stake: Fixed order size used by ``bt.sizers.FixedSize``.
    """

    broker: BrokerConfig = field(default_factory=BrokerConfig)
    stake: int = 100


__all__ = ["BrokerConfig", "BacktestConfig"]
