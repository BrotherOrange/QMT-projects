"""Live broker/trader abstraction (framework-agnostic).

This module defines the order/position *domain types* and the abstract
:class:`Broker` contract that a real trading backend (e.g. an ``xtquant``
miniQMT trader) implements. It is intentionally free of any vendor SDK
import so that callers depend on the abstraction, not the concrete SDK.

Dependency direction: ``live`` is an independent, future-facing sibling of
the backtest stack. Nothing here imports ``xtquant`` -- the concrete
implementation lives in :mod:`qmtquant.live.xtquant_broker` and imports the
SDK lazily inside its methods.
"""

from __future__ import annotations

import abc
import enum
from dataclasses import dataclass


class OrderSide(enum.Enum):
    """Direction of an order."""

    BUY = "buy"
    SELL = "sell"


class OrderType(enum.Enum):
    """Execution style of an order."""

    MARKET = "market"
    LIMIT = "limit"


@dataclass
class Order:
    """A trade instruction handed to a :class:`Broker`.

    Attributes:
        symbol: Instrument identifier (broker-specific convention, e.g. ``"600000.SH"``).
        side: Buy or sell, see :class:`OrderSide`.
        size: Number of shares/contracts (positive integer).
        price: Limit price; ``None`` for market orders.
        type: Order execution style, see :class:`OrderType`. Defaults to MARKET.
        id: Broker-assigned identifier, populated after the order is placed.
    """

    symbol: str
    side: OrderSide
    size: int
    price: float | None = None
    type: OrderType = OrderType.MARKET
    id: str | None = None


@dataclass
class Position:
    """A held position as reported by the broker.

    Attributes:
        symbol: Instrument identifier.
        size: Net quantity currently held.
        avg_price: Average entry/cost price of the position.
    """

    symbol: str
    size: int
    avg_price: float


class Broker(abc.ABC):
    """Abstract live-trading contract.

    Concrete subclasses wire this to a real trading backend. The interface is
    deliberately minimal: session lifecycle, order placement/cancellation, and
    account/position queries.
    """

    @abc.abstractmethod
    def connect(self) -> None:
        """Establish the trading session (login / handshake)."""

    @abc.abstractmethod
    def disconnect(self) -> None:
        """Tear down the trading session and release resources."""

    @abc.abstractmethod
    def place_order(self, order: Order) -> str:
        """Submit ``order`` and return the broker-assigned order id."""

    @abc.abstractmethod
    def cancel_order(self, order_id: str) -> None:
        """Cancel a previously placed order by its broker id."""

    @abc.abstractmethod
    def get_positions(self) -> list[Position]:
        """Return the current open positions."""

    @abc.abstractmethod
    def get_cash(self) -> float:
        """Return available cash in the trading account."""


__all__ = ["Broker", "Order", "OrderSide", "OrderType", "Position"]
