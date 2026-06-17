"""统一量化运行时：一套策略，回放数据做回测/模拟、实时数据做实盘。

公开 API::

    from qmtquant.runtime import Strategy, Context, Bar, ReplayFeed, run, Result

策略只依赖 :class:`Strategy`/:class:`Context` 与 :class:`~qmtquant.live.broker.Broker`
抽象；切换回测/模拟/实盘只需更换 feed 与 broker。
"""

from __future__ import annotations

from .strategy import Strategy, Context
from .feed import Bar, Feed, ReplayFeed
from .engine import run
from .result import Result, Metrics, compute_metrics

__all__ = [
    "Strategy",
    "Context",
    "Bar",
    "Feed",
    "ReplayFeed",
    "run",
    "Result",
    "Metrics",
    "compute_metrics",
]
