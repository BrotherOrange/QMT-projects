"""Contract tests for the xtquant data source + the live-trading empty shells.

The ``live/`` broker (``XtQuantBroker``) is deliberately unimplemented until QMT
trading qualification work is done. These tests pin the contracts:

    * the xtquant shells import cleanly (no ``import xtquant`` at module top),
    * ``XtQuantDataSource`` is now IMPLEMENTED (data side) -- a live fetch test is
      provided but skipped unless ``QMT_LIVE_TESTS=1`` and the SDK/terminal exist,
    * every ``XtQuantBroker`` operational method still raises ``NotImplementedError``,
    * the abstract :class:`~qmtquant.live.broker.Broker` cannot be instantiated.
"""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
import pytest

from qmtquant.data.sources.base import OHLCV_COLUMNS
from qmtquant.data.sources.xtquant_source import XtQuantDataSource
from qmtquant.live.broker import Broker, Order, OrderSide
from qmtquant.live.xtquant_broker import XtQuantBroker


def test_xtquant_source_imports_without_sdk() -> None:
    """The module imports and the source constructs WITHOUT the SDK.

    The lazy ``import xtquant`` lives inside ``get_dataframe``; merely importing
    the module / constructing the source must not require the SDK. (On a machine
    with no xtquant, the module-level import at the top of this file would fail
    at collection if there were a top-level ``import xtquant`` -- so CI enforces
    the no-top-level-import contract.)
    """
    src = XtQuantDataSource(period="1d", dividend_type="front", download=False)
    assert src.period == "1d"
    assert src.dividend_type == "front"
    assert src.download is False


@pytest.mark.skipif(
    not os.environ.get("QMT_LIVE_TESTS"),
    reason="需要运行中的 miniQMT 终端 + 已接入的 xtquant；设 QMT_LIVE_TESTS=1 启用",
)
def test_xtquant_source_live_fetch() -> None:
    """Live: pull real daily bars and confirm the OHLCV contract holds."""
    pytest.importorskip("xtquant")
    src = XtQuantDataSource(period="1d")
    df = src.get_dataframe("000001.SZ", datetime(2026, 1, 1), datetime(2026, 6, 1))
    assert len(df) > 0
    assert list(df.columns) == list(OHLCV_COLUMNS)
    assert isinstance(df.index, pd.DatetimeIndex)


def test_xtquant_broker_methods_not_implemented() -> None:
    """Every operational method on the broker stub raises NotImplementedError."""
    broker = XtQuantBroker("test-account")
    order = Order(symbol="000001.SZ", side=OrderSide.BUY, size=100)

    with pytest.raises(NotImplementedError):
        broker.connect()
    with pytest.raises(NotImplementedError):
        broker.disconnect()
    with pytest.raises(NotImplementedError):
        broker.place_order(order)
    with pytest.raises(NotImplementedError):
        broker.cancel_order("some-id")
    with pytest.raises(NotImplementedError):
        broker.get_positions()
    with pytest.raises(NotImplementedError):
        broker.get_cash()


def test_broker_abc_not_instantiable() -> None:
    """The abstract Broker base class cannot be instantiated directly."""
    with pytest.raises(TypeError):
        Broker()  # type: ignore[abstract]
