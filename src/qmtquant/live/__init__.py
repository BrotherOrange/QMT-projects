"""Live-trading subpackage (future-facing).

Re-exports the :class:`~qmtquant.live.broker.Broker` abstraction, its domain
types, and the empty-shell :class:`~qmtquant.live.xtquant_broker.XtQuantBroker`
so callers depend on the abstraction rather than the concrete SDK.

These are empty shells today: the xtquant/miniQMT wiring is implemented after
QMT trading qualification is obtained.
"""

from __future__ import annotations

from .broker import Broker, Order, OrderSide, OrderType, Position
from .xtquant_broker import XtQuantBroker

__all__ = ["Broker", "Order", "OrderSide", "OrderType", "Position", "XtQuantBroker"]
