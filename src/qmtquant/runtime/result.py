"""回测/模拟运行结果与精简绩效指标。

:func:`compute_metrics` 由权益曲线自算 total_return / sharpe / max_drawdown / num_trades，
不依赖任何第三方回测框架。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass
class Metrics:
    """精简绩效指标。"""

    total_return: float        # 总收益率
    sharpe: float              # 年化夏普（按权益序列收益，假设日频；不足两点为 0）
    max_drawdown: float        # 最大回撤（正数，0~1）
    num_trades: int            # 成交笔数


@dataclass
class Result:
    """一次运行的完整结果。"""

    equity_curve: list[tuple[Any, float]]   # [(ts, equity), ...]
    trades: list[Any]                        # PaperBroker.Fill 列表
    metrics: Metrics
    final_cash: float
    final_positions: list[Any]               # Position 列表


def compute_metrics(equity_curve: list[tuple[Any, float]], num_trades: int,
                    *, periods_per_year: int = 252) -> Metrics:
    """由权益曲线计算精简指标。"""
    eq = np.array([v for _, v in equity_curve], dtype=float)
    if eq.size < 2 or eq[0] <= 0:
        return Metrics(total_return=0.0, sharpe=0.0, max_drawdown=0.0, num_trades=num_trades)

    total_return = float(eq[-1] / eq[0] - 1.0)

    rets = np.diff(eq) / eq[:-1]
    std = rets.std()
    sharpe = float(rets.mean() / std * np.sqrt(periods_per_year)) if std > 0 else 0.0

    running_max = np.maximum.accumulate(eq)
    drawdown = (running_max - eq) / running_max
    max_drawdown = float(drawdown.max())

    return Metrics(
        total_return=total_return,
        sharpe=sharpe,
        max_drawdown=max_drawdown,
        num_trades=num_trades,
    )


__all__ = ["Result", "Metrics", "compute_metrics"]
