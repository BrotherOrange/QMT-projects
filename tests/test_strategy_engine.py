"""Smoke checks #3-12: strategy + engine behaviour.

All assertions run against the shared, session-scoped ``result`` fixture
(the backtest is executed once in ``conftest.py``). We verify that:

    * indicators produced values (``indicator_ok`` flipped True),
    * orders were filled (``order_count > 0``),
    * ``notify_trade`` fired (``trade_count > 0``),
    * the broker value moved (commission + trading changed cash), and
    * all four analyzers returned values (Sharpe tolerated as None,
      DrawDown / Returns / TradeAnalyzer present).
"""

from __future__ import annotations

from qmtquant.backtest.engine import BacktestResult


def test_indicators_produced_values(result: BacktestResult) -> None:
    """RSI/SMA/CrossOver computed -> strategy set indicator_ok True."""
    assert result.strategy.indicator_ok is True


def test_orders_filled(result: BacktestResult) -> None:
    """At least one order reached Completed status."""
    assert result.strategy.order_count > 0


def test_notify_trade_fired(result: BacktestResult) -> None:
    """At least one trade closed (notify_trade saw isclosed)."""
    assert result.strategy.trade_count > 0


def test_broker_value_changed(result: BacktestResult) -> None:
    """Broker portfolio value moved between start and end (commission/trades)."""
    assert result.end_value != result.start_value


def test_analyzer_sharpe(result: BacktestResult) -> None:
    """SharpeRatio analyzer ran; value present or tolerated None."""
    metrics = result.metrics
    # The attribute must exist; backtrader may legitimately return None.
    assert hasattr(metrics, "sharpe")
    assert metrics.sharpe is None or isinstance(metrics.sharpe, float)
    # Raw analyzer payload must be available under its name.
    assert "sharpe" in metrics.raw


def test_analyzer_drawdown(result: BacktestResult) -> None:
    """DrawDown analyzer returned a value (or tolerated None)."""
    metrics = result.metrics
    assert hasattr(metrics, "max_drawdown")
    assert metrics.max_drawdown is None or isinstance(metrics.max_drawdown, float)
    assert "dd" in metrics.raw


def test_analyzer_returns(result: BacktestResult) -> None:
    """Returns analyzer returned a total-return value (or tolerated None)."""
    metrics = result.metrics
    assert hasattr(metrics, "total_return")
    assert metrics.total_return is None or isinstance(metrics.total_return, float)
    assert "ret" in metrics.raw


def test_analyzer_trades(result: BacktestResult) -> None:
    """TradeAnalyzer returned a total trade count (>= 0, ints only)."""
    metrics = result.metrics
    assert isinstance(metrics.total_trades, int)
    assert metrics.total_trades >= 0
    assert "trades" in metrics.raw
