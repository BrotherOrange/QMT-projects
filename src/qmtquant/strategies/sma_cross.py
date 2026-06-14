"""SMA double moving-average crossover strategy.

Migrated verbatim-in-spirit from the original ``test_backtrader.py`` smoke
test. The strategy combines:

* a fast/slow :class:`~backtrader.indicators.SMA` pair feeding a
  :class:`~backtrader.indicators.CrossOver` signal, and
* an :class:`~backtrader.indicators.RSI` indicator used purely to prove that
  indicator wiring works end-to-end.

Order/trade/indicator instrumentation is kept *inline* (no speculative
``BaseStrategy`` abstraction) so the test-suite can assert directly that:

* ``order_count`` increments when an order completes (orders actually fill),
* ``trade_count`` increments when ``notify_trade`` fires on a closed trade, and
* ``indicator_ok`` flips ``True`` once the RSI produces a real (non-NaN) value.
"""
from __future__ import annotations

import math

import backtrader as bt


class SmaCross(bt.Strategy):
    """Fast/slow SMA crossover entry with RSI indicator wiring.

    Parameters
    ----------
    fast:
        Period of the fast simple moving average. Default ``10``.
    slow:
        Period of the slow simple moving average. Default ``30``.
    rsi_period:
        Period of the RSI indicator. Default ``14``.

    Test-contract instance attributes (set in :meth:`__init__`):

    * ``order_count`` (int): number of completed orders.
    * ``trade_count`` (int): number of closed trades.
    * ``indicator_ok`` (bool): set ``True`` once the RSI yields a real value.
    * ``crossover``: the SMA :class:`~backtrader.indicators.CrossOver` signal.
    * ``rsi``: the :class:`~backtrader.indicators.RSI` indicator.
    """

    params = dict(fast=10, slow=30, rsi_period=14)

    def __init__(self) -> None:
        """Build indicators and initialise the instrumentation counters."""
        sma_fast = bt.indicators.SMA(self.data.close, period=self.p.fast)
        sma_slow = bt.indicators.SMA(self.data.close, period=self.p.slow)
        # CrossOver > 0 when fast crosses above slow, < 0 when below.
        self.crossover = bt.indicators.CrossOver(sma_fast, sma_slow)
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)

        # Test-contract instrumentation (kept inline on purpose).
        self.order_count: int = 0
        self.trade_count: int = 0
        self.indicator_ok: bool = False

    def next(self) -> None:
        """Run one bar: update RSI health flag, then act on the crossover."""
        # Prove the RSI indicator is producing real values (not warm-up NaN).
        if not math.isnan(self.rsi[0]):
            self.indicator_ok = True

        if self.position:
            # Exit the long position when the fast SMA crosses back below.
            if self.crossover[0] < 0:
                self.close()
        elif self.crossover[0] > 0:
            # Enter long when the fast SMA crosses above the slow SMA.
            self.buy()

    def notify_order(self, order: bt.Order) -> None:
        """Count fully completed orders (proves orders actually fill)."""
        if order.status == order.Completed:
            self.order_count += 1

    def notify_trade(self, trade: bt.Trade) -> None:
        """Count closed trades (proves ``notify_trade`` fires)."""
        if trade.isclosed:
            self.trade_count += 1


__all__ = ["SmaCross"]
