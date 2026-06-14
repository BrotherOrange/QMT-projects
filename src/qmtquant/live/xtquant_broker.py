"""Empty-shell xtquant (miniQMT) broker.

Concrete :class:`~qmtquant.live.broker.Broker` subclass targeting the
``xtquant.xttrader`` SDK shipped with miniQMT. Every method is a stub that
raises :class:`NotImplementedError` with a TODO describing the post-QMT-
qualification work, so the package imports cleanly today and the live wiring
can be filled in once trading access is granted.

Note: there is intentionally **no** top-level ``import xtquant``. The SDK is
only available inside a licensed miniQMT environment, so it must be imported
lazily inside the methods (after qualification).
"""

from __future__ import annotations

from .broker import Broker, Order, Position

_TODO = (
    "TODO: implement via xtquant.xttrader after QMT qualification: "
    "import XtQuantTrader/StockAccount inside methods; account login; "
    "order_stock / cancel_order_stock / query_stock_positions / query_stock_asset."
)


class XtQuantBroker(Broker):
    """miniQMT live broker stub backed by ``xtquant.xttrader`` (not yet wired)."""

    def __init__(self, account_id: str, *, mini_qmt_path: str | None = None) -> None:
        """Record connection parameters for later use.

        Args:
            account_id: The QMT capital/stock account id used to log in.
            mini_qmt_path: Filesystem path to the running miniQMT ``userdata_mini``
                directory that ``XtQuantTrader`` connects to. Optional until the
                live session is implemented.
        """
        self.account_id = account_id
        self.mini_qmt_path = mini_qmt_path

    def connect(self) -> None:
        """Establish the miniQMT trading session.

        TODO (post-qualification): ``from xtquant.xttrader import XtQuantTrader``
        and ``from xtquant.xttype import StockAccount``; construct
        ``XtQuantTrader(self.mini_qmt_path, session_id)``; call ``start()`` then
        ``connect()``; ``subscribe(StockAccount(self.account_id))``.
        """
        raise NotImplementedError(_TODO)

    def disconnect(self) -> None:
        """Tear down the miniQMT trading session.

        TODO (post-qualification): call ``XtQuantTrader.stop()`` and drop the
        trader/account references.
        """
        raise NotImplementedError(_TODO)

    def place_order(self, order: Order) -> str:
        """Submit ``order`` via ``xtquant.xttrader.XtQuantTrader.order_stock``.

        TODO (post-qualification): map :class:`OrderSide`/:class:`OrderType` to
        ``xtconstant`` codes (e.g. ``STOCK_BUY``/``STOCK_SELL``,
        ``FIX_PRICE``/``LATEST_PRICE``); call ``order_stock(account, symbol,
        order_type, volume, price_type, price, ...)``; return the resulting
        order id as ``str``.
        """
        raise NotImplementedError(_TODO)

    def cancel_order(self, order_id: str) -> None:
        """Cancel an order via ``XtQuantTrader.cancel_order_stock``.

        TODO (post-qualification): call ``cancel_order_stock(account,
        int(order_id))`` (or ``cancel_order_stock_sysid`` when using the
        exchange system id).
        """
        raise NotImplementedError(_TODO)

    def get_positions(self) -> list[Position]:
        """Query holdings via ``XtQuantTrader.query_stock_positions``.

        TODO (post-qualification): call ``query_stock_positions(account)`` and
        map each ``XtPosition`` (stock_code / volume / avg_price /
        open_price) to a :class:`Position`.
        """
        raise NotImplementedError(_TODO)

    def get_cash(self) -> float:
        """Query available cash via ``XtQuantTrader.query_stock_asset``.

        TODO (post-qualification): call ``query_stock_asset(account)`` and return
        the ``XtAsset.cash`` field as ``float``.
        """
        raise NotImplementedError(_TODO)


__all__ = ["XtQuantBroker"]
