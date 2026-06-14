"""Contract tests for the live-trading empty shells.

The ``live/`` package and the ``XtQuantDataSource`` are deliberately
unimplemented until QMT trading qualification is obtained. These tests pin the
"shell" contract:

    * the xtquant shells import cleanly (no ``import xtquant`` at module top),
    * every operational method raises ``NotImplementedError``, and
    * the abstract :class:`~qmtquant.live.broker.Broker` cannot be instantiated.

Keeping these as tests ensures the shells stay shells until someone
intentionally implements them (which will flip these tests red on purpose).
"""

from __future__ import annotations

import pytest

from qmtquant.data.sources.xtquant_source import XtQuantDataSource
from qmtquant.live.broker import Broker, Order, OrderSide
from qmtquant.live.xtquant_broker import XtQuantBroker


def test_xtquant_source_not_implemented() -> None:
    """XtQuantDataSource imports but its data accessor is unimplemented."""
    src = XtQuantDataSource()
    with pytest.raises(NotImplementedError):
        src.get_dataframe("000001.SZ")


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
