"""策略接口：:class:`Strategy` 抽象与运行上下文 :class:`Context`。

用户**继承 :class:`Strategy` 自己实现 ``on_bar``**（本框架不提供任何策略逻辑）。
``on_bar`` 收到的 :class:`Context` 暴露：当前 bar、历史序列、broker（下单/查询）、
以及 ``buy``/``sell`` 便捷下单。策略只依赖这些接口与 :class:`~qmtquant.live.broker.Broker`
抽象，故回测/模拟/实盘之间切换时策略代码无需改动。
"""

from __future__ import annotations

import abc

from ..live.broker import Broker, Order, OrderSide, OrderType, Position
from .feed import Bar


class Context:
    """传给策略的运行上下文。"""

    def __init__(self, broker: Broker, symbol: str, bar: Bar | None, history: list[Bar]) -> None:
        self.broker = broker
        self.symbol = symbol
        self.bar = bar
        self._history = history

    @property
    def now(self):
        """当前 bar 的时间戳（``on_init`` 时为 None）。"""
        return self.bar.ts if self.bar is not None else None

    def history(self, n: int, field: str = "close") -> list[float]:
        """返回截至当前 bar（含）最近 ``n`` 根的某字段序列（最旧→最新）。"""
        bars = self._history[-n:]
        return [getattr(b, field) for b in bars]

    @property
    def cash(self) -> float:
        return self.broker.get_cash()

    def position(self, symbol: str | None = None) -> Position | None:
        """返回某标的当前持仓（默认当前标的），无则 None。"""
        symbol = symbol or self.symbol
        for p in self.broker.get_positions():
            if p.symbol == symbol:
                return p
        return None

    # ---- 便捷下单（转发到 broker.place_order）--------------------------
    def buy(self, size: int, price: float | None = None, *, symbol: str | None = None) -> str:
        return self.order(OrderSide.BUY, size, price, symbol=symbol)

    def sell(self, size: int, price: float | None = None, *, symbol: str | None = None) -> str:
        return self.order(OrderSide.SELL, size, price, symbol=symbol)

    def order(self, side: OrderSide, size: int, price: float | None = None, *,
              symbol: str | None = None) -> str:
        otype = OrderType.LIMIT if price is not None else OrderType.MARKET
        return self.broker.place_order(
            Order(symbol=symbol or self.symbol, side=side, size=size, price=price, type=otype)
        )


class Strategy(abc.ABC):
    """策略基类。用户继承并实现 :meth:`on_bar`（``on_init``/``on_stop`` 可选）。"""

    def on_init(self, ctx: Context) -> None:
        """运行开始前调用一次（可做参数/状态初始化）。"""

    @abc.abstractmethod
    def on_bar(self, ctx: Context) -> None:
        """每根 bar 收盘后调用：在此读数据、下单。"""

    def on_stop(self, ctx: Context) -> None:
        """运行结束后调用一次。"""


__all__ = ["Strategy", "Context"]
