"""交易 broker 子包。

再导出 :class:`~qmtquant.live.broker.Broker` 抽象与域类型、本地模拟
:class:`~qmtquant.live.paper_broker.PaperBroker`（回测/模拟用），以及未来实盘的
:class:`~qmtquant.live.xtquant_broker.XtQuantBroker`（仍为 stub）。三者实现同一 `Broker`
抽象，故策略在它们之间切换时代码不变。
"""

from __future__ import annotations

from .broker import Broker, Order, OrderSide, OrderType, Position
from .paper_broker import PaperBroker, AShareRules, Fill
from .xtquant_broker import XtQuantBroker

__all__ = [
    "Broker",
    "Order",
    "OrderSide",
    "OrderType",
    "Position",
    "PaperBroker",
    "AShareRules",
    "Fill",
    "XtQuantBroker",
]
