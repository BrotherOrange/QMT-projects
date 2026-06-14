"""Cerebro builder/runner — the heart of the backtest engine.

Migrated from the old inline cerebro assembly in ``test_backtrader.py``. The
two concerns are deliberately decoupled:

* :func:`build_cerebro` — *how* to assemble a cerebro (feed + strategy + broker
  + commission + sizer + analyzers), and
* :func:`run_backtest` — *run it and collect* a structured
  :class:`BacktestResult`.

The engine depends only on the :class:`~qmtquant.data.sources.base.DataSource`
abstraction and a :class:`bt.Strategy` subclass. The synthetic source is the
sole concrete fallback and is imported lazily so the engine never hard-couples
to a specific data backend.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import backtrader as bt

from ..config import BacktestConfig
from ..data.sources.base import DataSource
from ..strategies.sma_cross import SmaCross
from .analyzers import Metrics, add_standard_analyzers, extract_metrics


@dataclass
class BacktestResult:
    """Structured result of a single backtest run.

    Attributes
    ----------
    cerebro:
        The configured (and already-run) cerebro instance, e.g. for plotting.
    strategy:
        The first strategy instance returned by ``cerebro.run()``.
    start_value:
        Broker portfolio value before the run.
    end_value:
        Broker portfolio value after the run.
    metrics:
        Extracted headline :class:`Metrics`.
    """

    cerebro: bt.Cerebro
    strategy: bt.Strategy
    start_value: float
    end_value: float
    metrics: Metrics


def build_cerebro(
    feed: bt.feeds.PandasData,
    strategy: type[bt.Strategy] = SmaCross,
    *,
    config: BacktestConfig | None = None,
    strategy_kwargs: dict[str, Any] | None = None,
) -> bt.Cerebro:
    """Assemble a cerebro from a feed, strategy and config.

    Wires the data feed, strategy, broker cash, commission, a
    :class:`~backtrader.sizers.FixedSize` sizer and the standard analyzer
    preset. Does *not* run the cerebro.

    Parameters
    ----------
    feed:
        A backtrader pandas data feed.
    strategy:
        The strategy class to add. Defaults to :class:`SmaCross`.
    config:
        Backtest configuration; defaults to :class:`BacktestConfig`.
    strategy_kwargs:
        Optional keyword arguments forwarded to the strategy.
    """
    config = config or BacktestConfig()

    cerebro = bt.Cerebro()
    cerebro.adddata(feed)
    cerebro.addstrategy(strategy, **(strategy_kwargs or {}))

    cerebro.broker.setcash(config.broker.cash)
    cerebro.broker.setcommission(commission=config.broker.commission)
    cerebro.addsizer(bt.sizers.FixedSize, stake=config.stake)

    add_standard_analyzers(cerebro)
    return cerebro


def run_backtest(
    source: DataSource | None = None,
    *,
    symbol: str = "SYNTH",
    strategy: type[bt.Strategy] = SmaCross,
    config: BacktestConfig | None = None,
    feed: bt.feeds.PandasData | None = None,
    strategy_kwargs: dict[str, Any] | None = None,
) -> BacktestResult:
    """Run a backtest end-to-end and collect a :class:`BacktestResult`.

    Parameters
    ----------
    source:
        A :class:`~qmtquant.data.sources.base.DataSource`. When ``None`` (and no
        explicit ``feed`` is given) a :class:`SyntheticDataSource` is created
        lazily as the default fallback.
    symbol:
        Symbol passed to ``source.to_feed``. Defaults to ``"SYNTH"``.
    strategy:
        Strategy class to run. Defaults to :class:`SmaCross`.
    config:
        Backtest configuration; defaults to :class:`BacktestConfig`.
    feed:
        A pre-built feed; if provided, ``source``/``symbol`` are ignored.
    strategy_kwargs:
        Optional keyword arguments forwarded to the strategy.
    """
    if feed is None:
        if source is None:
            # Lazy import keeps the engine decoupled from concrete sources.
            from ..data.sources.synthetic import SyntheticDataSource

            source = SyntheticDataSource()
        feed = source.to_feed(symbol)

    cerebro = build_cerebro(
        feed,
        strategy,
        config=config,
        strategy_kwargs=strategy_kwargs,
    )

    start_value = cerebro.broker.getvalue()
    strat = cerebro.run()[0]
    end_value = cerebro.broker.getvalue()

    return BacktestResult(
        cerebro=cerebro,
        strategy=strat,
        start_value=start_value,
        end_value=end_value,
        metrics=extract_metrics(strat),
    )


__all__ = ["BacktestResult", "build_cerebro", "run_backtest"]
