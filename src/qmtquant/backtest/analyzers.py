"""Analyzer preset and brittle nested-dict metric extraction.

backtrader analyzers return deeply-nested ``AutoOrderedDict`` structures whose
exact key paths are coupled to the backtrader version. This module isolates
that version-coupling in one place:

* :func:`add_standard_analyzers` attaches the four standard analyzers
  (SharpeRatio / DrawDown / Returns / TradeAnalyzer) under *stable* names, and
* :func:`extract_metrics` pulls the exact keys the smoke checks rely on into a
  typed, ``None``-tolerant :class:`Metrics` dataclass.

If a future backtrader bump moves a key, only this file needs to change.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import backtrader as bt


@dataclass(frozen=True, slots=True)
class Metrics:
    """Typed view over the headline backtest metrics.

    All scalar fields tolerate ``None`` because analyzers may legitimately
    produce no value (e.g. Sharpe with too few returns, no trades, etc.).

    Attributes
    ----------
    sharpe:
        Annualised Sharpe ratio, or ``None``.
    max_drawdown:
        Maximum drawdown (percent), or ``None``.
    total_return:
        Total compound return (``rtot``), or ``None``.
    total_trades:
        Number of trades recorded by the TradeAnalyzer (``0`` if none).
    raw:
        Full ``{analyzer_name: get_analysis()}`` mapping for callers that need
        the detailed nested structures.
    """

    sharpe: float | None
    max_drawdown: float | None
    total_return: float | None
    total_trades: int
    raw: dict[str, Any]


def add_standard_analyzers(cerebro: bt.Cerebro) -> None:
    """Attach the standard analyzer preset under stable names.

    Names used (and relied on by :func:`extract_metrics`):

    * ``sharpe`` -> :class:`~backtrader.analyzers.SharpeRatio`
    * ``dd``     -> :class:`~backtrader.analyzers.DrawDown`
    * ``ret``    -> :class:`~backtrader.analyzers.Returns`
    * ``trades`` -> :class:`~backtrader.analyzers.TradeAnalyzer`
    """
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
    cerebro.addanalyzer(bt.analyzers.Returns, _name="ret")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")


def extract_metrics(strategy: bt.Strategy) -> Metrics:
    """Pull the headline metrics out of a run strategy's analyzers.

    The nested key paths (``sharperatio``, ``max.drawdown``, ``rtot``,
    ``total.total``) are the brittle, version-coupled part. We use ``.get(...)``
    throughout so a missing key yields ``None``/``0`` rather than raising.
    """
    analyzers = strategy.analyzers

    sharpe_analysis = analyzers.sharpe.get_analysis()
    dd_analysis = analyzers.dd.get_analysis()
    ret_analysis = analyzers.ret.get_analysis()
    trades_analysis = analyzers.trades.get_analysis()

    sharpe = sharpe_analysis.get("sharperatio")
    # DrawDown nests the headline figure under max.drawdown.
    max_drawdown = dd_analysis.get("max", {}).get("drawdown")
    total_return = ret_analysis.get("rtot")
    # TradeAnalyzer nests the count under total.total.
    total_trades = trades_analysis.get("total", {}).get("total", 0)

    raw: dict[str, Any] = {
        "sharpe": sharpe_analysis,
        "dd": dd_analysis,
        "ret": ret_analysis,
        "trades": trades_analysis,
    }

    return Metrics(
        sharpe=sharpe,
        max_drawdown=max_drawdown,
        total_return=total_return,
        total_trades=total_trades,
        raw=raw,
    )


__all__ = ["Metrics", "add_standard_analyzers", "extract_metrics"]
