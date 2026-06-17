"""本地模拟撮合 broker（实现 :class:`~qmtquant.live.broker.Broker` 抽象）。

`PaperBroker` 在内存里模拟 A 股交易：现金、持仓、撮合、费用全部本地计算，
**绝不调用 xtquant.xttrader、绝不触碰真实资金账户**。它与未来的 `XtQuantBroker`
实现同一个 `Broker` 抽象，因此策略代码从模拟切到实盘只需更换 broker 实例。

成交模型（配合 :mod:`qmtquant.runtime.engine`）：策略在第 t 根收盘时下单进入挂单队列，
由引擎在第 t+1 根调用 :meth:`process_pending` 撮合——市价单成交于该根开盘价，
限价单按该根 ``[low, high]`` 盘中撮合。即"收盘决策、下一根开盘成交"，无未来函数。

A 股规则（见 :class:`AShareRules`）：T+1、涨跌停不可成交、整手 100、
佣金(双向,最低5元) + 印花税(仅卖出) + 过户费(双向)。
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .broker import Broker, Order, OrderSide, OrderType, Position


@dataclass(frozen=True)
class AShareRules:
    """A 股交易规则与费率（默认值为常见的普通账户设置）。"""

    commission_rate: float = 0.0003        # 佣金 万三
    min_commission: float = 5.0            # 单笔最低佣金
    stamp_tax_rate: float = 0.0005         # 印花税（仅卖出）
    transfer_fee_rate: float = 0.00001     # 过户费（双向）
    lot_size: int = 100                    # 整手股数
    enforce_t1: bool = True                # T+1：当日买入当日不可卖
    enforce_price_limit: bool = True       # 涨跌停不可成交


@dataclass
class Fill:
    """一笔成交记录。"""

    ts: object
    symbol: str
    side: OrderSide
    size: int
    price: float
    commission: float
    stamp_tax: float
    transfer_fee: float
    order_id: str


@dataclass
class _Pos:
    """内部持仓（含 T+1 可卖/锁定拆分）。``size == sellable + locked_today``。"""

    symbol: str
    size: int = 0
    avg_price: float = 0.0
    sellable: int = 0          # T+1 已解锁、可卖
    locked_today: int = 0      # 当日买入、锁定


class PaperBroker(Broker):
    """本地模拟撮合 broker（A 股规则）。策略可见面严格等于 :class:`Broker` 抽象。"""

    def __init__(self, *, cash: float = 100_000.0, rules: AShareRules | None = None) -> None:
        self._cash = float(cash)
        self.rules = rules or AShareRules()
        self._positions: dict[str, _Pos] = {}
        self._pending: list[Order] = []
        self._market: dict[str, object] = {}   # symbol -> Bar（当前可成交行情）
        self._trades: list[Fill] = []
        self._oid = 0
        self._connected = False

    # ---- Broker 抽象 ---------------------------------------------------
    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def place_order(self, order: Order) -> str:
        """登记一笔订单，返回订单号。实际撮合在下一根 :meth:`process_pending`。

        买入数量在此向下取整到整手；其余校验（涨跌停 / T+1 / 现金）在成交时进行。
        """
        self._oid += 1
        order.id = str(self._oid)
        if order.side is OrderSide.BUY and self.rules.lot_size > 1:
            order.size = (order.size // self.rules.lot_size) * self.rules.lot_size
        if order.size > 0:
            self._pending.append(order)
        return order.id

    def cancel_order(self, order_id: str) -> None:
        self._pending = [o for o in self._pending if o.id != order_id]

    def get_positions(self) -> list[Position]:
        return [
            Position(symbol=p.symbol, size=p.size, avg_price=p.avg_price)
            for p in self._positions.values()
            if p.size > 0
        ]

    def get_cash(self) -> float:
        return self._cash

    # ---- 引擎接口（撮合/行情/结算，非策略可见面）-----------------------
    def update_market(self, bar) -> None:
        """设置某标的当前可成交行情（引擎每根 bar 调用）。"""
        self._market[bar.symbol] = bar

    def roll_day(self) -> None:
        """日切：T+1 解锁（当日锁定的持仓变为可卖）。"""
        for p in self._positions.values():
            p.sellable += p.locked_today
            p.locked_today = 0

    def equity(self) -> float:
        """总资产 = 现金 + 持仓按当前 bar 收盘价的市值。"""
        mv = 0.0
        for p in self._positions.values():
            bar = self._market.get(p.symbol)
            if bar is not None and p.size:
                mv += p.size * bar.close
        return self._cash + mv

    def process_pending(self) -> None:
        """对挂单逐一尝试撮合（市价成交于当前根开盘，限价按盘中 [low,high]）。"""
        still: list[Order] = []
        for o in self._pending:
            bar = self._market.get(o.symbol)
            if bar is None or o.size <= 0:
                still.append(o)
                continue
            filled = self._try_fill(o, bar)
            if not filled:
                still.append(o)
        self._pending = still

    # ---- 内部撮合 ------------------------------------------------------
    def _fill_price(self, o: Order, bar) -> float | None:
        """返回成交价；不满足成交条件返回 None。"""
        if o.type is OrderType.MARKET:
            return bar.open
        # 限价单：买价≥bar.low 可成交（取 min(open,limit)）；卖价≤bar.high 可成交（取 max(open,limit)）
        if o.price is None:
            return bar.open
        if o.side is OrderSide.BUY:
            return min(bar.open, o.price) if bar.low <= o.price else None
        return max(bar.open, o.price) if bar.high >= o.price else None

    def _try_fill(self, o: Order, bar) -> bool:
        price = self._fill_price(o, bar)
        if price is None:
            return False  # 限价未触及，继续挂着

        r = self.rules
        if o.side is OrderSide.BUY:
            # 涨停不可买
            if r.enforce_price_limit and bar.up_limit is not None and price >= bar.up_limit:
                return False
            amount = price * o.size
            commission = max(amount * r.commission_rate, r.min_commission)
            transfer = amount * r.transfer_fee_rate
            cost = amount + commission + transfer
            if cost > self._cash:
                return True  # 现金不足：拒单（移出挂单队列，不成交）
            self._cash -= cost
            p = self._positions.setdefault(o.symbol, _Pos(symbol=o.symbol))
            new_size = p.size + o.size
            p.avg_price = (p.avg_price * p.size + price * o.size) / new_size
            p.size = new_size
            p.locked_today += o.size  # T+1 锁定
            self._trades.append(Fill(bar.ts, o.symbol, o.side, o.size, price,
                                     commission, 0.0, transfer, o.id or ""))
            return True

        # 卖出
        p = self._positions.get(o.symbol)
        if p is None or p.size <= 0:
            return True  # 无持仓可卖：放弃
        # 跌停不可卖
        if r.enforce_price_limit and bar.down_limit is not None and price <= bar.down_limit:
            return False
        qty = min(o.size, p.size)
        if r.enforce_t1:
            qty = min(qty, p.sellable)
        if qty <= 0:
            return False  # T+1 未解锁，继续挂着
        amount = price * qty
        commission = max(amount * r.commission_rate, r.min_commission)
        stamp = amount * r.stamp_tax_rate
        transfer = amount * r.transfer_fee_rate
        self._cash += amount - commission - stamp - transfer
        p.size -= qty
        p.sellable -= qty
        if p.size == 0:
            p.avg_price = 0.0
        self._trades.append(Fill(bar.ts, o.symbol, o.side, qty, price,
                                 commission, stamp, transfer, o.id or ""))
        return True

    @property
    def trades(self) -> list[Fill]:
        """成交流水（只读内省，供查看模拟结果）。"""
        return list(self._trades)


__all__ = ["PaperBroker", "AShareRules", "Fill"]
